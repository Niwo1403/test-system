# custom
from .table_models import *
from .database import _create_tables_if_not_exist, db

_create_tables_if_not_exist()  # must be run after import of models ("from .table_models import *")

# TODO: remove in production:
if db.session.query(User).first() is None:  # if no user exist, created default one
    u = User(username="admin", password="admin")
    db.session.add(u)
    db.session.commit()
