function initializeApp() {
  var location;
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
      location = {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude
      }
      console.log(location);
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
