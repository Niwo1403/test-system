# std
from json import dumps as json_dumps
from typing import Dict, List, Callable
# 3rd party
from pytest import fixture
from flask.testing import FlaskClient
# custom
from test_system.constants import PRE_COLLECT_TESTS_SURVEY_KEYWORD, EXPIRES_SURVEY_KEYWORD, PRE_COLLECT_TESTS_KEY
from test_system.models import Token, User, Test
from test_system.routes.token import ROUTE

MANDATORY_STRING_VALUE_KEYS = [Test.CATEGORIES.PERSONAL_DATA_TEST.name, Test.CATEGORIES.EXPORTABLE_TEST.name,
                               User.username.key, User.password.key]
MANDATORY_KEYS = MANDATORY_STRING_VALUE_KEYS + [EXPIRES_SURVEY_KEYWORD]


@fixture()
def create_post_data(username, password, test_names) -> Callable[..., Dict]:
    def _create_post_data(without_keys: List = None, with_replacements: Dict = None, expires: bool = True) -> Dict:
        base_post_data = {
            Token.max_usage_count.key: 10,
            EXPIRES_SURVEY_KEYWORD: expires,

            User.username.key: username,
            User.password.key: password}
        base_post_data.update(test_names)
        base_post_data[PRE_COLLECT_TESTS_KEY] = list(map(
            lambda test_name: {PRE_COLLECT_TESTS_SURVEY_KEYWORD: test_name}, base_post_data[PRE_COLLECT_TESTS_KEY]))

        if without_keys is not None:
            for without_key in without_keys:
                base_post_data.pop(without_key, None)
        if with_replacements is not None:
            base_post_data.update(with_replacements)
        return base_post_data
    return _create_post_data


def test_post_token__with_success(client: FlaskClient, session, create_post_data):
    test_cases = [create_post_data(),
                  create_post_data(expires=False),
                  create_post_data(without_keys=[Token.max_usage_count.key]),
                  create_post_data(without_keys=[Token.max_usage_count.key], expires=False),
                  create_post_data(without_keys=[PRE_COLLECT_TESTS_KEY]),
                  create_post_data(without_keys=[PRE_COLLECT_TESTS_KEY, Token.max_usage_count.key])]

    for test_data in test_cases:
        resp = client.post(ROUTE, data=json_dumps(test_data))
        assert resp.status_code == 201, (f"Can't POST token to {ROUTE} with data {test_data}"
                                         f"\n\nReceived response:\n{resp.get_data(True)}")

        token_hash = resp.get_data(True)
        token = Token.query.filter_by(token=token_hash).first()
        assert token is not None, f"Could not write Token to database\n\nReceived response:\n{resp.get_data(True)}"

        database_token_data = {
            Test.CATEGORIES.PERSONAL_DATA_TEST.name: token.personal_data_test_name,
            PRE_COLLECT_TESTS_KEY: token.pre_collect_test_names,
            Test.CATEGORIES.EXPORTABLE_TEST.name: token.exportable_test_name,
            Token.max_usage_count.key: token.max_usage_count,
            EXPIRES_SURVEY_KEYWORD: token.creation_timestamp is not None
        }
        # copy database_token_data as base for correct data and update it with passed test data
        # (non passed values are considered correct, since default values can be anything)
        correct_token_data = database_token_data.copy()
        correct_token_data.update(test_data)
        if PRE_COLLECT_TESTS_KEY in test_data:
            correct_token_data[PRE_COLLECT_TESTS_KEY] = list(map(lambda e: e[PRE_COLLECT_TESTS_SURVEY_KEYWORD],
                                                                 correct_token_data[PRE_COLLECT_TESTS_KEY]))
        # drop user data, so only token data remains
        correct_token_data.pop(User.username.key, None)
        correct_token_data.pop(User.password.key, None)

        assert database_token_data == correct_token_data and len(token_hash) == 128, \
            (f"Got token with wrong data in database at route {ROUTE} with post data {test_data}: {token}"
             f"\n\nReceived response:\n{resp.get_data(True)}")


def test_post_token__with_bad_request(client: FlaskClient, session, raise_if_change_in_tables, create_post_data):
    bad_data = [
        create_post_data(without_keys=[mandatory_key])
        for mandatory_key in MANDATORY_KEYS
    ] + [
        create_post_data(with_replacements={mandatory_key: mandatory_key_replacement})
        for mandatory_key in MANDATORY_STRING_VALUE_KEYS
        for mandatory_key_replacement in ["", 10, None, True, ["asdf"]]
    ] + [
        create_post_data(with_replacements={EXPIRES_SURVEY_KEYWORD: wrong_expires_value})
        for wrong_expires_value in ["", "asdf", 10, None, ["asdf"]]
    ] + [
        create_post_data(with_replacements={PRE_COLLECT_TESTS_KEY: wrong_pre_collect_value})
        for wrong_pre_collect_value in ["asdf", None, 10, 3.14, ["asdf"]]
    ] + [
        create_post_data(with_replacements={Token.max_usage_count.key: wrong_usage_counts})
        for wrong_usage_counts in ["", None, 3.14, ["asdf"], "asdf"]
    ]

    with raise_if_change_in_tables(Token, User, Test):
        for bad_post_data in bad_data:
            resp = client.post(ROUTE, data=json_dumps(bad_post_data))
            assert resp.status_code == 400, (f"Got wrong status code at {ROUTE} for bad request with data: "
                                             f"{bad_post_data}\n\nReceived response:\n{resp.get_data(True)}")


def test_post_token__with_unauthorized_request(client: FlaskClient, session, raise_if_change_in_tables,
                                               create_post_data):
    unauthorized_data = [
        create_post_data(with_replacements=replacement)
        for replacement in [{User.username.key: "UNKNOWN USERNAME"}, {User.password.key: "WRONG PASSWORD"}]
    ]

    with raise_if_change_in_tables(Token, User, Test):
        for unauthorized_post_data in unauthorized_data:
            resp = client.post(ROUTE, data=json_dumps(unauthorized_post_data))
            assert resp.status_code == 401, (f"Got wrong status code at {ROUTE} for unauthorized request with data: "
                                             f"{unauthorized_post_data}\n\nReceived response:\n{resp.get_data(True)}")


def test_post_token__with_unknown_test(client: FlaskClient, session, raise_if_change_in_tables, create_post_data):
    unknown_test_data = [
        create_post_data(with_replacements=replacement)
        for replacement in [{Test.CATEGORIES.PERSONAL_DATA_TEST.name: "UNKNOWN TEST"},
                            {Test.CATEGORIES.EXPORTABLE_TEST.name: "UNKNOWN TEST"}]
    ]

    with raise_if_change_in_tables(Token, User, Test):
        for unknown_test_post_data in unknown_test_data:
            resp = client.post(ROUTE, data=json_dumps(unknown_test_post_data))
            assert resp.status_code == 404, (f"Got wrong status code at {ROUTE} for unknown test name with data: "
                                             f"{unknown_test_post_data}\n\nReceived response:\n{resp.get_data(True)}")


def test_post_token__with_wrong_test(client: FlaskClient, session, raise_if_change_in_tables,
                                     create_post_data, test_names):
    first_pre_collect_test = test_names[PRE_COLLECT_TESTS_KEY][0]
    unknown_test_data = [
        create_post_data(with_replacements=replacement)
        for replacement in [{Test.CATEGORIES.PERSONAL_DATA_TEST.name: test_names[Test.CATEGORIES.EXPORTABLE_TEST.name]},
                            {Test.CATEGORIES.PERSONAL_DATA_TEST.name: first_pre_collect_test},
                            {Test.CATEGORIES.EXPORTABLE_TEST.name: test_names[Test.CATEGORIES.PERSONAL_DATA_TEST.name]},
                            {Test.CATEGORIES.EXPORTABLE_TEST.name: first_pre_collect_test}]
    ]

    with raise_if_change_in_tables(Token, User, Test):
        for unknown_test_post_data in unknown_test_data:
            resp = client.post(ROUTE, data=json_dumps(unknown_test_post_data))
            assert resp.status_code == 400, (f"Got wrong status code at {ROUTE} for wrong test name with data: "
                                             f"{unknown_test_post_data}\n\nReceived response:\n{resp.get_data(True)}")
