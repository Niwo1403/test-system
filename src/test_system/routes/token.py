# std
from json import loads as json_loads, JSONDecodeError
# 3rd party
from flask import request, abort
from schema import Schema, And, Use, SchemaError, Optional
# custom
from test_system import app
from test_system.constants import API_PREFIX, PRE_COLLECT_TESTS_SURVEY_KEYWORD, EXPIRES_SURVEY_KEYWORD, \
    PRE_COLLECT_TESTS_KEY
from test_system.models import db, Token, User, Test

ROUTE = f'{API_PREFIX}/token/'

TOKEN_DATA_SCHEMA = Schema({Test.CATEGORIES.PERSONAL_DATA_TEST.name: And(str, len),
                            Optional(PRE_COLLECT_TESTS_KEY, default=[]): [
                                And(Use(lambda e: e[PRE_COLLECT_TESTS_SURVEY_KEYWORD]), str, len)],
                            Test.CATEGORIES.EVALUABLE_TEST.name: And(str, len),
                            Optional(Token.max_usage_count.key, default=None): And(int, lambda n: 0 <= n),
                            EXPIRES_SURVEY_KEYWORD: bool,
                            User.username.key: And(str, len),
                            User.password.key: And(str, len)})


@app.route(ROUTE, methods=['POST'])
def post_token():
    try:
        post_token_data = json_loads(request.data.decode())
        if PRE_COLLECT_TESTS_KEY in post_token_data:
            post_token_data[PRE_COLLECT_TESTS_KEY] = list(filter(
                len, post_token_data[PRE_COLLECT_TESTS_KEY]))
        post_token_data = TOKEN_DATA_SCHEMA.validate(post_token_data)
    except (JSONDecodeError, TypeError):
        return abort(400, "Data validation failed, wrong JSON.")
    except SchemaError:
        return abort(400, "Data validation failed.")

    personal_data_test_name = post_token_data[Test.CATEGORIES.PERSONAL_DATA_TEST.name]
    pre_collect_test_names = post_token_data[PRE_COLLECT_TESTS_KEY]
    evaluable_test_name = post_token_data[Test.CATEGORIES.EVALUABLE_TEST.name]
    max_usage_count = post_token_data[Token.max_usage_count.key]
    expires = post_token_data[EXPIRES_SURVEY_KEYWORD]
    username = post_token_data[User.username.key]
    password = post_token_data[User.password.key]

    user: User = User.query.filter_by(username=username).first()
    if user is None or not user.is_password_valid(password):
        abort(401, "User doesn't exist or password is wrong.")

    # Test if personal data and evaluable test exist
    Test.get_category_test_or_abort(personal_data_test_name, Test.CATEGORIES.PERSONAL_DATA_TEST)
    Test.get_category_test_or_abort(evaluable_test_name, Test.CATEGORIES.EVALUABLE_TEST)

    app.logger.info(f"Requested token as {user}")

    token = Token.generate_token(max_usage_count,
                                 personal_data_test_name,
                                 pre_collect_test_names,
                                 evaluable_test_name,
                                 expires=expires)
    db.session.add(token)
    db.session.commit()
    app.logger.info(f"Created {token}")

    return token.token, 201
