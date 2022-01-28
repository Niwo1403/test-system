# custom
from test_system import util


def test_generate_hash():
    test_password = "test password"
    test_username = "test username"
    generated_salted_hash = util.generate_hash(test_password, test_username)
    salt, generated_hash = generated_salted_hash.split(util.HASH_SEPARATOR)
    re_generated_salted_hash = util.generate_hash(test_password, test_username, salt=salt)
    assert generated_salted_hash is not None, "Got empty or None response."
    assert len(generated_hash) == 128, "Hash got wrong length."
    assert generated_salted_hash == re_generated_salted_hash, "Re-generation of hash failed."
