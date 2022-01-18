# 3rd party
from flask_sqlalchemy import SQLAlchemy
# custom
from personality_test_system.constants import APP_CONFIG
from personality_test_system import app


app.config.update(**APP_CONFIG)

db = SQLAlchemy(app)
_create_tables_if_not_exist = db.metadata.create_all
