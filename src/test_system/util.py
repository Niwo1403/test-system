# std
from time import time
from datetime import datetime
from hashlib import sha3_512
from typing import Optional, Callable
# no relative or custom imports in this file!

PASSWORD_PEPPER = "test_systems great pepper :) ..."
HASH_SEPARATOR = "#"


def generate_password_hash(clear_password: str, username: str, salt: Optional[str] = None) -> str:
    """
    Generates a hashed password from a clear_password, username and salt.
    If no salt is passed, it will be generated using system time.
    """
    salt = salt or str(round(time() * 1000))  # time millis as salt if not passed
    advanced_password = clear_password + username + PASSWORD_PEPPER + salt
    hashed_password = str(sha3_512(advanced_password.encode()).hexdigest())
    return salt + HASH_SEPARATOR + hashed_password


def _generate_password_hash_from_input():
    """
    Used to generate a hashed password using data read from input.
    """
    username = input("Enter username: ")
    password = input("Enter password: ")
    hash_password = generate_password_hash(password, username)
    print("Hashed password:", hash_password)


def generate_hash_token() -> str:
    """
    Generate a hash token as SHA3 512 and returns it as str.
    """
    now = datetime.now()
    token_seed = str(now).encode()
    token_hash = sha3_512(token_seed).hexdigest()
    return token_hash


def generate_unknown_hash_token(is_unknown: Callable[[str], bool], max_tries: int = 2) -> str:
    """
    Tries max_tries times to create a hash token for which is_unknown (called with the token) return True.
    If a token can't be generated, a RuntimeError is raised.
    """
    for _ in range(max_tries):
        token_hash = generate_hash_token()
        if is_unknown(token_hash):
            break
    else:
        raise RuntimeError(f"Couldn't generate an unknown hash within {max_tries} tries.")
    return token_hash


if __name__ == "__main__":
    _generate_password_hash_from_input()
