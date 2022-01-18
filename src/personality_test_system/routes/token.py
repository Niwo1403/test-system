# 3rd party
from flask import request, abort
# custom
from personality_test_system import app
from personality_test_system.constants import API_PREFIX
from personality_test_system.models import db, Token, User


@app.route(f'{API_PREFIX}/token/', methods=['POST'])
def get_token():
    username = request.args.get("username", default=None, type=str)
    password = request.args.get("password", default=None, type=str)
    user = db.session.query(User).filter_by(username=username).first()
    if user is None or not user.validate_password(password):
        abort(401)
    app.logger.info(f"Requested token with username '{username}' and valid password.")

    max_usage_count = request.args.get("max_usage_count", default=None, type=int)
    personality_test_name = request.args.get("personality_test_name", type=str)
    if personality_test_name is None:
        abort(400)

    token = Token.generate_token(max_usage_count, personality_test_name)
    db.session.add(token)
    db.session.commit()
    app.logger.info(f"Created and saved token: {token}")

    return token.token

