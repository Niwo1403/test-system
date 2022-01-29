# std
from sys import path
from os.path import join as path_join, realpath, dirname
from pytest import fixture
from typing import ContextManager
# 3rd party
from dotenv import load_dotenv
from sqlalchemy.event import listen, remove

FILE_DIR = dirname(realpath(__file__))
path.append(path_join(FILE_DIR, "../src"))  # add src directory to path to import from test_system
load_dotenv(path_join(FILE_DIR, ".env"), override=True)  # load test env variables for testing before project imports & code

# custom
from test_system import app  # must not be at top of file
from test_system.models import db

app.config['TESTING'] = True


@fixture()
def client():
    """
    Used as client to simulate the sending of a requests to the flask backend.

    E.g.:

    resp = client.get(route)

    resp = client.post(route, data=data_as_str)
    """
    with app.test_client() as client:
        yield client


@fixture()
def raise_if_insert_in_tables():
    """
    Fixture to get a DatabaseInsertDetector to throw an AssertionError
    in case any passed table gets an insert statement.


    E.g. trying to insert data in TableA, TableB or TableC within the following with statement will fail:

    def test_a_function(raise_if_insert_in_tables):
        with raise_if_insert_in_tables(TableA, TableB, TableC):
            # your test code goes here... (insert into tables will raise exception)

    :return: A DatabaseInsertDetector to be used with a "with" statement.
    """

    class DatabaseInsertDetector(ContextManager):

        IDENTIFIER = "after_insert"

        @staticmethod
        def _on_db_changed(mapper, connection, target):
            assert False, f"Database got insertion for {mapper} with data: {target}"

        def __init__(self, *tables: db.Model):
            self.tables = tables

        def __enter__(self):
            for table in self.tables:
                listen(table, self.IDENTIFIER, self._on_db_changed)

        def __exit__(self, exc_type, exc_val, exc_tb):
            for table in self.tables:
                remove(table, self.IDENTIFIER, self._on_db_changed)

    return DatabaseInsertDetector


@fixture(scope='function')
def session(request):
    """
    Creates a temporary database session for testing.
    Can be used to add rows or commit added, deleted & manipulated rows
    without actually changing the database after it.

    The database session commits will automatically be rolled back,
    after the test. The changes won't be present, in an other test.
    """
    connection = db.engine.connect()
    transaction = connection.begin()

    session = db.create_scoped_session(options={"bind": connection, "binds": {}})
    db.session = session

    def teardown_db_connection():
        transaction.rollback()
        connection.close()
        session.remove()
    request.addfinalizer(teardown_db_connection)

    return session
