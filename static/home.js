var queryPAL = function(query, callback) {
  $.ajax({
    type: 'POST',
    url: '/api/pal',
    data: {
      quest: query,
      client: 'web'
    },
    success: function (response) {
      callback(response.response);
    }
  });
}

$(document).ready(function () {

  $('.prompt').focus();

  $('.prompt').on('keypress', function (e) {
    if (e.which == 13) {
      queryPAL($(this).val(), function (result) {
        $('.result').html(result);
      });
    }
  });

});
