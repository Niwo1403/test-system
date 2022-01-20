# 3rd party
from flask import redirect
# custom
from test_system.constants import DEFAULT_INDEX_FILE
from test_system import app


@app.route('/', methods=['GET'])
def root():
    return redirect(DEFAULT_INDEX_FILE)
