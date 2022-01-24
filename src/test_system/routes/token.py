# std
from json import loads
# 3rd party
from flask import request, abort
# custom
from test_system import app
from test_system.constants import API_PREFIX
from test_system.models import db, Token, User, Test


@app.route(f'{API_PREFIX}/token/', methods=['POST'])
def post_token():
    username = request.args.get("username", type=str)
    password = request.args.get("password", type=str)
    max_usage_count = request.args.get("max-usage-count", type=int)
    pre_collection_test_names = request.args.get("pre-collection-test-names", type=str)
    evaluable_test_name = request.args.get("evaluable-test-name", type=str)
    if not all((pre_collection_test_names, evaluable_test_name, username, password)):
        abort(400, "Argument missing or not valid.")

    user = User.query.filter_by(username=username).first()
    if user is None or not user.validate_password(password):
        abort(401, "User doesn't exist or password is wrong.")

    evaluable_test = Test.query.filter_by(name=evaluable_test_name).first()
    if evaluable_test is None:
        abort(404, f"Test with name '{evaluable_test_name}' doesn't exist.")

    app.logger.info(f"Requested token with username '{username}' and valid password.")

    token = Token.generate_token(max_usage_count, evaluable_test_name, loads(pre_collection_test_names))
    db.session.add(token)
    db.session.commit()
    app.logger.info(f"Created and saved token: {token}")

    return token.token

