# custom
from .pdf import PDF
from test_system.models import EvaluableTestAnswer, Person, TestAnswer


class CertificateManager:

    def __init__(self, evaluable_test_answer: EvaluableTestAnswer, person: Person):
        self.pdf = PDF()
        self.evaluable_test_answer = evaluable_test_answer
        self.person = person

    def generate_certificate(self) -> bytes:
        self._add_personal_data_text()
        self.pdf.add_default_cell()
        self._add_answer_text()
        return self.pdf.get_pdf_bytes()

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
