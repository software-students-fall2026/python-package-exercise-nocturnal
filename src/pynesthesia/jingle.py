import json
import random
import struct
from pathlib import Path

import tones
from tones.mixer import Mixer


config_file = Path(__file__).with_name("jingleConfig.json")
jingle_config = json.loads(config_file.read_text(encoding="utf-8"))


def frequency(note):
    """convert a note number to frequency"""
    return 440 * 2 ** ((note - 69) / 12)


def create_mixer(waveform, attack, decay, vibrato):
    """prepare the melody and backing tracks"""
    # mixer example grabbed from this url: https://github.com/eriknyquist/tones#example
    mixer = Mixer(jingle_config["sampleRate"], 0.8)
    mixer.create_track(0, waveform, attack=attack, decay=decay, vibrato_frequency=5.0, vibrato_variance=vibrato)

    # play the backing tracks together
    for track in range(1, 5):
        mixer.create_track(track, tones.SINE_WAVE, attack=0.01, decay=0.08)

    return mixer


def add_melody(mixer, choices, rhythm, notes, root_note, chord_root, seconds_per_beat, final_measure):
    """choose and play the melody notes"""
    for index, note_beats in enumerate(rhythm):
        # end on the starting note
        final_note = final_measure and index == len(rhythm) - 1
        note = root_note if final_note else chord_root + choices.choice(notes)
        # pitch bend example grabbed from this url: https://github.com/eriknyquist/tones#example
        # gently bend some notes upward
        bend = not final_note and choices.randrange(5) == 0
        end_frequency = frequency(note + 1) if bend else None

        # leave a small gap after each note
        mixer.add_tone(0, frequency(note), note_beats * seconds_per_beat * 0.95, endfrequency=end_frequency)
        mixer.add_silence(0, note_beats * seconds_per_beat * 0.05)


def add_harmony(mixer, notes, chord_root, seconds_per_beat):
    """play a chord under the melody"""
    for track, index in enumerate([0, 2, 4], start=1):
        note = chord_root - 12 + notes[index]
        mixer.add_tone(track, frequency(note), 4 * seconds_per_beat, amplitude=0.4)


def add_bass(mixer, chord_root, seconds_per_beat):
    """play two low notes per measure"""
    for _ in range(2):
        mixer.add_tone(4, frequency(chord_root - 24), min(0.27, 2 * seconds_per_beat), amplitude=0.7)
        mixer.add_silence(4, max(0, 2 * seconds_per_beat - 0.27))


def finish_measure(mixer, measure, seconds_per_beat, final_measure):
    """mix the tracks and prepare audio bytes"""
    # keep each measure the right length
    start = round(measure * jingle_config["beatsPerMeasure"] * seconds_per_beat * jingle_config["sampleRate"])
    end = round((measure + 1) * jingle_config["beatsPerMeasure"] * seconds_per_beat * jingle_config["sampleRate"])
    sample_count = end - start
    samples = list(mixer.mix())[:sample_count]
    samples.extend([0.0] * (sample_count - len(samples)))

    # fade the final measure into silence
    if final_measure:
        fade_samples = min(len(samples), int(jingle_config["sampleRate"] * 0.35))
        for index in range(fade_samples):
            samples[-fade_samples + index] *= 1 - index / max(1, fade_samples - 1)

    # make little endian audio for mp3
    audio = [int(max(-1, min(1, sample)) * 32767) for sample in samples]
    return struct.pack(f"<{len(audio)}h", *audio)


def choose_settings(choices):
    """choose the settings for one jingle"""
    # keep the choices in this order
    keys = [
        "waveforms", "attackTimes", "decayTimes",
        "vibratoAmounts", "tempos", "scales", "rootNotes",
    ]

    return [choices.choice(jingle_config[key]) for key in keys]


def audio_blocks(seed, measures=jingle_config["measuresDefault"]):
    """make one measure of audio at a time"""
    # the same seed makes the same choices
    choices = random.Random(int(seed, 16))

    # keep these settings throughout the jingle
    waveform, attack, decay, vibrato, tempo, notes, root_note = choose_settings(choices)
    waveform = getattr(tones, waveform)
    seconds_per_beat = 60 / tempo

    for measure in range(measures):
        final_measure = measure == measures - 1
        mixer = create_mixer(waveform, attack, decay, vibrato)

        # choose a rhythm and chord for each measure
        rhythm = choices.choice(jingle_config["rhythms"])
        # return to the starting chord at the end
        chord_root = root_note if final_measure else root_note + choices.choice(notes[:-1])

        add_melody(mixer, choices, rhythm, notes, root_note, chord_root, seconds_per_beat, final_measure)
        add_harmony(mixer, notes, chord_root, seconds_per_beat)
        add_bass(mixer, chord_root, seconds_per_beat)
        yield finish_measure(mixer, measure, seconds_per_beat, final_measure)

