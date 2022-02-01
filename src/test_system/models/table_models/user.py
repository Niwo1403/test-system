# custom
from test_system.models.database import db
from test_system.util import generate_hash, HASH_SEPARATOR


class User(db.Model):
    __tablename__ = "user"

    username = db.Column(db.String, primary_key=True)
    password = db.Column(db.String)

    def __init__(self, /, **kwargs):
        if "password" in kwargs and "username" in kwargs:
            kwargs["password"] = generate_hash(kwargs["password"], kwargs["username"])
        super(User, self).__init__(**kwargs)

    def __repr__(self):
        return f"User {self.username}: {self.password[:25]}..."

    def validate_password(self, test_password: str):
        salt = self.password.split(HASH_SEPARATOR)[0]
        hashed_test_password = generate_hash(test_password, self.username, salt)
        return hashed_test_password == self.password
