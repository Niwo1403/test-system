# 3rd party
import requests
from flask.testing import FlaskClient
# custom
from test_system.routes.root import ROUTE

# In case a database connection is required for any of the following tests, add session to its parameters!


def test_if_file_is_accessible__via_redirect(client: FlaskClient):
    resp = client.get(ROUTE, follow_redirects=True)
    assert resp.status_code == 200,  f"Can't GET index file at '{ROUTE}'\n\nReceived response:\n{resp.get_data(True)}"


def test_if_file_is_accessible__directly(client: FlaskClient):
    test_request_routes = ["/index.html", "script.js", "/style.css", "/img/certificate_background.png"]

    for test_request_route in test_request_routes:
        resp = client.get(test_request_route)
        assert resp.status_code == 200,  (f"Can't GET file at '{test_request_route}'"
                                          f"\n\nReceived response:\n{resp.get_data(True)}")


def test_if_extern_code_is_available():
    test_links = [
        "https://unpkg.com/jquery",
        "https://unpkg.com/survey-jquery@1.9.2/survey.jquery.min.js",
        "https://unpkg.com/survey-core@1.9.2/modern.min.css"
    ]

    for test_link in test_links:
        resp = requests.head(test_link, allow_redirects=True)
        assert resp.status_code == 200, f"Got wrong status code for link: {test_link}"
