# std
from typing import List
from pytest import fixture
from _pytest.monkeypatch import MonkeyPatch
# 3rd party
from mock import patch
# custom
from test_system import util


TEST_PASSWORD = "test password"
TEST_USERNAME = "test username"

hashes = ["0"*128, "0"*128, "0"*128, "0"*128]


class IOReplacer:

    def __init__(self, inputs: List = None):
        self.inputs = iter(map(str, inputs) if inputs else [])
        self.output = ""

        self.monkeypatch = MonkeyPatch()
        self.monkeypatch.setattr('builtins.input', self.input)
        self.monkeypatch.setattr('builtins.print', self.print)

    def input(self, *args, **kwargs):
        return next(self.inputs)

    def print(self, *args, sep: str = " ", end: str = "\n", **kwargs) -> None:
        self.output += sep.join(args) + end


@fixture()
def hash_generation_io_replacer() -> IOReplacer:
    return IOReplacer(inputs=[TEST_USERNAME, TEST_PASSWORD])


def _assert_correct_password_test_hash(generated_salted_hash):
    salt, generated_hash = generated_salted_hash.split(util.HASH_SEPARATOR)
    assert len(generated_hash) == 128, f"Hash got wrong length: len(generated_hash)"
    re_generated_salted_hash = util.generate_password_hash(TEST_PASSWORD, TEST_USERNAME, salt=salt)
    assert generated_salted_hash == re_generated_salted_hash, "Re-generation of hash failed."


def test_generate_password_hash():
    generated_salted_hash = util.generate_password_hash(TEST_PASSWORD, TEST_USERNAME)
    _assert_correct_password_test_hash(generated_salted_hash)


def test__generate_password_hash_from_input(hash_generation_io_replacer):
    util._generate_password_hash_from_input()
    generated_salted_hash = hash_generation_io_replacer.output.split(":")[-1].strip()
    _assert_correct_password_test_hash(generated_salted_hash)


def test_generate_hash_token():
    hash_token = util.generate_hash_token()
    assert len(hash_token) == 128, f"Hash got wrong length: {len(hash_token)}"
    assert all(map(lambda c: c in "0123456789abcdef", hash_token)), f"Hash got wrong character: {hash_token}"


@patch("test_system.util.generate_hash_token", wraps=lambda: hashes.pop(0) if hashes else "1"*128)
def test_generate_unknown_hash_token(_):
    first_try_generation_unknown_hash_token = util.generate_unknown_hash_token(
        lambda token: token == "0" * 128, max_tries=1)
    last_try_unknown_hash_token = util.generate_unknown_hash_token(
        lambda token: token != "0" * 128, max_tries=len(hashes) + 1)

    for unknown_hash_token, expected_hash in [(first_try_generation_unknown_hash_token, "0"*128),
                                              (last_try_unknown_hash_token, "1"*128)]:
        assert len(unknown_hash_token) == 128, f"Hash got wrong length: {len(unknown_hash_token)}"
        assert all(map(lambda c: c in "0123456789abcdef", unknown_hash_token)), \
            f"Hash got wrong character: {unknown_hash_token}"
        assert unknown_hash_token == expected_hash, f"Expected hash to be {expected_hash} not {unknown_hash_token}"
