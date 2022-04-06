# std
from typing import List, Callable
from io import BytesIO
# 3rd party
from pytest import fixture
from flask.testing import FlaskClient
from PyPDF2.pdf import PdfFileReader
from PyPDF2.utils import PdfReadError
# custom
from test_system.models import Token, Test, TestAnswer, EvaluableTestAnswer
from test_system.routes.test_answer_pdf import ROUTE


@fixture()
def test_answer(session, token, personal_data_answer) -> TestAnswer:
    test_answer = TestAnswer(answer_json={"Q": "A"},
                             test_name=token.evaluable_test_name,
                             personal_data_answer_id=personal_data_answer.id)
    session.add(test_answer)
    session.commit()
    return test_answer


@fixture()
def create_evaluated_evaluable_test_answer_for_token(session, test_answer) -> Callable[[Token], EvaluableTestAnswer]:
    def _create_evaluated_evaluable_test_answer_for_token(token: Token) -> EvaluableTestAnswer:
        evaluated_evaluable_test_answer = EvaluableTestAnswer(was_evaluated_with_token=token.token,
                                                              test_answer_id=test_answer.id)
        session.add(evaluated_evaluable_test_answer)
        session.commit()
        return evaluated_evaluable_test_answer
    return _create_evaluated_evaluable_test_answer_for_token


@fixture()
def evaluated_evaluable_test_answer(create_evaluated_evaluable_test_answer_for_token, token) -> EvaluableTestAnswer:
    return create_evaluated_evaluable_test_answer_for_token(token)


@fixture()
def unevaluated_evaluable_test_answer(session, test_answer) -> EvaluableTestAnswer:
    unevaluated_evaluable_test_answer = EvaluableTestAnswer(was_evaluated_with_token=None,
                                                            test_answer_id=test_answer.id)
    session.add(unevaluated_evaluable_test_answer)
    session.commit()
    return unevaluated_evaluable_test_answer


@fixture()
def incomplete_evaluable_test_answers(session, test_names, token) -> List[EvaluableTestAnswer]:
    test_answer = TestAnswer(answer_json={}, test_name=test_names[Test.CATEGORIES.EVALUABLE_TEST.name])
    session.add(test_answer)
    session.commit()
    incomplete_evaluable_test_answers = [
        EvaluableTestAnswer(was_evaluated_with_token=token.token, test_answer_id=None),
        EvaluableTestAnswer(was_evaluated_with_token=None, test_answer_id=None),
        EvaluableTestAnswer(was_evaluated_with_token=token.token, test_answer_id=test_answer.id),
        EvaluableTestAnswer(was_evaluated_with_token=None, test_answer_id=test_answer.id)
    ]
    session.add_all(incomplete_evaluable_test_answers)
    session.commit()
    return incomplete_evaluable_test_answers


def test_get_test_answer_pdf__with_success(client: FlaskClient, session,
                                           token, unlimited_token, no_use_token, expired_token,
                                           create_evaluated_evaluable_test_answer_for_token):
    test_cases = [(token, create_evaluated_evaluable_test_answer_for_token(token)),
                  (expired_token, create_evaluated_evaluable_test_answer_for_token(expired_token)),
                  (no_use_token, create_evaluated_evaluable_test_answer_for_token(no_use_token))]

    for test_token, evaluable_test_answer in test_cases:
        resp = client.get(ROUTE, query_string={"evaluable-test-answer-id": evaluable_test_answer.id,
                                               "token": test_token.token})
        assert resp.status_code == 200, (f"Can't GET test-answer-pdf from {ROUTE} with {evaluable_test_answer}"
                                         f"\n\nReceived response:\n{resp.get_data(True)}")

        try:
            PdfFileReader(BytesIO(resp.data))
        except PdfReadError as pdf_error:
            assert pdf_error is None, (f"Got invalid pdf bytes from {ROUTE} for {evaluable_test_answer}"
                                       f"\n\nReceived response:\n{resp.get_data(True)}")


def test_get_test_answer_pdf__with_bad_request(client: FlaskClient, session, raise_if_change_in_tables,
                                               token, evaluated_evaluable_test_answer,
                                               unevaluated_evaluable_test_answer):
    query_strings = [
        {"evaluable-test-answer-id": evaluated_evaluable_test_answer.id},
        {"evaluable-test-answer-id": evaluated_evaluable_test_answer.id, "token": None},
        {"evaluable-test-answer-id": unevaluated_evaluable_test_answer.id},
        {"evaluable-test-answer-id": unevaluated_evaluable_test_answer.id, "token": None},
        {"token": token.token},
        {"evaluable-test-answer-id": None, "token": token.token}
    ]

    with raise_if_change_in_tables(Token, TestAnswer, EvaluableTestAnswer):
        for query_string in query_strings:
            resp = client.get(ROUTE, query_string=query_string)
            assert resp.status_code == 400, (f"Got wrong status code at {ROUTE} for bad request with arguments: "
                                             f"{query_string}\n\nReceived response:\n{resp.get_data(True)}")


def test_get_test_answer_pdf__with_unknown_data(client: FlaskClient, session, raise_if_change_in_tables,
                                                token, incomplete_evaluable_test_answers):
    query_strings = [
        {"token": token.token, "evaluable-test-answer-id": str(incomplete_evaluable_test_answer.id)}
        for incomplete_evaluable_test_answer in incomplete_evaluable_test_answers
    ] + [{"token": token.token, "evaluable-test-answer-id": "-1"}]

    with raise_if_change_in_tables(Token, TestAnswer, EvaluableTestAnswer):
        for query_string in query_strings:
            resp = client.get(ROUTE, query_string=query_string)
            assert resp.status_code == 404, (f"Got wrong status code at {ROUTE} for request with unknown data & "
                                             f"arguments: {query_string}\n\nReceived response:\n{resp.get_data(True)}")


def test_get_test_answer_pdf__with_unauthorized_request(client: FlaskClient, session, raise_if_change_in_tables,
                                                        unknown_token_name, no_use_token, expired_token,
                                                        token, unlimited_token, unevaluated_evaluable_test_answer,
                                                        evaluated_evaluable_test_answer):
    query_strings = [
        {"token": "##########", "evaluable-test-answer-id": evaluated_evaluable_test_answer.id},
        {"token": token.token, "evaluable-test-answer-id": unevaluated_evaluable_test_answer.id},
        # passed token doesn't match used token of evaluated_evaluable_test_answer
        {"token": no_use_token.token, "evaluable-test-answer-id": evaluated_evaluable_test_answer.id},
        {"token": expired_token.token, "evaluable-test-answer-id": evaluated_evaluable_test_answer.id},
        {"token": unlimited_token.token, "evaluable-test-answer-id": evaluated_evaluable_test_answer.id}
    ]

    with raise_if_change_in_tables(Token, TestAnswer, EvaluableTestAnswer):
        for query_string in query_strings:
            resp = client.get(ROUTE, query_string=query_string)
            assert resp.status_code == 401, (f"Got wrong status code at {ROUTE} for unauthorized request with "
                                             f"arguments: {query_string}\n\nReceived response:\n{resp.get_data(True)}")
