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

/*
(function(d, s, id) {
  var js, fjs = d.getElementsByTagName(s)[0];
  if (d.getElementById(id)) return;
  js = d.createElement(s); js.id = id;
  js.src = "//connect.facebook.net/en_US/sdk.js";
  fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));

window.fbAsyncInit = function() {
  FB.init({
    appId   : '363891403803678',
    xfbml   : true,
    version : 'v2.2',
    cookie  : true  
  });
}  
*/
function handleFacebook(payload) {
  FB.getLoginStatus(function(response) {
    if (response.status === 'connected') {
      // post if app is authorized
      FB.api('/me/feed', 'post', {message: payload.data}, function(response) {
        // get rid of login stuff if it was presented
        $('#facebook_login').remove();
        // show confirmation that the post was successful
        $('.history').prepend('<li><div class="result">' +
                              "Ok, I've sent your post to Facebook" +
                              '</div></li>');
      });
    }
    else {
      // gotta show the login button (to get around popup blocker)
      var fb_login_button = '<fb:login-button max_rows="1" size="large" show_faces="false" '+
       '"auto_logout_link="false" scope="publish_actions"></fb:login-button>';

      $('.history').prepend('<li id="facebook_login"><div class="result">' +
                      "You'll need to login to Facebook first<br>" +
                      fb_login_button + '</div>');
      FB.XFBML.parse(document.getElementById('.history')); // changes XFBML to valid HTML
    }
  });
}

$(document).ready(function () {

  // show speak checkbox only if browser supports tts
  if ('SpeechSynthesisUtterance' in window && !navigator.userAgent.match(/(iPad|iPhone|iPod)/g) ? true : false)  {
    $("#speak").show();
    $("#speak-check").attr("checked", true);
  }

  // FB.login(function(response) {
  //   console.log("it's here");
  // });

  var showResult = function (query, result) {
    prompt.removeAttr('disabled');
    $('#go-btn').removeAttr('disabled');
    if (result.status) {

      // external stuff
      if (result.status == 3) {
        if (result.external === 'facebook') {
          handleFacebook(result.payload);
          return;
        }
      }
      else {
        var data = '';
        if (result.hasOwnProperty('data')) {
          data = '<div class="data" onclick="expandData(this);">...<br>' +
                 result.data.replace(/\n+/ig, '<br>') + '</div>'
        }
        $('.history').prepend('<li><div class="query">' + query +
                              '</div><div class="result">' +
                              result.summary.replace(/\n+/ig, '<br>') +
                              '</div>' + data + '</li>');
      }
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