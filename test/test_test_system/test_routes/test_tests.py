# std
from json import loads as json_loads
from pytest import fixture
from typing import List
# 3rd party
from flask.testing import FlaskClient
# custom
from test_system.models import Token, Test
from test_system.routes.tests import ROUTE
from test_system.constants import PRE_COLLECT_TESTS_KEY


def _create_and_commit_token(session, *args) -> Token:
    token = Token.generate_token(*args)
    session.add(token)
    session.commit()
    return token


@fixture()
def unknown_test_tokens(session, test_names) -> List[Token]:
    unknown_test_tokens = [
        _create_and_commit_token(session, 10, None, test_names[PRE_COLLECT_TESTS_KEY],
                                 test_names[Test.CATEGORIES.EVALUABLE_TEST.name]),
        _create_and_commit_token(session, 10, test_names[Test.CATEGORIES.PERSONAL_DATA_TEST.name],
                                 test_names[PRE_COLLECT_TESTS_KEY], None)]
    return unknown_test_tokens


@fixture()
def wrong_test_tokens(session, test_names) -> List[Token]:
    personal_data_test = test_names[Test.CATEGORIES.PERSONAL_DATA_TEST.name]
    evaluable_test = test_names[Test.CATEGORIES.EVALUABLE_TEST.name]
    pre_collect_tests = test_names[PRE_COLLECT_TESTS_KEY]
    wrong_test_tokens = [
        _create_and_commit_token(session, 10, evaluable_test, pre_collect_tests, evaluable_test),
        _create_and_commit_token(session, 10, pre_collect_tests[0], pre_collect_tests, evaluable_test),
        _create_and_commit_token(session, 10, personal_data_test, pre_collect_tests, personal_data_test),
        _create_and_commit_token(session, 10, personal_data_test, pre_collect_tests, pre_collect_tests[0])]
    return wrong_test_tokens


def test_get_tests__with_success(client: FlaskClient, session, raise_if_change_in_tables,
                                 token: Token, unlimited_token: Token, test_names):
    for test_token in (token, unlimited_token):
        with raise_if_change_in_tables(Token, Test):  # get request should not change data
            resp = client.get(ROUTE, query_string={"token": test_token.token})
        assert resp.status_code == 200, f"Can't GET tests from {ROUTE} with token: {test_token}"

        resp_tests = json_loads(resp.data.decode())
        resp_test_names = {
            Test.CATEGORIES.PERSONAL_DATA_TEST.name: resp_tests["personal_data_test"]["name"],
            PRE_COLLECT_TESTS_KEY: [pre_collect_test_description["name"]
                                    for pre_collect_test_description in resp_tests["pre_collect_tests"]],
            Test.CATEGORIES.EVALUABLE_TEST.name: resp_tests["evaluable_test"]["name"]
        }

        assert resp_test_names == test_names, f"Got tests with wrong names in response data at route {ROUTE} "\
                                              f"with {test_token}"


def test_get_tests__with_bad_request(client: FlaskClient, session, raise_if_change_in_tables):
    test_query_strings = [
        {},
        {"token": None},
    ]

    with raise_if_change_in_tables(Token, Test):
        for query_string in test_query_strings:
            resp = client.get(ROUTE, query_string=query_string)
            assert resp.status_code == 400, (f"Got wrong status code at {ROUTE} for bad request "
                                             f"with arguments: {query_string}")


def test_get_tests__with_unauthorized_request(client: FlaskClient, session, raise_if_change_in_tables,
                                              unknown_token_name: str, no_use_token: Token, expired_token: Token):
    test_query_strings = [
        {"token": unknown_token_name},
        {"token": no_use_token.token},
        {"token": expired_token.token}
    ]

    with raise_if_change_in_tables(Token, Test):
        for query_string in test_query_strings:
            resp = client.get(ROUTE, query_string=query_string)
            assert resp.status_code == 401, (f"Got wrong status code at {ROUTE} for unauthorized request "
                                             f"with arguments: {query_string}")


def test_get_tests__with_unknown_test_in_token(client: FlaskClient, session, raise_if_change_in_tables,
                                               unknown_test_tokens: List[Token]):
    with raise_if_change_in_tables(Token, Test):
        for unknown_test_token in unknown_test_tokens:
            resp = client.get(ROUTE, query_string={"token": unknown_test_token.token})
            assert resp.status_code == 404, (f"Got wrong status code at {ROUTE} for request "
                                             f"with unknown test in {unknown_test_token}")


def test_get_tests__with_wrong_test_in_token(client: FlaskClient, session, raise_if_change_in_tables,
                                             wrong_test_tokens: List[Token]):
    with raise_if_change_in_tables(Token, Test):
        for wrong_test_token in wrong_test_tokens:
            resp = client.get(ROUTE, query_string={"token": wrong_test_token.token})
            assert resp.status_code == 500, (f"Got wrong status code at {ROUTE} for request "
                                             f"with wrong test in {wrong_test_token}")
