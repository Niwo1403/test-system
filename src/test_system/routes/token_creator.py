# std
from json import dumps as json_dumps
# custom
from test_system import app
from test_system.constants import API_PREFIX, PRE_COLLECT_TESTS_SURVEY_KEYWORD, EXPIRES_SURVEY_KEYWORD, \
    PRE_COLLECT_TESTS_KEY
from test_system.models import User, Test, Token

ROUTE = f'{API_PREFIX}/token-creator/'


@app.route(ROUTE, methods=['GET'])
def get_token_creator():
    personal_data_test_names = Test.get_test_names_of_category(Test.CATEGORIES.PERSONAL_DATA_TEST)
    pre_collect_test_names = Test.get_test_names_of_category(Test.CATEGORIES.PRE_COLLECT_TEST)
    exportable_test_names = Test.get_test_names_of_category(Test.CATEGORIES.EXPORTABLE_TEST)

    last_created_token: Token = Token.query.order_by(Token.creation_timestamp.desc()).first()
    token_exist = last_created_token is not None

    token_creator_test = {
        "title": "Create new token",
        "logoPosition": "right",
        "pages": [
            {
                "name": "page1",
                "elements": [
                    {
                        "type": "dropdown",
                        "name": Test.CATEGORIES.PERSONAL_DATA_TEST.name,
                        "title": "Personal data test",
                        "defaultValueExpression": last_created_token.personal_data_test_name if token_exist else None,
                        "isRequired": True,
                        "choices": personal_data_test_names,
                        "choicesOrder": "asc"
                    },
                    {
                        "type": "matrixdynamic",
                        "name": PRE_COLLECT_TESTS_KEY,
                        "title": "Additional information",
                        "defaultValue": [{PRE_COLLECT_TESTS_SURVEY_KEYWORD: pre_collect_test_name}
                                         for pre_collect_test_name in last_created_token.pre_collect_test_names
                                         ] if token_exist else None,
                        "columns": [{"name": PRE_COLLECT_TESTS_SURVEY_KEYWORD, "title": "Multiple possible"}],
                        "choices": pre_collect_test_names + exportable_test_names,
                        "rowCount": 1,
                        "allowRowsDragAndDrop": True
                    },
                    {
                        "type": "dropdown",
                        "name": Test.CATEGORIES.EXPORTABLE_TEST.name,
                        "title": "Test whose answers will be exported",
                        "defaultValueExpression": last_created_token.exportable_test_name if token_exist else None,
                        "isRequired": True,
                        "choices": exportable_test_names,
                        "choicesOrder": "asc"
                    },
                    {
                        "type": "text",
                        "name": "max_usage_count",
                        "title": "Max usages",
                        "description": "Leave empty for unlimited uses",
                        "inputType": "number",
                        "min": 0
                    },
                    {
                        "type": "boolean",
                        "name": EXPIRES_SURVEY_KEYWORD,
                        "title": "Should the token be limited in time?",
                        "defaultValue": "true",
                        "isRequired": True
                    },
                    {
                        "type": "text",
                        "name": User.username.key,
                        "title": "Username",
                        "isRequired": True
                    },
                    {
                        "type": "text",
                        "name": User.password.key,
                        "title": "Password",
                        "isRequired": True
                    }
                ]
            }
        ]
    }
    app.logger.info("Sending token-creator JSON.")
    return json_dumps(token_creator_test)
