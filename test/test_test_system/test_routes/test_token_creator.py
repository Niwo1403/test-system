# std
from json import loads as json_loads, JSONDecodeError
# 3rd party
from flask.testing import FlaskClient
# custom
from test_system.routes.token_creator import ROUTE


def test_token_creator__with_success(client: FlaskClient, session):
    resp = client.get(ROUTE)
    assert resp.status_code == 200,  (f"Got wrong status Code for GET token-creator at '{ROUTE}'"
                                      f"\n\nReceived response:\n{resp.get_data(True)}")

    try:
        resp_token_creator = json_loads(resp.get_data(True))
        elements = resp_token_creator["pages"][0]["elements"]
    except JSONDecodeError:
        assert False, (f"Got invalid JSON for GET token-creator at '{ROUTE}'"
                       f"\n\nReceived response:\n{resp.get_data(True)}")
    except (IndexError, KeyError):
        assert False, (f"Got wrong JSON format (key missing / list empty) for GET token-creator at '{ROUTE}'"
                       f"\n\nReceived response:\n{resp.get_data(True)}")
    assert len(elements) >= 2, (f"Missing input elements for GET token-creator at '{ROUTE}'"
                                f"\n\nReceived response:\n{resp.get_data(True)}")

