# std
from pytest import fixture
from typing import List
from io import BytesIO
# 3rd party
from flask.testing import FlaskClient
from PyPDF2.pdf import PdfFileReader
from PyPDF2.utils import PdfReadError
# custom
from test_system.models import db, Person, TestAnswer, Token, EvaluableTestAnswer
from test_system.routes.certificate import ROUTE


@fixture()
def person(session) -> Person:
    person = Person(name="TestName", gender=Person.GENDERS.s, age=22)
    session.add(person)
    session.commit()
    return person


@fixture()
def test_answer(session, token: Token, person: Person) -> TestAnswer:
    test_answer = TestAnswer(date=db.func.now(),
                             answer_set={},
                             test_name=token.evaluable_test_name,
                             person_id=person.id)
    session.add(test_answer)
    session.commit()
    return test_answer


@fixture()
def evaluable_test_answers(session, test_answer) -> List[EvaluableTestAnswer]:
    evaluable_test_answers = [EvaluableTestAnswer(was_evaluated_with_token=True, test_answer_id=test_answer.id),
                              EvaluableTestAnswer(was_evaluated_with_token=False, test_answer_id=test_answer.id)]
    session.add_all(evaluable_test_answers)
    session.commit()
    return evaluable_test_answers


def test_get_certificate__with_success(client: FlaskClient, session, token: Token, evaluable_test_answers):
    for evaluable_test_answer in evaluable_test_answers:
        resp = client.get(ROUTE, query_string={"evaluable-test-answer-id": evaluable_test_answer.id,
                                               "token": token.token})
        assert resp.status_code == 200, f"Can't GET certificate from {ROUTE} with {evaluable_test_answer}"
        try:
            PdfFileReader(BytesIO(resp.data))
        except PdfReadError as e:
            assert e is None, f"Got invalid pdf bytes from {ROUTE} for {evaluable_test_answer}"
