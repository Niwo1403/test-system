# std
from json import dumps as json_dumps
from typing import Dict
# 3rd party
from pytest import fixture
from flask.testing import FlaskClient
from werkzeug.test import TestResponse
# custom
from test_system.models import Person, Test, TestAnswer, EvaluableTestAnswer
from test_system.routes.test_answer import ROUTE


TEST_ANSWER = {"Question A": "Answer A"}
TEST_ANSWER_JSON = json_dumps(TEST_ANSWER)
EVALUABLE_TEST_ANSWER = {"Category A": {"Question 1": "1", "Question 2": "2"},
                         "Category B": {"Question 1": "3", "Question 2": "4"},
                         "Question X": "5",
                         "Ignored question": "TEXT!"}
EVALUABLE_TEST_ANSWER_JSON = json_dumps(EVALUABLE_TEST_ANSWER)


@fixture()
def person(session) -> Person:
    person = Person(answer_json={"name": "TestName", "age": 33, "gender": "s"})
    session.add(person)
    session.commit()
    return person


@fixture()
def pre_collect_test() -> Test:
    return Test.query.filter_by(name="PreCol").first()


@fixture()
def evaluable_test() -> Test:
    return Test.query.filter_by(name="PersTest").first()


@fixture()
def personal_data_test() -> Test:
    return Test.query.filter_by(name="Person").first()


def _assert_right_test_answer_data(answer: TestAnswer, person: Person, test: Test, correct_test_answer: Dict,
                                   resp: TestResponse) -> None:
    assert answer is not None, f"Could not write TestAnswer to database\n\nReceived response:\n{resp.get_data(True)}"
    assert answer.answer_json == correct_test_answer and \
           answer.test_name == test.name and \
           answer.person_id == person.id, (f"TestAnswer which was written to database has wrong data: {answer}"
                                           f"\n\nReceived response:\n{resp.get_data(True)}")


def test_post_test_answer__with_success(client: FlaskClient, session, person, pre_collect_test, evaluable_test):
    pre_collect_resp = client.post(ROUTE,
                                   data=TEST_ANSWER_JSON,
                                   query_string={"test-name": pre_collect_test.name, "person-id": person.id})
    evaluable_resp = client.post(ROUTE,
                                 data=EVALUABLE_TEST_ANSWER_JSON,
                                 query_string={"test-name": evaluable_test.name, "person-id": person.id})

    for resp in (pre_collect_resp, ):  # only for pre collect test answers
        assert resp.status_code == 201,  (f"Can't POST test answer to {ROUTE} with data: {TEST_ANSWER}, "
                                          f"and test: {pre_collect_test}\n\nReceived response:\n{resp.get_data(True)}")

        test_answer_id = resp.get_data(True)
        answer: TestAnswer = TestAnswer.query.filter_by(id=test_answer_id).first()
        _assert_right_test_answer_data(answer, person, pre_collect_test, TEST_ANSWER, resp)

    for eval_resp in (evaluable_resp, ):  # only for evaluable test answers
        assert eval_resp.status_code == 201, (f"Can't POST test answer to {ROUTE} with data: {EVALUABLE_TEST_ANSWER}, "
                                              f"test: {evaluable_test}\n\nReceived response:\n{resp.get_data(True)}")

        evaluable_test_answer_id = eval_resp.get_data(True)
        evaluable_answer: EvaluableTestAnswer = EvaluableTestAnswer.query.filter_by(id=evaluable_test_answer_id).first()
        assert evaluable_answer is not None, ("Could not write EvaluableTestAnswer to database"
                                              f"\n\nReceived response:\n{resp.get_data(True)}")

        answer: TestAnswer = evaluable_answer.test_answer
        _assert_right_test_answer_data(answer, person, evaluable_test, EVALUABLE_TEST_ANSWER, resp)


def test_post_test_answer__with_bad_request(client: FlaskClient, session, raise_if_change_in_tables,
                                            person, pre_collect_test, evaluable_test):
    correct_query_string = {"test-name": evaluable_test.name, "person-id": person.id}
    test_arguments = [
                      # missing argument
                      (TEST_ANSWER_JSON, {"person-id": person.id}),
                      (EVALUABLE_TEST_ANSWER_JSON, {"test-name": evaluable_test.name}),
                      (TEST_ANSWER_JSON, {"test-name": pre_collect_test.name}),
                      # invalid JSON
                      ("", correct_query_string),
                      ("{", correct_query_string),
                      ("{true: \"3\"}", correct_query_string),
                      ("{'true': \"3\"}", correct_query_string),
                      # invalid schema
                      ("{\"key\": null}", correct_query_string)]

    with raise_if_change_in_tables(Person, Test, TestAnswer, EvaluableTestAnswer):
        for data, query_string in test_arguments:
            resp = client.post(ROUTE, data=data, query_string=query_string)
            assert resp.status_code == 400, (f"Got wrong status code at {ROUTE} for arguments: {query_string}, "
                                             f"and data {data}\n\nReceived response:\n{resp.get_data(True)}")


def test_post_test_answer__with_wrong_test(client: FlaskClient, session, raise_if_change_in_tables,
                                           person, personal_data_test):
    unknown_test_name = "?`?`?`?`?`?`?`?`?`?`?`?`?`?`?"

    with raise_if_change_in_tables(Person, Test, TestAnswer, EvaluableTestAnswer):
        resp = client.post(ROUTE,
                           data=TEST_ANSWER_JSON,
                           query_string={"test-name": unknown_test_name, "person-id": person.id})
        assert resp.status_code == 404, (f"Got wrong status code at {ROUTE} for unknown test name: {unknown_test_name}"
                                         f"\n\nReceived response:\n{resp.get_data(True)}")

        resp = client.post(ROUTE,
                           data=TEST_ANSWER_JSON,
                           query_string={"test-name": personal_data_test.name, "person-id": person.id})
        assert resp.status_code == 400, (f"Got wrong status code at {ROUTE} for test with wrong test category: "
                                         f"{personal_data_test.name}\n\nReceived response:\n{resp.get_data(True)}")


def test_post_test_answer__with_wrong_person(client: FlaskClient, session, raise_if_change_in_tables,
                                             pre_collect_test, evaluable_test):
    unknown_person_id = -1
    test_arguments = [(TEST_ANSWER_JSON, {"test-name": pre_collect_test.name, "person-id": unknown_person_id}),
                      (EVALUABLE_TEST_ANSWER_JSON, {"test-name": evaluable_test.name, "person-id": unknown_person_id})]

    with raise_if_change_in_tables(Person, Test, TestAnswer, EvaluableTestAnswer):
        for data, query_string in test_arguments:
            resp = client.post(ROUTE, data=data, query_string=query_string)
            assert resp.status_code == 404, (f"Got wrong status code at {ROUTE} for data: {data} and query_string: "
                                             f"{query_string}\n\nReceived response:\n{resp.get_data(True)}")
