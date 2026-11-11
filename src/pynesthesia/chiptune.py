"""
chiptune.py - turn a SHA-256 hash into a short, dark, fast chiptune (WAV).

A melody (with echo), a bass line, a pulsing rhythm layer, a fast arpeggio and drums
(with a crash every 4 bars). Standard library only so we preserve that classic keygen chiptune style.
credits to classic keygen music such as funky stars, EDGE, toilet story, Winamp 5.0. XM files were used to study the breakdown of melodies.

The whole idea in 3 steps:
    1. hash  -> 32 numbers from 0 to 255
    2. those numbers pick the key, the scale, the tempo, the melody, the bass, the rhythm,
       the arpeggio and the drums
    3. notes -> sound waves -> WAV bytes

The song is built on a grid of 8th notes: 8 slots per bar.
"""

import io
import math
import random
import struct
import wave
from pathlib import Path

RATE = 22050                            # sound samples per second
MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]    # the 7 notes of a minor scale (gives the dark mood)

# the scales the hash can pick from: semitone offsets above the key note, 7 notes each.
# All of them are dark; the differences in one or two notes change the flavor.
SCALES = {
    "minor":          MINOR_SCALE,                # sad / heroic, the keygen default
    "dorian":         [0, 2, 3, 5, 7, 9, 10],     # minor but cool / jazzy (that raised 6th)
    "harmonic minor": [0, 2, 3, 5, 7, 8, 11],     # dramatic, "egyptian" sounding
    "phrygian":       [0, 1, 3, 5, 7, 8, 10],     # dark and tense
}

WAVES = ["square", "triangle", "saw", "pulse"]   # the sounds the melody can use

# drum patterns: 8 slots per bar, "x" = hit, "." = nothing. The hash picks one.
DRUM_PATTERNS = [
    {"kick": "x...x...", "snare": "..x...x.", "hat": "xxxxxxxx"},   # steady rock beat
    {"kick": "x..x..x.", "snare": "..x...x.", "hat": "x.x.x.x."},   # bouncier kick
    {"kick": "x.......", "snare": "....x...", "hat": "xxxxxxxx"},   # slow half-time
    {"kick": "x....x..", "snare": "..x...x.", "hat": "x.xxx.xx"},   # broken beat
    {"kick": "x.x.x.x.", "snare": "..x...x.", "hat": ".x.x.x.x"},   # driving, off-beat hats
]

# arpeggio orders: which chord note plays on each 16th (0 = low, 1 = middle, 2 = high)
ARP_PATTERNS = [
    [0, 1, 2, 1],   # up-down
    [0, 1, 2, 2],   # climb and hold
    [2, 1, 0, 1],   # down-up
    [0, 2, 1, 2],   # zig-zag
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
        elif wave_type == "pulse":
            value = 1.0 if position < 0.25 else -1.0  # thin square: high only 1/4 of the time (nasal)
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


def make_melody(seed, root, scale=MINOR_SCALE):
    """16 melody notes picked by hash bytes 2-17. None means a rest (silence)."""
    melody = []
    for byte in seed[2:18]:
        if byte % 5 == 0:                     # about 1 in 5 notes is a rest
            melody.append(None)
        else:
            step = scale[byte % 7]            # which note of the scale
            octave = (byte // 7) % 2          # low or high octave
            melody.append(root + step + 12 * octave)
    return melody


def make_bass(seed, root, scale=MINOR_SCALE):
    """One bass note per bar for 4 bars. Bar 1 is always the home note; bytes 18-20 pick the rest."""
    bass = [root - 12]
    for byte in seed[18:21]:
        bass.append(root - 12 + scale[byte % 7])
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

    # let the hash decide the seed
    root = 57 + seed[0] % 12                    # the key: one of 12 notes (A3 ... G#4)
    if bpm is None:
        bpm = 130 + seed[1] % 31                # the tempo: 130-160 beats per minute
    scale = list(SCALES.values())[seed[24] % len(SCALES)]   # the mood: minor, dorian, harmonic minor or phrygian
    melody = make_melody(seed, root, scale)
    bass = make_bass(seed, root, scale)
    rhythm = make_rhythm(seed)
    drums = DRUM_PATTERNS[seed[22] % len(DRUM_PATTERNS)]
    arp = ARP_PATTERNS[seed[25] % len(ARP_PATTERNS)]
    rng = random.Random(seed[23:])              # "random" drum noise that is the same every time

    # the chord for each bar: the bass note plus the scale notes 2 and 4 steps above it (1st, 3rd, 5th)
    positions = [0] + [byte % 7 for byte in seed[18:21]]      # the same scale positions make_bass used
    chords = [[root - 12 + 12 * ((p + k) // 7) + scale[(p + k) % 7] for k in (0, 2, 4)] for p in positions]

    # everything sits on a grid of 8th notes (2 per beat, 8 per bar).
    eighth = 60 / bpm / 2                       # seconds per 8th note
    eighth_len = int(RATE * eighth)
    song = [0.0] * (eighth_len * 8 * bars)      # empty "tape": 8 eighth notes per bar
    lead = [0.0] * len(song)                    # the melody gets its own tape so we can add echo to it

    # the melody, one short note per 8th (60% of the slot), looping as long as the song lasts
    for i in range(8 * bars):
        note = melody[i % len(melody)]
        if note is not None:
            add_to_song(lead, i * eighth_len, tone(note_to_freq(note), eighth * 0.6, wave_type))

    # echo: add a quieter copy of the melody from a dotted 8th ago. Because the copy already
    # contains older echoes, they repeat and fade out by themselves.
    delay = eighth_len * 3 // 2
    for i in range(delay, len(lead)):
        lead[i] += 0.35 * lead[i - delay]
    add_to_song(song, 0, lead)

    # the arpeggio: the bar's chord played one note at a time, very fast (16th notes), high and quiet
    sixteenth_len = eighth_len // 2
    for bar in range(bars):
        chord = chords[bar % len(chords)]
        for step in range(16):
            note = chord[arp[step % len(arp)]] + 24
            blip = tone(note_to_freq(note), eighth / 4, "pulse", volume=0.06)
            add_to_song(song, bar * 8 * eighth_len + step * sixteenth_len, blip)

    # the bass, a short punchy note on every beat (4 per bar)
    for bar in range(bars):
        for beat in range(4):
            low_note = tone(note_to_freq(bass[bar % len(bass)]), eighth * 1.4, "triangle", volume=0.4)
            add_to_song(song, (bar * 8 + beat * 2) * eighth_len, low_note)

    # the rhythm layer: very short quiet blips of the bass note, jumping between two octaves
    for bar in range(bars):
        for slot in range(8):
            if rhythm[slot]:
                note = bass[bar % len(bass)] + (12 if slot % 2 == 0 else 24)
                pulse = tone(note_to_freq(note), eighth / 3, "square", volume=0.1)
                add_to_song(song, (bar * 8 + slot) * eighth_len, pulse)

    # the drums, following the hash-picked pattern in every bar (short, snappy hits)
    for bar in range(bars):
        if bar % 4 == 0:                        # a long crash cymbal at the start of every 4 bars
            add_to_song(song, bar * 8 * eighth_len, noise_hit(0.5, 0.12, rng))
        for slot in range(8):
            start = (bar * 8 + slot) * eighth_len
            if drums["kick"][slot] == "x":
                add_to_song(song, start, kick())
            if drums["snare"][slot] == "x":
                add_to_song(song, start, noise_hit(0.08, 0.35, rng))
            if drums["hat"][slot] == "x":
                add_to_song(song, start, noise_hit(0.02, 0.08, rng))

    # make it as loud as possible without distorting, then pack it as a WAV file
    loudest = max(abs(x) for x in song) or 1.0
    numbers = [int(x / loudest * 0.9 * 32767) for x in song]
    samples = struct.pack(f"<{len(numbers)}h", *numbers)  # "<" = little-end first (what WAV needs), "h" = 16-bit
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)                     # mono
        wav.setsampwidth(2)                     # 16-bit numbers
        wav.setframerate(RATE)
        wav.writeframes(samples)
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
