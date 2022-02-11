# 3rd party
from flask.testing import FlaskClient
# custom
from test_system.routes.root import ROUTE


def test_if_file_is_accessible__via_redirect(client: FlaskClient):
    resp = client.get(ROUTE, follow_redirects=True)
    assert resp.status_code == 200,  f"Can't GET index file at '{ROUTE}'"


def test_if_file_is_accessible__directly(client: FlaskClient):
    test_request_routes = ["/index.html", "script.js", "/style.css"]

    for test_request_route in test_request_routes:
        resp = client.get(test_request_route)
        assert resp.status_code == 200,  f"Can't GET file at '{test_request_route}'"
