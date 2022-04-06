# std
from json import loads as json_loads
from json.decoder import JSONDecodeError
# 3rd party
from flask import request, abort
from schema import Schema, SchemaError
# custom
from test_system import app
from test_system.constants import API_PREFIX
from test_system.models import db, TestAnswer, Test

PERSONAL_DATA_SCHEMA = Schema({str: lambda v: v is not None})

ROUTE = f"{API_PREFIX}/person/"  # as variable for tests


@app.route(ROUTE, methods=['POST'])
def post_person():
    test_name = request.args.get("test-name", type=str)
    if not all((test_name, )):
        abort(400, "Argument missing or invalid.")

    try:
        personal_data = json_loads(request.data.decode())
        personal_data = PERSONAL_DATA_SCHEMA.validate(personal_data)
    except (JSONDecodeError, TypeError):
        return abort(400, "Data validation failed, wrong JSON.")
    except SchemaError:
        return abort(400, "Data validation failed.")

    test: Test = Test.query.filter_by(name=test_name).first()
    if test is None:
        abort(404, "Test doesn't exist.")
    if test.test_category != Test.CATEGORIES.PERSONAL_DATA_TEST:
        abort(400, "Can't post test-answer of non personal data test.")

    test_answer = TestAnswer(answer_json=personal_data, test_name=test.name)
    db.session.add(test_answer)
    db.session.commit()  # required to generate id of person

    app.logger.info(f"Created {test_answer}")

    return str(test_answer.id), 201
