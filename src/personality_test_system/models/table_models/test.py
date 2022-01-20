# custom
from personality_test_system.models.database import db


class Test(db.Model):
    __tablename__ = "test"

    name = db.Column(db.String, primary_key=True)
    description_json = db.Column(db.JSON)
    answers = db.relationship("TestAnswer")

    def __repr__(self):
        return f"Test '{self.name}': {self.description_json}"
