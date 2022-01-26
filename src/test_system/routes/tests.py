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

    personal_data_test = Test.get_category_test_or_abort(token.personal_data_test_name,
                                                         assert_category=Test.CATEGORIES.PERSONAL_DATA_TEST)
    evaluable_test = Test.get_category_test_or_abort(token.evaluable_test_name,
                                                     assert_category=Test.CATEGORIES.EVALUABLE_TEST)
    pre_collection_tests = Test.query.filter(Test.name.in_(token.pre_collection_test_names)).all()

    pre_collection_test_names = ', '.join(test.name for test in pre_collection_tests)
    app.logger.info(f"Requested personal data test '{personal_data_test.name}', "
                    f"pre collection tests '{pre_collection_test_names}' "
                    f"and evaluable test '{evaluable_test.name}' with token '{token.token}'.")

    tests = {
        "personal_data_test": personal_data_test.description_json,
        "pre_collection_tests": [test.description_json for test in pre_collection_tests],
        "evaluable_test": evaluable_test.description_json
    }
    tests_json = json.dumps(tests)
    return tests_json
