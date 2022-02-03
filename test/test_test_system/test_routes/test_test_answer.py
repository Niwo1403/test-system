# std
from json import dumps as json_dumps
from pytest import fixture
# custom
from test_system.models import Person, Test, TestAnswer
from test_system.routes.test_answer import ROUTE


test_answer = {"Question A": "Answer A"}


@fixture()
def person():
    return Person(id=1, name="Test name", age=33, gender=Person.GENDERS.s)


@fixture()
def test():
    return Test(name="PreColTest", description_json={"a": "b"}, test_category=Test.CATEGORIES.PRE_COLLECT_TEST)


@fixture()
def personal_data_test():
    return Test(name="PersonalDataTest", description_json={"a": "b"}, test_category=Test.CATEGORIES.PERSONAL_DATA_TEST)


def test_post_test_answer__with_success(client, session, person, test):
    session.add_all((person, test))
    session.commit()

    resp = client.post(ROUTE,
                       data=json_dumps(test_answer),
                       query_string={"test-name": test.name, "person-id": person.id})
    assert resp.status_code == 201,  f"Can't POST test answer to {ROUTE} with data: {test_answer}"

    test_answer_id = resp.data.decode()
    answer = TestAnswer.query.filter_by(id=test_answer_id).first()
    assert answer is not None, "Could not write TestAnswer to database"
    assert answer.answer_set == test_answer and \
           answer.test_name == test.name and \
           answer.person_id == person.id, f"TestAnswer written to database, got wrong data: {answer}"


def test_post_test_answer__with_bad_request(client, session, raise_if_change_in_tables, person, test):
    session.add_all((person, test))
    session.commit()

    test_arguments = [{"person-id": person.id}]

    with raise_if_change_in_tables(Person, Test, TestAnswer):
        for query_string in test_arguments:
            resp = client.post(ROUTE, data=json_dumps(test_answer), query_string=query_string)
            assert resp.status_code == 400, f"Got wrong status code at {ROUTE} for arguments: {query_string}"


def test_post_test_answer__with_wrong_test(client, session, raise_if_change_in_tables, person, personal_data_test):
    session.add_all((person, personal_data_test))
    session.commit()

    unknown_test_name = "?`?`?`?`?`?`?`?`?`?`?`?`?`?`?"

    with raise_if_change_in_tables(Person, Test, TestAnswer):
        resp = client.post(ROUTE,
                           data=json_dumps(test_answer),
                           query_string={"test-name": unknown_test_name, "person-id": person.id})
        assert resp.status_code == 404, f"Got wrong status code at {ROUTE} for unknown test name: {unknown_test_name}"

        resp = client.post(ROUTE,
                           data=json_dumps(test_answer),
                           query_string={"test-name": personal_data_test.name, "person-id": person.id})
        assert resp.status_code == 500, (f"Got wrong status code at {ROUTE} for test "
                                         f"with wrong test category: {personal_data_test.name}")


def test_post_test_answer__with_wrong_person(client, session, raise_if_change_in_tables, test):
    session.add(test)
    session.commit()

    with raise_if_change_in_tables(Person, Test, TestAnswer):
        resp = client.post(ROUTE,
                           data=json_dumps(test_answer),
                           query_string={"test-name": test.name, "person-id": -1})
        assert resp.status_code == 404, f"Got wrong status code at {ROUTE} for unknown person with id: {-1}"
