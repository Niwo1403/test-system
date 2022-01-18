# 3rd party
from flask import request, abort
# custom
from personality_test_system import app
from personality_test_system.constants import API_PREFIX
from personality_test_system.models import db, Token, PersonalityTest


@app.route(f'{API_PREFIX}/personality-test/', methods=['GET'])
def get_personality_test():
    request_token = request.args.get("token", type=str)
    if request_token is None:
        abort(400)

    token = db.session.query(Token).filter_by(token=request_token).first()
    if token is None or token.is_expired():
        abort(404)

    pers_test = db.session.query(PersonalityTest).filter_by(name=token.personality_test_name).first()
    if pers_test is None:
        abort(500)

    app.logger.info(f"Requested personality-test '{pers_test.name}' with token '{token.token}'.")

    return pers_test.description_json
