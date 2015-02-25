var queryPAL = function(query, usdat, clidat, callback) {
  $.ajax({
    type: 'POST',
    url: '/api/pal',
    data: {
      query: query,
      client: 'web',
      'user-data': usdat,
      'client-data': clidat
    },
    success: function (response) {
      callback(query, response.result);
    },
    error: function () {
      console.log('server error');
      $('.prompt').removeAttr('disabled');
      $('#go-btn').removeAttr('disabled');
    }
  });
};

function expandData (el) {
    $(el).parent().toggleClass('expanded');
    return true;
}
window.fbAsyncInit = function() {
    FB.init({
        appId   : '363891403803678',
        xfbml   : true,
        version : 'v2.2',
        cookie  : true
    });

    FB.Event.subscribe('auth.authResponseChange', function(fbResponse) {
        handleFacebook(fbMessage);
    });
};

(function(d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) return;
    js = d.createElement(s); js.id = id;
    js.src = "//connect.facebook.net/en_US/sdk.js";
    fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));

function handleFacebook(payload) {
    var $history = $('.history');
    FB.getLoginStatus(function(response) {
        if (response.status === 'connected') {
            // post if app is authorized
            FB.api('/me/feed', 'post', {message: payload.data}, function(response) {
                // get rid of login stuff if it was presented
                $('#facebook_login').remove();
                // show confirmation that the post was successful
                var message = "Ok, I've posted that to Facebook";
                $history.prepend('<li><div class="result">' + message +
                '</div></li>');
                speakIfAppropriate(message);
            });
        }
        else {
            // gotta show the login button (to get around popup blocker)
            var fb_login_button = '<fb:login-button max_rows="1" size="large" show_faces="false" '+
                '"auto_logout_link="false" scope="publish_actions"></fb:login-button>';

            var message = "Before I can post, you'll need to login to Facebook"
            $history.prepend('<li id="facebook_login"><div class="result">' + message +'<br>' +
            fb_login_button + '</div>');
            speakIfAppropriate(message);
            FB.XFBML.parse(document.getElementById('.history')); // changes XFBML to valid HTML
            fbMessage = payload; // remember the message if/when the user gets logged in (async is hell)
        }
        $('#prompt').removeAttr('disabled');
        $('#go-btn').removeAttr('disabled');
    });
}

function speakIfAppropriate(message) {
    if($('#speak-check').is(':checked')) {
        var utterance = new SpeechSynthesisUtterance(message);
        utterance.rate = 1.1;
        if ('maleVoice' in window){
            utterance.voice = window.maleVoice;
            console.log(window.maleVoice.name + " is speaking.");
        }
        window.speechSynthesis.speak(utterance);
    }
}

function chooseVoice() {
    var maleVoices = [
        "Google UK English Male", // Sexy British male
        "Daniel", // Generic British male
        "Bruce", // Stephen Hawking-ish
        "Alex",
        "Fred"
    ];
    var voices = window.speechSynthesis.getVoices();
    if (voices.length > 0) {

        // filter the male voices
        var filteredVoices = {};
        $.each(voices, function(index, voice){
            if ($.inArray(voice.name, maleVoices) !== -1){
                filteredVoices[voice.name] = voice;
            }
        });

        // pick the first one in maleVoices order
        for(var i=0; i<maleVoices.length; i++) {
            var voiceName = maleVoices[i];
            if (filteredVoices.hasOwnProperty(voiceName)) {
                window.maleVoice = filteredVoices[voiceName];
                return window.maleVoice;
            }
        }
        return null;
    }
}

var mapGo;

$(document).ready(function () {
    var $prompt = $('#prompt');
    var $goBtn = $('#go-btn');
    var $userData = $('#user-data');
    var $speakCheck = $('#speak-check');
    var $history = $('.history');
    var lastQuery = '';
    
    // show speak checkbox only if browser supports it
    if ('SpeechSynthesisUtterance' in window && !navigator.userAgent.match(/(iPad|iPhone|iPod)/g) ? true : false) {
        $("#speak").show();
        chooseVoice();
        // load user preference on speech from cookie
        if (document.cookie) {
            if (document.cookie === 'speech=true') {
                $speakCheck.attr("checked", true);
            }
        }
    }

    // FOR THE LOVE OF GOD PLEASE COMMENT ME WHOEVER WROTE THIS
    var showResult = function (query, result) {
        // external stuff
        if (result.status == 4) {
            if (result.external === 'facebook') {
                handleFacebook(result.payload);
                return;
            }
        }
        else if (result.status == 3) {
            var needs = result.needs_client;
            var keys = Object.keys(needs);
            var sendError = function (msg) {
                $userData.html('');
                $history.prepend('<li class="error"><div class="query">' +
                query + '</div><div class="result">' +
                msg + '</div></li>');
            };
            var handleIndex = function (i, data) {
                if (i >= keys.length) {
                    queryPAL(query, getUserData(), data, showResult);
                    return true;
                }

                var need = keys[i];
                var type = needs[need].type;
                var msg = needs[need].msg;
                switch (type) {
                    case 'loc':
                        if (navigator.geolocation) {
                            navigator.geolocation.getCurrentPosition(function (idx) {
                                return function (pos) {
                                    data[need] = pos.coords.latitude + ',' + pos.coords.longitude;
                                    return handleIndex(idx + 1, data);
                                };
                            }(i), function (posError) {
                                return sendError(msg);
                            });
                        } else {
                            return sendError(msg);
                        }
                        break;
                    default:
                        return sendError(msg);
                }

            };
            handleIndex(0, {});
        }
        else if (result.status == 2) {
            $userData.html('');
            for (need in result.needs_user) {
                var type = result.needs_user[need].type;
                var def = result.needs_user[need].default;
                switch (type) {
                    case 'str':
                        $userData.append(
                            '<li data-type="' + type + '" data-param="' + need + '">' +
                            need + ': ' + '<input type="text" value="' + def + '"></li>');
                        break;
                    default:
                        console.log('unknown requested data type')
                }
            }
        }
        else if (result.status == 1) {
            $userData.html('');
            var data = '';
            if (result.hasOwnProperty('data')) {
                data = '<div class="data"><span class="data-toggler" onclick="expandData(this);">...</span>' +
                result.data.replace(/\n+/ig, '<br>') + '</div>'
            }
            $history.prepend('<li><div class="query">' + query +
            '</div><div class="result">' +
            result.summary.replace(/\n+/ig, '<br>') +
            '</div>' + data + '</li>');
        }
        else {
            $userData.html('');
            $history.prepend('<li class="error"><div class="query">' +
            query + '</div><div class="result">' +
            result.summary.replace(/\n+/ig, '<br>') +
            '</div></li>');
        }

        if ($speakCheck.is(':checked') && result.status <= 1) {
            // to avoid pronouncing 'li' etc.
            var no_html = result.summary.replace(/(<([^>]+)>)/ig, '');
            speakIfAppropriate(no_html);
        }

        $prompt.val('')
               .focus()
               .removeAttr('disabled');
        $goBtn.removeAttr('disabled');
    };

    var getUserData = function () {
        var ret = {};
        $userData.find('li').each(function () {
            var li = $(this);
            var need = li.attr('data-param');
            var type = li.attr('data-type');
            switch (type) {
                case 'str':
                    ret[need] = li.find('input').val();
                    break;
            }
        });
        return ret;
    };

    var sendQuery = function () {
        var query = $prompt.val();

        ($speakCheck.is(":checked") && !window.maleVoice) && chooseVoice();

        if (query.length > 0) {
            $prompt.attr('disabled', 'disabled');
            $goBtn.attr('disabled', 'disabled');
            lastQuery = query;
            queryPAL(query, getUserData(), {}, showResult);
        }
    };

    $prompt.on('keypress', function (e) {
      // 'enter' key
      if (e.which == 13) {
        sendQuery();
      }
    });

    // remember if user has checked the speech checbox
    $speakCheck.on('click', function(event) {
      if($speakCheck.is(':checked')) {
        document.cookie = 'speech=true;';
      }
      else {
        document.cookie = 'speech=false;';
      }
    });

    $goBtn.on('click', sendQuery);

    mapGo = function (el) {
      var div = $(el).parent();
      var userData = getUserData();
      var lat = div.find('.lat').val();
      var lng = div.find('.lng').val();
      userData['location'] = lat + ',' + lng;
      queryPAL(div.find('.q').val(), userData, {}, showResult);
    };
});
