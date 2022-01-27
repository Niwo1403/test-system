function getTokenFromUrl() {
    const url = new URL(window.location.href);
    return url.searchParams.get("token");
}

const INITIAL_TOKEN = getTokenFromUrl();

function backToLogin() {
    window.location.href = "/index.html?token=" + INITIAL_TOKEN;
}
