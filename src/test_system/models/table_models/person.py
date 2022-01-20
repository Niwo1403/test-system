# custom
from test_system.models.database import db


class Person(db.Model):
    __tablename__ = "person"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    gender = db.Column(db.String)
    age = db.Column(db.Integer)
    position = db.Column(db.String)
    answers = db.relationship("TestAnswer")

    def __repr__(self):
        return (f"{self.id}:\n\t"
                f"name: {self.name}\n\t"
                f"gender: {self.gender}\n\t"
                f"age: {self.age}\n\t"
                f"position: {self.position}")
