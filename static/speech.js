
(function($, window, document){

    var DEBUG = false;
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
        var $goBtn = $("#go-btn");

        var micStates = {
            notListening: "/static/mic.gif",
            listening: "/static/mic-animate.gif",
            disabled: "/static/mic-slash.gif"
        };

        function setMic(state) {
            $mic.attr("src", micStates[state]);
        }

        // Currently only supported in Chrome
        if (!('webkitSpeechRecognition' in window)) {
            $mic.hide();
        }
        else{
            $mic.show();

            function stopListening() {
                setMic('notListening');
                recognition.isListening = false;
                recognition.abort();
                debugLog("Stopped listening");
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
                    debugLog("Ignoring onend");
                    return;
                }
                stopListening();
                debugLog("Ending recognition");
                $prompt.val(final_transcript);
                $prompt.focus();

                // Automatically send the query if PAL is going to talk back
                if ($('#speak-check').is(':checked')) {
                    $goBtn.click();
                }
            };

            recognition.onresult = function (event) {
                if (final_transcript){
                    $prompt.val(final_transcript);
                    stopListening();
                    return;
                }
                var interim_transcript = '';
                for (var i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                        final_transcript += event.results[i][0].transcript;
                        if (final_transcript.lastIndexOf("Hal") !== -1) {
                            final_transcript = final_transcript.replace(/[ph]al/i, "PAL");
                        }
                        debugLog("Final: " + final_transcript);
                        $prompt.val(final_transcript);
                        stopListening();
                    } else {
                        interim_transcript += event.results[i][0].transcript;
                        debugLog("Interim: " + interim_transcript);
                        if (interim_transcript.lastIndexOf("Hal") !== -1) {
                            interim_transcript = interim_transcript.replace(/[ph]al/i, "PAL");
                        }
                        $prompt.val(interim_transcript);
                    }
                }
            };

            $mic.on("click", function(event) {
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

            // If the user clicks Go or starts typing,
            // we shouldn't be listening
            $goBtn.on("click", stopListening);
            $prompt.on("keypress", stopListening);
        }
    });
})(jQuery, window, document);