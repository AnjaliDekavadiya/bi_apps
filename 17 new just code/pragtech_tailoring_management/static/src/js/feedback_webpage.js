document.addEventListener("DOMContentLoaded", function () {
    var orderDropdown = document.getElementById("order_id");
    var selectedProduct = document.getElementById("selected_product");
    var feedbackTextarea = document.getElementById("feedback");
    var voiceButton = document.getElementById("voice-button");
    var stopButton = document.getElementById("stop-button");
    var recognition = new webkitSpeechRecognition();
    var isListening = false;
    var currentTranscript = "";

    recognition.onresult = function (event) {
        var spokenText = event.results[0][0].transcript;
        currentTranscript += spokenText + ' ';
        feedbackTextarea.value = currentTranscript;
    };

    recognition.onend = function () {
        isListening = false;
        voiceButton.innerText = "Start Recording";
        feedbackTextarea.focus();
        var cursorPosition = feedbackTextarea.value.length;
        feedbackTextarea.setSelectionRange(cursorPosition, cursorPosition);
    };

    orderDropdown.addEventListener("change", function () {
        var selectedOrderId = this.value;
        var selectedProductText = selectedOrderId === "" ? "" : orderProducts[selectedOrderId].join(", ");
        selectedProduct.innerHTML = selectedProductText;
    });

    voiceButton.addEventListener("click", function () {
        if (!isListening) {
            isListening = true;
            voiceButton.innerText = "...";
            recognition.start();
        } else {
            isListening = false;
            recognition.stop();
            voiceButton.innerText = "Start Recording";
        }
    });

    stopButton.addEventListener("click", function () {
        currentTranscript = "";
        feedbackTextarea.value = "";
    });
});