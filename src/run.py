# custom
from personality_test_system import app, PORT


if __name__ == '__main__':
    app.run(threaded=True, port=PORT)  # threaded=True for multiple user access
