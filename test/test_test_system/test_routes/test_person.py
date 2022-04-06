# std
from json import dumps as json_dumps
from typing import Dict
# 3rd party
from pytest import fixture
from flask.testing import FlaskClient
# custom
from test_system.routes.person import ROUTE
from test_system.models import TestAnswer


@fixture()
def person_default_query_string(personal_data_test_name) -> Dict[str, str]:
    return {"test-name": personal_data_test_name}


def test_post_person__with_success(client: FlaskClient, session, person_default_query_string):
    test_cases = {
        "data without extra": {"name": "Max M.", "age": 18, "gender": "d"},
        "data with extra": {"name": "Max M.", "age": 18, "gender": "d", "position": "POS"}
    }

    for data_name, test_data in test_cases.items():
        resp = client.post(ROUTE, data=json_dumps(test_data), query_string=person_default_query_string)
        assert resp.status_code == 201, (f"Can't POST test-answer to {ROUTE} with data {data_name}: {test_data}"
                                         f"\n\nReceived response:\n{resp.get_data(True)}")

        personal_data_answer_id = resp.get_data(True)
        personal_data_answer = TestAnswer.query.filter_by(id=personal_data_answer_id).first()
        assert personal_data_answer is not None, (f"Could not write person to database"
                                                  f"\n\nReceived response:\n{resp.get_data(True)}")

        assert personal_data_answer.answer_json == test_data, ("Person written to database, got wrong data"
                                                               f"\n\nReceived response:\n{resp.get_data(True)}")


def test_post_person__with_bad_request(client: FlaskClient, session, raise_if_change_in_tables,
                                       person_default_query_string, evaluable_test, pre_collect_test):
    test_cases = {
        "data with None age": {"age": None, "gender": "d", "position": "POS"},
        "data with None name": {"name": None, "gender": "d", "position": "POS"},
        "data with None position": {"name": "", "age": 18, "position": None}
    }
    for k, v in test_cases.items():
        test_cases[k] = json_dumps(v)
    test_cases.update({
        "data with wrong json (missing })": '{"name": "Max M.", "age": 20, "gender": "d", "position": "POS" ',
        "data with wrong json (wrong key type)": '{"name": "Max M.", "age": 20, "gender": "d", null: "POS"}'})

    wrong_query_strings = [{}, {"test-name": evaluable_test.name}, {"test-name": pre_collect_test.name}]

    with raise_if_change_in_tables(TestAnswer):
        for wrong_query_string in wrong_query_strings:
            resp = client.post(ROUTE, data=json_dumps({"name": "ASDF"}), query_string=wrong_query_string)
            assert resp.status_code == 400, (f"Got wrong status code at {ROUTE} for request with missing test name"
                                             f"\n\nReceived response:\n{resp.get_data(True)}")
        for data_name, test_data in test_cases.items():
            resp = client.post(ROUTE, data=test_data, query_string=person_default_query_string)
            assert resp.status_code == 400, (f"Got wrong status code at {ROUTE} for {data_name}: {test_data}"
                                             f"\n\nReceived response:\n{resp.get_data(True)}")


def test_post_person__with_unknown_test(client: FlaskClient, session, raise_if_change_in_tables):
    resp = client.post(ROUTE, data=json_dumps({"name": "ASDF"}), query_string={"test-name": "UNKNOWN TEST"})
    assert resp.status_code == 404, (f"Got wrong status code at {ROUTE} for request with unknown test name"
                                     f"\n\nReceived response:\n{resp.get_data(True)}")
