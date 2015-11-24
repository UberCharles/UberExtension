var app = {
  server: "https:/uber-extension.herokuapp.com/api/",
  websocketUrl: "ws://uber-extension.herokuapp.com/api/request_status",
  currentLocation: null,
  selectedDestination: null,
  currentRequest: null,
  JWT: null
}

// TODO: Make products load in background thread
app.initialize = function() {
  this.isAuthenticated(function(cookie) {
    if (cookie) {
      this.startLoading("Determining your location...");
      // Get JWT from cookie (used to authenticate websocket connections)
      this.JWT = cookie.value;
      this.getLocation(function() {
        if (this.currentLocation) {
          this.getProducts();
          this.loadAutoComplete();
          this.initializeRequestStatusWebsockets();
        } else {
          // Handle no location case
        }
      }.bind(this));
    // If not authenticated, create new tab with login page
    } else {
      chrome.tabs.create({ url: "https://uber-extension.herokuapp.com/login" });
    }
  }.bind(this));
};

app.removeProducts = function() {
  $('tr').remove();
}

app.startLoading = function(message) {
  $('#loading-message').text(message);
  $('#loading-area').css("display", "block");
  this.removeProducts();
}

app.stopLoading = function(message) {
  $('#loading-message').text("");
  $('#loading-area').css("display", "none");
}

app.initializeRequestStatusWebsockets = function() {
  var ws = new WebSocket(this.websocketUrl);
  ws.onopen = function() {
    console.log("Websocket connection opened!");
    ws.send(JSON.stringify({type: "auth", message: this.JWT}));
  }.bind(this);
  ws.onmessage = function (event) {
    requestEvent = JSON.parse(event.data);
    console.log(requestEvent);
    if (requestEvent.type === "requests.status_changed") {
      if (requestEvent.status === "no_drivers_available") {
        this.stopLoading();
        this.removeRequest();
        this.getProducts();
      }

      if (requestEvent.status === "arriving") {
        this.startLoading("Your uber is arriving!");
      }

      if (requestEvent.status === "in_progress") {
        this.startLoading("Ride in progress!");
      }

      // Does uber automatically find a new driver if he cancels, or does the user need to request again?
      if (requestEvent.status === "driver_canceled") {
        this.stopLoading();
        this.removeRequest();
        this.getProducts();
      }

      if (requestEvent.status === "completed") {
        this.stopLoading();
        this.removeRequest();
        this.getProducts();
      }

      if (requestEvent.status === "processing") {
        this.startLoading("Request acknowledged! Searching for a driver...");
      }

      if (requestEvent.status === "rider_canceled") {
        this.stopLoading();
        this.removeRequest();
        this.getProducts();
      }

      if (requestEvent.status === "accepted") {
        console.log(requestEvent);
        if (requestEvent.details) {
          this.renderRequest(requestEvent.details);
        } else {
          this.startLoading("Your driver is on the way!");
        }
      }
    }
  }.bind(this);
  ws.onclose = function(event) {
    console.log("Websocket connection closed!");
  }.bind(this);
}

app.getLocation = function(callback) {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
      this.currentLocation = {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude
      }
      callback();
    }.bind(this));
  } else {
    this.currentLocation = null;
    callback();
  }
};

app.displayProducts = function(products) {
  products.forEach(function(product) {
    var newRowString = '<tr class="product-row">' + 
      '<td class="product-name">' + product.display_name + '</td>' + 
      '<td class="product-description">' + product.description + '</td>' + 
      // Display N/A if no price details
      '<td class="product-price">' + (product.price_details ? product.price_details.cost_per_distance : 'N/A') + 
      '</td></tr>';
    var $newRow = $(newRowString).attr('data-product-id', product.product_id);
    $('#products-table').append($newRow);
  });

  // Remove loading bar
  this.stopLoading();

  // Add click handler for requesting a ride
  // Should probably be a separate function
  $('.product-row').click(function(event) {
    this.startLoading("Requesting an Uber...");
    var requestDetails = {
      product_id: $(event.currentTarget).data("productId"),
      start_latitude: this.currentLocation.latitude,
      start_longitude: this.currentLocation.longitude
    }

    // Set destination only if user selected one already
    if (this.selectedDestination) {
      requestDetails.end_latitude = this.selectedDestination.latitude,
      requestDetails.end_longitude = this.selectedDestination.longitude
    }

    console.log(requestDetails);

    $.ajax({
      url: this.server + "requests",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify(requestDetails)
    })
      .done(function(response) {
        this.currentRequest = response;
        console.log(this.currentRequest);
        this.startLoading("Request acknowledged! Searching for a driver...");
      }.bind(this));
  }.bind(this));
}

app.getProducts = function() {
  this.startLoading("Looking up Uber products available in your area");
  $.get(this.server + "products", this.currentLocation)
    .done(function(response) {
      this.displayProducts(response.products);
    }.bind(this));
};

app.loadAutoComplete = function() {
  autocompleteService = new google.maps.places.Autocomplete($('#search-places').get(0));
  autocompleteService.addListener('place_changed', function() {

    var place = autocompleteService.getPlace();
    this.selectedDestination = {
      latitude: place.geometry.location.lat(),
      longitude: place.geometry.location.lng()
    }

    var priceEstimateData = {
      start_latitude: this.currentLocation.latitude,
      start_longitude: this.currentLocation.longitude,
      end_latitude: this.selectedDestination.latitude,
      end_longitude: this.selectedDestination.longitude
    }

    $.get(this.server + "estimates/price", priceEstimateData)
    .done(function(response) {
      console.log(response);
      response.prices.forEach(function(productEstimate) {
        $('[data-product-id=' + productEstimate.product_id + ']')
          .find('.product-price').text(productEstimate.estimate);
      });
    }.bind(this));

  }.bind(this));
};

app.isAuthenticated = function(callback) {
  document.addEventListener('DOMContentLoaded', function() {
    var cookieDetails = {
      url: "https://uber-extension.herokuapp.com/",
      name: "JWT"
    }
    chrome.cookies.get(cookieDetails, function(cookie) {
      if (!cookie) {
        callback(false);
      } else {
        callback(cookie);
      }
    });
  });
}

app.renderRequest = function(requestDetails) {
  this.stopLoading();
  this.removeProducts();
  $('#driver-name').text(requestDetails.driver.name);
  $('#driver-number').text(requestDetails.driver.phone_number);
  $('#driver-image').attr("src", requestDetails.driver.picture_url || "resources/driver.png");
  $('#driver-eta').text(requestDetails.eta);
  $('#driver-car-make').text(requestDetails.vehicle.make);
  $('#driver-car-model').text(requestDetails.vehicle.model);
  $('#driver-car-license').text(requestDetails.vehicle.license_plate);
  $('#driver-car-image').text(requestDetails.vehicle.picture_url || "resources/vehicle.png")
  $('#request-display').css("display", "block");
  $('#cancel-request-button').click(function(event) {
    this.removeRequest();
    this.startLoading("Canceling request...");
    $.ajax({
      url: this.server + "requests/" + this.currentRequest.request_id,
      method: "DELETE",
    })
      .done(function(response) {
        this.stopLoading();
        this.getProducts();
      }.bind(this))
  }.bind(this));
}

app.removeRequest = function() {
  $('#driver-name').text("");
  $('#driver-number').text("");
  $('#driver-image').attr("src", "");
  $('#driver-eta').text("");
  $('#driver-car-make').text("");
  $('#driver-car-model').text("");
  $('#driver-car-license').text("");
  $('#request-display').css("display", "none");
}

app.initialize();