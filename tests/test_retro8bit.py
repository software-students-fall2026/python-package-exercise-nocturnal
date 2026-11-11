import hashlib
import io
import wave

import pytest

import pynesthesia.retro8bit as retro

# two hashes that differ by one character of input
HASH = hashlib.sha256(b"nocturnal").hexdigest()
OTHER = hashlib.sha256(b"nocturnal!").hexdigest()
SEED = bytes.fromhex(HASH)


def wav_info(data):
    """open wav bytes and return (channels, sample width, sample rate, frames)"""
    with wave.open(io.BytesIO(data)) as song:
        return song.getnchannels(), song.getsampwidth(), song.getframerate(), song.getnframes()


# ---------------------------------------------------------------- note_to_freq

def test_note_to_freq_known_notes():
    """note 69 is A at 440 Hz, and every 12 notes up doubles the frequency"""
    assert retro.note_to_freq(69) == 440
    assert retro.note_to_freq(81) == 880
    assert retro.note_to_freq(57) == 220


# ---------------------------------------------------------------- tone

@pytest.mark.parametrize("wave_type", list(retro.WAVES))
def test_tone_length_and_volume(wave_type):
    """a tone has the right number of samples and never goes past its 0-15 volume"""
    samples = retro.tone(440, 0.2, wave_type, volume=12)
    assert len(samples) == int(retro.RATE * 0.2)
    assert max(abs(x) for x in samples) <= 12 / 15
    assert any(x != 0 for x in samples)


def test_tone_volume_moves_in_steps():
    """like the real chip, a pulse only uses the 16 volume levels (multiples of 1/15)"""
    samples = retro.tone(440, 0.2, "pulse50", volume=15)
    levels = {round(abs(x) * 15, 9) for x in samples}
    assert all(level == int(level) for level in levels)
    assert max(levels) == 15
    assert len(levels) <= 16


def test_triangle_is_stair_stepped():
    """the triangle only has a handful of fixed heights, not a smooth slope"""
    samples = retro.tone(220, 10, "triangle", volume=15)   # a long note fades slowly
    first_frame = samples[:retro.FRAME]           # so the volume is still 15 here
    assert len({round(x, 6) for x in first_frame}) <= 16
    assert max(first_frame) <= 1.0
    assert min(first_frame) >= -1.0


def test_wave_types_sound_different():
    """each pulse width and the triangle make different samples"""
    sounds = [retro.tone(440, 0.05, wave_type) for wave_type in retro.WAVES]
    for i, first in enumerate(sounds):
        for second in sounds[i + 1:]:
            assert first != second


def test_arp_changes_the_sound():
    """a chip-chord arpeggio flips the pitch, so it differs from a plain note"""
    plain = retro.tone(440, 0.1, "pulse25")
    chord = retro.tone(440, 0.1, "pulse25", arp=[0, 3, 7])
    assert plain != chord
    assert len(plain) == len(chord)
    assert plain[:retro.FRAME] == chord[:retro.FRAME]   # first frame uses jump 0, so it matches


# ---------------------------------------------------------------- make_melody / make_bass / make_rhythm

def test_melody_uses_only_the_scale():
    """16 notes, each a rest (None) or a scale note above the root"""
    root = 60
    melody = retro.make_melody(SEED, root)
    assert len(melody) == 16
    for note in melody:
        if note is not None:
            assert (note - root) % 12 in retro.MINOR_SCALE
            assert root <= note < root + 24


def test_melody_follows_another_scale():
    """passing a different scale changes which notes are allowed"""
    phrygian = retro.SCALES["phrygian"]
    melody = retro.make_melody(SEED, 60, phrygian)
    assert len(melody) == 16
    assert all((note - 60) % 12 in phrygian for note in melody if note is not None)


def test_bass_starts_at_home():
    """4 bass notes, the first is the home note one octave down"""
    bass = retro.make_bass(SEED, 60)
    assert len(bass) == 4
    assert bass[0] == 48
    assert all((note - 48) % 12 in retro.MINOR_SCALE for note in bass)


def test_rhythm_is_8_slots_starting_on():
    """8 on/off slots and the first one is always on"""
    rhythm = retro.make_rhythm(SEED)
    assert len(rhythm) == 8
    assert rhythm[0] == 1
    assert set(rhythm) <= {0, 1}


# ---------------------------------------------------------------- drum sounds

def test_kick_is_six_frames_long():
    """the kick is 6 frames of falling triangle pitch, starting loud"""
    samples = retro.kick()
    one_frame = len(retro.tone(100, retro.FRAME / retro.RATE, "triangle"))
    assert len(samples) == 6 * one_frame
    assert max(abs(x) for x in samples) <= 1.0
    assert max(abs(x) for x in samples[:one_frame]) > 0.5


def test_noise_is_always_the_same():
    """the shift register is not random: the same settings give the same noise"""
    first = retro.noise_hit(0.05, 10, clock=2)
    assert first == retro.noise_hit(0.05, 10, clock=2)
    assert len(first) == int(retro.RATE * 0.05)
    assert max(abs(x) for x in first) <= 10 / 15


def test_metallic_noise_is_different():
    """metallic mode mixes different bits, so the pattern changes"""
    normal = retro.noise_hit(0.05, 10, clock=1)
    metallic = retro.noise_hit(0.05, 10, clock=1, metallic=True)
    assert normal != metallic
    assert len(normal) == len(metallic)


# ---------------------------------------------------------------- create_retro

def test_same_hash_makes_same_tune():
    """the same hash must always give exactly the same tune"""
    first = retro.create_retro(HASH)
    assert first == retro.create_retro(HASH)
    assert len(first) > 0


def test_different_hashes_make_different_tunes():
    """a tiny change in the input gives a different tune"""
    assert retro.create_retro(HASH) != retro.create_retro(OTHER)


def test_output_is_8_bit_wav():
    """the bytes open as a mono 8-bit wav at the module's sample rate"""
    channels, width, rate, frames = wav_info(retro.create_retro(HASH))
    assert channels == 1
    assert width == 1
    assert rate == retro.RATE
    assert frames > 0


@pytest.mark.parametrize("bars, bpm", [(1, 60), (4, 150), (7, 240)])
def test_length_matches_bars_and_bpm(bars, bpm):
    """length = bars x 8 eighth notes x samples per eighth note"""
    *_, frames = wav_info(retro.create_retro(HASH, bpm=bpm, bars=bars))
    eighth_len = int(retro.RATE * 60 / bpm / 2)
    assert frames == eighth_len * 8 * bars


def test_hash_picks_tempo_between_135_and_165():
    """without bpm, the song length matches a tempo of 135-165 picked by hash byte 1"""
    bpm = 135 + SEED[1] % 31
    *_, frames = wav_info(retro.create_retro(HASH))
    assert 135 <= bpm <= 165
    assert frames == int(retro.RATE * 60 / bpm / 2) * 8 * 4


def test_options_change_the_tune():
    """bpm, bars and wave_type each change the result"""
    base = retro.create_retro(HASH, bpm=140, bars=2, wave_type="pulse25")
    assert retro.create_retro(HASH, bpm=150, bars=2, wave_type="pulse25") != base
    assert retro.create_retro(HASH, bpm=140, bars=3, wave_type="pulse25") != base
    assert retro.create_retro(HASH, bpm=140, bars=2, wave_type="triangle") != base


@pytest.mark.parametrize("bad_hash", ["", "abc", "zz" * 32, "00" * 31, "00" * 33])
def test_rejects_bad_hashes(bad_hash):
    """anything that is not a 64-character hex sha-256 hash raises ValueError"""
    with pytest.raises(ValueError):
        retro.create_retro(bad_hash)


@pytest.mark.parametrize("options", [
    {"bpm": 59},
    {"bpm": 241},
    {"bars": 0},
    {"wave_type": "square"},
])
def test_rejects_bad_options(options):
    """out-of-range or unknown options raise ValueError"""
    with pytest.raises(ValueError):
        retro.create_retro(HASH, **options)


# ---------------------------------------------------------------- save_retro

def test_save_writes_the_tune(tmp_path):
    """the saved file contains exactly the tune create_retro makes"""
    target = tmp_path / "tune.wav"
    result = retro.save_retro(HASH, target, bars=1)
    assert result == target
    assert target.exists()
    assert target.read_bytes() == retro.create_retro(HASH, bars=1)


def test_save_does_not_replace_a_file(tmp_path):
    """an existing file is never overwritten"""
    target = tmp_path / "tune.wav"
    target.write_bytes(b"keep me")
    with pytest.raises(FileExistsError):
        retro.save_retro(HASH, target, bars=1)
    assert target.read_bytes() == b"keep me"


def test_save_with_bad_hash_writes_nothing(tmp_path):
    """a bad hash raises ValueError and no file is created"""
    target = tmp_path / "tune.wav"
    with pytest.raises(ValueError):
        retro.save_retro("not a hash", target)
    assert not target.exists()
