# std
from time import time
from hashlib import sha3_512
from typing import Optional
# custom
from personality_test_system.models.database import db
from personality_test_system.constants import PASSWORD_PEPPER, HASH_SEPARATOR


class User(db.Model):
    __tablename__ = "user"

    username = db.Column(db.String, primary_key=True)
    password = db.Column(db.String)

    @staticmethod
    def generate_hash(clear_password: str, username: str, salt: Optional[str] = None) -> str:
        salt = salt or str(round(time() * 1000))  # time millis as salt if not passed
        advanced_password = clear_password + username + PASSWORD_PEPPER + salt
        hashed_password = str(sha3_512(advanced_password.encode()).hexdigest())
        return salt + HASH_SEPARATOR + hashed_password

    def __init__(self, /, **kwargs):
        if "password" in kwargs and "username" in kwargs:
            kwargs["password"] = self.generate_hash(kwargs["password"], kwargs["username"])
        super(User, self).__init__(**kwargs)

    def __repr__(self):
        return f"{self.username}: {self.password}"

    def validate_password(self, test_password: str):
        salt = self.password.split(HASH_SEPARATOR)[0]
        hashed_test_password = self.generate_hash(test_password, self.username, salt)
        return hashed_test_password == self.password
