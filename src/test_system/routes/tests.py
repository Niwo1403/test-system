# std
import json
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
    if token is None or token.is_invalid():
        abort(401, "Token doesn't exist or is expired.")

    personal_data_test = token.personal_data_test
    Test.assert_test_existence_and_category(personal_data_test, Test.CATEGORIES.PERSONAL_DATA_TEST)
    exportable_test = token.exportable_test
    Test.assert_test_existence_and_category(exportable_test, Test.CATEGORIES.EXPORTABLE_TEST)
    pre_collect_tests = token.get_pre_collect_tests()

    pre_collect_test_names = ', '.join(test.name for test in pre_collect_tests)
    app.logger.info(f"Requested personal data test '{personal_data_test.name}', "
                    f"pre collect tests '{pre_collect_test_names}' "
                    f"and exportable test '{exportable_test.name}' with token '{token.token}'")

    tests = {
        "personal_data_test": personal_data_test.get_named_description_dict(),
        "pre_collect_tests": [test.get_named_description_dict() for test in pre_collect_tests],
        "exportable_test": exportable_test.get_named_description_dict()
    }
    tests_json = json.dumps(tests)
    return tests_json
