# std
from json import dumps as json_dumps
# custom
from test_system import app
from test_system.constants import API_PREFIX, PRE_COLLECT_TESTS_SURVEY_KEYWORD, EXPIRES_SURVEY_KEYWORD
from test_system.models import User, Test, Token

ROUTE = f'{API_PREFIX}/token-creator/'


@app.route(ROUTE, methods=['GET'])
def get_token_creator():
    personal_data_test_names = Test.get_test_names_of_category(Test.CATEGORIES.PERSONAL_DATA_TEST)
    pre_collect_test_names = Test.get_test_names_of_category(Test.CATEGORIES.PRE_COLLECT_TEST)
    evaluable_test_names = Test.get_test_names_of_category(Test.CATEGORIES.EVALUABLE_TEST)

    last_created_token: Token = Token.query.order_by(Token.creation_timestamp.desc()).first()
    token_exist = last_created_token is not None

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
                        "defaultValueExpression": last_created_token.personal_data_test_name if token_exist else None,
                        "isRequired": True,
                        "choices": personal_data_test_names,
                        "choicesOrder": "asc"
                    },
                    {
                        "type": "matrixdynamic",
                        "name": Test.CATEGORIES.PRE_COLLECT_TESTS.name,
                        "title": "Zusatz Informationen",
                        "defaultValue": [{PRE_COLLECT_TESTS_SURVEY_KEYWORD: pre_collect_test_name}
                                         for pre_collect_test_name in last_created_token.pre_collect_test_names
                                         ] if token_exist else None,
                        "columns": [{"name": PRE_COLLECT_TESTS_SURVEY_KEYWORD, "title": "Mehrere möglich"}],
                        "choices": pre_collect_test_names + evaluable_test_names,
                        "rowCount": 1,
                        "allowRowsDragAndDrop": True
                    },
                    {
                        "type": "dropdown",
                        "name": Test.CATEGORIES.EVALUABLE_TEST.name,
                        "title": "Automatisch auswertbarer Test",
                        "defaultValueExpression": last_created_token.evaluable_test_name if token_exist else None,
                        "isRequired": True,
                        "choices": evaluable_test_names,
                        "choicesOrder": "asc"
                    },
                    {
                        "type": "text",
                        "name": "max_usage_count",
                        "title": "Maximale Nutzungen",
                        "description": "Leer lassen für unbegrenzte Nutzung",
                        "inputType": "number",
                        "min": 0
                    },
                    {
                        "type": "boolean",
                        "name": EXPIRES_SURVEY_KEYWORD,
                        "title": "Soll der Token zeitlich beschrenkt sein?",
                        "defaultValue": "true",
                        "isRequired": True
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
