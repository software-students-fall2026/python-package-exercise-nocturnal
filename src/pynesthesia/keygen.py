import mido


def create_jingle(seed_hash: str) -> mido.MidiFile:
    """turn a sha-256 hash into a short piano melody"""
    seed = bytes.fromhex(seed_hash)
    if len(seed) != 32:
        raise ValueError("expected a sha-256 hash")

    # use notes from a fixed scale
    scale = [60, 63, 65, 67, 70, 72, 75, 77]

    # create a midi file with one track
    song = mido.MidiFile(type=0)
    track = mido.MidiTrack()
    song.tracks.append(track)

    # use the piano instrument
    track.append(mido.Message("program_change", program=0))

    # choose one note for each byte in the hash
    for value in seed:
        note = scale[value % len(scale)]
        # start the note, then stop it after one beat
        track.append(mido.Message("note_on", note=note, velocity=64))
        track.append(mido.Message("note_off", note=note, time=song.ticks_per_beat))

    return song
