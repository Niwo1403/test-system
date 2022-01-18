# custom
from personality_test_system import app, PORT

from sys import stderr

if __name__ == '__main__':
    print(app.root_path, file=stderr)
    app.run(threaded=True, port=PORT)  # threaded=True for multiple user access
