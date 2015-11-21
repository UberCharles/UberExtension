var app = {
  server: "http://localhost:8888/api/",
  currentLocation: null,
  selectedDestination: null,
  currentRequest: null,
  JWT: null
}

// TODO: Make products load in background thread
app.initialize = function() {
  this.isAuthenticated(function(cookie) {
    if (cookie) {
      // Get JWT from cookie (used to authenticate websocket connections)
      console.log(cookie);
      this.JWT = cookie.value;
      console.log(this.JWT);
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
      chrome.tabs.create({ url: "http://localhost:8888/login" });
    }
  }.bind(this));
};

app.initializeRequestStatusWebsockets = function() {
  var ws = new WebSocket("ws://localhost:8888/api/request_status");
  ws.onopen = function() {
     ws.send(JSON.stringify({type: "auth", message: this.JWT}));
  }.bind(this);
  ws.onmessage = function (event) {
     console.log(JSON.parse(event.data));
  };
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
    var newRowString = '<tr class="product-row"><td>' +
      product.display_name + '</td><td>' + 
      product.description + '</td><td>' + 
      // Display N/A if no price details
      (product.price_details ? product.price_details.cost_per_distance : 'N/A') + '</td></tr>';
    var $newRow = $(newRowString).attr('data-product-id', product.product_id);
    $('#products-table').append($newRow);
  });

  // Remove loading bar
  $('#products-loader').removeClass("progress");

  // Add click handler for requesting a ride
  // Should probably be a separate function
  $('.product-row').click(function(event) {
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

    $.ajax({
      url: this.server + "requests",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify(requestDetails)
    })
      .done(function(response) {
        this.currentRequest = response;
        console.log(this.currentRequest);
      }.bind(this));
  }.bind(this));
}

app.getProducts = function() {
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
  }.bind(this));
};

app.isAuthenticated = function(callback) {
  document.addEventListener('DOMContentLoaded', function() {
    var cookieDetails = {
      url: "http://localhost:8888/",
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

app.initialize();