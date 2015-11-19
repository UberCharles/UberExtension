var server = "http://localhost:8888/api/"

function displayProducts(products) {
  products.forEach(function(product) {
    var newRow = "<tr><td>" +
      product.display_name + "</td><td>" + 
      product.description + "</td><td>" + 
      product.price_details.cost_per_distance + "</td></tr>";

    $('#products-table').append(newRow);
  });
}

function getProducts(coordinates) {
  $.get(server + "products", coordinates)
    .done(function(response) {
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
