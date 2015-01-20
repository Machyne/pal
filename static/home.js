var queryPAL = function(query, callback) {
  $.ajax({
    type: 'POST',
    url: '/api/pal',
    data: {
      query: query,
      client: 'web'
    },
    success: function (response) {
      callback(response.result.response);
    }
  });
};

$(document).ready(function () {

  var showResult = function (result) {
        $('.result').html(result);
      },
      prompt = $('.prompt'),
      sendQuery = function () {
        if (prompt.val().length > 0) {
          queryPAL(prompt.val(), showResult);
        }
      };

  prompt.focus();

  prompt.on('keypress', function (e) {
    // 'enter' key
    if (e.which == 13) {
      sendQuery();
    }
  }).on('change', sendQuery);

  $('#go-btn').on('click', sendQuery);

});
