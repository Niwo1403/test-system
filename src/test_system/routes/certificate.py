# std
from io import BytesIO
# 3rd party
from flask import request, abort, send_file
# custom
from test_system import app
from test_system.constants import API_PREFIX
from test_system.models import TestAnswer, Person, Token
from test_system.managers.certificate_manager import CertificateManager

ROUTE = f'{API_PREFIX}/certificate/'


@app.route(ROUTE, methods=['GET'])
def get_certificate():
    download = request.args.get("download", type=bool, default=False)
    test_answer_id = request.args.get("test-answer-id", type=int)
    token_str = request.args.get("token", type=str)
    if not all((test_answer_id, token_str)):
        abort(400, "Argument missing or not valid.")

    test_answer = TestAnswer.query.filter_by(id=test_answer_id).first()
    if test_answer is None:
        abort(404, "TestAnswer not found.")
    person = Person.query.filter_by(id=test_answer.person_id).first()
    if person is None:
        abort(404, "Person for TestAnswer not found.")
    token = Token.query.filter_by(token=token_str).first()
    if (token is None or token.is_expired()) and not test_answer.was_evaluated_with_token:
        abort(401, "Token not found or invalid.")

    cm = CertificateManager(test_answer, person)
    pdf_bytes = cm.generate_certificate()

    if test_answer.was_evaluated_with_token:
        app.logger.info(f"Regenerated certificate for {person}")
    else:
        token.use_for(test_answer)
        app.logger.info(f"Generated certificate for {person} and used {token}")

    return send_file(BytesIO(pdf_bytes),
                     mimetype='application/pdf',
                     as_attachment=download,
                     attachment_filename=f"Personality test certificate - {person.name}.pdf")
