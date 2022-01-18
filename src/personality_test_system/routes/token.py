# custom
from personality_test_system import app
from personality_test_system.constants import API_PREFIX


@app.route(f'{API_PREFIX}/token/', methods=['GET'])
def get_token():
    return "Hello World"

