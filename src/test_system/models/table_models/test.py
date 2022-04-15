# std
from enum import Enum
from typing import Dict, Union, List
# 3rd party
from flask import abort
# custom
from test_system.models.database import db


class TestCategory(Enum):
    # str values use for error message generation (as category name)
    PERSONAL_DATA_TEST = "personal data"
    PRE_COLLECT_TEST = "pre collect"
    EXPORTABLE_TEST = "exportable"


class Test(db.Model):
    __tablename__ = "test"

    name = db.Column(db.String, primary_key=True)
    description_json = db.Column(db.JSON)
    test_category = db.Column(db.Enum(TestCategory))

    CATEGORIES = TestCategory

    @classmethod
    def get_test_names_of_category(cls, test_category: CATEGORIES) -> List[str]:
        """
        Returns all names of tests, which have the category test_category.
        """
        return [row[0] for row in cls.query.filter_by(test_category=test_category).values(Test.name)]

    @classmethod
    def get_category_test_or_abort(cls, test_name: str, assert_category: TestCategory,
                                   wrong_category_status_code: int = 400) -> "Test":
        """
        Returns the test with name test_name and category assert_category.
        If the requests test doesn't exist, the request will be aborted by a raised exception.
        """
        test: Test = cls.query.filter_by(name=test_name).first()
        if assert_category is not None:
            cls.assert_test_existence_and_category(test, assert_category, wrong_category_status_code)
        return test

    @staticmethod
    def assert_test_existence_and_category(test: "Test", assert_category: TestCategory,
                                           wrong_category_status_code: int = 500) -> None:
        """
        If the passed test doesn't exist or doesn't have the assert_category,
        the request will be aborted by a raised exception.
        """
        if test is None:
            abort(404, f"The {assert_category.value} test doesn't exist.")
        if test.test_category != assert_category:
            abort(wrong_category_status_code,
                  f"Trying to use {test.test_category.value} test as {assert_category.value} test.")

    def __repr__(self):
        return f"Test '{self.name}' ({self.test_category}): {self.description_json}"

    def get_named_description_dict(self) -> Dict[str, Union[str, Dict]]:
        """
        Crates a dictionary, containing the "name" and "description" of the test.
        """
        return {"name": self.name, "description": self.description_json}
