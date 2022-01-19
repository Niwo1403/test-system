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
        return f"{self.token} (Test: {self.personality_test_name}, usages: {self.max_usage_count})"

    def is_expired(self) -> bool:
        expired = self.max_usage_count is not None and self.max_usage_count <= 0
        if expired:
            db.session.delete(self)
            db.session.commit()
        return expired

    def remove_usage(self) -> None:
        self.max_usage_count -= 1
        db.session.commit()
