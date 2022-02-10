# std
from json import dumps as json_dumps
# 3rd party
from flask.testing import FlaskClient
# custom
from test_system.models import Token
from test_system.routes.token import ROUTE


def test_post_token__with_success(client: FlaskClient, session, username: str, password: str, test_names):
    max_usage_count = 10
    query_string = {"username": username,
                    "password": password,
                    "max-usage-count": str(max_usage_count),
                    "personal-data-test-name": test_names["PERSONAL_DATA_TEST"],
                    "pre-collect-test-names": json_dumps(test_names["PRE_COLLECT_TESTS"]),
                    "evaluable-test-name": test_names["EVALUABLE_TEST"]}
    resp = client.post(ROUTE, query_string=query_string)
    assert resp.status_code == 201, f"Can't POST token to {ROUTE} with arguments {query_string}"

    token_hash = resp.data.decode()
    token = Token.query.filter_by(token=token_hash).first()
    assert token is not None, "Could not write Token to database"

    token_test_names = {
        "PERSONAL_DATA_TEST": token.personal_data_test_name,
        "PRE_COLLECT_TESTS": token.pre_collect_test_names,
        "EVALUABLE_TEST": token.evaluable_test_name
    }
    assert token_test_names == test_names and token.max_usage_count == max_usage_count and len(token_hash) == 128, \
        f"Got token with wrong data at route {ROUTE} with arguments {query_string}: {token}"
