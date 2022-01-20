# 3rd party
from flask import Flask
# custom
from test_system.constants import STATIC_FOLDER, STATIC_URL_PATH, LOG_LEVEL


app = Flask(__name__, static_url_path=STATIC_URL_PATH, static_folder=STATIC_FOLDER)
app.logger.setLevel(LOG_LEVEL)
