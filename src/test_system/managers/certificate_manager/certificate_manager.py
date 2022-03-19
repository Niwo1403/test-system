# std
from io import BytesIO
from typing import List
# 3rd party
from sqlalchemy.engine import Row
# custom
from test_system.models import db, TestAnswer, Person, \
    EvaluableQuestionAnswer, EvaluableQuestionName, EvaluableTestAnswer
from .pdf import PDF


class CertificateManager:
    """
    Can be used to create a certificate.
    A certificate includes at first the initially set information about the person who answered the test.
    After the personal information, EvaluableTestAnswers can be added using the add_answer method;
    this will also evaluate the evaluable_test_answer.
    In the end, the PDF can be created and obtained as a file using the get_pdf method.
    """

    @staticmethod
    def _get_category_averages(evaluable_test_answer_id: int) -> List[Row]:
        return db.session.query(EvaluableQuestionName.category, db.func.avg(EvaluableQuestionAnswer.value))\
            .join(EvaluableQuestionAnswer).filter_by(evaluable_test_answer_id=evaluable_test_answer_id)\
            .group_by(EvaluableQuestionName.category).all()

    def __init__(self, person: Person):
        self.pdf = PDF()
        self.person = person
        self._add_personal_data_text()

    def add_answer(self, evaluable_test_answer: EvaluableTestAnswer) -> None:
        """
        Evaluates the evaluable_test_answer and adds the result to the certificate.
        """
        self.pdf.add_default_cell()
        self._add_answer(evaluable_test_answer)

    def get_pdf(self) -> BytesIO:
        """
        Creates the actual PDF and returns its bytes as BytesIO object.
        """
        pdf_bytes = self.pdf.get_pdf_bytes()
        return BytesIO(pdf_bytes)

    def _add_personal_data_text(self):
        self.pdf.add_default_cell(f'Name: {self.person.name}')
        self.pdf.add_default_cell(f'Alter: {self.person.age}')
        self.pdf.add_default_cell(f'Geschlecht: {self.person.gender.value}')
        if self.person.position is not None:
            self.pdf.add_default_cell(f'Position: {self.person.position}')

    def _add_answer(self, evaluable_test_answer: EvaluableTestAnswer):
        self._add_answer_header(evaluable_test_answer.test_answer)
        self._add_answer_results_to_body(evaluable_test_answer.id)

    def _add_answer_header(self, test_answer: TestAnswer) -> None:
        self.pdf.add_default_cell(f'Test "{test_answer.test_name}" '
                                  f'(abgegeben: {test_answer.creation_timestamp.strftime("%d.%m.%Y, %H:%M:%S")})')

    def _add_answer_results_to_body(self, evaluable_test_answer_id: int):
        category_averages = self._get_category_averages(evaluable_test_answer_id)
        self.pdf.add_default_cell('Test Kategorie Durchschnitte:')
        for category, avg in category_averages:
            self.pdf.add_default_cell(f"{category}: {float(avg)}")
