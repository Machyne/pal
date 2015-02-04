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
  if ('SpeechSynthesisUtterance' in window && !navigator.userAgent.match(/(iPad|iPhone|iPod)/g) ? true : false)  {
    $("#speak").show();
    $("#speak-check").attr("checked", true);
  }

  var showResult = function (query, result) {
    prompt.removeAttr('disabled');
    $('#go-btn').removeAttr('disabled');
    if (result.status) {
      var data = '';
      if (result.hasOwnProperty('data')) {
        data = '<div class="data" onclick="expandData(this);">...<br>' +
               result.data.replace(/\n+/ig, '<br>') + '</div>'
      }
      $('.history').prepend('<li><div class="query">' + query +
                            '</div><div class="result">' +
                            result.summary.replace(/\n+/ig, '<br>') +
                            '</div>' + data + '</li>');
    } else {
      $('.history').prepend('<li class="error"><div class="query">' +
                            query + '</div><div class="result">' +
                            result.summary.replace(/\n+/ig, '<br>') +
                            '</div></li>');
    };
    if($('#speak-check').is(':checked')) {
      // to avoid pronouncing 'li' etc.
      var no_html = result.summary.replace(/(<([^>]+)>)/ig, '');
      var utterance = new SpeechSynthesisUtterance(no_html);
      utterance.rate = 1.1;
      window.speechSynthesis.speak(utterance);
    }

    $('#prompt').val('');
    $('#prompt').focus();
  };
  var prompt = $('#prompt');
  var sendQuery = function () {
    var query = prompt.val();
    prompt.attr('disabled', 'disabled');
    $('#go-btn').attr('disabled', 'disabled');
    lastQuery = query;
    queryPAL(query, showResult);
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
