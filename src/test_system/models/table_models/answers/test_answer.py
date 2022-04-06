# custom
from test_system.models.database import db


class TestAnswer(db.Model):
    __tablename__ = "test_answer"

    id = db.Column(db.Integer, primary_key=True)
    creation_timestamp = db.Column(db.TIMESTAMP, default=db.func.now())
    answer_json = db.Column(db.JSON)
    test_name = db.Column(db.String, db.ForeignKey("test.name"))
    personal_data_answer_id = db.Column(db.Integer, db.ForeignKey("test_answer.id"), default=None)

    def __repr__(self):
        return (f"Answer {self.id} ("
                f"test: {self.test_name},"
                f"personal_data_answer_id: {self.personal_data_answer_id},"
                f"date: {self.creation_timestamp},"
                f"answer_json: {self.answer_json})")
