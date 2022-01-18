# 3rd party
from flask import redirect
# custom
from constants import DEFAULT_INDEX_FILE
from app import app


@app.route('/', methods=['GET'])
def root():
    return redirect(DEFAULT_INDEX_FILE)
