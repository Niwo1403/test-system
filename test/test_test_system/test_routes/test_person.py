# std
from json import dumps as json_dumps
from typing import Callable, ContextManager
# 3rd party
from flask.testing import FlaskClient
# custom
from test_system.routes.person import ROUTE
from test_system.models import Person, db


def test_post_person__with_success(client: FlaskClient):
    test_cases = {
        "data with out position": {"name": "Max M.", "age": 18, "gender": "s"},
        "data with position": {"name": "Max M.", "age": 18, "gender": "s", "position": "POS"}
    }

    for data_name, test_data in test_cases.items():
        resp = client.post(ROUTE, data=json_dumps(test_data))
        assert resp.status_code == 201, f"Can't POST person to {ROUTE} with data {data_name}: {test_data}"

        person_id = resp.data.decode()
        person = Person.query.filter_by(id=person_id).first()
        assert person is not None, "Could not write person to database"

        db_data = {"name": person.name, "age": person.age, "gender": person.gender.value}  # use .value for enums
        if "position" in test_data:
            db_data["position"] = person.position
        assert db_data == test_data, "Person written to database, got wrong data"


def test_post_person__with_bad_request(client: FlaskClient,
                                       raise_if_change_in_tables: Callable[[db.Model], ContextManager]):
    test_cases = {
        "data with no name": {"age": 18, "gender": "s", "position": "POS"},
        "data with no age": {"name": "", "gender": "s", "position": "POS"},
        "data with no gender": {"name": "", "age": 18, "position": "POS"},
        "data with age out of range": {"name": "Max M.", "age": -1, "gender": "s", "position": "POS"},
        "data with unknown gender": {"name": "Max M.", "age": 18, "gender": "UNKNOWN", "position": "POS"},
        "data with age wrong type": {"name": "Max M.", "age": "18", "gender": "s", "position": "POS"}
    }
    for k, v in test_cases.items():
        test_cases[k] = json_dumps(v)
    test_cases.update({
        "data with wrong json (missing })": '{"name": "Max M.", "age": 20, "gender": "s", "position": "POS" ',
        "data with wrong json (wrong key type)": '{"name": "Max M.", "age": 20, "gender": "s", null: "POS"}'})

    with raise_if_change_in_tables(Person):
        for data_name, test_data in test_cases.items():
            resp = client.post(ROUTE, data=test_data)
            assert resp.status_code == 400, f"Got wrong status code at {ROUTE} for {data_name}: {test_data}"
