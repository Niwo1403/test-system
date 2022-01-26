# custom
from .table_models import *
from .database import _create_tables_if_not_exist, db

_create_tables_if_not_exist()  # must be run after import of models ("from .table_models import *")

# TODO: remove in production:
if User.query.first() is None:  # if no user exist, assume database is empty & create development examples
    u = User(username="admin", password="admin")
    p = Test(name="PersTest", description_json={"Test": True}, test_category=Test.CATEGORIES.EVALUABLE_TEST)
    p2 = Test(name="Person", description_json={"Person": True}, test_category=Test.CATEGORIES.PERSONAL_DATA_TEST)
    p3 = Test(name="PreCol", description_json={"Pre collecting...": True}, test_category=Test.CATEGORIES.PRE_COLLECT_TEST)
    t = Token(token="asdf",
              max_usage_count=2,
              personal_data_test_name="Person",
              pre_collection_test_names=["UnknownTest", "PersTest"],
              evaluable_test_name="PersTest")
    db.session.add_all((u, p, p2, p3, t))
    db.session.commit()
