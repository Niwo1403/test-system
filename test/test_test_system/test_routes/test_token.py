# std
from json import dumps as json_dumps
from pytest import fixture
from typing import Dict, List, Callable
# 3rd party
from flask.testing import FlaskClient
# custom
from test_system.models import Token, User, Test
from test_system.routes.token import ROUTE

PRE_COLLECT_TESTS = Test.CATEGORIES.PRE_COLLECT_TESTS.name
MANDATORY_KEYS = [Test.CATEGORIES.PERSONAL_DATA_TEST.name, Test.CATEGORIES.EVALUABLE_TEST.name,
                  User.username.key, User.password.key]


@fixture()
def create_post_data(username, password, test_names) -> Callable:
    def _create_post_data(without_keys: List = None, with_replacements: Dict = None) -> Dict:
        base_post_data = {
            Token.max_usage_count.key: 10,

            User.username.key: username,
            User.password.key: password}
        base_post_data.update(test_names)
        base_post_data[PRE_COLLECT_TESTS] = list(map(
            lambda test_name: {"tests": test_name}, base_post_data[PRE_COLLECT_TESTS]))

        if without_keys is not None:
            for without_key in without_keys:
                base_post_data.pop(without_key, None)
        if with_replacements is not None:
            base_post_data.update(with_replacements)
        return base_post_data
    return _create_post_data


def test_post_token__with_success(client: FlaskClient, session, create_post_data, test_names):
    test_cases = [create_post_data(),
                  create_post_data(without_keys=[Token.max_usage_count.key]),
                  create_post_data(without_keys=[PRE_COLLECT_TESTS]),
                  create_post_data(without_keys=[PRE_COLLECT_TESTS, Token.max_usage_count.key])]

    for test_data in test_cases:
        resp = client.post(ROUTE, data=json_dumps(test_data))
        assert resp.status_code == 201, f"Can't POST token to {ROUTE} with data {test_data}\n\n{resp.data.decode()}"

        token_hash = resp.data.decode()
        token = Token.query.filter_by(token=token_hash).first()
        assert token is not None, "Could not write Token to database"

        database_token_data = {
            Test.CATEGORIES.PERSONAL_DATA_TEST.name: token.personal_data_test_name,
            PRE_COLLECT_TESTS: token.pre_collect_test_names,
            Test.CATEGORIES.EVALUABLE_TEST.name: token.evaluable_test_name,
            Token.max_usage_count.key: token.max_usage_count
        }
        # copy database_token_data as base for correct data and update it with passed test data
        # (non passed values are considered correct, since default values can be anything)
        correct_token_data = database_token_data.copy()
        correct_token_data.update(test_data)
        if PRE_COLLECT_TESTS in test_data:
            correct_token_data[PRE_COLLECT_TESTS] = list(map(lambda e: e["tests"],
                                                             correct_token_data[PRE_COLLECT_TESTS]))
        # drop user data, so only token data remains
        correct_token_data.pop(User.username.key, None)
        correct_token_data.pop(User.password.key, None)

        assert database_token_data == correct_token_data and len(token_hash) == 128, \
            f"Got token with wrong data in database at route {ROUTE} with post data {test_data}: {token}"


def test_post_token__with_bad_request(client: FlaskClient, session, raise_if_change_in_tables, create_post_data):
    bad_data = [
        create_post_data(without_keys=[mandatory_key])
        for mandatory_key in MANDATORY_KEYS
    ] + [
        create_post_data(with_replacements={mandatory_key: ""})
        for mandatory_key in MANDATORY_KEYS
    ] + [
        create_post_data(with_replacements={mandatory_key: 10})
        for mandatory_key in MANDATORY_KEYS
    ] + [
        create_post_data(with_replacements={mandatory_key: None})
        for mandatory_key in MANDATORY_KEYS
    ] + [
        create_post_data(with_replacements={PRE_COLLECT_TESTS: wrong_pre_collect_value})
        for wrong_pre_collect_value in ["", None, 3.14, ["asdf"]]
    ] + [
        create_post_data(with_replacements={Token.max_usage_count.key: wrong_usage_counts})
        for wrong_usage_counts in ["", None, 3.14, ["asdf"], "asdf"]
    ]

    with raise_if_change_in_tables(Token, User, Test):
        for bad_post_data in bad_data:
            resp = client.post(ROUTE, data=json_dumps(bad_post_data))
            assert resp.status_code == 400, (f"Got wrong status code at {ROUTE} for bad request "
                                             f"with data: {bad_post_data}")


def test_post_token__with_unauthorized_request(client: FlaskClient, session, raise_if_change_in_tables,
                                               create_post_data):
    unauthorized_data = [
        create_post_data(with_replacements=replacement)
        for replacement in [{User.username.key: "UNKNOWN USERNAME"}, {User.password.key: "WRONG PASSWORD"}]
    ]

    with raise_if_change_in_tables(Token, User, Test):
        for unauthorized_post_data in unauthorized_data:
            resp = client.post(ROUTE, data=json_dumps(unauthorized_post_data))
            assert resp.status_code == 401, (f"Got wrong status code at {ROUTE} for unauthorized request "
                                             f"with data: {unauthorized_post_data}")


def test_post_token__with_unknown_test(client: FlaskClient, session, raise_if_change_in_tables, create_post_data):
    unknown_test_data = [
        create_post_data(with_replacements=replacement)
        for replacement in [{Test.CATEGORIES.PERSONAL_DATA_TEST.name: "UNKNOWN TEST"},
                            {Test.CATEGORIES.EVALUABLE_TEST.name: "UNKNOWN TEST"}]
    ]

    with raise_if_change_in_tables(Token, User, Test):
        for unknown_test_post_data in unknown_test_data:
            resp = client.post(ROUTE, data=json_dumps(unknown_test_post_data))
            assert resp.status_code == 404, (f"Got wrong status code at {ROUTE} for unknown test name in request "
                                             f"with data: {unknown_test_post_data}")


def test_post_token__with_wrong_test(client: FlaskClient, session, raise_if_change_in_tables,
                                     create_post_data, test_names):
    first_pre_collect_test = test_names[Test.CATEGORIES.PRE_COLLECT_TESTS.name][0]
    unknown_test_data = [
        create_post_data(with_replacements=replacement)
        for replacement in [{Test.CATEGORIES.PERSONAL_DATA_TEST.name: test_names[Test.CATEGORIES.EVALUABLE_TEST.name]},
                            {Test.CATEGORIES.PERSONAL_DATA_TEST.name: first_pre_collect_test},
                            {Test.CATEGORIES.EVALUABLE_TEST.name: test_names[Test.CATEGORIES.PERSONAL_DATA_TEST.name]},
                            {Test.CATEGORIES.EVALUABLE_TEST.name: first_pre_collect_test}]
    ]

    with raise_if_change_in_tables(Token, User, Test):
        for unknown_test_post_data in unknown_test_data:
            resp = client.post(ROUTE, data=json_dumps(unknown_test_post_data))
            assert resp.status_code == 400, (f"Got wrong status code at {ROUTE} for wrong test name in request "
                                             f"with data: {unknown_test_post_data}")
