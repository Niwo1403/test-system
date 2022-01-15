# 3rd party
from flask import Flask
# custom
from routes import init_routes
from constants import STATIC_FOLDER, STATIC_URL_PATH, PORT


app = Flask(__name__, static_url_path=STATIC_URL_PATH, static_folder=STATIC_FOLDER)
init_routes(app)


if __name__ == '__main__':
    app.run(threaded=True, port=PORT)  # threaded=True for multiple user access
