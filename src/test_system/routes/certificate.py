# std
from io import BytesIO
# 3rd party
from flask import request, abort, send_file
# custom
from test_system import app
from test_system.constants import API_PREFIX, CERTIFICATE_MIMETYPE
from test_system.models import EvaluableTestAnswer, Person, Token
from test_system.managers.certificate_manager import CertificateManager

ROUTE = f'{API_PREFIX}/certificate/'


@app.route(ROUTE, methods=['GET'])
def get_certificate():
    download = request.args.get("download", type=bool, default=False)
    evaluable_test_answer_id = request.args.get("evaluable-test-answer-id", type=int)
    token_str = request.args.get("token", type=str)
    if not all((evaluable_test_answer_id, token_str)):
        abort(400, "Argument missing or not valid.")

    evaluable_answer: EvaluableTestAnswer = EvaluableTestAnswer.query.filter_by(id=evaluable_test_answer_id).first()
    if evaluable_answer is None:
        abort(404, "EvaluableTestAnswer not found.")
    test_answer = evaluable_answer.test_answer
    if test_answer is None:
        abort(404, "TestAnswer of EvaluableTestAnswer not found.")
    person: Person = test_answer.answerer
    if person is None:
        abort(404, "Person, who answered TestAnswer not found.")
    token: Token = Token.query.filter_by(token=token_str).first()
    if (token is None or token.is_expired()) and not evaluable_answer.was_evaluated_with_token:
        abort(401, "Token not found or invalid.")

    cm = CertificateManager(person, evaluable_answer)
    cm.add_data_to_certificate()
    pdf = cm.get_pdf()

    if evaluable_answer.was_evaluated_with_token:
        app.logger.info(f"Regenerated certificate for {person}")
    else:
        token.use_for(evaluable_answer)
        app.logger.info(f"Generated certificate for {person} and used {token}")

    download_name = f"Personality test certificate - {person.name}.pdf"
    return send_file(pdf, mimetype=CERTIFICATE_MIMETYPE, as_attachment=download, download_name=download_name)
