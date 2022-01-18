# custom
from .database import db


class PersonalityTest(db.Model):
    __tablename__ = "personality_test"

    name = db.Column(db.String, primary_key=True)
    description_json = db.Column(db.JSON)
    tokens = db.relationship("PersonalityTest")
    answers = db.relationship("PersonalityTestAnswer")
