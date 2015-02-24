
(function($, window, document){

    var DEBUG = true;
    // Log a message if DEBUG is true
    function debugLog(message){
        DEBUG && console.log(message);
    }

    $(document).ready(function() {
        var final_transcript = '';
        var ignore_onend;
        var start_timestamp;
        var $prompt = $("#prompt");
        var $mic = $("#mic");

        var micStates = {
            notListening: "/static/mic.gif",
            listening: "/static/mic-animate.gif",
            disabled: "/static/mic-slash.gif"
        };

        function setMic(state) {
            $mic.attr("src", micStates[state]);
        }

        // Currently only supported in Chrome
        if (('webkitSpeechRecognition' in window)) {
            $mic.show();

            function stopListening() {
                setMic('notListening');
                recognition.isListening = false;
                recognition.stop();
            }

            var recognition = new webkitSpeechRecognition();
            // Return and show results before the speech ends
            recognition.interimResults = true;
            recognition.isListening = false;

            recognition.onstart = function () {
                debugLog("Beginning voice recognition");
                recognition.isListening = true;
                setMic('listening');
            };

            recognition.onerror = function (event) {
                debugLog("Recognition Error: " + event.error);
                stopListening();
                if (event.error == 'no-speech') {
                    ignore_onend = true;
                }
                if (event.error == 'audio-capture') {
                    ignore_onend = true;
                }
            };

            recognition.onend = function () {
                if (ignore_onend || !final_transcript) {
                    return;
                }
                stopListening();
                debugLog("Ending recognition");
                $prompt.val(final_transcript);
            };

            recognition.onresult = function (event) {
                if (final_transcript){
                    $prompt.val(final_transcript);
                    return;
                }
                var interim_transcript = '';
                for (var i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                        final_transcript += event.results[i][0].transcript;
                        debugLog("Final: " + final_transcript);
                        $prompt.val(final_transcript);
                        stopListening();
                    } else {
                        interim_transcript += event.results[i][0].transcript;
                        debugLog("Interim: " + interim_transcript);
                        $prompt.val(interim_transcript);
                    }
                }
            };
        }
        else {
            $mic.hide();
        }

        $mic.on("click", function (event) {
            debugLog("clicked mic");
            if (recognition.isListening) {
                stopListening();
                return;
            }
            final_transcript = '';
            $prompt.val('');
            ignore_onend = false;
            setMic('disabled');
            recognition.start();
            start_timestamp = event.timeStamp;
        });
    });
})(jQuery, window, document);