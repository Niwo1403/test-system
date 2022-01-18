# custom
from .table_models import *
from .database import _create_tables_if_not_exist

_create_tables_if_not_exist()  # must be run after import of models ("from .table_models import *")
