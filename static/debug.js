var queryPAL = function(query, callback) {
  $.ajax({
    type: 'POST',
    url: '/api/pal',
    data: {
      query: query,
      client: 'web'
    },
    success: function (response) {
      callback(response.result);
    }
  });
};

var queryEndpoint = function(query, endpoint) {
  $.ajax({
    type: 'POST',
    url: '/api/' + endpoint,
    data: {
      query: query,
      client: 'web'
    },
    success: function (response) {
      $('.' + endpoint + ' textarea').val(JSON.stringify(response));
      console.log(JSON.stringify(response));
    }
  });
}

$(document).ready(function () {

  var showResult = function (result) {
        var li = '<li' + (result.status ? '>' : ' class="error">');
        $('.history-result').append(li + result.summary + '</li>');
      },
      prompt = $('.prompt'),
      sendQuery = function () {
        var query = prompt.val();
        if (query.length > 0) {
          queryPAL(query, showResult);
          queryEndpoint(query, 'standard_nlp');
          queryEndpoint(query, 'features');
          queryEndpoint(query, 'classify');
          queryEndpoint(query, 'execute');
          $('.history-prompt').append('<li>' + query + '</li>');
        }
      };

  prompt.focus();

  prompt.on('keypress', function (e) {
    // 'enter' key
    if (e.which == 13) {
      sendQuery();
    }
  });

  $('#go-btn').on('click', sendQuery);

});
