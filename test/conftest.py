# std
from sys import path
from os.path import join as path_join
from pytest import fixture
# 3rd party
from dotenv import load_dotenv

path.append(path_join(path[0], "../src"))  # add src directory to path to import from test_system
load_dotenv(path_join(path[0], ".env"))  # load test env variables for testing before project imports & code

# custom
from test_system import app

app.config['TESTING'] = True
