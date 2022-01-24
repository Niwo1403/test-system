# std
import json
# 3rd party
from flask import request, abort
# custom
from test_system import app
from test_system.constants import API_PREFIX
from test_system.models import Token, Test


@app.route(f'{API_PREFIX}/tests/', methods=['GET'])
def get_tests():
    request_token = request.args.get("token", type=str)
    if request_token is None:
        abort(400, "Token missing.")

    token = Token.query.filter_by(token=request_token).first()
    if token is None or token.is_expired():
        abort(401, "Token doesn't exist or is expired.")

    evaluable_test = Test.query.filter_by(name=token.evaluable_test_name).first()
    if evaluable_test is None:
        abort(404, "Evaluable test doesn't exist.")
    if not evaluable_test.evaluable:
        abort(500, "Requested evaluable test isn't evaluable.")

    pre_collection_tests = Test.query.filter(Test.name.in_(token.pre_collection_test_names)).all()

    pre_collection_test_names = ', '.join(test.name for test in pre_collection_tests)
    app.logger.info(f"Requested pre collection tests '{pre_collection_test_names}' "
                    f"and evaluable test '{evaluable_test.name}' with token '{token.token}'.")

    tests = {
        "pre_collection_tests": [test.description_json for test in pre_collection_tests],
        "evaluable_test": evaluable_test.description_json
    }
    tests_json = json.dumps(tests)
    return tests_json
