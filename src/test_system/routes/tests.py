# std
import json
from typing import List, Optional
# 3rd party
from flask import request, abort
# custom
from test_system import app
from test_system.constants import API_PREFIX
from test_system.models import Token, Test

ROUTE = f'{API_PREFIX}/tests/'


@app.route(ROUTE, methods=['GET'])
def get_tests():
    request_token = request.args.get("token", type=str)
    if request_token is None:
        abort(400, "Token missing.")

    token: Token = Token.query.filter_by(token=request_token).first()
    if token is None or token.is_expired(remove_if_expired=True):
        abort(401, "Token doesn't exist or is expired.")

    personal_data_test = token.personal_data_test
    Test.assert_test_existence_and_category(personal_data_test, Test.CATEGORIES.PERSONAL_DATA_TEST)
    evaluable_test = token.evaluable_test
    Test.assert_test_existence_and_category(evaluable_test, Test.CATEGORIES.EVALUABLE_TEST)

    possible_pre_collection_tests: List[Optional[Test]] = [Test.query.filter_by(name=pre_collect_test_name).first()
                                                           for pre_collect_test_name in token.pre_collection_test_names]
    pre_collection_tests: List[Test] = list(filter(lambda test: test is not None, possible_pre_collection_tests))

    pre_collection_test_names = ', '.join(test.name for test in pre_collection_tests)
    app.logger.info(f"Requested personal data test '{personal_data_test.name}', "
                    f"pre collection tests '{pre_collection_test_names}' "
                    f"and evaluable test '{evaluable_test.name}' with token '{token.token}'")

    tests = {
        "personal_data_test": personal_data_test.get_named_description_dict(),
        "pre_collection_tests": [test.get_named_description_dict() for test in pre_collection_tests],
        "evaluable_test": evaluable_test.get_named_description_dict()
    }
    tests_json = json.dumps(tests)
    return tests_json
