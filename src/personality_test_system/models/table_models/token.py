# custom
from personality_test_system.models.database import db


class Token(db.Model):
    __tablename__ = "token"

    token = db.Column(db.String, primary_key=True)
    max_usage_count = db.Column(db.Integer)
    personality_test_name = db.Column(db.String, db.ForeignKey("personality_test.name"))  # references name (column) from personality_test (table)

    def __repr__(self):
        return f"{self.token} ({self.personality_test_name}): {self.max_usage_count}"
