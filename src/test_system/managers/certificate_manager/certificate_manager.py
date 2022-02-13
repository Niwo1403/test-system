# std
from io import BytesIO
# custom
from .pdf import PDF
from test_system.models import EvaluableTestAnswer, Person, TestAnswer


class CertificateManager:

    def __init__(self, person: Person, evaluable_test_answer: EvaluableTestAnswer):
        self.pdf = PDF()
        self.evaluable_test_answer = evaluable_test_answer
        self.person = person

    def add_data_to_certificate(self) -> None:
        self._add_personal_data_text()
        self.pdf.add_default_cell()
        self._add_answer_text()

    def get_pdf(self) -> BytesIO:
        pdf_bytes = self.pdf.get_pdf_bytes()
        return BytesIO(pdf_bytes)

    def _add_personal_data_text(self):
        self.pdf.add_default_cell(f'Name: {self.person.name}')
        self.pdf.add_default_cell(f'Alter: {self.person.age}')
        self.pdf.add_default_cell(f'Geschlecht: {self.person.gender.value}')
        if self.person.position is not None:
            self.pdf.add_default_cell(f'Position: {self.person.position}')

    def _add_answer_text(self):
        test_answer = self.evaluable_test_answer.test_answer
        self.pdf.add_default_cell(f'Test abgegeben am: {test_answer.date}')
        self.pdf.add_default_cell(f'Test Name: {test_answer.test_name}')
        self.pdf.add_default_cell(f'Test Antworten: {test_answer.answer_set}')
