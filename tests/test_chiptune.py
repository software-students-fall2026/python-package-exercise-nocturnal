import hashlib
import io
import random
import wave

import pytest

import pynesthesia.chiptune as chiptune

# two hashes that differ by one character of input
HASH = hashlib.sha256(b"nocturnal").hexdigest()
OTHER = hashlib.sha256(b"nocturnal!").hexdigest()
SEED = bytes.fromhex(HASH)


def wav_info(data):
    """open wav bytes and return (channels, sample width, sample rate, frames)"""
    with wave.open(io.BytesIO(data)) as song:
        return song.getnchannels(), song.getsampwidth(), song.getframerate(), song.getnframes()


# note_to_freq

def test_note_to_freq_known_notes():
    """note 69 is A at 440 Hz, and every 12 notes up doubles the frequency"""
    assert chiptune.note_to_freq(69) == 440
    assert chiptune.note_to_freq(81) == 880
    assert chiptune.note_to_freq(57) == 220


def test_note_to_freq_goes_up_with_the_note():
    """a higher note number always means a higher frequency"""
    assert chiptune.note_to_freq(61) > chiptune.note_to_freq(60)


# tone

@pytest.mark.parametrize("wave_type", chiptune.WAVES)
def test_tone_length_and_volume(wave_type):
    """a tone has the right number of samples and never goes past its volume"""
    samples = chiptune.tone(440, 0.5, wave_type, volume=0.3)
    assert len(samples) == int(chiptune.RATE * 0.5)
    assert max(abs(x) for x in samples) <= 0.3
    assert any(x != 0 for x in samples)


def test_tone_wave_types_sound_different():
    """square, triangle and saw produce different samples"""
    square = chiptune.tone(440, 0.1, "square")
    triangle = chiptune.tone(440, 0.1, "triangle")
    saw = chiptune.tone(440, 0.1, "saw")
    assert square != triangle
    assert triangle != saw
    assert square != saw


# make_melody / make_bass / make_rhythm

def test_melody_uses_only_the_minor_scale():
    """16 notes, each a rest (None) or a minor-scale note above the root"""
    root = 60
    melody = chiptune.make_melody(SEED, root)
    assert len(melody) == 16
    for note in melody:
        if note is not None:
            assert (note - root) % 12 in chiptune.MINOR_SCALE
            assert root <= note < root + 24


def test_bass_starts_at_home():
    """4 bass notes, the first is the home note one octave down"""
    bass = chiptune.make_bass(SEED, 60)
    assert len(bass) == 4
    assert bass[0] == 48
    assert all((note - 48) % 12 in chiptune.MINOR_SCALE for note in bass)


def test_rhythm_is_8_slots_starting_on():
    """8 on/off slots and the first one is always on"""
    rhythm = chiptune.make_rhythm(SEED)
    assert len(rhythm) == 8
    assert rhythm[0] == 1
    assert set(rhythm) <= {0, 1}


# drum sounds

def test_kick_is_short_and_loud():
    """the kick lasts 0.1 seconds and starts at full strength"""
    samples = chiptune.kick()
    assert len(samples) == int(chiptune.RATE * 0.1)
    assert max(abs(x) for x in samples) <= 0.8
    assert max(abs(x) for x in samples) > 0.1


def test_noise_hit_is_repeatable_with_same_seed():
    """the same random seed gives the same noise, so songs stay identical"""
    first = chiptune.noise_hit(0.05, 0.3, random.Random(1))
    second = chiptune.noise_hit(0.05, 0.3, random.Random(1))
    assert first == second
    assert len(first) == int(chiptune.RATE * 0.05)
    assert max(abs(x) for x in first) <= 0.3


# create_chiptune

def test_same_hash_makes_same_song():
    """the same hash must always give exactly the same song"""
    first = chiptune.create_chiptune(HASH)
    assert first == chiptune.create_chiptune(HASH)
    assert len(first) > 0


def test_different_hashes_make_different_songs():
    """a tiny change in the input gives a different song"""
    assert chiptune.create_chiptune(HASH) != chiptune.create_chiptune(OTHER)


def test_output_is_a_valid_wav():
    """the bytes open as a mono 16-bit wav at the module's sample rate"""
    channels, width, rate, frames = wav_info(chiptune.create_chiptune(HASH))
    assert channels == 1
    assert width == 2
    assert rate == chiptune.RATE
    assert frames > 0


@pytest.mark.parametrize("bars, bpm", [(1, 60), (4, 145), (7, 240)])
def test_length_matches_bars_and_bpm(bars, bpm):
    """length = bars x 8 eighth notes x samples per eighth note"""
    *_, frames = wav_info(chiptune.create_chiptune(HASH, bpm=bpm, bars=bars))
    eighth_len = int(chiptune.RATE * 60 / bpm / 2)
    assert frames == eighth_len * 8 * bars


def test_hash_picks_tempo_between_130_and_160():
    """without bpm, the song length matches a tempo of 130-160 picked by hash byte 1"""
    bpm = 130 + SEED[1] % 31
    *_, frames = wav_info(chiptune.create_chiptune(HASH))
    assert 130 <= bpm <= 160
    assert frames == int(chiptune.RATE * 60 / bpm / 2) * 8 * 4


def test_options_change_the_song():
    """bpm, bars and wave_type each change the result"""
    base = chiptune.create_chiptune(HASH, bpm=140, bars=2, wave_type="square")
    assert chiptune.create_chiptune(HASH, bpm=150, bars=2, wave_type="square") != base
    assert chiptune.create_chiptune(HASH, bpm=140, bars=3, wave_type="square") != base
    assert chiptune.create_chiptune(HASH, bpm=140, bars=2, wave_type="saw") != base


@pytest.mark.parametrize("bad_hash", ["", "abc", "zz" * 32, "00" * 31, "00" * 33])
def test_rejects_bad_hashes(bad_hash):
    """anything that is not a 64-character hex sha-256 hash raises ValueError"""
    with pytest.raises(ValueError):
        chiptune.create_chiptune(bad_hash)


@pytest.mark.parametrize("options", [
    {"bpm": 59},
    {"bpm": 241},
    {"bars": 0},
    {"wave_type": "kazoo"},
])
def test_rejects_bad_options(options):
    """out-of-range or unknown options raise ValueError"""
    with pytest.raises(ValueError):
        chiptune.create_chiptune(HASH, **options)


# save_chiptune

def test_save_writes_the_song(tmp_path):
    """the saved file contains exactly the song create_chiptune makes"""
    target = tmp_path / "song.wav"
    result = chiptune.save_chiptune(HASH, target, bars=1)
    assert result == target
    assert target.exists()
    assert target.read_bytes() == chiptune.create_chiptune(HASH, bars=1)


def test_save_does_not_replace_a_file(tmp_path):
    """an existing file is never overwritten"""
    target = tmp_path / "song.wav"
    target.write_bytes(b"keep me")
    with pytest.raises(FileExistsError):
        chiptune.save_chiptune(HASH, target, bars=1)
    assert target.read_bytes() == b"keep me"


def test_save_with_bad_hash_writes_nothing(tmp_path):
    """a bad hash raises ValzueError and no file is created"""
    target = tmp_path / "song.wav"
    with pytest.raises(ValueError):
        chiptune.save_chiptune("not a hash", target)
    assert not target.exists()
