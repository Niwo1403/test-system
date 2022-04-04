# std
from json import dumps as json_dumps
# 3rd party
from flask.testing import FlaskClient
# custom
from test_system.routes.person import ROUTE
from test_system.models import Person


def test_post_person__with_success(client: FlaskClient, session):
    test_cases = {
        "data with out position": {"name": "Max M.", "age": 18, "gender": "d"},
        "data with position": {"name": "Max M.", "age": 18, "gender": "d", "position": "POS"}
    }

    for data_name, test_data in test_cases.items():
        resp = client.post(ROUTE, data=json_dumps(test_data))
        assert resp.status_code == 201, (f"Can't POST person to {ROUTE} with data {data_name}: {test_data}"
                                         f"\n\nReceived response:\n{resp.get_data(True)}")

        person_id = resp.get_data(True)
        person = Person.query.filter_by(id=person_id).first()
        assert person is not None, f"Could not write person to database\n\nReceived response:\n{resp.get_data(True)}"

        for key in person.answer_json.keys():
            if key not in test_data:
                test_data[key] = None
        assert person.answer_json == test_data, ("Person written to database, got wrong data"
                                                 f"\n\nReceived response:\n{resp.get_data(True)}")


def test_post_person__with_bad_request(client: FlaskClient, session, raise_if_change_in_tables):
    test_cases = {
        "data with no name": {"age": 18, "gender": "d", "position": "POS"},
        "data with no age": {"name": "", "gender": "d", "position": "POS"},
        "data with no gender": {"name": "", "age": 18, "position": "POS"},
        "data with age out of range": {"name": "Max M.", "age": -1, "gender": "d", "position": "POS"},
        "data with unknown gender": {"name": "Max M.", "age": 18, "gender": "UNKNOWN", "position": "POS"},
        "data with age wrong type": {"name": "Max M.", "age": "18", "gender": "d", "position": "POS"}
    }
    for k, v in test_cases.items():
        test_cases[k] = json_dumps(v)
    test_cases.update({
        "data with wrong json (missing })": '{"name": "Max M.", "age": 20, "gender": "d", "position": "POS" ',
        "data with wrong json (wrong key type)": '{"name": "Max M.", "age": 20, "gender": "d", null: "POS"}'})

    with raise_if_change_in_tables(Person):
        for data_name, test_data in test_cases.items():
            resp = client.post(ROUTE, data=test_data)
            assert resp.status_code == 400, (f"Got wrong status code at {ROUTE} for {data_name}: {test_data}"
                                             f"\n\nReceived response:\n{resp.get_data(True)}")
