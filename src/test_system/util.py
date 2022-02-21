# std
from time import time
from datetime import datetime
from hashlib import sha3_512
from typing import Optional, Callable
# no relative or custom imports in this file!

PASSWORD_PEPPER = "personality_test_system berlin - user"
HASH_SEPARATOR = "#"


def generate_password_hash(clear_password: str, username: str, salt: Optional[str] = None) -> str:
    salt = salt or str(round(time() * 1000))  # time millis as salt if not passed
    advanced_password = clear_password + username + PASSWORD_PEPPER + salt
    hashed_password = str(sha3_512(advanced_password.encode()).hexdigest())
    return salt + HASH_SEPARATOR + hashed_password


def _generate_password_hash_from_input():
    username = input("Enter username: ")
    password = input("Enter password: ")
    hash_password = generate_password_hash(password, username)
    print("Hashed password:", hash_password)


def generate_hash_token() -> str:
    now = datetime.now()
    token_seed = str(now).encode()
    token_hash = sha3_512(token_seed).hexdigest()
    return token_hash


def generate_unknown_hash_token(is_known: Callable[[str], bool], max_tries: int = 2) -> str:
    for _ in range(max_tries):
        token_hash = generate_hash_token()
        if is_known(token_hash):
            return token_hash
    else:
        raise RuntimeError(f"Couldn't generate an unknown hash within {max_tries} tries.")


if __name__ == "__main__":
    _generate_password_hash_from_input()
