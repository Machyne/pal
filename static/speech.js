window.getSpeech = function($, window, document){
    $(document).ready(function() {
        var final_transcript = '';
        var recognizing = false;
        var ignore_onend;
        var start_timestamp;
        var $prompt = $("#prompt");
        var $mic = $("#mic");

        function setMic(file) {
            $mic.attr("src", "/static/" + file + ".gif");
        }

        if (('webkitSpeechRecognition' in window)) {
            $mic.show();
            var recognition = new webkitSpeechRecognition();
            recognition.interimResults = true;
            recognition.onstart = function () {
                recognizing = true;
                setMic('mic-animate');
            };
            recognition.onerror = function (event) {
                if (event.error == 'no-speech') {
                    setMic('mic');
                    ignore_onend = true;
                }
                if (event.error == 'audio-capture') {
                    setMic('mic');
                    ignore_onend = true;
                }
            };
            recognition.onend = function () {
                recognizing = false;
                if (ignore_onend) {
                    return;
                }
                setMic('mic');
                if (!final_transcript) {
                    return;
                }

            };
            recognition.onresult = function (event) {
                var interim_transcript = '';
                for (var i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                        final_transcript += event.results[i][0].transcript;
                        $prompt.val(final_transcript);
                    } else {
                        interim_transcript += event.results[i][0].transcript;
                        $prompt.val(interim_transcript);
                    }
                }
            };
        }
        else {
            $mic.hide();
        }

        $mic.on("click", function (event) {
            console.log("clicked mic");
            if (recognizing) {
                recognition.stop();
                return;
            }
            final_transcript = '';
            $prompt.val('');
            recognition.start();
            ignore_onend = false;
            setMic('mic-slash');
            start_timestamp = event.timeStamp;
        });
    });
};
window.getSpeech(jQuery, window, document);