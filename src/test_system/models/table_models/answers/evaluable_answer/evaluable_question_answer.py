# std
from typing import Dict, Any, List
# custom
from test_system.models.database import db
from .evaluable_test_answer import EvaluableTestAnswer
from .evaluable_question_name import EvaluableQuestionName


class EvaluableQuestionAnswer(db.Model):  # belongs to EvaluableTestAnswer
    __tablename__ = "evaluable_question_answer"

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer)
    evaluable_question_name_id = db.Column(db.Integer, db.ForeignKey("evaluable_question_name.id"))
    evaluable_test_answer_id = db.Column(db.Integer, db.ForeignKey("evaluable_test_answer.id"))

    @classmethod
    def create_answers(cls, answer_set: Dict[str, Dict[str, Any]],
                       evaluable_answer: EvaluableTestAnswer) -> List["EvaluableQuestionAnswer"]:
        evaluable_answer_id = evaluable_answer.id
        answers = []
        for question_category, category_answers in answer_set.items():
            for question_name, answer_value in category_answers.items():
                question_name_id = EvaluableQuestionName.get_id_for(question_category, question_name)
                evaluable_question_answer = cls(value=answer_value,
                                                evaluable_question_name_id=question_name_id,
                                                evaluable_test_answer_id=evaluable_answer_id)
                answers.append(evaluable_question_answer)
        return answers

    def __repr__(self):
        return (f"EvaluableQuestionAnswer {self.id} ("
                f"value: {self.value}, "
                f"evaluable_question_name_id: {self.evaluable_question_name_id}, "
                f"evaluable_test_answer_id: {self.evaluable_test_answer_id})")
