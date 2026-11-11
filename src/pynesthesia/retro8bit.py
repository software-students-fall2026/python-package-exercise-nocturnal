"""
retro8bit.py - turn a SHA-256 hash into a full 8-bit retro game tune (8-bit WAV).

The 8-bit adaptation of chiptune.py: same idea and layout, but it plays by the rules of
an old 8-bit game console's sound chip:
    - only 4 voices: 2 pulse waves, 1 triangle wave and 1 noise channel
    - pulse waves come in 3 widths: 12.5%, 25% and 50% (thin, nasal, full)
    - the triangle is stair-stepped (16 levels), which gives it that gritty bass sound
    - volume has only 16 levels (0-15), so notes fade out in little steps
    - the WAV itself is 8-bit audio (256 loudness levels): extra crunchy

Standard library only.
"""

import io
import wave
from pathlib import Path

RATE = 22050                            # sound samples per second
FRAME = RATE // 60                      # samples per "frame": the chip's effects tick 60 times a second
MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]    # the 7 notes of a minor scale (gives the dark mood)

# the scales the hash can pick from (same dark set as chiptune.py)
SCALES = {
    "minor":          MINOR_SCALE,                # sad / heroic, the classic
    "dorian":         [0, 2, 3, 5, 7, 9, 10],     # minor but cool / jazzy
    "harmonic minor": [0, 2, 3, 5, 7, 8, 11],     # dramatic
    "phrygian":       [0, 1, 3, 5, 7, 8, 10],     # dark and tense
}

# the voices the melody can use: pulse waves by width (how long the wave stays "high"), or the triangle
WAVES = {"pulse12": 0.125, "pulse25": 0.25, "pulse50": 0.5, "triangle": None}

# drum patterns: 8 slots per bar, "x" = hit, "." = nothing. The hash picks one.
DRUM_PATTERNS = [
    {"kick": "x...x...", "snare": "..x...x.", "hat": "xxxxxxxx"},   # steady beat
    {"kick": "x..x..x.", "snare": "..x...x.", "hat": "x.x.x.x."},   # bouncy
    {"kick": "x.......", "snare": "....x...", "hat": "xxxxxxxx"},   # slow half-time
    {"kick": "x.x.x.x.", "snare": "..x...x.", "hat": ".x.x.x.x"},   # driving, off-beat hats
]


def note_to_freq(note):
    """Note number is frequency in Hz. Note 69 is the A at 440 Hz; +12 is one octave up."""
    return 440 * 2 ** ((note - 69) / 12)


def tone(freq, seconds, wave_type="pulse25", volume=12, arp=None):
    """Make one note on the sound chip.
    volume: 0-15, like the real chip. It steps down to 0 over the note (a stepped fade).
    """
    length = int(RATE * seconds)
    duty = WAVES[wave_type]
    samples = []
    phase = 0.0
    for i in range(length):
        frame = i // FRAME                                   # which 1/60 s tick we are in
        jump = arp[frame % len(arp)] if arp else 0           # chord flip for this frame (or none)
        phase = (phase + freq * 2 ** (jump / 12) / RATE) % 1.0
        if duty is None:                                     # triangle, stair-stepped into 16 levels
            value = round((4 * abs(phase - 0.5)) * 7.5) / 7.5 - 1   # 0-15 steps, then shift to -1..+1
        else:                                                # pulse: high for `duty` of each cycle
            value = 1.0 if phase < duty else -1.0
        level = round(volume * (1 - i / length))             # volume 0-15, fading in whole steps
        samples.append(value * level / 15)
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
    """8 on/off slots for the chord stabs, from the 8 bits of hash byte 21.
    The first slot is always on, so every bar starts with a chord."""
    pattern = [(seed[21] >> slot) & 1 for slot in range(8)]
    pattern[0] = 1
    return pattern


def kick():
    """Kick drum, the 8-bit way: the triangle voice dropping fast in pitch (a short 'bwoom')."""
    samples = []
    for frame, freq in enumerate([180, 120, 80, 55, 45, 40]):   # one pitch per frame, sliding down
        samples += tone(freq, FRAME / RATE, "triangle", volume=15 - 2 * frame)
    return samples


def noise_hit(seconds, volume, clock, metallic=False):
    """Snare or hi-hat from the noise voice.
    """
    length = int(RATE * seconds)
    register = 1
    tap = 6 if metallic else 1
    samples = []
    for i in range(length):
        if i % clock == 0:
            new_bit = (register & 1) ^ ((register >> tap) & 1)
            register = (register >> 1) | (new_bit << 14)
        value = 1.0 if register & 1 else -1.0
        level = round(volume * (1 - i / length))             # volume 0-15, fading in whole steps
        samples.append(value * level / 15)
    return samples


def create_retro(seed_hash, bpm=None, bars=4, wave_type="pulse25"):
    """Turn a SHA-256 hash (64 hex characters) into 8-bit WAV bytes. Same hash -> same song."""
    seed = bytes.fromhex(seed_hash)             # 64 hex characters -> 32 numbers (0-255)
    if len(seed) != 32:
        raise ValueError("expected a sha-256 hash (64 hex characters)")
    if bpm is not None and not 60 <= bpm <= 240:
        raise ValueError("bpm must be between 60 and 240")
    if bars < 1:
        raise ValueError("bars must be at least 1")
    if wave_type not in WAVES:
        raise ValueError(f"wave must be one of {list(WAVES)}")

    # let the hash pick how we want this to play out
    root = 57 + seed[0] % 12                    # the key: one of 12 notes (A3 ... G#4)
    if bpm is None:
        bpm = 135 + seed[1] % 31                # the tempo: 135-165 beats per minute (game speed)
    scale = list(SCALES.values())[seed[24] % len(SCALES)]
    melody = make_melody(seed, root, scale)
    bass = make_bass(seed, root, scale)
    rhythm = make_rhythm(seed)
    drums = DRUM_PATTERNS[seed[22] % len(DRUM_PATTERNS)]

    # the chord for each bar, as jumps above the bass note: 1st, 3rd and 5th of the scale
    positions = [0] + [byte % 7 for byte in seed[18:21]]      # the same scale positions make_bass used
    chords = [[12 * ((p + k) // 7) + scale[(p + k) % 7] - scale[p] for k in (0, 2, 4)] for p in positions]

    # everything sits on a grid of 8th notes (2 per beat, 8 per bar)
    eighth = 60 / bpm / 2                       # seconds per 8th note
    eighth_len = int(RATE * eighth)
    song = [0.0] * (eighth_len * 8 * bars)

    # voice 1 (pulse): the melody, one short note per 8th, looping as long as the song lasts
    # voice 2 (pulse): the classic 8-bit "fake echo": the same melody one 8th later, quieter and thinner
    for i in range(8 * bars):
        note = melody[i % len(melody)]
        if note is not None:
            freq = note_to_freq(note)
            add_to_song(song, i * eighth_len, tone(freq, eighth * 0.7, wave_type, volume=12))
            add_to_song(song, (i + 1) * eighth_len, tone(freq, eighth * 0.7, "pulse12", volume=4))

    # voice 2 also plays chord stabs on the rhythm slots: one note flipping through the chord every frame
    for bar in range(bars):
        for slot in range(8):
            if rhythm[slot]:
                note = bass[bar % len(bass)] + 24
                stab = tone(note_to_freq(note), eighth * 0.5, "pulse12", volume=5, arp=chords[bar % len(chords)])
                add_to_song(song, (bar * 8 + slot) * eighth_len, stab)

    # voice 3 (triangle): the bass, so low notes and its octave on every 8th
    for bar in range(bars):
        for slot in range(8):
            note = bass[bar % len(bass)] + (0 if slot % 2 == 0 else 12)
            low = tone(note_to_freq(note), eighth * 0.8, "triangle", volume=15)
            add_to_song(song, (bar * 8 + slot) * eighth_len, low)

    # voice 4 (noise) + the triangle kick: the drums, following the hash-picked seed
    for bar in range(bars):
        for slot in range(8):
            start = (bar * 8 + slot) * eighth_len
            if drums["kick"][slot] == "x":
                add_to_song(song, start, kick())
            if drums["snare"][slot] == "x":
                add_to_song(song, start, noise_hit(0.1, 10, clock=2))
            if drums["hat"][slot] == "x":
                add_to_song(song, start, noise_hit(0.03, 4, clock=1, metallic=True))

    # pack it as an 8-bit WAV file: every sample becomes one byte from 0 to 255 (128 = silence)
    loudest = max(abs(x) for x in song) or 1.0
    samples = bytes(int(128 + x / loudest * 0.9 * 127) for x in song)
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)                     # mono
        wav.setsampwidth(1)                     # 8-bit numbers: the "8-bit" in 8-bit music
        wav.setframerate(RATE)
        wav.writeframes(samples)
    return buffer.getvalue()


def save_retro(seed_hash, path, bpm=None, bars=4, wave_type="pulse25"):
    """Create the 8-bit tune and write it to `path` as a .wav file.

    Refuses to replace a file that already exists (raises FileExistsError),
    the same way save_chiptune does. Returns the path written.
    """
    path = Path(path)
    data = create_retro(seed_hash, bpm=bpm, bars=bars, wave_type=wave_type)
    with path.open("xb") as file:
        file.write(data)
    return path
