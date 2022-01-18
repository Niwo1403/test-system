# custom
from models.database import db


class PersonalityTestAnswer(db.Model):
    __tablename__ = "personality_test_answer"

    answer_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.TIMESTAMP)
    answer_set = db.Column(db.JSON)
    personality_test_name = db.Column(db.String, db.ForeignKey("personality_test.name"))
    person_id = db.Column(db.String, db.ForeignKey("person.id"))
