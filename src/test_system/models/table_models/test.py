# std
from enum import Enum
from typing import Dict, Union
# 3rd party
from flask import abort
# custom
from test_system.models.database import db


class TestCategory(Enum):
    # str values use for error message generation (as category name)
    PERSONAL_DATA_TEST = "personal data"
    PRE_COLLECT_TEST = "pre collect"
    EVALUABLE_TEST = "evaluable"


class Test(db.Model):
    __tablename__ = "test"

    name = db.Column(db.String, primary_key=True)
    description_json = db.Column(db.JSON)
    test_category = db.Column(db.Enum(TestCategory))
    answers = db.relationship("TestAnswer")

    CATEGORIES = TestCategory

    @classmethod
    def get_category_test_or_abort(cls, test_name: str, assert_category: TestCategory,
                                   wrong_category_status_code: int = 500) -> "Test":
        test: Test = cls.query.filter_by(name=test_name).first()
        if assert_category is not None:
            if test is None:
                abort(404, f"The {assert_category.value} test doesn't exist.")
            if test.test_category != assert_category:
                abort(wrong_category_status_code,
                      f"Trying to use {test.test_category.value} test as {assert_category.value} test.")
        return test

    def __repr__(self):
        return f"Test '{self.name}' ({self.test_category}): {self.description_json}"

    def get_named_description_dict(self) -> Dict[str, Union[str, Dict]]:
        return {"name": self.name, "description": self.description_json}
