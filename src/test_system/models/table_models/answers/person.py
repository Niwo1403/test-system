# custom
from test_system.models.database import db


class Person(db.Model):
    __tablename__ = "person"

    id = db.Column(db.Integer, primary_key=True)
    answer_json = db.Column(db.JSON)

    def __repr__(self):
        return f"Person {self.id} ({self.answer_json})"
