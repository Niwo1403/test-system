# custom
from test_system.models.database import db


class EvaluableQuestionAnswer(db.Model):  # belongs to EvaluableTestAnswer
    __tablename__ = "evaluable_question_answer"

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer)
    question_name_id = db.Column(db.Integer, db.ForeignKey("evaluable_question_name.id"))
    test_answer_id = db.Column(db.Integer, db.ForeignKey("evaluable_test_answer.id"))

    def __repr__(self):
        return (f"EvaluableQuestionAnswer {self.id} ("
                f"value: {self.value}, "
                f"question_name_id: {self.question_name_id}, "
                f"test_answer_id: {self.test_answer_id})")
