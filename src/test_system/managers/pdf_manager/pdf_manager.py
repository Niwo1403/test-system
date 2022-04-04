# std
from io import BytesIO
# custom
from test_system.models import TestAnswer, Person, EvaluableTestAnswer
from .pdf import PDF


class PdfManager:
    """
    Can be used to create a PDF.
    A PDF includes at first the initially set information about the person who answered the test.
    After the personal information, EvaluableTestAnswers can be added using the add_answer method;
    this will also evaluate the evaluable_test_answer.
    In the end, the PDF can be created and obtained as a file using the get_pdf method.
    """

    def __init__(self, person: Person):
        self.pdf = PDF()
        self.person = person
        self.pdf.add_formatted_json(self.person.answer_json)

    def add_answer(self, evaluable_test_answer: EvaluableTestAnswer) -> None:
        """
        Adds the answers of the evaluable_test_answer to the PDF.
        """
        self.pdf.add_default_cell()
        self._add_answer(evaluable_test_answer.test_answer)

    def get_pdf(self) -> BytesIO:
        """
        Creates the actual PDF and returns its bytes as BytesIO object.
        """
        pdf_bytes = self.pdf.get_pdf_bytes()
        return BytesIO(pdf_bytes)

    def _add_answer(self, test_answer: TestAnswer):
        self._add_answer_header(test_answer)
        self.pdf.add_formatted_json(test_answer.answer_json)

    def _add_answer_header(self, test_answer: TestAnswer) -> None:
        self.pdf.add_default_cell(f'Test "{test_answer.test_name}" '
                                  f'(submitted: {test_answer.creation_timestamp.strftime("%d.%m.%Y, %H:%M:%S")})')

