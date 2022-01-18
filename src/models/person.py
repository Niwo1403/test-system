# custom
from models.database import db


class Person(db.Model):
    __tablename__ = "person"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    gender = db.Column(db.String)
    age = db.Column(db.Integer)
    position = db.Column(db.String)
    answers = db.relationship("PersonalityTestAnswer")
