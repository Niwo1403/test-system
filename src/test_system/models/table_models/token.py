# std
from hashlib import sha3_512
from datetime import datetime
from typing import List
# custom
from test_system.models.database import db
from .answers import EvaluableTestAnswer


class Token(db.Model):
    __tablename__ = "token"

    token = db.Column(db.String, primary_key=True)
    max_usage_count = db.Column(db.Integer)
    personal_data_test_name = db.Column(db.String, db.ForeignKey("test.name"))
    pre_collection_test_names = db.Column(db.ARRAY(db.String))  # references name (column) from test (table)
    evaluable_test_name = db.Column(db.String, db.ForeignKey("test.name"))

    personal_data_test = db.relationship("Test", foreign_keys=[personal_data_test_name])
    evaluable_test = db.relationship("Test", foreign_keys=[evaluable_test_name])

    @classmethod
    def generate_token(cls,
                       max_usage_count: int,
                       personal_data_test_name: str,
                       pre_collection_test_names: List[str],
                       evaluable_test_name: str) -> "Token":
        now = datetime.now()
        token_seed = str(now).encode()
        token_hash = sha3_512(token_seed).hexdigest()
        return cls(token=token_hash,
                   max_usage_count=max_usage_count,
                   personal_data_test_name=personal_data_test_name,
                   pre_collection_test_names=pre_collection_test_names,
                   evaluable_test_name=evaluable_test_name)

    def __repr__(self):
        return (f"Token '{self.token}' ("
                f"personal data test: {self.personal_data_test_name}, "
                f"pre collection Tests: {self.pre_collection_test_names}, "
                f"evaluable test: {self.evaluable_test_name}, "
                f"usages: {self.max_usage_count})")

    def is_expired(self, remove_if_expired: bool = False) -> bool:
        expired = self.max_usage_count is not None and self.max_usage_count <= 0
        if remove_if_expired and expired:
            db.session.delete(self)
            db.session.commit()
        return expired

    def use_for(self, evaluable_test_answer: EvaluableTestAnswer) -> None:
        evaluable_test_answer.was_evaluated_with_token = True
        self.max_usage_count -= 1
        db.session.commit()
        self.is_expired(remove_if_expired=True)
