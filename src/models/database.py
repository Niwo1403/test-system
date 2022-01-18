# 3rd party
from flask_sqlalchemy import SQLAlchemy
# custom
from constants import APP_CONFIG
from app import app


app.config.update(**APP_CONFIG)

db = SQLAlchemy(app)
