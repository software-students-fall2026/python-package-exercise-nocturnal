import hashlib

from pynesthesia.hashseed import generate_file_hash


def test_known_file_hash(tmp_path):
    """check a file against a known sha256 hash"""
    test_file = tmp_path / "hello_bro.txt"
    test_file.write_bytes(b"hello")

    assert generate_file_hash(test_file) == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def test_generate_file_hash(tmp_path):
    """check hashes for empty, small, and large files"""
    test_files = [
        ("empty_file_yo.dat", b""),
        ("random.txt", b"random text file"),
        ("exact_buffer.bin", b"A" * 131072),
        ("really_large_file_bro.dat", b"B" * 350000),
    ]
    for file_name, file_contents in test_files:
        test_file = tmp_path / file_name
        test_file.write_bytes(file_contents)

        assert generate_file_hash(test_file) == hashlib.sha256(file_contents).hexdigest()


def test_generate_file_hash_with_invalid_path(tmp_path):
    """check that missing files and directories cannot be hashed"""
    for path in [tmp_path / "this_file_definitely_does_not_exist.xyz", tmp_path]:
        assert generate_file_hash(path) is None