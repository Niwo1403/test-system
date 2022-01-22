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
        return (f"id: {self.id}, "
                f"name: {self.name}, "
                f"gender: {self.gender}, "
                f"age: {self.age}, "
                f"position: {self.position}")
