const API_PREFIX = "/api";

function getTokenFromUrl() {
    const url = new URL(window.location.href);
    return url.searchParams.get("token");
}

function loadTestForPassedToken() {
    const token = getTokenFromUrl();
    if (token === null) {
        alert("Token missing.");
    } else {
        const xhr = new XMLHttpRequest();
        xhr.onload = function() {
            if (this.status === 200) {
                const jsonResp = JSON.parse(this.responseText);
                processTests(jsonResp);
            } else {
                displayError(this.responseText);
            }
        }
        xhr.open("GET", API_PREFIX + "/tests/?token=" + token, true);
        xhr.send();
    }
}

function displayError(responseText) {
    document.getElementById("token_res").innerHTML = "ERROR: <br>" + responseText;
}

function processTests(testsJson) {
    document.getElementById("token_res").innerHTML = "Token resp: <br>" + JSON.stringify(testsJson);
}