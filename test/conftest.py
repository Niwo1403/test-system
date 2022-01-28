# std
from sys import path
from os.path import join as path_join, realpath, dirname
from pytest import fixture
# 3rd party
from dotenv import load_dotenv

FILE_DIR = dirname(realpath(__file__))
path.append(path_join(FILE_DIR, "../src"))  # add src directory to path to import from test_system
load_dotenv(path_join(FILE_DIR, ".env"), override=True)  # load test env variables for testing before project imports & code

# custom
from test_system import app  # must not be at top of file

app.config['TESTING'] = True
