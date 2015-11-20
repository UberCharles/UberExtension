$(function() {
  // Copied from http://jsfiddle.net/briguy37/2mvfd/
  // Just need something that looks like UUID's, actual values don't matter
  function generateUUID() {
    var d = new Date().getTime();
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
  };
  $('#webhook-button').click(function(event) {
    var webhookEventDetails = {
      event_id: generateUUID(),
      event_time: Date.now(),
      event_type: "requests.status_changed",
      meta: {
        resource_id: $('#request-id').val(),
        resource_type: "request",
        // sets status based on radio buttons
        status: $('input[type=radio]:checked').attr("id")
      },
      resource_href: "https://api.uber.com/v1/requests/" + $('#request-id').val()
    }
    $.post($('#endpoint-id').val(), JSON.stringify(webhookEventDetails));
  });
});