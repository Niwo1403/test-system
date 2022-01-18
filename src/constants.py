# routes

API_PREFIX = "/api"
DEFAULT_INDEX_FILE = "/index.html"

# flask

STATIC_URL_PATH = ""
STATIC_FOLDER = "../static"

PORT = 5000

# database

APP_CONFIG = {
    'SQLALCHEMY_DATABASE_URI': "sqlite:///:memory:",  # TODO: Adjust... postgresql://scott:tiger@localhost/mydatabase
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_ECHO': False  # if true, all statements will be logged - maybe useful for debugging
}
