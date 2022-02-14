# std
from typing import List
from pytest import fixture
from _pytest.monkeypatch import MonkeyPatch
# custom
from test_system import util


class IOReplacer:

    def __init__(self, inputs: List = None):
        self.inputs = iter(map(str, inputs) if inputs else [])
        self.output = ""

        self.monkeypatch = MonkeyPatch()
        self.monkeypatch.setattr('builtins.input', self.input)
        self.monkeypatch.setattr('builtins.print', self.print)

    def input(self, *args, **kwargs):
        return next(self.inputs)

    def print(self, *args, sep: str = " ", end: str = "\n", **kwargs):
        self.output += sep.join(args) + end


TEST_PASSWORD = "test password"
TEST_USERNAME = "test username"


@fixture()
def io_replacer() -> IOReplacer:
    return IOReplacer(inputs=[TEST_USERNAME, TEST_PASSWORD])


def _assert_correct_test_hash(generated_salted_hash):
    salt, generated_hash = generated_salted_hash.split(util.HASH_SEPARATOR)
    assert len(generated_hash) == 128, "Hash got wrong length."
    re_generated_salted_hash = util.generate_hash(TEST_PASSWORD, TEST_USERNAME, salt=salt)
    assert generated_salted_hash == re_generated_salted_hash, "Re-generation of hash failed."


def test_generate_hash():
    generated_salted_hash = util.generate_hash(TEST_PASSWORD, TEST_USERNAME)
    _assert_correct_test_hash(generated_salted_hash)


def test__generate_hash_from_input(io_replacer):
    util._generate_hash_from_input()
    generated_salted_hash = io_replacer.output.split(":")[-1].strip()
    _assert_correct_test_hash(generated_salted_hash)
