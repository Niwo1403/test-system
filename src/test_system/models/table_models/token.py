# std
from typing import List, Optional
# 3rd party
from sqlalchemy.sql.expression import text
# custom
from test_system.constants import MAX_HASH_GENERATION_TRY_COUNT, TOKEN_PERIOD_OF_VALIDITY_IN_DAYS
from test_system.util import generate_unknown_hash_token
from test_system.models.database import db
from .answers import EvaluableTestAnswer
from .test import Test


class Token(db.Model):
    __tablename__ = "token"

    token = db.Column(db.String, primary_key=True)
    max_usage_count: db.Column = db.Column(db.Integer)
    personal_data_test_name = db.Column(db.String, db.ForeignKey("test.name"))
    pre_collect_test_names = db.Column(db.ARRAY(db.String))  # references name (column) from test (table)
    evaluable_test_name = db.Column(db.String, db.ForeignKey("test.name"))
    creation_timestamp: db.Column = db.Column(db.TIMESTAMP)  # no default value here, otherwise None can't be inserted

    personal_data_test = db.relationship("Test", foreign_keys=[personal_data_test_name])
    evaluable_test = db.relationship("Test", foreign_keys=[evaluable_test_name])

    @classmethod
    def generate_token(cls,
                       max_usage_count: Optional[int],
                       personal_data_test_name: str,
                       pre_collect_test_names: List[str],
                       evaluable_test_name: str,
                       expires: bool = True) -> "Token":
        token_hash = generate_unknown_hash_token(
            lambda test_token: cls.query.filter_by(token=test_token).first() is None, MAX_HASH_GENERATION_TRY_COUNT)
        return cls(creation_timestamp=db.func.now() if expires else None,
                   token=token_hash,
                   max_usage_count=max_usage_count,
                   personal_data_test_name=personal_data_test_name,
                   pre_collect_test_names=pre_collect_test_names,
                   evaluable_test_name=evaluable_test_name)

    @staticmethod
    def get_earliest_valid_sql_timestamp():
        return text(f"NOW() - INTERVAL '1 DAY' * {TOKEN_PERIOD_OF_VALIDITY_IN_DAYS}")

    def __init__(self, **kwargs):
        if "creation_timestamp" not in kwargs:  # do manually to enable None passing
            kwargs["creation_timestamp"] = db.func.now()
        super(Token, self).__init__(**kwargs)

    def __repr__(self):
        return (f"Token '{self.token}' ("
                f"personal data test: {self.personal_data_test_name}, "
                f"pre collect Tests: {self.pre_collect_test_names}, "
                f"evaluable test: {self.evaluable_test_name}, "
                f"usages: {self.max_usage_count})")

    def is_invalid(self) -> bool:
        return self._is_expired() or self._has_no_usage_left()

    def use_for(self, evaluable_test_answer: EvaluableTestAnswer) -> None:
        evaluable_test_answer.was_evaluated_with_token = self.token
        if self.max_usage_count is not None:
            self.max_usage_count -= 1
            db.session.commit()

    def get_pre_collect_tests(self) -> List[Test]:
        possible_pre_collect_tests = [Test.query.filter_by(name=pre_collect_test_name).first()
                                      for pre_collect_test_name in self.pre_collect_test_names]
        pre_collect_tests = list(filter(lambda test: test is not None, possible_pre_collect_tests))
        return pre_collect_tests

    def _is_expired(self) -> bool:
        if self.creation_timestamp is None:
            return False

        unexpired_token = Token.query.filter_by(token=self.token)\
            .filter(Token.creation_timestamp >= Token.get_earliest_valid_sql_timestamp()).first()
        return unexpired_token != self

    def _has_no_usage_left(self) -> bool:
        return self.max_usage_count is not None and self.max_usage_count <= 0
