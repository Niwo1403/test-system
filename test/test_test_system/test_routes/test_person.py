# std
from json import dumps as json_dumps
# 3rd party
from flask.testing import FlaskClient
# custom
from test_system.routes.person import ROUTE


def test_post_person__with_success(client: FlaskClient):
    test_cases = {
        "data with out position": {"name": "Max M.", "age": 18, "gender": "s"},
        "data with position": {"name": "Max M.", "age": 18, "gender": "s", "position": "POS"}
    }

    for data_name, test_data in test_cases.items():
        resp = client.post(ROUTE, data=json_dumps(test_data))
        assert resp.status_code == 201, f"Can't POST person to {ROUTE} with data {data_name}: {test_data}"


def test_post_person__with_bad_request(client: FlaskClient):
    test_cases = {
        "data with missing attr": {"name": "Max M.", "age": 18, "position": "POS"},
        "data with age out of range": {"name": "Max M.", "age": -1, "gender": "s", "position": "POS"},
        "data with unknown gender": {"name": "Max M.", "age": 18, "gender": "UNKNOWN", "position": "POS"},
        "data with age wrong type": {"name": "Max M.", "age": "18", "gender": "s", "position": "POS"},
        "data with name empty": {"name": "", "age": 18, "gender": "s", "position": "POS"}
    }

    for data_name, test_data in test_cases.items():
        resp = client.post(ROUTE, data=json_dumps(test_data))
        assert resp.status_code == 400, f"Got wrong status code at {ROUTE} for {data_name}: {test_data}"
