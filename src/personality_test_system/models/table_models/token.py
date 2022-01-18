# std
from hashlib import sha3_512
from datetime import datetime
# custom
from personality_test_system.models.database import db


class Token(db.Model):
    __tablename__ = "token"

    token = db.Column(db.String, primary_key=True)
    max_usage_count = db.Column(db.Integer)
    personality_test_name = db.Column(db.String, db.ForeignKey("personality_test.name"))  # references name (column) from personality_test (table)

    @classmethod
    def generate_token(cls, max_usage_count: int, personality_test_name: str) -> "Token":
        now = datetime.now()
        token_seed = str(now).encode()
        token_hash = sha3_512(token_seed).hexdigest()
        return cls(token=token_hash, max_usage_count=max_usage_count, personality_test_name=personality_test_name)

    def __repr__(self):
        return f"{self.token} ({self.personality_test_name}): {self.max_usage_count}"
