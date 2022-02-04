# custom
from test_system.models.database import db


class TestAnswer(db.Model):
    __tablename__ = "test_answer"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.TIMESTAMP)
    answer_set = db.Column(db.JSON)
    test_name = db.Column(db.String, db.ForeignKey("test.name"))
    person_id = db.Column(db.Integer, db.ForeignKey("person.id"))

    def __repr__(self):
        return (f"Answer {self.id} ("
                f"test: {self.test_name},"
                f"person_id: {self.person_id},"
                f"date: {self.date},"
                f"answer_set: {self.answer_set})")
