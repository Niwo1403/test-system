# 3rd party
from sqlalchemy.exc import IntegrityError
# custom
from test_system import app
from .table_models import User, Test, Token
from .database import db


default_user = User(username="admin", password="admin")

default_personal_data_test = Test(name="PersonalDataTest", description_json={
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

default_pre_collect_test = Test(name="PreCol", description_json={
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

default_test = Test(name="Test1", description_json={
    "title": "Test 1",
    "description": "Some questions about an object, etc. :)",
    "logoPosition": "right",
    "pages": [
        {
            "name": "page1",
            "elements": [
                {
                    "type": "text",
                    "name": "Name",
                    "title": "Object name"
                },
                {
                    "type": "checkbox",
                    "name": "Abilities",
                    "title": "It can",
                    "choices": [
                        {
                            "value": "swimable",
                            "text": "swim"
                        },
                        {
                            "value": "soundable",
                            "text": "sound"
                        },
                        {
                            "value": "burnable",
                            "text": "burn"
                        }
                    ]
                },
                {
                    "type": "radiogroup",
                    "name": "Expensiveness",
                    "title": "Is it expensive",
                    "choices": [
                        {
                            "value": "high",
                            "text": "+"
                        },
                        {
                            "value": "mid",
                            "text": "o"
                        },
                        {
                            "value": "low",
                            "text": "-"
                        }
                    ]
                },
                {
                    "type": "dropdown",
                    "name": "Coolness",
                    "title": "Is it cool?",
                    "choices": [
                        {
                            "value": "high",
                            "text": "++"
                        },
                        "o_o",
                        {
                            "value": "low",
                            "text": "--"
                        }
                    ]
                },
                {
                    "type": "rating",
                    "name": "Object rating",
                    "title": "Rate the object"
                },
                {
                    "type": "boolean",
                    "name": "Owning",
                    "title": "Do you own the object?"
                }
            ],
            "title": "About an object of your choice"
        },
        {
            "name": "page2",
            "elements": [
                {
                    "type": "signaturepad",
                    "name": "PI",
                    "title": "Can your write Pi?"
                },
                {
                    "type": "rating",
                    "name": "Survey rating",
                    "title": "Rate the Survey",
                    "rateMax": 10
                }
            ],
            "title": "General..."
        }
    ]
}, test_category=Test.CATEGORIES.EXPORTABLE_TEST)

test_token = Token(token="asdf",
                   max_usage_count=2,
                   personal_data_test_name="PersonalDataTest",
                   pre_collect_test_names=["PreCol", "PreCol"],
                   exportable_test_name="Test1")

DEFAULT_ORM_OBJECTS = [default_user, default_personal_data_test, default_pre_collect_test, default_test, test_token]


def _create_default_database_data():
    db.session.add_all(DEFAULT_ORM_OBJECTS)
    try:
        db.session.commit()
    except IntegrityError:
        app.logger.error("IntegrityError: Failed adding data to database - maybe data already exists.")
        db.session.rollback()
