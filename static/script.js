const API_PREFIX = "/api/";

function getArgumentFromUrl(argumentName) {
    const url = new URL(window.location.href);
    return url.searchParams.get(argumentName);
}

const INITIAL_TOKEN = getArgumentFromUrl("token");

function buildUrl(routeName, includeToken = false, urlArgs={}) {
    if (includeToken) {
        urlArgs["token"] = INITIAL_TOKEN;
    }
    const urlArgsList = Object.keys(urlArgs).map(function(key) { return key + "=" + urlArgs[key];});
    let urlArgsStr = urlArgsList.join("&");
    if (urlArgsStr.length >= 1) {
        urlArgsStr = "?" + urlArgsStr
    }
    if (!routeName.startsWith("/")) {
        routeName = "/" + routeName;
    }
    return routeName + urlArgsStr;
}

function buildApiUrl(routeName, includeToken = false, urlArgs = {}) {
    return buildUrl(API_PREFIX + routeName, includeToken, urlArgs);
}

function backToLogin() {
    window.location.href = buildUrl("index.html", true);
}

function loadResult() {
    const evaluableTestAnswerId = getArgumentFromUrl("evaluable-test-answer-id");
    const certificateView = document.getElementById("certificate-view");
    certificateView.src = buildApiUrl("certificate/", true,
        {"evaluable-test-answer-id": evaluableTestAnswerId});
}
