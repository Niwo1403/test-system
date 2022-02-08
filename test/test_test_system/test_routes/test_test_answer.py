# std
from json import dumps as json_dumps
from typing import Dict
from pytest import fixture
# custom
from test_system.models import Person, Test, TestAnswer, EvaluableTestAnswer, EvaluableQuestionAnswer
from test_system.routes.test_answer import ROUTE


test_answer = {"Question A": "Answer A"}
test_answer_json = json_dumps(test_answer)
evaluable_test_answer = {"Category A": {"Row 1": "1", "Row 2": "2"}, "Category B": {"Row 1": "3", "Row 2": "4"}}
evaluable_test_answer_json = json_dumps(evaluable_test_answer)


@fixture()
def person(session) -> Person:
    person = Person.query.filter_by(id=1).first()
    if person is None:
        person = Person(id=1, name="TestName", age=33, gender=Person.GENDERS.s)
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


def _assert_right_test_answer_data(answer: TestAnswer, person: Person, test: Test, correct_test_answer: Dict) -> None:
    assert answer is not None, "Could not write TestAnswer to database"
    assert answer.answer_set == correct_test_answer and \
           answer.test_name == test.name and \
           answer.person_id == person.id, f"TestAnswer which was written to database has wrong data: {answer}"


def test_post_test_answer__with_success(client, session, person, pre_collect_test, evaluable_test):
    pre_collect_resp = client.post(ROUTE,
                                   data=test_answer_json,
                                   query_string={"test-name": pre_collect_test.name, "person-id": person.id})
    evaluable_resp = client.post(ROUTE,
                                 data=evaluable_test_answer_json,
                                 query_string={"test-name": evaluable_test.name, "person-id": person.id})

    for resp in (pre_collect_resp, ):  # only for pre collect test answers
        assert resp.status_code == 201,  (f"Can't POST test answer to {ROUTE} with data: {test_answer}, "
                                          f"and test: {pre_collect_test}")

        test_answer_id = resp.data.decode()
        answer: TestAnswer = TestAnswer.query.filter_by(id=test_answer_id).first()
        _assert_right_test_answer_data(answer, person, pre_collect_test, test_answer)

    for eval_resp in (evaluable_resp, ):  # only for evaluable test answers
        assert eval_resp.status_code == 201, (f"Can't POST test answer to {ROUTE} with data: {evaluable_test_answer}, "
                                              f"and test: {evaluable_test}")

        evaluable_test_answer_id = eval_resp.data.decode()
        evaluable_answer: EvaluableTestAnswer = EvaluableTestAnswer.query.filter_by(id=evaluable_test_answer_id).first()
        assert evaluable_answer is not None, "Could not write EvaluableTestAnswer to database"

        answer: TestAnswer = evaluable_answer.test_answer
        _assert_right_test_answer_data(answer, person, evaluable_test, evaluable_test_answer)


def test_post_test_answer__with_bad_request(client, session, raise_if_change_in_tables,
                                            person, pre_collect_test, evaluable_test):
    correct_query_string = {"test-name": evaluable_test.name, "person-id": person.id}
    test_arguments = [
                      # missing argument
                      (test_answer_json, {"person-id": person.id}),
                      (evaluable_test_answer_json, {"test-name": evaluable_test.name}),
                      (test_answer_json, {"test-name": pre_collect_test.name}),
                      # invalid JSON
                      ("", correct_query_string),
                      ("{", correct_query_string),
                      ("{true: \"3\"}", correct_query_string),
                      ("{'true': \"3\"}", correct_query_string)]

    wrong_schema_data = [
                         # wrong value; str value
                         {"2": {}}, {"2": True}, {"2": None},
                         # wrong second value; dict value
                         {"category": {"Row 1": {}}}, {"category": {"Row 1": True}}, {"category": {"Row 1": None}}]
    test_arguments += list(map(lambda wrong_data: (json_dumps(wrong_data), correct_query_string), wrong_schema_data))

    with raise_if_change_in_tables(Person, Test, TestAnswer, EvaluableTestAnswer, EvaluableQuestionAnswer):
        for data, query_string in test_arguments:
            resp = client.post(ROUTE, data=data, query_string=query_string)
            assert resp.status_code == 400, (f"Got wrong status code at {ROUTE} for arguments: {query_string}, "
                                             f"and data {data}")


def test_post_test_answer__with_wrong_test(client, session, raise_if_change_in_tables, person, personal_data_test):
    unknown_test_name = "?`?`?`?`?`?`?`?`?`?`?`?`?`?`?"

    with raise_if_change_in_tables(Person, Test, TestAnswer, EvaluableTestAnswer, EvaluableQuestionAnswer):
        resp = client.post(ROUTE,
                           data=test_answer_json,
                           query_string={"test-name": unknown_test_name, "person-id": person.id})
        assert resp.status_code == 404, f"Got wrong status code at {ROUTE} for unknown test name: {unknown_test_name}"

        resp = client.post(ROUTE,
                           data=test_answer_json,
                           query_string={"test-name": personal_data_test.name, "person-id": person.id})
        assert resp.status_code == 400, (f"Got wrong status code at {ROUTE} for test "
                                         f"with wrong test category: {personal_data_test.name}")


def test_post_test_answer__with_wrong_person(client, session, raise_if_change_in_tables,
                                             pre_collect_test, evaluable_test):
    unknown_person_id = -1
    test_arguments = [(test_answer_json, {"test-name": pre_collect_test.name, "person-id": unknown_person_id}),
                      (evaluable_test_answer_json, {"test-name": evaluable_test.name, "person-id": unknown_person_id})]

    with raise_if_change_in_tables(Person, Test, TestAnswer, EvaluableTestAnswer, EvaluableQuestionAnswer):
        for data, query_string in test_arguments:
            resp = client.post(ROUTE, data=data, query_string=query_string)
            assert resp.status_code == 404, (f"Got wrong status code at {ROUTE} for unknown person with id: "
                                             f"{unknown_person_id}, data: {data}, and query_string {query_string}")
