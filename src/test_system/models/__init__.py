# custom
from .table_models import *
from .database import _create_tables_if_not_exist, db
from .default_database_data import _create_default_database_data

_create_tables_if_not_exist()  # must be run after import of models ("from .table_models import *")

if User.query.first() is None:  # if no user exist, assume database is empty & create some default data as examples
    _create_default_database_data()
