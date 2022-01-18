# custom
from app import app
from constants import API_PREFIX


@app.route(f'{API_PREFIX}/token/', methods=['GET'])
def get_token():
    return "Hello World"

