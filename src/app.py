# 3rd party
from flask import Flask
# custom
from constants import STATIC_FOLDER, STATIC_URL_PATH


app = Flask(__name__, static_url_path=STATIC_URL_PATH, static_folder=STATIC_FOLDER)
