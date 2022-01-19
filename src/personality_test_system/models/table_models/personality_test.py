# custom
from personality_test_system.models.database import db


class PersonalityTest(db.Model):
    __tablename__ = "personality_test"

    name = db.Column(db.String, primary_key=True)
    description_json = db.Column(db.JSON)
    answers = db.relationship("PersonalityTestAnswer")

    def __repr__(self):
        return f"Test '{self.name}': {self.description_json}"
