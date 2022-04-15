# std
from io import BytesIO
from typing import Dict
# custom
from test_system.models import TestAnswer, ExportableTestAnswer
from test_system.constants import DATA_URL_START
from .pdf import PDF


class PdfManager:
    """
    Can be used to create a PDF.
    A PDF includes at first the initially set personal data information about the answerer of the test.
    After the personal information, ExportableTestAnswers can be added using the add_answer method.
    In the end, the PDF can be created and obtained as a file using the get_pdf method.
    """

    def __init__(self, test_answer: TestAnswer):
        self.pdf = PDF()
        self._add_answer_json(test_answer.answer_json)

    def add_answer(self, exportable_test_answer: ExportableTestAnswer) -> None:
        """
        Adds the answers of the exportable_test_answer to the PDF.
        """
        self.pdf.add_default_cell()
        self._add_answer(exportable_test_answer.test_answer)

    def get_pdf(self) -> BytesIO:
        """
        Creates the actual PDF and returns its bytes as BytesIO object.
        """
        pdf_bytes = self.pdf.get_pdf_bytes()
        return BytesIO(pdf_bytes)

    def _add_answer(self, test_answer: TestAnswer) -> None:
        self._add_answer_header(test_answer)
        self._add_answer_json(test_answer.answer_json)

    def _add_answer_json(self, answer_json: Dict) -> None:
        image_data = {}
        non_image_data = {}
        for k, v in answer_json.items():
            if type(v) is str and v.startswith(DATA_URL_START):
                image_data[k] = v
            else:
                non_image_data[k] = v

        self.pdf.add_formatted_json(non_image_data)
        self.pdf.add_titled_data_urls(image_data)

    def _add_answer_header(self, test_answer: TestAnswer) -> None:
        self.pdf.add_default_cell(f'Test "{test_answer.test_name}" '
                                  f'(submitted: {test_answer.creation_timestamp.strftime("%d.%m.%Y, %H:%M:%S")})')

