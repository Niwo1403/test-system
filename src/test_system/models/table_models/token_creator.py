# custom
from test_system.models.database import db
from test_system.util import generate_password_hash, HASH_SEPARATOR


class TokenCreator(db.Model):
    __tablename__ = "token_creator"

    username: db.Column = db.Column(db.String, primary_key=True)
    password: db.Column = db.Column(db.String)

    def __init__(self, /, **kwargs):
        if "password" in kwargs and "username" in kwargs:
            kwargs["password"] = generate_password_hash(kwargs["password"], kwargs["username"])
        super().__init__(**kwargs)

    def __repr__(self):
        return f"TokenCreator {self.username} (pw: ...{self.password[-10:]})"

    def is_password_valid(self, test_password: str) -> bool:
        salt = self.password.split(HASH_SEPARATOR)[0]
        hashed_test_password = generate_password_hash(test_password, self.username, salt)
        return hashed_test_password == self.password
