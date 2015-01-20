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
        $('.history-result').prepend('<li>' + result + '</li>');
      },
      prompt = $('.prompt'),
      sendQuery = function () {
        var query = prompt.val();
        if (query.length > 0) {
          queryPAL(query, showResult);
          $('.history-prompt').prepend('<li>' + query + '</li>');
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
