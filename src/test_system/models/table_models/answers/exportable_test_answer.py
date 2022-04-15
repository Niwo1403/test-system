# custom
from test_system.models.database import db


class ExportableTestAnswer(db.Model):
    __tablename__ = "exportable_test_answer"

    id = db.Column(db.Integer, primary_key=True)
    was_saved_with_token = db.Column(db.String, db.ForeignKey("token.token"), default=None)
    test_answer_id = db.Column(db.Integer, db.ForeignKey("test_answer.id"))

    test_answer = db.relationship("TestAnswer")

    def __repr__(self):
        return (f"ExportableTestAnswer {self.id} ("
                f"was_saved_with_token: {self.was_saved_with_token}, "
                f"test_answer_id: {self.test_answer_id})")
