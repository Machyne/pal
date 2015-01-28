var queryPAL = function(query, callback) {
  $.ajax({
    type: 'POST',
    url: '/api/pal',
    data: {
      query: query,
      client: 'web'
    },
    success: function (response) {
      callback(query, response.result);
    },
    error: function () {
      $('.prompt').removeAttr('disabled');
      $('#go-btn').removeAttr('disabled');
    }
  });
};

function expandData (el) {
  $(el).toggleClass('expanded');
  return true;
}

$(document).ready(function () {

  // show speak checkbox only if browser supports tts
  if ('SpeechSynthesisUtterance' in window) {
    $("#speak").show();
    $("#speak-check").attr("checked", true);
  }

  var showResult = function (query, result) {
    prompt.removeAttr('disabled');
    $('#go-btn').removeAttr('disabled');
    if (result.response) {
      console.log('no error');
      var data = '';
      if (result.hasOwnProperty('data')) {
        data = '<div class="data" onclick="expandData(this);">...<br>' +
               result.data + '</div>'
      }
      $('.history').prepend('<li><div class="query">' + query +
                            '</div><div class="result">' +
                            result.summary + '</div>' +
                            data + '</li>');
    } else {
      console.log('error');
      $('.history').prepend('<li class="error"><div class="query">' +
                            query + '</div><div class="result">' +
                            result.summary + '</div></li>');
    };
    if($('#speak-check').is(':checked')) {
      // to avoid pronouncing 'li' etc.
      var no_html = result.summary.replace(/(<([^>]+)>)/ig, '');
      var utterance = new SpeechSynthesisUtterance(no_html);
      utterance.rate = 1.1;
      window.speechSynthesis.speak(utterance);
    }
  };
  var prompt = $('.prompt');
  var lastQuery = '';
  var sendQuery = function () {
    var query = prompt.val();
    if (query.length > 0 && query.trim() != lastQuery.trim()) {
      prompt.attr('disabled', 'disabled');
      $('#go-btn').attr('disabled', 'disabled');
      lastQuery = query;
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
