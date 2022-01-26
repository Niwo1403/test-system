
function getTokenFromUrl() {
    const url = new URL(window.location.href);
    return url.searchParams.get("token");
}

function loadTestForPassedToken() {
    const token = getTokenFromUrl();
    if (token === null) {
        alert("Token missing.");
    } else {
        document.getElementById("token_res").innerHTML = "Token: " + token;
    }
}