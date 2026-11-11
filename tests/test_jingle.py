import random
import pynesthesia.jingle as jingle
from pynesthesia.jingle import jingle_config


def test_jingle_is_repeatable():
    """check that the same seed produces the same jingle"""
    seed = "00" * 32
    first_jingle = list(jingle.audio_blocks(seed, measures=2))
    second_jingle = list(jingle.audio_blocks(seed, measures=2))

    assert first_jingle == second_jingle
    assert any(first_jingle[0])


def test_different_hashes_make_different_jingles():
    """check that changes throughout the hash affect the music"""
    first = list(jingle.audio_blocks("00" * 32, measures=2))
    second = list(jingle.audio_blocks("00" * 31 + "01", measures=2))

    assert first != second


def test_measures_set_jingle_length():
    """check that more measures make more music"""
    blocks = list(jingle.audio_blocks("02" * 32, measures=3))

    assert len(blocks) == 3
    assert all(any(block) for block in blocks)
    assert blocks[0] != blocks[1]


def test_rhythm_lengths():
    """check that each rhythm fills its measure"""
    for rhythm in jingle_config["rhythms"]:
        assert sum(rhythm) == jingle_config["beatsPerMeasure"]

def test_valid_scales(): 
    """check that every scale is a valid scale (ends an octave up)"""
    for scale in jingle_config["scales"]: 
        assert scale[0] == 0
        assert scale[-1] == 12
        assert scale == sorted(scale)

def test_tempo_speed(): 
    """check that every tempo is a reasonable speed"""
    for tempo in jingle_config["tempos"]: 
        assert 60 <= tempo <= 200

def test_settings_in_config(): 
    """check that the chosen settings are vaild"""
    settings = jingle.choose_settings(random.Random(0))
    waveform, attack, decay, vibrato, tempo, scale, root_note = settings

    assert tempo in jingle_config["tempos"]
    assert scale in jingle_config["scales"]
    assert root_note in jingle_config["rootNotes"]

