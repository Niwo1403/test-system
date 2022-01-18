# 3rd party
from flask import redirect
# custom
from personality_test_system.constants import DEFAULT_INDEX_FILE
from personality_test_system import app


@app.route('/', methods=['GET'])
def root():
    return redirect(DEFAULT_INDEX_FILE)
