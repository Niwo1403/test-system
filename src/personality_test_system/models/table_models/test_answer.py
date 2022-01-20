# custom
from personality_test_system.models.database import db


class TestAnswer(db.Model):
    __tablename__ = "test_answer"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.TIMESTAMP)
    answer_set = db.Column(db.JSON)
    test_name = db.Column(db.String, db.ForeignKey("test.name"))
    person_id = db.Column(db.Integer, db.ForeignKey("person.id"))

    def __repr__(self):
        return (f"{self.id}:\n\t"
                f"test: {self.test_name},\n\t"
                f"person_id: {self.person_id},\n\t"
                f"date: {self.date},\n\t"
                f"answer_set: {self.answer_set}")

