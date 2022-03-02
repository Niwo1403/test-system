# std
from io import BytesIO
# custom
from .pdf import PDF
from test_system.models import db, EvaluableTestAnswer, Person, EvaluableQuestionAnswer, EvaluableQuestionName


class CertificateManager:

    def __init__(self, person: Person):
        self.pdf = PDF()
        self.person = person
        self._add_personal_data_text()

    def add_answer(self, evaluable_test_answer: EvaluableTestAnswer) -> None:
        self.pdf.add_default_cell()
        self._add_answer(evaluable_test_answer)

    def get_pdf(self) -> BytesIO:
        pdf_bytes = self.pdf.get_pdf_bytes()
        return BytesIO(pdf_bytes)

    def _add_personal_data_text(self):
        self.pdf.add_default_cell(f'Name: {self.person.name}')
        self.pdf.add_default_cell(f'Alter: {self.person.age}')
        self.pdf.add_default_cell(f'Geschlecht: {self.person.gender.value}')
        if self.person.position is not None:
            self.pdf.add_default_cell(f'Position: {self.person.position}')

    def _add_answer(self, evaluable_test_answer: EvaluableTestAnswer):
        test_answer = evaluable_test_answer.test_answer
        self.pdf.add_default_cell(f'Test "{test_answer.test_name}" '
                                  f'(abgegeben: {test_answer.creation_timestamp.strftime("%d.%m.%Y, %H:%M:%S")})')

        category_averages = db.session.query(EvaluableQuestionName.category,
                                             db.func.avg(EvaluableQuestionAnswer.value)).join(EvaluableQuestionAnswer)\
            .filter_by(evaluable_test_answer_id=evaluable_test_answer.id).group_by(EvaluableQuestionName.category).all()
        self.pdf.add_default_cell('Test Kategorie Durchschnitte:')
        for category, avg in category_averages:
            self.pdf.add_default_cell(f"{category}: {float(avg)}")
