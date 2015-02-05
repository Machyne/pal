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
    FB.getLoginStatus(function(response) {
        if (response.status === 'connected') {
            // post if app is authorized
            FB.api('/me/feed', 'post', {message: payload.data}, function(response) {
                // get rid of login stuff if it was presented
                $('#facebook_login').remove();
                // show confirmation that the post was successful
                var message = "Ok, I've posted that to Facebook";
                $('.history').prepend('<li><div class="result">' + message +
                '</div></li>');
                speakIfAppropriate(message);
            });
        }
        else {
            // gotta show the login button (to get around popup blocker)
            var fb_login_button = '<fb:login-button max_rows="1" size="large" show_faces="false" '+
                '"auto_logout_link="false" scope="publish_actions"></fb:login-button>';

            var message = "Before I can post, you'll need to login to Facebook"
            $('.history').prepend('<li id="facebook_login"><div class="result">' + message +'<br>' +
            fb_login_button + '</div>');
            speakIfAppropriate(message);
            FB.XFBML.parse(document.getElementById('.history')); // changes XFBML to valid HTML
            fbMessage = payload; // remember the message if/when the user gets logged in (async is hell)
        }
    });
}

function speakIfAppropriate(message) {
    if($('#speak-check').is(':checked')) {
        var utterance = new SpeechSynthesisUtterance(message);
        utterance.rate = 1.1;
        window.speechSynthesis.speak(utterance);
    }
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
        }
            // to avoid pronouncing 'li' etc.
        var no_html = result.summary.replace(/(<([^>]+)>)/ig, '');
        speakIfAppropriate(no_html);

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