# std
from pytest import fixture
from typing import List
from io import BytesIO
# 3rd party
from flask.testing import FlaskClient
from PyPDF2.pdf import PdfFileReader
from PyPDF2.utils import PdfReadError
# custom
from test_system.models import db, Token, Person, Test, TestAnswer, EvaluableTestAnswer, EvaluableQuestionAnswer
from test_system.routes.certificate import ROUTE


@fixture()
def person(session) -> Person:
    person = Person(name="TestName", gender=Person.GENDERS.s, age=22)
    session.add(person)
    session.commit()
    return person


@fixture()
def person_with_position(session) -> Person:
    person = Person(name="TestName", age=33, gender=Person.GENDERS.s, position="POSITION...")
    session.add(person)
    session.commit()
    return person


def _test_answer(session, token: Token, person: Person) -> TestAnswer:
    test_answer = TestAnswer(answer_set={}, test_name=token.evaluable_test_name, person_id=person.id)
    session.add(test_answer)
    session.commit()
    return test_answer


@fixture()
def test_answer(session, token: Token, person: Person) -> TestAnswer:
    return _test_answer(session, token, person)


@fixture()
def test_answer_2(session, token: Token, person_with_position: Person) -> TestAnswer:
    return _test_answer(session, token, person_with_position)


def _add_example_answers(session, evaluable_test_answer: EvaluableTestAnswer):
    answers = EvaluableQuestionAnswer.create_answers({"CATEGORY A": {"QUESTION 1": "3", "QUESTION 2": "1"}},
                                                     evaluable_test_answer)
    session.add_all(answers)
    session.commit()


@fixture()
def evaluated_evaluable_test_answer(session, test_answer) -> EvaluableTestAnswer:
    evaluated_evaluable_test_answer = EvaluableTestAnswer(was_evaluated_with_token=True, test_answer_id=test_answer.id)
    session.add(evaluated_evaluable_test_answer)
    session.commit()
    _add_example_answers(session, evaluated_evaluable_test_answer)
    return evaluated_evaluable_test_answer


def _unevaluated_evaluable_test_answer(session, test_answer) -> EvaluableTestAnswer:
    unevaluated_evaluable_test_answer = EvaluableTestAnswer(was_evaluated_with_token=False,
                                                            test_answer_id=test_answer.id)
    session.add(unevaluated_evaluable_test_answer)
    session.commit()
    _add_example_answers(session, unevaluated_evaluable_test_answer)
    return unevaluated_evaluable_test_answer


@fixture()
def unevaluated_evaluable_test_answer(session, test_answer) -> EvaluableTestAnswer:
    return _unevaluated_evaluable_test_answer(session, test_answer)


@fixture()
def unevaluated_evaluable_test_answer_2(session, test_answer_2) -> EvaluableTestAnswer:
    return _unevaluated_evaluable_test_answer(session, test_answer_2)


@fixture()
def incomplete_evaluable_test_answers(session, test_names) -> List[EvaluableTestAnswer]:
    test_answer = TestAnswer(answer_set={}, test_name=test_names[Test.CATEGORIES.EVALUABLE_TEST.name], person_id=None)
    session.add(test_answer)
    session.commit()
    incomplete_evaluable_test_answers = [
        EvaluableTestAnswer(was_evaluated_with_token=True, test_answer_id=None),
        EvaluableTestAnswer(was_evaluated_with_token=False, test_answer_id=None),
        EvaluableTestAnswer(was_evaluated_with_token=True, test_answer_id=test_answer.id),
        EvaluableTestAnswer(was_evaluated_with_token=False, test_answer_id=test_answer.id)
    ]
    session.add_all(incomplete_evaluable_test_answers)
    session.commit()
    return incomplete_evaluable_test_answers


@fixture()
def unlimited_token(session, test_names) -> Token:
    unlimited_token = Token.generate_token(None,
                                           test_names[Test.CATEGORIES.PERSONAL_DATA_TEST.name],
                                           test_names[Test.CATEGORIES.PRE_COLLECT_TESTS.name],
                                           test_names[Test.CATEGORIES.EVALUABLE_TEST.name])
    session.add(unlimited_token)
    session.commit()
    return unlimited_token


def test_get_certificate__with_success(client: FlaskClient, session,
                                       token: Token, no_use_token: Token, unlimited_token: Token,
                                       evaluated_evaluable_test_answer: EvaluableTestAnswer,
                                       unevaluated_evaluable_test_answer: EvaluableTestAnswer,
                                       unevaluated_evaluable_test_answer_2: EvaluableTestAnswer):
    test_cases = [(token, evaluated_evaluable_test_answer),
                  (token, unevaluated_evaluable_test_answer),
                  # EvaluableTestAnswers (like unevaluated_evaluable_test_answer) must NOT repeat,
                  # since the unevaluated answers will be evaluated after first request!
                  (unlimited_token, unevaluated_evaluable_test_answer_2),
                  (no_use_token, evaluated_evaluable_test_answer)]

    for token, evaluable_test_answer in test_cases:
        pre_was_evaluated_with_token = evaluable_test_answer.was_evaluated_with_token
        pre_max_usage_count = token.max_usage_count
        resp = client.get(ROUTE, query_string={"evaluable-test-answer-id": evaluable_test_answer.id,
                                               "token": token.token})

        token = Token.query.filter_by(token=token.token).first()
        evaluable_test_answer = EvaluableTestAnswer.query.filter_by(id=evaluable_test_answer.id).first()
        assert token is not None, f"Token was deleted while GET certificate request at {ROUTE}"
        assert evaluable_test_answer is not None, ("EvaluableTestAnswer was deleted while GET certificate request "
                                                   f"at {ROUTE}")

        assert resp.status_code == 200, f"Can't GET certificate from {ROUTE} with {evaluable_test_answer}"

        assert token.max_usage_count == pre_max_usage_count if pre_was_evaluated_with_token \
            else token.max_usage_count is None or token.max_usage_count + 1 == pre_max_usage_count, \
            f"Got wrong max_usage_count after request with {token} & {evaluable_test_answer}"

        try:
            PdfFileReader(BytesIO(resp.data))
        except PdfReadError as e:
            assert e is None, f"Got invalid pdf bytes from {ROUTE} for {evaluable_test_answer}"


def test_get_certificate__with_bad_request(client: FlaskClient, session, raise_if_change_in_tables,
                                           token: Token, evaluated_evaluable_test_answer: EvaluableTestAnswer,
                                           unevaluated_evaluable_test_answer: EvaluableTestAnswer):
    query_strings = [
        {"evaluable-test-answer-id": evaluated_evaluable_test_answer.id},
        {"evaluable-test-answer-id": evaluated_evaluable_test_answer.id, "token": None},
        {"evaluable-test-answer-id": unevaluated_evaluable_test_answer.id},
        {"evaluable-test-answer-id": unevaluated_evaluable_test_answer.id, "token": None},
        {"token": token.token},
        {"evaluable-test-answer-id": None, "token": token.token}
    ]

    with raise_if_change_in_tables(Token, Person, TestAnswer, EvaluableTestAnswer, EvaluableQuestionAnswer):
        for query_string in query_strings:
            resp = client.get(ROUTE, query_string=query_string)
            assert resp.status_code == 400, (f"Got wrong status code at {ROUTE} for bad request "
                                             f"with arguments: {query_string}")


def test_get_certificate__with_unknown_data(client: FlaskClient, session, raise_if_change_in_tables,
                                            token: Token, incomplete_evaluable_test_answers: List[EvaluableTestAnswer]):
    query_strings = [
        {"token": token.token, "evaluable-test-answer-id": str(incomplete_evaluable_test_answer.id)}
        for incomplete_evaluable_test_answer in incomplete_evaluable_test_answers
    ] + [{"token": token.token, "evaluable-test-answer-id": "-1"}]

    with raise_if_change_in_tables(Token, Person, TestAnswer, EvaluableTestAnswer, EvaluableQuestionAnswer):
        for query_string in query_strings:
            resp = client.get(ROUTE, query_string=query_string)
            assert resp.status_code == 404, (f"Got wrong status code at {ROUTE} for request with unknown data & "
                                             f"with arguments: {query_string}")


def test_get_certificate__with_unauthorized_request(client: FlaskClient, session, raise_if_change_in_tables,
                                                    unknown_token_name: str, no_use_token: Token,
                                                    unevaluated_evaluable_test_answer: EvaluableTestAnswer):
    query_strings = [
        {"token": unknown_token_name, "evaluable-test-answer-id": unevaluated_evaluable_test_answer.id},
        {"token": no_use_token.token, "evaluable-test-answer-id": unevaluated_evaluable_test_answer.id}
    ]

    with raise_if_change_in_tables(Token, Person, TestAnswer, EvaluableTestAnswer, EvaluableQuestionAnswer):
        for query_string in query_strings:
            resp = client.get(ROUTE, query_string=query_string)
            assert resp.status_code == 401, (f"Got wrong status code at {ROUTE} for unauthorized request "
                                             f"with arguments: {query_string}")
