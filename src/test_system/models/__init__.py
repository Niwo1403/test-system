# custom
from .table_models import *
from .database import _create_tables_if_not_exist, db

_create_tables_if_not_exist()  # must be run after import of models ("from .table_models import *")

# TODO: remove in production:
if User.query.first() is None:  # if no user exist, assume database is empty & create development examples
    u = User(username="admin", password="admin")
    p = Test(name="PersTest", description_json={"Test": True}, evaluable=True)
    t = Token(token="asdf",
              max_usage_count=2,
              evaluable_test_name="PersTest",
              pre_collection_test_names=["UnknownTest", "PersTest"])
    db.session.add_all((u, p, t))
    db.session.commit()
