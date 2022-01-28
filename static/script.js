function getArgumentFromUrl(argumentName) {
    const url = new URL(window.location.href);
    return url.searchParams.get(argumentName);
}

const INITIAL_TOKEN = getArgumentFromUrl("token");

function backToLogin() {
    window.location.href = "/index.html?token=" + INITIAL_TOKEN;
}
