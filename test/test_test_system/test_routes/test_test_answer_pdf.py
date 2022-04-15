# std
from typing import List, Callable
from io import BytesIO
# 3rd party
from pytest import fixture
from flask.testing import FlaskClient
from PyPDF2.pdf import PdfFileReader
from PyPDF2.utils import PdfReadError
# custom
from test_system.models import Token, Test, TestAnswer, ExportableTestAnswer
from test_system.routes.test_answer_pdf import ROUTE


@fixture()
def test_answer(session, token, personal_data_answer) -> TestAnswer:
    test_answer = TestAnswer(answer_json={"Q": "A", "png_img": (
        "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABEAAAAQCAYAAADwMZRfAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJ"
        "cEhZcwAADsMAAA7DAcdvqGQAAADvSURBVDhPzZPNDoIwEISnrX8XVDwYjVHjzfd/JU8m6kU9ANp1ty1CEb144UvIsEs7bIegiMGf6KB/EU9CZ+"
        "4oVm6Jul54XNaOWVBPPIkstMGgvrletxCbiIFWmE62GI83vve0WC33SNOdr1uITdhAyLIc1lp3D6Nxvd2R54WvW2h8nUt8jDDZO6NSf2YiiIdb"
        "KOolykSMG8QmfP7haAEUD1/LZu45eHOSrCvjGrFJlsEYAzNaApKBvJ0zAWek+/PvuUgmFWei/Ehaa5nZXUopp4N+j+h2ILKnsLbiM1hBWs2zy9"
        "HC12sG251/pysmwAu6coiwp57CVAAAAABJRU5ErkJggg==")},
                             test_name=token.exportable_test_name,
                             personal_data_answer_id=personal_data_answer.id)
    session.add(test_answer)
    session.commit()
    return test_answer


@fixture()
def create_exported_exportable_test_answer_for_token(session, test_answer) -> Callable[[Token], ExportableTestAnswer]:
    def _create_exported_exportable_test_answer_for_token(token: Token) -> ExportableTestAnswer:
        exported_exportable_test_answer = ExportableTestAnswer(was_exported_with_token=token.token,
                                                               test_answer_id=test_answer.id)
        session.add(exported_exportable_test_answer)
        session.commit()
        return exported_exportable_test_answer

    return _create_exported_exportable_test_answer_for_token


@fixture()
def exported_exportable_test_answer(create_exported_exportable_test_answer_for_token, token) -> ExportableTestAnswer:
    return create_exported_exportable_test_answer_for_token(token)


@fixture()
def not_exported_exportable_test_answer(session, test_answer) -> ExportableTestAnswer:
    not_exported_exportable_test_answer = ExportableTestAnswer(was_exported_with_token=None,
                                                               test_answer_id=test_answer.id)
    session.add(not_exported_exportable_test_answer)
    session.commit()
    return not_exported_exportable_test_answer


@fixture()
def incomplete_exportable_test_answers(session, test_names, token) -> List[ExportableTestAnswer]:
    test_answer = TestAnswer(answer_json={}, test_name=test_names[Test.CATEGORIES.EXPORTABLE_TEST.name])
    session.add(test_answer)
    session.commit()
    incomplete_exportable_test_answers = [
        ExportableTestAnswer(was_exported_with_token=token.token, test_answer_id=None),
        ExportableTestAnswer(was_exported_with_token=None, test_answer_id=None),
        ExportableTestAnswer(was_exported_with_token=token.token, test_answer_id=test_answer.id),
        ExportableTestAnswer(was_exported_with_token=None, test_answer_id=test_answer.id)
    ]
    session.add_all(incomplete_exportable_test_answers)
    session.commit()
    return incomplete_exportable_test_answers


def test_get_test_answer_pdf__with_success(client: FlaskClient, session,
                                           token, unlimited_token, no_use_token, expired_token,
                                           create_exported_exportable_test_answer_for_token):
    test_cases = [(token, create_exported_exportable_test_answer_for_token(token)),
                  (expired_token, create_exported_exportable_test_answer_for_token(expired_token)),
                  (no_use_token, create_exported_exportable_test_answer_for_token(no_use_token))]

    for test_token, exportable_test_answer in test_cases:
        resp = client.get(ROUTE, query_string={"exportable-test-answer-id": exportable_test_answer.id,
                                               "token": test_token.token})
        assert resp.status_code == 200, (f"Can't GET test-answer-pdf from {ROUTE} with {exportable_test_answer}"
                                         f"\n\nReceived response:\n{resp.get_data(True)}")

        try:
            PdfFileReader(BytesIO(resp.data))
        except PdfReadError as pdf_error:
            assert pdf_error is None, (f"Got invalid pdf bytes from {ROUTE} for {exportable_test_answer}"
                                       f"\n\nReceived response:\n{resp.get_data(True)}")


def test_get_test_answer_pdf__with_bad_request(client: FlaskClient, session, raise_if_change_in_tables,
                                               token, exported_exportable_test_answer,
                                               not_exported_exportable_test_answer):
    query_strings = [
        {"exportable-test-answer-id": exported_exportable_test_answer.id},
        {"exportable-test-answer-id": exported_exportable_test_answer.id, "token": None},
        {"exportable-test-answer-id": not_exported_exportable_test_answer.id},
        {"exportable-test-answer-id": not_exported_exportable_test_answer.id, "token": None},
        {"token": token.token},
        {"exportable-test-answer-id": None, "token": token.token}
    ]

    with raise_if_change_in_tables(Token, TestAnswer, ExportableTestAnswer):
        for query_string in query_strings:
            resp = client.get(ROUTE, query_string=query_string)
            assert resp.status_code == 400, (f"Got wrong status code at {ROUTE} for bad request with arguments: "
                                             f"{query_string}\n\nReceived response:\n{resp.get_data(True)}")


def test_get_test_answer_pdf__with_unknown_data(client: FlaskClient, session, raise_if_change_in_tables,
                                                token, incomplete_exportable_test_answers):
    query_strings = [
                        {"token": token.token, "exportable-test-answer-id": str(incomplete_exportable_test_answer.id)}
                        for incomplete_exportable_test_answer in incomplete_exportable_test_answers
                    ] + [{"token": token.token, "exportable-test-answer-id": "-1"}]

    with raise_if_change_in_tables(Token, TestAnswer, ExportableTestAnswer):
        for query_string in query_strings:
            resp = client.get(ROUTE, query_string=query_string)
            assert resp.status_code == 404, (f"Got wrong status code at {ROUTE} for request with unknown data & "
                                             f"arguments: {query_string}\n\nReceived response:\n{resp.get_data(True)}")


def test_get_test_answer_pdf__with_unauthorized_request(client: FlaskClient, session, raise_if_change_in_tables,
                                                        unknown_token_name, no_use_token, expired_token,
                                                        token, unlimited_token, not_exported_exportable_test_answer,
                                                        exported_exportable_test_answer):
    query_strings = [
        {"token": "##########", "exportable-test-answer-id": exported_exportable_test_answer.id},
        {"token": token.token, "exportable-test-answer-id": not_exported_exportable_test_answer.id},
        # passed token doesn't match used token of exported_exportable_test_answer
        {"token": no_use_token.token, "exportable-test-answer-id": exported_exportable_test_answer.id},
        {"token": expired_token.token, "exportable-test-answer-id": exported_exportable_test_answer.id},
        {"token": unlimited_token.token, "exportable-test-answer-id": exported_exportable_test_answer.id}
    ]

    with raise_if_change_in_tables(Token, TestAnswer, ExportableTestAnswer):
        for query_string in query_strings:
            resp = client.get(ROUTE, query_string=query_string)
            assert resp.status_code == 401, (f"Got wrong status code at {ROUTE} for unauthorized request with "
                                             f"arguments: {query_string}\n\nReceived response:\n{resp.get_data(True)}")
