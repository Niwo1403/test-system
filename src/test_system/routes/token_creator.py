# std
from json import dumps as json_dumps
# custom
from test_system import app
from test_system.constants import API_PREFIX
from test_system.models import User, Test

ROUTE = f'{API_PREFIX}/token-creator/'


@app.route(ROUTE, methods=['GET'])
def get_token_creator():
    personal_data_test_names = Test.get_test_names_of_category(Test.CATEGORIES.PERSONAL_DATA_TEST)
    pre_collect_test_names = Test.get_test_names_of_category(Test.CATEGORIES.PRE_COLLECT_TEST)
    evaluable_test_names = Test.get_test_names_of_category(Test.CATEGORIES.EVALUABLE_TEST)
    token_creator_test = {
        "title": "Neuen Token erstellen",
        "logoPosition": "right",
        "pages": [
            {
                "name": "page1",
                "elements": [
                    {
                        "type": "dropdown",
                        "name": Test.CATEGORIES.PERSONAL_DATA_TEST.name,
                        "title": "Persönliche Daten Test",
                        "isRequired": True,
                        "choices": personal_data_test_names
                    },
                    {
                        "type": "matrixdynamic",
                        "name": Test.CATEGORIES.PRE_COLLECT_TEST.name,
                        "title": "Zusatz Informationen",
                        "columns": [{"name": "tests", "title": "Mehrere möglich"}],
                        "choices": pre_collect_test_names + evaluable_test_names
                    },
                    {
                        "type": "dropdown",
                        "name": Test.CATEGORIES.EVALUABLE_TEST.name,
                        "title": "Automatisch auswertbarer Test",
                        "isRequired": True,
                        "choices": evaluable_test_names
                    },
                    {
                        "type": "text",
                        "name": User.username.key,
                        "title": "Nutzername",
                        "isRequired": True
                    },
                    {
                        "type": "text",
                        "name": User.password.key,
                        "title": "Passwort",
                        "isRequired": True
                    }
                ]
            }
        ]
    }
    return json_dumps(token_creator_test)
