from flask import Flask
from constants import API_PREFIX


def init_test_routes(app: Flask) -> None:
    @app.route(f'{API_PREFIX}/', methods=['GET'])
    def api():
        return "Hello World"

