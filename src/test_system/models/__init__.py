# 3rd party
from sqlalchemy.exc import IntegrityError
# custom
from test_system import app
from .table_models import *
from .database import _create_tables_if_not_exist, db

_create_tables_if_not_exist()  # must be run after import of models ("from .table_models import *")


if User.query.first() is None:  # if no user exist, assume database is empty & create development examples
    default_user = User(username="admin", password="admin")
    person_test = Test(name="Person", description_json={
        "title": "Personal data",
        "logoPosition": "right",
        "pages": [
            {
                "name": "page1",
                "elements": [
                    {
                        "type": "text",
                        "name": "name",
                        "title": "Name:",
                        "isRequired": True
                    },
                    {
                        "type": "text",
                        "name": "age",
                        "title": "Age",
                        "isRequired": True,
                        "inputType": "number",
                        "min": 1,
                        "max": 200
                    },
                    {
                        "type": "radiogroup",
                        "name": "gender",
                        "title": "Gender",
                        "isRequired": True,
                        "choices": [
                            {
                                "value": "m",
                                "text": "male"
                            },
                            {
                                "value": "f",
                                "text": "female"
                            },
                            {
                                "value": "d",
                                "text": "diverse"
                            }
                        ]
                    }
                ]
            }
        ]
    }, test_category=Test.CATEGORIES.PERSONAL_DATA_TEST)
    pre_collect_test = Test(name="PreCol", description_json={
        "title": "Additional Information",
        "logoPosition": "right",
        "pages": [
            {
                "name": "page1",
                "elements": [
                    {
                        "type": "text",
                        "name": "word",
                        "title": "Favorite word",
                        "isRequired": True
                    }
                ]
            }
        ]
    }, test_category=Test.CATEGORIES.PRE_COLLECT_TEST)
    pers_test = Test(name="PersTest", description_json={
        "title": "Test",
        "description": "Matrix Test",
        "logoPosition": "right",
        "pages": [
            {
                "name": "page1",
                "elements": [
                    {
                        "type": "matrix",
                        "name": "ABC",
                        "titleLocation": "hidden",
                        "isRequired": True,
                        "columns": [
                            {
                                "value": "1",
                                "text": "strongly disagree"
                            },
                            {
                                "value": "2",
                                "text": "partially disagree"
                            },
                            {
                                "value": "3",
                                "text": "partially agree"
                            },
                            {
                                "value": "4",
                                "text": "strongly agree"
                            }
                        ],
                        "rows": [
                            {
                                "value": "Question 1",
                                "text": "First question"
                            },
                            {
                                "value": "Question 2",
                                "text": "Second question"
                            }
                        ]
                    },
                    {
                        "type": "matrix",
                        "name": "DEF",
                        "titleLocation": "hidden",
                        "isRequired": True,
                        "columns": [
                            {
                                "value": "1",
                                "text": "strongly disagree"
                            },
                            {
                                "value": "2",
                                "text": "partially disagree"
                            },
                            {
                                "value": "3",
                                "text": "partially agree"
                            },
                            {
                                "value": "4",
                                "text": "strongly agree"
                            }
                        ],
                        "rows": [
                            {
                                "value": "Question 3",
                                "text": "Third question"
                            },
                            {
                                "value": "Question 4",
                                "text": "Fourth question"
                            }
                        ]
                    }
                ]
            },
            {
                "name": "page2",
                "elements": [
                    {
                        "type": "matrix",
                        "name": "DEF",
                        "titleLocation": "hidden",
                        "isRequired": True,
                        "columns": [
                            {
                                "value": "1",
                                "text": "strongly disagree"
                            },
                            {
                                "value": "2",
                                "text": "partially disagree"
                            },
                            {
                                "value": "3",
                                "text": "partially agree"
                            },
                            {
                                "value": "4",
                                "text": "strongly agree"
                            }
                        ],
                        "rows": [
                            {
                                "value": "Question 5",
                                "text": "Fifth question"
                            },
                            {
                                "value": "Question 6",
                                "text": "Sixth question"
                            }
                        ]
                    },
                    {
                        "type": "matrix",
                        "name": "ABC",
                        "titleLocation": "hidden",
                        "isRequired": True,
                        "columns": [
                            {
                                "value": "1",
                                "text": "strongly disagree"
                            },
                            {
                                "value": "2",
                                "text": "partially disagree"
                            },
                            {
                                "value": "3",
                                "text": "partially agree"
                            },
                            {
                                "value": "4",
                                "text": "strongly agree"
                            }
                        ],
                        "rows": [
                            {
                                "value": "Question 7",
                                "text": "Seventh question"
                            },
                            {
                                "value": "Question 8",
                                "text": "Eighth question"
                            }
                        ]
                    }
                ]
            }
        ]
    }, test_category=Test.CATEGORIES.EVALUABLE_TEST)
    test_token = Token(token="asdf",
                       max_usage_count=2,
                       personal_data_test_name="Person",
                       pre_collect_test_names=["PreCol", "PreCol"],
                       evaluable_test_name="PersTest")
    db.session.add_all((default_user, person_test, pre_collect_test, pers_test, test_token))
    try:
        db.session.commit()
    except IntegrityError:
        app.logger.error("IntegrityError: Failed adding data to database - maybe data already exists.")
        db.session.rollback()
