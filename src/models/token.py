# custom
from .database import db


class Token(db.Model):
    __tablename__ = "token"

    token = db.Column(db.String, primary_key=True)
    max_usage_count = db.Column(db.Integer)
    personality_test_name = db.Column(db.String, db.ForeignKey("personality_test.name"))  # references name (column) from personality_test (table)
