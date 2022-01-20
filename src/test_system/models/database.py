# 3rd party
from flask_sqlalchemy import SQLAlchemy
# custom
from test_system.constants import APP_CONFIG
from test_system import app


app.config.update(**APP_CONFIG)
db = SQLAlchemy(app)


def _create_tables_if_not_exist() -> None:
    db.create_all()
    db.session.commit()
