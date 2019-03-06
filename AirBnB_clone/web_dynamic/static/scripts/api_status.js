$(document).ready(function () { 
  /* update status */
  let url = 'http://35.231.97.140:8002/api/v1/status/';
  $.get(url, function(status) {
    if (status.status === 'OK') {
      $('#api_status').addClass('available');
    } else {
      $('#api_status').removeClass('available');
    }
  });
});
