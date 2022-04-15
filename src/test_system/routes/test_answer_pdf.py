# 3rd party
from flask import request, abort, send_file
# custom
from test_system import app
from test_system.constants import API_PREFIX, CERTIFICATE_MIMETYPE
from test_system.models import ExportableTestAnswer, TestAnswer, Token
from test_system.managers.pdf_manager import PdfManager

ROUTE = f'{API_PREFIX}/test-answer-pdf/'


@app.route(ROUTE, methods=['GET'])
def get_test_answer_pdf():
    download = request.args.get("download", type=bool, default=False)
    exportable_test_answer_id = request.args.get("exportable-test-answer-id", type=int)
    token_str = request.args.get("token", type=str)
    if not all((exportable_test_answer_id, token_str)):
        abort(400, "Argument missing or not valid.")

    exportable_answer: ExportableTestAnswer = ExportableTestAnswer.query.filter_by(id=exportable_test_answer_id).first()
    if exportable_answer is None:
        abort(404, "ExportableTestAnswer not found.")
    test_answer: TestAnswer = exportable_answer.test_answer
    if test_answer is None:
        abort(404, "TestAnswer of ExportableTestAnswer not found.")
    personal_data_test_answer: TestAnswer = TestAnswer.query.filter_by(id=test_answer.personal_data_answer_id).first()
    if personal_data_test_answer is None:
        abort(404, "Personal data answer, which belongs to TestAnswer not found.")

    token: Token = Token.query.filter_by(token=token_str).first()
    if token is None or not token.was_used_for_answer(exportable_answer):
        abort(401, "Token not found or invalid.")

    pm = PdfManager(personal_data_test_answer)
    pm.add_answer(exportable_answer)
    pdf = pm.get_pdf()

    app.logger.info(f"Generated PDF for {personal_data_test_answer}")

    return send_file(pdf, mimetype=CERTIFICATE_MIMETYPE, as_attachment=download, download_name="answers.pdf")
