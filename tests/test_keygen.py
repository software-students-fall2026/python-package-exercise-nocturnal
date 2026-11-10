import hashlib
from io import BytesIO

import pytest
import pynesthesia.keygen as keygen


def midi_bytes(song):
    output = BytesIO()
    song.save(file=output)
    return output.getvalue()


def test_jingle_is_repeatable():
    seed = hashlib.sha256(b"same file").hexdigest()
    assert midi_bytes(keygen.create_jingle(seed)) == midi_bytes(keygen.create_jingle(seed))


def test_different_hashes_make_different_jingles():
    first = keygen.create_jingle("00" * 32)
    second = keygen.create_jingle("01" * 32)
    assert midi_bytes(first) != midi_bytes(second)


def test_jingle_uses_all_hash_bytes():
    song = keygen.create_jingle("00" * 31 + "01")
    track = song.tracks[0]
    assert track[0].type == "program_change"
    assert track[0].program == 0
    assert [message.note for message in track if message.type == "note_on"] == [60] * 31 + [63]
    assert len([message for message in track if message.type == "note_off"]) == 32


def test_jingle_requires_a_sha256_hash():
    with pytest.raises(ValueError):
        keygen.create_jingle("00")
    with pytest.raises(ValueError):
        keygen.create_jingle("not hex")
