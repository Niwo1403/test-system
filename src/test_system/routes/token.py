# std
from json import loads
# 3rd party
from flask import request, abort
# custom
from test_system import app
from test_system.constants import API_PREFIX
from test_system.models import db, Token, User, Test

ROUTE = f'{API_PREFIX}/token/'


@app.route(ROUTE, methods=['POST'])
def post_token():
    username = request.args.get("username", type=str)
    password = request.args.get("password", type=str)
    max_usage_count = request.args.get("max-usage-count", type=int)
    personal_data_test_name = request.args.get("personal-data-test-name", type=str)
    pre_collect_test_names = request.args.get("pre-collect-test-names", type=str)
    evaluable_test_name = request.args.get("evaluable-test-name", type=str)
    if not all((personal_data_test_name, pre_collect_test_names, evaluable_test_name, username, password)):
        abort(400, "Argument missing or not valid.")

    user: User = User.query.filter_by(username=username).first()
    if user is None or not user.validate_password(password):
        abort(401, "User doesn't exist or password is wrong.")

    # Test if personal data and evaluable test exist
    Test.get_category_test_or_abort(personal_data_test_name, Test.CATEGORIES.PERSONAL_DATA_TEST)
    Test.get_category_test_or_abort(evaluable_test_name, Test.CATEGORIES.EVALUABLE_TEST)

    app.logger.info(f"Requested token with username '{username}' and valid password")

    token = Token.generate_token(max_usage_count,
                                 personal_data_test_name,
                                 loads(pre_collect_test_names),
                                 evaluable_test_name)
    db.session.add(token)
    db.session.commit()
    app.logger.info(f"Created {token}")

    return token.token, 201

