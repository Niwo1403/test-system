# std
from json import loads as json_loads
from json.decoder import JSONDecodeError
# 3rd party
from flask import request, abort
from schema import Schema, SchemaError
# custom
from test_system import app
from test_system.constants import API_PREFIX
from test_system.models import db, Person, Test, TestAnswer, Token, EvaluableTestAnswer

TEST_SCHEMA = Schema({str: lambda v: v is not None})  # Only first key must be string

ROUTE = f'{API_PREFIX}/test-answer/'


@app.route(ROUTE, methods=['POST'])
def post_test_answer():
    test_name = request.args.get("test-name", type=str)
    person_id = request.args.get("person-id", type=int)
    token_str = request.args.get("token", type=str)
    if not all((test_name, person_id, token_str)):
        abort(400, "Argument missing or not valid.")

    token: Token = Token.query.filter_by(token=token_str).first()
    if token is None or token.is_invalid():
        abort(401, "Token not found or invalid.")

    test: Test = Test.query.filter_by(name=test_name).first()
    if test is None:
        abort(404, "Test doesn't exist.")
    if test.test_category == Test.CATEGORIES.PERSONAL_DATA_TEST:
        abort(400, "Can't post test-answer of personal data test.")
    person: Person = Person.query.filter_by(id=person_id).first()
    if person is None:
        abort(404, "Person doesn't exist.")  # Person not found

    try:
        answer_json = json_loads(request.data.decode())
        answer_json = TEST_SCHEMA.validate(answer_json)
    except JSONDecodeError:
        return abort(400, "Data validation failed, wrong JSON.")
    except SchemaError:
        return abort(400, "Data validation failed.")

    answer = TestAnswer(answer_json=answer_json, test_name=test_name, person_id=person.id)
    db.session.add(answer)
    db.session.commit()

    app.logger.info(f"Created answer for test '{answer.test_name}' for {person}")

    if test.test_category == Test.CATEGORIES.EVALUABLE_TEST:
        evaluable_answer = EvaluableTestAnswer(test_answer_id=answer.id)
        db.session.add(evaluable_answer)
        db.session.commit()

        token.use_for(evaluable_answer)
        return str(evaluable_answer.id), 201

    return str(answer.id), 201
