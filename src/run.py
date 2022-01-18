# custom
from app import app
import routes  # required to load all routes!
from constants import PORT


if __name__ == '__main__':
    app.run(threaded=True, port=PORT)  # threaded=True for multiple user access
