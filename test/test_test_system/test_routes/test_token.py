# std
from json import dumps as json_dumps
from pytest import fixture
from typing import Dict
# 3rd party
from flask.testing import FlaskClient
# custom
from test_system.models import Token, User, Test
from test_system.routes.token import ROUTE


max_usage_count = 10


@fixture()
def correct_query_string(username, password, test_names):
    return {"username": username,
            "password": password,
            "max-usage-count": str(max_usage_count),
            "personal-data-test-name": test_names["PERSONAL_DATA_TEST"],
            "pre-collect-test-names": json_dumps(test_names["PRE_COLLECT_TESTS"]),
            "evaluable-test-name": test_names["EVALUABLE_TEST"]}


def _copy_with_update(src: Dict, key: str, new_value=None) -> Dict:
    copy = src.copy()
    copy[key] = new_value
    return copy


def test_post_token__with_success(client: FlaskClient, session, correct_query_string, test_names):
    query_string = correct_query_string
    resp = client.post(ROUTE, query_string=query_string)
    assert resp.status_code == 201, f"Can't POST token to {ROUTE} with arguments {query_string}"

    token_hash = resp.data.decode()
    token = Token.query.filter_by(token=token_hash).first()
    assert token is not None, "Could not write Token to database"

    token_test_names = {
        "PERSONAL_DATA_TEST": token.personal_data_test_name,
        "PRE_COLLECT_TESTS": token.pre_collect_test_names,
        "EVALUABLE_TEST": token.evaluable_test_name
    }
    assert token_test_names == test_names and token.max_usage_count == max_usage_count and len(token_hash) == 128, \
        f"Got token with wrong data at route {ROUTE} with arguments {query_string}: {token}"


def test_post_token__with_bad_request(client: FlaskClient, session, raise_if_change_in_tables, correct_query_string):
    bad_query_strings = [
        _copy_with_update(correct_query_string, key)
        for key in correct_query_string.keys()
    ]

    with raise_if_change_in_tables(Token, User, Test):
        for query_string in bad_query_strings:
            resp = client.post(ROUTE, query_string=query_string)
            assert resp.status_code == 400, (f"Got wrong status code at {ROUTE} for bad request "
                                             f"with arguments: {query_string}")


def test_post_token__with_unauthorized_request(client: FlaskClient, session, raise_if_change_in_tables,
                                               correct_query_string):
    unauthorized_query_strings = [
        _copy_with_update(correct_query_string, "username", "UNKNOWN USERNAME"),
        _copy_with_update(correct_query_string, "password", "WRONG PASSWORD")
    ]

    with raise_if_change_in_tables(Token, User, Test):
        for query_string in unauthorized_query_strings:
            resp = client.post(ROUTE, query_string=query_string)
            assert resp.status_code == 401, (f"Got wrong status code at {ROUTE} for unauthorized request "
                                             f"with arguments: {query_string}")


def test_post_token__with_unknown_test(client: FlaskClient, session, raise_if_change_in_tables, correct_query_string):
    unknown_test_query_strings = [
        _copy_with_update(correct_query_string, "personal-data-test-name", "UNKNOWN TEST"),
        _copy_with_update(correct_query_string, "evaluable-test-name", "UNKNOWN TEST")
    ]

    with raise_if_change_in_tables(Token, User, Test):
        for query_string in unknown_test_query_strings:
            resp = client.post(ROUTE, query_string=query_string)
            assert resp.status_code == 404, (f"Got wrong status code at {ROUTE} for unknown test name in request "
                                             f"with arguments: {query_string}")


def test_post_token__with_wrong_test(client: FlaskClient, session, raise_if_change_in_tables,
                                     correct_query_string, test_names):
    first_pre_collect_test = test_names["PRE_COLLECT_TESTS"][0]
    wrong_test_query_strings = [
        _copy_with_update(correct_query_string, "personal-data-test-name", test_names["EVALUABLE_TEST"]),
        _copy_with_update(correct_query_string, "personal-data-test-name", first_pre_collect_test),
        _copy_with_update(correct_query_string, "evaluable-test-name", test_names["PERSONAL_DATA_TEST"]),
        _copy_with_update(correct_query_string, "evaluable-test-name", first_pre_collect_test)
    ]

    with raise_if_change_in_tables(Token, User, Test):
        for query_string in wrong_test_query_strings:
            resp = client.post(ROUTE, query_string=query_string)
            assert resp.status_code == 400, (f"Got wrong status code at {ROUTE} for wrong test name in request "
                                             f"with arguments: {query_string}")
