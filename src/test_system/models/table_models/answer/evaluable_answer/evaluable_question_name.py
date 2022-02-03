# custom
from test_system.models.database import db


class EvaluableQuestionName(db.Model):
    __tablename__ = "evaluable_question_name"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String)
    name = db.Column(db.String)
