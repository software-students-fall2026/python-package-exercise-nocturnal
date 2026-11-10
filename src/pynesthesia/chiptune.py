"""
chiptune.py - turn a SHA-256 hash into a short, dark, fast chiptune (WAV).

A melody, a bass line, a pulsing rhythm layer and drums. Standard library only.

    from pynesthesia.hashseed import generate_file_hash
    from pynesthesia.chiptune import create_chiptune, save_chiptune

    digest = generate_file_hash("/path/to/any/file")       # 64-character hex string
    wav_bytes = create_chiptune(digest)                     # the song, as WAV bytes
    save_chiptune(digest, "song.wav", bpm=150, bars=8)      # or write it to a file

The whole idea in 3 steps:
    1. hash  -> 32 numbers from 0 to 255
    2. those numbers pick the key, the tempo, the melody, the bass, the rhythm and the drums
    3. notes -> sound waves -> WAV bytes

The song is built on a grid of 8th notes: 8 slots per bar.
"""

import io
import math
import random
import sys
import wave
from array import array
from pathlib import Path

RATE = 22050                            # sound samples per second
MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]    # the 7 notes of a minor scale (gives the dark mood)
WAVES = ["square", "triangle", "saw"]   # the sounds the melody can use

# drum patterns: 8 slots per bar, "x" = hit, "." = nothing. The hash picks one.
DRUM_PATTERNS = [
    {"kick": "x...x...", "snare": "..x...x.", "hat": "xxxxxxxx"},   # steady rock beat
    {"kick": "x..x..x.", "snare": "..x...x.", "hat": "x.x.x.x."},   # bouncier kick
    {"kick": "x.......", "snare": "....x...", "hat": "xxxxxxxx"},   # slow half-time
]


def note_to_freq(note):
    """Note number -> frequency in Hz. Note 69 is the A at 440 Hz; +12 is one octave up."""
    return 440 * 2 ** ((note - 69) / 12)


def tone(freq, seconds, wave_type="square", volume=0.3):
    """Make one note: a list of numbers that wiggle `freq` times per second."""
    length = int(RATE * seconds)
    samples = []
    for i in range(length):
        position = (i * freq / RATE) % 1.0          # where we are inside one wave cycle (0 to 1)
        if wave_type == "square":
            value = 1.0 if position < 0.5 else -1.0  # jump between high and low
        elif wave_type == "triangle":
            value = 4 * abs(position - 0.5) - 1      # slide up and down (softer sound)
        else:
            value = 2 * position - 1                 # saw: ramp up, then drop (buzzy sound)
        fade = 1 - i / length                         # get quieter towards the end of the note
        samples.append(value * volume * fade)
    return samples


def add_to_song(song, start, samples):
    """Mix a note into the song starting at position `start` (cut off anything past the end)."""
    for i, value in enumerate(samples):
        if start + i < len(song):
            song[start + i] += value


def make_melody(seed, root):
    """16 melody notes picked by hash bytes 2-17. None means a rest (silence)."""
    melody = []
    for byte in seed[2:18]:
        if byte % 5 == 0:                     # about 1 in 5 notes is a rest
            melody.append(None)
        else:
            step = MINOR_SCALE[byte % 7]      # which note of the scale
            octave = (byte // 7) % 2          # low or high octave
            melody.append(root + step + 12 * octave)
    return melody


def make_bass(seed, root):
    """One bass note per bar for 4 bars. Bar 1 is always the home note; bytes 18-20 pick the rest."""
    bass = [root - 12]
    for byte in seed[18:21]:
        bass.append(root - 12 + MINOR_SCALE[byte % 7])
    return bass


def make_rhythm(seed):
    """8 on/off slots for the pulsing rhythm layer, from the 8 bits of hash byte 21.
    The first slot is always on, so every bar starts with a pulse."""
    pattern = [(seed[21] >> slot) & 1 for slot in range(8)]
    pattern[0] = 1
    return pattern


def kick():
    """Kick drum: a low sine wave whose pitch drops fast (the 'boom')."""
    length = int(RATE * 0.1)                     # short = punchy
    samples = []
    phase = 0.0
    for i in range(length):
        fade = 1 - i / length
        phase += (50 + 100 * fade ** 3) / RATE   # pitch slides from 150 Hz down to 50 Hz
        samples.append(math.sin(2 * math.pi * phase) * fade * 0.8)
    return samples


def noise_hit(seconds, volume, rng):
    """Snare or hi-hat: a short burst of random numbers that fades out (the 'tss')."""
    length = int(RATE * seconds)
    return [rng.uniform(-1, 1) * volume * (1 - i / length) ** 2 for i in range(length)]


def create_chiptune(seed_hash, bpm=None, bars=4, wave_type="square"):
    """Turn a SHA-256 hash (64 hex characters) into WAV bytes. Same hash -> same song."""
    seed = bytes.fromhex(seed_hash)             # 64 hex characters -> 32 numbers (0-255)
    if len(seed) != 32:
        raise ValueError("expected a sha-256 hash (64 hex characters)")
    if bpm is not None and not 60 <= bpm <= 240:
        raise ValueError("bpm must be between 60 and 240")
    if bars < 1:
        raise ValueError("bars must be at least 1")
    if wave_type not in WAVES:
        raise ValueError(f"wave must be one of {WAVES}")

    # step 3: let the hash decide
    root = 57 + seed[0] % 12                    # the key: one of 12 notes (A3 ... G#4)
    if bpm is None:
        bpm = 130 + seed[1] % 31                # the tempo: 130-160 beats per minute
    melody = make_melody(seed, root)
    bass = make_bass(seed, root)
    rhythm = make_rhythm(seed)
    drums = DRUM_PATTERNS[seed[22] % len(DRUM_PATTERNS)]
    rng = random.Random(seed[23:])              # "random" drum noise that is the same every time

    # timing: everything sits on a grid of 8th notes (2 per beat, 8 per bar).
    # "Tight" = every sound is shorter than its slot, so there is a tiny gap before the next one.
    eighth = 60 / bpm / 2                       # seconds per 8th note
    eighth_len = int(RATE * eighth)
    song = [0.0] * (eighth_len * 8 * bars)      # empty "tape": 8 eighth notes per bar

    # step 4a: the melody, one short note per 8th (60% of the slot), looping as long as the song lasts
    for i in range(8 * bars):
        note = melody[i % len(melody)]
        if note is not None:
            add_to_song(song, i * eighth_len, tone(note_to_freq(note), eighth * 0.6, wave_type))

    # step 4b: the bass, a short punchy note on every beat (4 per bar)
    for bar in range(bars):
        for beat in range(4):
            low_note = tone(note_to_freq(bass[bar % len(bass)]), eighth * 1.4, "triangle", volume=0.4)
            add_to_song(song, (bar * 8 + beat * 2) * eighth_len, low_note)

    # step 4c: the rhythm layer: very short quiet blips of the bass note, jumping between two octaves
    for bar in range(bars):
        for slot in range(8):
            if rhythm[slot]:
                note = bass[bar % len(bass)] + (12 if slot % 2 == 0 else 24)
                pulse = tone(note_to_freq(note), eighth / 3, "square", volume=0.1)
                add_to_song(song, (bar * 8 + slot) * eighth_len, pulse)

    # step 4d: the drums, following the hash-picked pattern in every bar (short, snappy hits)
    for bar in range(bars):
        for slot in range(8):
            start = (bar * 8 + slot) * eighth_len
            if drums["kick"][slot] == "x":
                add_to_song(song, start, kick())
            if drums["snare"][slot] == "x":
                add_to_song(song, start, noise_hit(0.08, 0.35, rng))
            if drums["hat"][slot] == "x":
                add_to_song(song, start, noise_hit(0.02, 0.08, rng))

    # step 4e: make it as loud as possible without distorting, then pack it as a WAV file
    loudest = max(abs(x) for x in song) or 1.0
    samples = array("h", (int(x / loudest * 0.9 * 32767) for x in song))
    if sys.byteorder == "big":
        samples.byteswap()                      # WAV files store numbers little-end first
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)                     # mono
        wav.setsampwidth(2)                     # 16-bit numbers
        wav.setframerate(RATE)
        wav.writeframes(samples.tobytes())
    return buffer.getvalue()


def save_chiptune(seed_hash, path, bpm=None, bars=4, wave_type="square"):
    """Create the chiptune and write it to `path` as a .wav file.

    Refuses to replace a file that already exists (raises FileExistsError),
    the same way the CLI refuses to replace jingle.mid. Returns the path written.
    """
    path = Path(path)
    data = create_chiptune(seed_hash, bpm=bpm, bars=bars, wave_type=wave_type)
    with path.open("xb") as file:
        file.write(data)
    return path
