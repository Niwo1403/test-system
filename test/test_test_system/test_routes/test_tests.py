# std
from json import loads as json_loads
from pytest import fixture
from typing import List
# 3rd party
from flask.testing import FlaskClient
# custom
from test_system.models import Token, Test
from test_system.routes.tests import ROUTE


@fixture()
def token(session, test_names) -> Token:
    token = Token.generate_token(10,
                                 test_names["PERSONAL_DATA_TEST"],
                                 test_names["PRE_COLLECT_TESTS"],
                                 test_names["EVALUABLE_TEST"])
    session.add(token)
    session.commit()
    return token


@fixture()
def no_use_token(session, test_names) -> Token:
    no_use_token = Token.generate_token(0,
                                        test_names["PERSONAL_DATA_TEST"],
                                        test_names["PRE_COLLECT_TESTS"],
                                        test_names["EVALUABLE_TEST"])
    session.add(no_use_token)
    session.commit()
    return no_use_token


@fixture()
def unknown_test_tokens(session, test_names) -> List[Token]:
    unknown_test_tokens = [
        Token.generate_token(10, None, test_names["PRE_COLLECT_TESTS"], test_names["EVALUABLE_TEST"]),
        Token.generate_token(10, test_names["PERSONAL_DATA_TEST"], test_names["PRE_COLLECT_TESTS"], None)]
    session.add_all(unknown_test_tokens)
    session.commit()
    return unknown_test_tokens


@fixture()
def wrong_test_tokens(session, test_names) -> List[Token]:
    personal_data_test = test_names["PERSONAL_DATA_TEST"]
    evaluable_test = test_names["EVALUABLE_TEST"]
    pre_collect_tests = test_names["PRE_COLLECT_TESTS"]
    wrong_test_tokens = [
        Token.generate_token(10, evaluable_test, pre_collect_tests, evaluable_test),
        Token.generate_token(10, pre_collect_tests[0], pre_collect_tests, evaluable_test),
        Token.generate_token(10, personal_data_test, pre_collect_tests, personal_data_test),
        Token.generate_token(10, personal_data_test, pre_collect_tests, pre_collect_tests[0])]
    session.add_all(wrong_test_tokens)
    session.commit()
    return wrong_test_tokens


def test_get_tests__with_success(client: FlaskClient, raise_if_change_in_tables, token: Token, test_names):
    with raise_if_change_in_tables(Token, Test):  # get request should not change data
        resp = client.get(ROUTE, query_string={"token": token.token})
    assert resp.status_code == 200, f"Can't GET tests from {ROUTE} with token: {token}"

    resp_tests = json_loads(resp.data.decode())
    resp_test_names = {
        "PERSONAL_DATA_TEST": resp_tests["personal_data_test"]["name"],
        "PRE_COLLECT_TESTS": [pre_collect_test_description["name"]
                              for pre_collect_test_description in resp_tests["pre_collect_tests"]],
        "EVALUABLE_TEST": resp_tests["evaluable_test"]["name"]
    }

    assert resp_test_names == test_names, f"Got tests with wrong names in response data at route {ROUTE} with {token}"


def test_get_tests__with_bad_request(client: FlaskClient, raise_if_change_in_tables):
    test_query_strings = [
        {},
        {"token": None},
    ]

    with raise_if_change_in_tables(Token, Test):
        for query_string in test_query_strings:
            resp = client.get(ROUTE, query_string=query_string)
            assert resp.status_code == 400, (f"Got wrong status code at {ROUTE} for bad request "
                                             f"with arguments: {query_string}")


def test_get_tests__with_unauthorized_request(client: FlaskClient, raise_if_change_in_tables, no_use_token: Token):
    test_query_strings = [
        {"token": "UNKNOWN TOKEN"},
        {"token": no_use_token.token},
    ]

    with raise_if_change_in_tables(Token, Test):
        for query_string in test_query_strings:
            resp = client.get(ROUTE, query_string=query_string)
            assert resp.status_code == 401, (f"Got wrong status code at {ROUTE} for unauthorized request "
                                             f"with arguments: {query_string}")


def test_get_tests__with_unknown_test_in_token(client: FlaskClient, raise_if_change_in_tables,
                                               unknown_test_tokens: List[Token]):
    with raise_if_change_in_tables(Token, Test):
        for unknown_test_token in unknown_test_tokens:
            resp = client.get(ROUTE, query_string={"token": unknown_test_token.token})
            assert resp.status_code == 404, (f"Got wrong status code at {ROUTE} for request "
                                             f"with unknown test in {unknown_test_token}")


def test_get_tests__with_wrong_test_in_token(client: FlaskClient, raise_if_change_in_tables,
                                             wrong_test_tokens: List[Token]):
    with raise_if_change_in_tables(Token, Test):
        for wrong_test_token in wrong_test_tokens:
            resp = client.get(ROUTE, query_string={"token": wrong_test_token.token})
            assert resp.status_code == 500, (f"Got wrong status code at {ROUTE} for request "
                                             f"with wrong test in {wrong_test_token}")
