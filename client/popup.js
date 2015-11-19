var server = "http://localhost:8888/api/"

function displayProducts(products) {
  products.forEach(function(product) {
    var newRowString = "<tr><td>" +
      product.display_name + "</td><td>" + 
      product.description + "</td><td>" + 
      // Display N/A if no price details
      (product.price_details ? product.price_details.cost_per_distance : "N/A") + "</td></tr>";
    var $newRow = $(newRowString).attr("data-product-id", product.product_id);
    $('#products-table').append($newRow);
  });

  $('#products-loader').removeClass("progress");
}

// TODO: Make products load in background thread
function getProducts(coordinates) {
  $.get(server + "products", coordinates)
    .done(function(response) {
      console.log(response);
      displayProducts(response.products);
    });
}

function initializeApp() {
  var location;
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
      location = {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude
      }
      getProducts(location);
      autocompleteService = new google.maps.places.Autocomplete($('#search-places').get(0));
      autocompleteService.addListener('place_changed', function() {
        var place = autocompleteService.getPlace();
        var selectedLocation = {
          latitude: place.geometry.location.lat(),
          longitude: place.geometry.location.long()
        }
        console.log(selectedLocation);
      });
    });
  } else {
    // Notify usere we can't determine their location
  }
} 

document.addEventListener('DOMContentLoaded', function() {
  var cookieDetails = {
    url: "http://localhost:8888/",
    name: "JWT"
  }
  chrome.cookies.get(cookieDetails, function(cookie) {
    if (!cookie) {
      console.log("If triggered");
      chrome.tabs.create({ url: "http://localhost:8888/login" });
    } else {
      initializeApp();
    }
  });
});
