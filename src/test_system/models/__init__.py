# custom
from .table_models import *
from .database import _create_tables_if_not_exist, db

_create_tables_if_not_exist()  # must be run after import of models ("from .table_models import *")


if User.query.first() is None:  # if no user exist, assume database is empty & create development examples
    default_user = User(username="admin", password="admin")
    person_test = Test(name="Person", description_json={
        "title": "Persöhnliche Daten",
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
                        "title": "Alter",
                        "isRequired": True,
                        "inputType": "number",
                        "min": 1,
                        "max": 200
                    },
                    {
                        "type": "radiogroup",
                        "name": "gender",
                        "title": "Geschlecht",
                        "isRequired": True,
                        "choices": [
                            {
                                "value": "m",
                                "text": "männlich"
                            },
                            {
                                "value": "w",
                                "text": "weiblich"
                            },
                            {
                                "value": "s",
                                "text": "sonstiges"
                            }
                        ]
                    },
                    {
                        "type": "text",
                        "name": "position",
                        "title": "Position"
                    }
                ]
            }
        ]
    }, test_category=Test.CATEGORIES.PERSONAL_DATA_TEST)
    pre_collect_test = Test(name="PreCol", description_json={
        "title": "Zusetzliche persöhnliche Daten",
        "logoPosition": "right",
        "pages": [
            {
                "name": "page1",
                "elements": [
                    {
                        "type": "text",
                        "name": "word",
                        "title": "Lieblingswort",
                        "isRequired": True
                    }
                ]
            }
        ]
    }, test_category=Test.CATEGORIES.PRE_COLLECT_TEST)
    pers_test = Test(name="PersTest", description_json={
        "title": "Persöhnliche Daten",
        "description": "Matrix Test",
        "logoPosition": "right",
        "pages": [
            {
                "name": "page1",
                "elements": [
                    {
                        "type": "matrix",
                        "name": "ABC",
                        "title": "Kategorie ABC",
                        "isRequired": True,
                        "columns": [
                            {
                                "value": "1",
                                "text": "tgnz"
                            },
                            {
                                "value": "2",
                                "text": "tnz"
                            },
                            {
                                "value": "3",
                                "text": "ttz"
                            },
                            {
                                "value": "4",
                                "text": "tz"
                            },
                            {
                                "value": "5",
                                "text": "tvz"
                            }
                        ],
                        "rows": [
                            {
                                "value": "Row 1",
                                "text": "Frage 1"
                            },
                            {
                                "value": "Row 2",
                                "text": "Frage 2"
                            },
                            {
                                "value": "Row 3",
                                "text": "Frage 3"
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
    db.session.commit()
