var reminders = {
  datePicker: null,
  timePicker: null
};

reminders.initialize = function() {
  this.initializeDayPicker();
  this.initializeDatePicker();
  this.initializeLocationAutocomplete();
}

reminders.initializeDatePicker = function() {
  $date_input = $('#event_date').pickadate({
    // Can't set reminders in past
    min: true,
    onSet: function(setDate) {
      var newDate = new Date(setDate.select);
      // If the new date is today, then set the minimum time to "true" which
      // Prevents any time in the past from being selected
      if (newDate.toDateString() === new Date().toDateString()) {
        this.timePicker.set("min", true)
      // Else if the date is in the future (date picker won't allow you to select
      // Dates in the past), allow any time of the day 
      } else {
        this.timePicker.set("min", new Date(setDate.select))
      }
    }.bind(this)
  });
  this.datePicker = $date_input.pickadate('picker');
  // Initialize date picker to current day
  this.datePicker.set("select", new Date());
}

reminders.initializeDayPicker = function() {
  $time_input = $('#event_time').pickatime({
    min: true
  });
  this.timePicker = $time_input.pickatime('picker');
}

reminders.initializeLocationAutocomplete = function() {
  autocompleteService = new google.maps.places.Autocomplete($('#event_location').get(0));
  autocompleteService.addListener('place_changed', function() {

    var place = autocompleteService.getPlace();
    this.selectedDestination = {
      latitude: place.geometry.location.lat(),
      longitude: place.geometry.location.lng()
    }

  }.bind(this));
}

$(function() {
  reminders.initialize();
});