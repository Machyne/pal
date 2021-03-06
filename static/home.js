var resetQueryBar = function () {
    $('#prompt').removeAttr('disabled');
    $('#go-btn').removeAttr('disabled');
    $('#loader').hide();
    document.getElementById('prompt').focus();
    document.getElementById('prompt').select();
};
var genericError = {
    result: {
        status: 0,
        summary: "I got confused, please try again later."
    },
    service: "unknown"
};

var queryPAL = function (query, usdat, clidat, callback) {
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
        callback(query, response);
    },
    error: function () {
        console.log('server error');
        callback(query, genericError);
    }
  });
};

function expandData (el) {
    $(el).parent().toggleClass('expanded');
    return true;
}

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

            var message = "Before I can post, you'll need to login to Facebook";
            $history.prepend('<li id="facebook_login"><div class="result">' + message +'<br>' +
            fb_login_button + '</div>');
            speakIfAppropriate(message);
            FB.XFBML.parse(document.getElementById('.history')); // changes XFBML to valid HTML
            fbMessage = payload; // remember the message if/when the user gets logged in (async is hell)
        }
        resetQueryBar();
    });
}

function speakIfAppropriate(message) {
    if($('#speak-check').is(':checked')) {
        var utterance = new SpeechSynthesisUtterance(message);
        utterance.rate = 1.1;
        if ('maleVoice' in window){
            utterance.voice = window.maleVoice;
            utterance.lang = utterance.voice.lang;
            utterance.rate = 1.0;
            console.log(window.maleVoice.name + " is speaking.");
        }
        window.speechSynthesis.speak(utterance);
    }
}

function chooseVoice() {
    // One-liner to query the options:
    // $.each(window.speechSynthesis.getVoices(), function(index, voice) { voice.lang.indexOf("es") !== -1 && console.log(voice) })
    if(!window.speechSynthesis){
        return null;
    }

    var maleVoices = [
        // TODO: just map user-agent to voice
        "Daniel", // Generic British male
        "Fred", // Stephen Hawking-ish
        "Alex", // Polite American
        "Bruce", // Fast robot
        "Ralph", // Deep robot
        "English United Kingdom" // the only male voice available on Android
    ];
    var languageVoices = {
        deu: ["Google Deutsch", "Anna"],
        spa: ["Google Español", "Diego"],
        fra: ["Google Français", "Thomas"],
        ita: ["Google Italiano", "Alice"],
        por: ["Google Español", "Diego"]
        // Spanish is closer than any of the english voices
    };
    var voices = window.speechSynthesis.getVoices();
    if (voices.length > 0) {
        var voiceOptions = {};
        $.each(voices, function(index, voice){
            voiceOptions[voice.name] = voice;
        });
        window.voiceOptions = voiceOptions;
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
    else {
        window.speechSynthesis.onvoiceschanged = chooseVoice;
    }
}

function attributionImageForService(service) {
    // return HTML for with logo for API attribution
    switch(service) {
        case "weather":
            var yahooImage ='./static/yahoo_purple_retina.png';
            return '<a href="//www.yahoo.com/?ilc=401" target="_blank"> <img src="' + yahooImage + '" height="25"/></a>';
        case "yelp":
            var yelpImage = './static/yelp_logo_100x50.png';
            return '<a href="//yelp.com/" target="_blank"> <img src="' + yelpImage + '" height="25"/></a>';
        case "wa":
            var waImage = './static/wa-logo.png';
            return '<a href="//wolframalpha.com/" target="_blank"> <img src="' + waImage + '" height="25"/></a>';
        case "ultralingua":
            var ulImage = './static/ultralingua.png';
            return '<a href="//developer.ultralingua.com" target="_blank"> '
                    + '<img src=' + ulImage + ' height="25" title="Ultralingua, Inc"/></a>';
        case "movie":
            var tmdbImage = './static/tmdb.png';
            return '<a href="//www.themoviedb.org" target="_blank"> <img src="' + tmdbImage + '" height="25"/></a>';
        default:
            return "";
    }
}

function shutUp() {
    // If PAL is talking, stop.
    window.speechSynthesis &&
    window.speechSynthesis.speaking &&
    window.speechSynthesis.cancel();
}

var mapGo;

$(document).ready(function () {
    var $prompt = $('#prompt');
    var $goBtn = $('#go-btn');
    var $userData = $('#user-data');
    var $speakCheck = $('#speak-check');
    var $history = $('.history');
    var $loader = $('#loader');
    var lastQuery = '';

    FB.init({
        appId   : '363891403803678',
        xfbml   : true,
        version : 'v2.2',
        cookie  : true
    });

    FB.Event.subscribe('auth.authResponseChange', function(fbResponse) {
        handleFacebook(fbMessage);
    });
    
    // show speak checkbox only if browser supports it
    if ('SpeechSynthesisUtterance' in window && !navigator.userAgent.match(/(iPad|iPhone|iPod)/g)) {
        window.speechSynthesis.onvoiceschanged = chooseVoice;
        shutUp(); // if the user reloads while PAL is talking
        $("#speak").show();

        // Initialize speech
        // load user preference on speech from cookie
        if (document.cookie) {
            if (document.cookie.indexOf('speech=true') > -1) {
                // speech=true is in the cookie
                $speakCheck.attr("checked", true);
            }
        }
    }

    // FOR THE LOVE OF GOD PLEASE COMMENT ME WHOEVER WROTE THIS
    var showResult = function (query, response) {
        shutUp();
        var result = response.result;
        var service = response.service;
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
                resetQueryBar();
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
            return handleIndex(0, {});
        }
        else if (result.status == 2) {
            $userData.html('');
            for (i in result.needs_user) {
                var need = result.needs_user[i][0];
                var data = result.needs_user[i][1];
                var type = data.type;
                var def = data.default;
                var name = data.name;
                var scratch = false;
                switch (type) {
                    case 'str':
                        scratch = scratch || 'text';
                        break;
                    case 'hidden':
                        scratch = scratch || 'password';
                        $('#user-data').append(
                            '<li data-type="' + type + '" data-param="' + need + '">' +
                            name + ': ' +
                            '<input type="' + scratch + '" value="' + (def || '') + '"></li>');
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
            var prependString = '<li><div class="query">' + query +
                '</div><div class="result">' +
                result.summary.replace(/\n+/ig, '<br>') +
                data + '<br><div class="attribution">' +
                attributionImageForService(service) + '</div></div></li>';
            $history.prepend(prependString);
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
            var no_html = result.summary.replace(/(<([^>]+)>)/ig, ' ');
            speakIfAppropriate(no_html);
        }

        resetQueryBar();
    };

    var getUserData = function () {
        var ret = {};
        $userData.find('li').each(function () {
            var li = $(this);
            var need = li.attr('data-param');
            var type = li.attr('data-type');
            switch (type) {
                case 'str':
                case 'hidden':
                    ret[need] = li.find('input').val();
                    break;
            }
        });
        return ret;
    };

    var sendQuery = function () {
        var query = $prompt.val();

        if (query.length > 0 && !($prompt.attr('disabled') === 'disabled')) {
            $prompt.attr('disabled', 'disabled');
            $goBtn.attr('disabled', 'disabled');
            $loader.show();
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

    // remember if user has checked the speech checkbox
    $speakCheck.on('click', function() {
        document.cookie = $speakCheck.is(':checked') ? 'speech=true;' : 'speech=false;';
        shutUp();
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

    $prompt.focus();
});
