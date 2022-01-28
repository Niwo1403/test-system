const API_PREFIX = "/api";

function getArgumentFromUrl(argumentName) {
    const url = new URL(window.location.href);
    return url.searchParams.get(argumentName);
}

const INITIAL_TOKEN = getArgumentFromUrl("token");

function backToLogin() {
    window.location.href = "/index.html?token=" + INITIAL_TOKEN;
}

function loadResult() {
    const testAnswerId = getArgumentFromUrl("test-answer-id");
    const certificateView = document.getElementById("certificate-view");
    certificateView.src = API_PREFIX + "/certificate/?token=" + INITIAL_TOKEN + "&test-answer-id=" + testAnswerId;
}
