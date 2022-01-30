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
def raise_if_change_in_tables():
    """
    Fixture to get a DatabaseChangeDetector to throw an AssertionError
    in case any passed table gets an insert statement.


    E.g. trying to insert data in TableA, TableB or TableC within the following with statement will fail:

    def test_a_function(raise_if_change_in_tables):
        with raise_if_change_in_tables(TableA, TableB, TableC):
            # your test code goes here... (insert into tables will raise exception)

    :return: A DatabaseChangeDetector to be used with a "with" statement.
    """

    class DatabaseChangeDetector(ContextManager):

        IDENTIFIERS = ["after_insert", "after_update", "after_delete"]

        @staticmethod
        def _on_db_change(mapper, connection, target):
            assert False, f"Database got change for {mapper} concerning data: {target}"

        def __init__(self, *tables: db.Model):
            self.tables = tables

        def __iter__(self):
            for table in self.tables:
                for identifier in self.IDENTIFIERS:
                    yield table, identifier

        def __enter__(self):
            for table, identifier in self:
                listen(table, identifier, self._on_db_change)

        def __exit__(self, exc_type, exc_val, exc_tb):
            for table, identifier in self:
                remove(table, identifier, self._on_db_change)

    return DatabaseChangeDetector


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
