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

  // show speak checkbox only if browser supports tts
  if ('SpeechSynthesisUtterance' in window) {
    $("#speak").show();
    $("#speak-check").attr("checked", true);
  }

  var showResult = function (result) {
        $('.result').html(result);
        $('.history-result').prepend('<li>' + result + '</li>');
        if($('#speak-check').is(':checked')) {
          var utterance = new SpeechSynthesisUtterance(result);
          utterance.rate = 1.3;
          window.speechSynthesis.speak(utterance);
        }
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
  });

  $('#go-btn').on('click', sendQuery);

});
