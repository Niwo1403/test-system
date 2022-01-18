# custom
from .table_models import *
from .database import _create_tables_if_not_exist, db

_create_tables_if_not_exist()  # must be run after import of models ("from .table_models import *")

# TODO: remove in production:
if db.session.query(User).first() is None:  # if no user exist, created default one
    u = User(username="admin", password="admin")
    db.session.add(u)
    db.session.commit()

if db.session.query(PersonalityTest).first() is None:  # if no user exist, created default one
    p = PersonalityTest(name="PersTest", description_json={"Test": True})
    db.session.add(p)
    db.session.commit()

if db.session.query(Token).first() is None:  # if no user exist, created default one
    t = Token(token="asdf", personality_test_name="PersTest", max_usage_count=2)
    db.session.add(t)
    db.session.commit()
