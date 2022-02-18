# 3rd party
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
# custom
from test_system.constants import APP_CONFIG
from test_system import app


app.config.update(**APP_CONFIG)
db = SQLAlchemy(app)


def _create_tables_if_not_exist() -> None:
    try:
        db.create_all()
        db.session.commit()
    except IntegrityError:
        app.logger.error("IntegrityError: Failed creating database - maybe it already exists.")
        db.session.rollback()
