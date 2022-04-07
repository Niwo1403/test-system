# std
from json import dumps as json_dumps
from typing import Optional
# 3rd party
from pytest import fixture
from flask.testing import FlaskClient
from werkzeug.test import TestResponse
# custom
from test_system.models import Test, TestAnswer, Token, EvaluableTestAnswer
from test_system.routes.test_answer import ROUTE


TEST_ANSWER = {"Question A": "Answer A"}
TEST_ANSWER_JSON = json_dumps(TEST_ANSWER)
EVALUABLE_TEST_ANSWER = {"Category A": {"Question 1": "1", "Question 2": "2"},
                         "Category B": {"Question 1": "3", "Question 2": "4"},
                         "Question X": "5",
                         "Ignored question": "TEXT!"}
EVALUABLE_TEST_ANSWER_JSON = json_dumps(EVALUABLE_TEST_ANSWER)


def _check_token_usage(evaluable_answer: Optional[EvaluableTestAnswer], test_token: Token, resp: TestResponse):
    pre_max_usage_count = test_token.max_usage_count  # is still the old value
    # token must be reloaded after extern change:
    test_token = Token.query.filter_by(token=test_token.token).first()
    assert test_token.max_usage_count is None or test_token.max_usage_count + 1 == pre_max_usage_count, \
        (f"Got wrong max_usage_count after request at {ROUTE} with {test_token}"
         f"\n\nReceived response:\n{resp.get_data(True)}")
    assert evaluable_answer is not None, ("Could not write EvaluableTestAnswer to database"
                                          f"\n\nReceived response:\n{resp.get_data(True)}")
    assert evaluable_answer.was_evaluated_with_token == test_token.token, \
        f"Wrong token was used to save EvaluableTestAnswer\n\nReceived response:\n{resp.get_data(True)}"


def test_post_test_answer__with_success(client: FlaskClient, session, personal_data_answer, token, unlimited_token,
                                        pre_collect_test, evaluable_test):
    test_cases = [
        (token, pre_collect_test),
        (token, evaluable_test),
        (unlimited_token, evaluable_test),
    ]

    for test_token, test_test in test_cases:
        resp = client.post(ROUTE, data=EVALUABLE_TEST_ANSWER_JSON, query_string={
            "test-name": test_test.name, "personal-data-answer-id": personal_data_answer.id, "token": test_token.token})
        assert resp.status_code == 201, (f"Can't POST test answer to {ROUTE} with data {EVALUABLE_TEST_ANSWER}, "
                                         f"{test_test}, {test_token}\n\nReceived response:\n{resp.get_data(True)}")

        resp_id = resp.get_data(True)
        if test_test.test_category == Test.CATEGORIES.EVALUABLE_TEST:
            evaluable_answer: EvaluableTestAnswer = EvaluableTestAnswer.query.filter_by(id=resp_id).first()
            _check_token_usage(evaluable_answer, test_token, resp)
            answer: TestAnswer = evaluable_answer.test_answer
        else:
            answer: TestAnswer = TestAnswer.query.filter_by(id=resp_id).first()

        assert answer is not None, (f"Could not write TestAnswer to database"
                                    f"\n\nReceived response:\n{resp.get_data(True)}")
        assert answer.answer_json == EVALUABLE_TEST_ANSWER and \
               answer.test_name == test_test.name and \
               answer.personal_data_answer_id == personal_data_answer.id, (
                f"TestAnswer which was written to database has wrong data: {answer}"
                f"\n\nReceived response:\n{resp.get_data(True)}")


def test_post_test_answer__with_bad_request(client: FlaskClient, session, raise_if_change_in_tables,
                                            personal_data_answer, token, pre_collect_test, evaluable_test):
    correct_query_string = {"test-name": evaluable_test.name, "personal-data-answer-id": personal_data_answer.id}
    test_arguments = [
                      # missing argument
                      (TEST_ANSWER_JSON, {"personal-data-answer-id": personal_data_answer.id, "token": token.token}),
                      (EVALUABLE_TEST_ANSWER_JSON, {"test-name": evaluable_test.name, "token": token.token}),
                      (TEST_ANSWER_JSON, {"test-name": pre_collect_test.name, "token": token.token}),
                      (EVALUABLE_TEST_ANSWER_JSON,
                       {"test-name": evaluable_test.name, "personal-data-answer-id": personal_data_answer.id}),
                      (TEST_ANSWER_JSON,
                       {"test-name": pre_collect_test.name, "personal-data-answer-id": personal_data_answer.id}),
                      # invalid JSON
                      ("", correct_query_string),
                      ("{", correct_query_string),
                      ("{true: \"3\"}", correct_query_string),
                      ("{'true': \"3\"}", correct_query_string),
                      # invalid schema
                      ("{\"key\": null}", correct_query_string)]

    with raise_if_change_in_tables(Test, TestAnswer, EvaluableTestAnswer, Token):
        for data, query_string in test_arguments:
            resp = client.post(ROUTE, data=data, query_string=query_string)
            assert resp.status_code == 400, (f"Got wrong status code at {ROUTE} for arguments: {query_string}, "
                                             f"and data {data}\n\nReceived response:\n{resp.get_data(True)}")


def test_post_test_answer__with_wrong_test(client: FlaskClient, session, raise_if_change_in_tables,
                                           personal_data_answer, token, personal_data_test):
    unknown_test_name = "?`?`?`?`?`?`?`?`?`?`?`?`?`?`?"

    with raise_if_change_in_tables(Test, TestAnswer, EvaluableTestAnswer, Token):
        resp = client.post(ROUTE, data=TEST_ANSWER_JSON, query_string={
            "test-name": unknown_test_name, "personal-data-answer-id": personal_data_answer.id, "token": token.token})
        assert resp.status_code == 404, (f"Got wrong status code at {ROUTE} for unknown test name: {unknown_test_name}"
                                         f"\n\nReceived response:\n{resp.get_data(True)}")

        resp = client.post(ROUTE,
                           data=TEST_ANSWER_JSON,
                           query_string={"test-name": personal_data_test.name,
                                         "personal-data-answer-id": personal_data_answer.id,
                                         "token": token.token})
        assert resp.status_code == 400, (f"Got wrong status code at {ROUTE} for test with wrong test category: "
                                         f"{personal_data_test.name}\n\nReceived response:\n{resp.get_data(True)}")


def test_post_test_answer__with_unauthorized_request(client: FlaskClient, session, raise_if_change_in_tables,
                                                     personal_data_answer, pre_collect_test, evaluable_test,
                                                     expired_token, no_use_token):
    unknown_token = "#####################"
    test_arguments = []
    for wrong_token in (unknown_token, expired_token.token, no_use_token.token):
        test_arguments += [
            (TEST_ANSWER_JSON, {"test-name": pre_collect_test.name,
                                "personal-data-answer-id": personal_data_answer.id,
                                "token": wrong_token}),
            (EVALUABLE_TEST_ANSWER_JSON, {"test-name": evaluable_test.name,
                                          "personal-data-answer-id": personal_data_answer.id,
                                          "token": wrong_token})]

    with raise_if_change_in_tables(Test, TestAnswer, EvaluableTestAnswer, Token):
        for data, query_string in test_arguments:
            resp = client.post(ROUTE, data=data, query_string=query_string)
            assert resp.status_code == 401, (f"Got wrong status code at {ROUTE} for data: {data} and query_string: "
                                             f"{query_string}\n\nReceived response:\n{resp.get_data(True)}")


def test_post_test_answer__with_wrong_personal_data_answer(client: FlaskClient, session, raise_if_change_in_tables,
                                                           token, pre_collect_test, evaluable_test):
    unknown_personal_data_answer_id = -1
    test_arguments = [(TEST_ANSWER_JSON, {"test-name": pre_collect_test.name,
                                          "personal-data-answer-id": unknown_personal_data_answer_id,
                                          "token": token.token}),
                      (EVALUABLE_TEST_ANSWER_JSON, {"test-name": evaluable_test.name,
                                                    "personal-data-answer-id": unknown_personal_data_answer_id,
                                                    "token": token.token})]

    with raise_if_change_in_tables(Test, TestAnswer, EvaluableTestAnswer, Token):
        for data, query_string in test_arguments:
            resp = client.post(ROUTE, data=data, query_string=query_string)
            assert resp.status_code == 404, (f"Got wrong status code at {ROUTE} for data: {data} and query_string: "
                                             f"{query_string}\n\nReceived response:\n{resp.get_data(True)}")
