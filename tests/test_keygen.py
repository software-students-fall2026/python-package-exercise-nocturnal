import pytest
import hashlib

from pynesthesia.keygen import generate_file_hash

def test_generate_file_hash_with_text_file(tmp_path):
    """simulate txt file"""
    file = tmp_path / "random.txt"
    random_bytes = b"random text file"

    file.write_bytes(random_bytes)
    expected_output = hashlib.sha256(random_bytes).hexdigest()

    assert generate_file_hash(file) == expected_output

def test_generate_file_hash_with_empty_file(tmp_path):
    """simulate empty file"""
    file = tmp_path / "empty_file_yo.dat"
    random_bytes = b""

    file.write_bytes(random_bytes)
    expected_output = hashlib.sha256(random_bytes).hexdigest()

    assert generate_file_hash(file) == expected_output

def test_generate_file_hash_with_exact_buffer_size(tmp_path):
    """simulate file exactly matching the 128 KB buffer size"""
    file = tmp_path / "exact_buffer.bin"
    random_bytes = b"A" * 131072

    file.write_bytes(random_bytes)
    expected_output = hashlib.sha256(random_bytes).hexdigest()

    assert generate_file_hash(file) == expected_output

def test_generate_file_hash_with_multi_chunk_large_file(tmp_path):
    """simulate large file with multiple chunks"""
    file = tmp_path / "really_large_file_bro.dat"
    random_bytes = b"B" * 350000

    file.write_bytes(random_bytes)
    expected_output = hashlib.sha256(random_bytes).hexdigest()

    assert generate_file_hash(file) == expected_output

def test_generate_file_hash_with_missing_file():
    """simulate file not found error condition"""
    filepath = "this_file_definitely_does_not_exist.xyz"

    assert generate_file_hash(filepath) is None

def test_generate_file_hash_with_permission_denied(tmp_path):
    """simulate permission error condition by reading a directory path instead of a file"""
    filepath = tmp_path

    assert generate_file_hash(filepath) is None