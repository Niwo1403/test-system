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
    const exportableTestAnswerId = getArgumentFromUrl("exportable-test-answer-id");
    const pdfView = document.getElementById("pdf-view");
    pdfView.data = buildApiUrl("test-answer-pdf/", true,
        {"exportable-test-answer-id": exportableTestAnswerId});
}

function copyFromElm(elmId) {
    const selection = window.getSelection();
    selection.removeAllRanges();

    const elm = document.getElementById(elmId);
    const range = document.createRange();
    range.selectNodeContents(elm);
    selection.addRange(range);

    document.execCommand('copy');
}