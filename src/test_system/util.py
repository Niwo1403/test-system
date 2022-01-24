# std
from time import time
from hashlib import sha3_512
from typing import Optional
# no relative or custom imports in this file!

PASSWORD_PEPPER = "personality_test_system berlin - user"
HASH_SEPARATOR = "#"


def generate_hash(clear_password: str, username: str, salt: Optional[str] = None) -> str:
    salt = salt or str(round(time() * 1000))  # time millis as salt if not passed
    advanced_password = clear_password + username + PASSWORD_PEPPER + salt
    hashed_password = str(sha3_512(advanced_password.encode()).hexdigest())
    return salt + HASH_SEPARATOR + hashed_password


def _generate_hash_from_input():
    username = input("Enter username: ")
    password = input("Enter password: ")
    hash_password = generate_hash(password, username)
    print("Hashed password:", hash_password)


if __name__ == "__main__":
    _generate_hash_from_input()
