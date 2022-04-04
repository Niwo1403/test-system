# custom
from test_system.models.database import db


class EvaluableTestAnswer(db.Model):
    __tablename__ = "evaluable_test_answer"

    id = db.Column(db.Integer, primary_key=True)
    was_evaluated_with_token = db.Column(db.String, db.ForeignKey("token.token"), default=None)
    test_answer_id = db.Column(db.Integer, db.ForeignKey("test_answer.id"))

    test_answer = db.relationship("TestAnswer")

    def __repr__(self):
        return (f"EvaluableTestAnswer {self.id} ("
                f"was_evaluated_with_token: {self.was_evaluated_with_token}, "
                f"test_answer_id: {self.test_answer_id})")

    def was_evaluated(self) -> bool:
        """
        Returns True, if a PDF was generated for this answer earlier.
        """
        return self.was_evaluated_with_token is not None
