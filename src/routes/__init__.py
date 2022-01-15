# 3rd party
from flask import Flask, redirect
# custom
from .test import init_test_routes
from constants import DEFAULT_INDEX_FILE


def init_routes(app: Flask) -> None:
    @app.route('/', methods=['GET'])
    def default_request():
        return redirect(DEFAULT_INDEX_FILE)

    init_test_routes(app)
