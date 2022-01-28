# custom
from test_system import app, PORT


if __name__ == '__main__':
    app.run(threaded=True, port=PORT, host="0.0.0.0")  # threaded=True for multiple user access
