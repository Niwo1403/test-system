# custom
from .table_models import *
from .database import _create_tables_if_not_exist, db

_create_tables_if_not_exist()  # must be run after import of models ("from .table_models import *")

# TODO: remove in production:
if db.session.query(User).first() is None:  # if no user exist, assume database is empty & create development examples
    u = User(username="admin", password="admin")
    p = PersonalityTest(name="PersTest", description_json={"Test": True})
    t = Token(token="asdf", personality_test_names=["UnknownTest", "PersTest"], max_usage_count=2)
    db.session.add_all((u, p, t))
    db.session.commit()
