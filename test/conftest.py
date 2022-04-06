# std
from sys import path
from os.path import join as path_join, realpath, dirname
from typing import ContextManager, Optional, Callable
from datetime import datetime
# 3rd party
from pytest import fixture
from dotenv import load_dotenv
from sqlalchemy.event import listen, remove

FILE_DIR = dirname(realpath(__file__))
path.append(path_join(FILE_DIR, "../src"))  # add src directory to path to import from test_system
load_dotenv(path_join(FILE_DIR, ".env"), override=True)  # load test env variables for testing before project imports & code

# custom
from test_system import app  # must not be at top of file
from test_system.constants import PRE_COLLECT_TESTS_KEY
from test_system.models import db, Token, Test, TestAnswer

app.config['TESTING'] = True


@fixture()
def test_names():
    return {
        Test.CATEGORIES.PERSONAL_DATA_TEST.name: "Person",
        PRE_COLLECT_TESTS_KEY: ["PreCol", "PreCol"],
        Test.CATEGORIES.EVALUABLE_TEST.name: "PersTest"
    }


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
    Should be listed in the parameters of all tests, which interact with the database in any way!
    
    Creates a temporary database session for testing.
    Can be used to add rows or commit added, deleted & manipulated rows
    without actually changing the database after it.

    The database session commits will automatically be rolled back,
    after the test. The changes won't be present, in an other test.
    """
    connection = db.engine.connect()
    transaction = connection.begin()

    session = db.create_scoped_session(options={"bind": connection, "binds": {}, "expire_on_commit": False})
    db.session = session

    def teardown_db_connection():
        transaction.rollback()
        connection.close()
        session.remove()
    request.addfinalizer(teardown_db_connection)

    return session


@fixture()
def username():
    return "admin"


@fixture()
def password():
    return "admin"


@fixture()
def create_token(session, test_names) -> Callable:
    def _create_token(usages: Optional[int] = None, expires: bool = True) -> Token:
        token = Token.generate_token(usages,
                                     test_names[Test.CATEGORIES.PERSONAL_DATA_TEST.name],
                                     test_names[PRE_COLLECT_TESTS_KEY],
                                     test_names[Test.CATEGORIES.EVALUABLE_TEST.name],
                                     expires=expires)
        session.add(token)
        session.commit()
        return token
    return _create_token


@fixture()
def token(create_token) -> Token:
    return create_token(usages=10)


@fixture()
def no_use_token(create_token) -> Token:
    return create_token(usages=0)


@fixture()
def expired_token(session, create_token) -> Token:
    expired_token = create_token(usages=None)
    expired_token.creation_timestamp = datetime(1000, 1, 20)
    session.commit()
    return expired_token


@fixture()
def unlimited_token(create_token) -> Token:
    return create_token(usages=None, expires=False)


@fixture()
def unknown_token_name() -> str:
    return "UNKNOWN TOKEN"


@fixture()
def personal_data_test_name(test_names):
    return test_names[Test.CATEGORIES.PERSONAL_DATA_TEST.name]


@fixture()
def personal_data_test(personal_data_test_name) -> Test:
    return Test.query.filter_by(name=personal_data_test_name).first()


@fixture()
def personal_data_answer(session, personal_data_test) -> TestAnswer:
    personal_data_answer = TestAnswer(answer_json={"name": "TestName", "age": 33, "gender": "d"},
                                      test_name=personal_data_test.name)
    session.add(personal_data_answer)
    session.commit()
    return personal_data_answer


@fixture()
def pre_collect_test() -> Test:
    return Test.query.filter_by(name="PreCol").first()


@fixture()
def evaluable_test() -> Test:
    return Test.query.filter_by(name="PersTest").first()
