import lameenc

import pynesthesia.jingle as jingle


def save_mp3(seed, output, measures=jingle.jingle_config["measuresDefault"]):
    """encode the generated electronic audio as an mp3"""
    encoder = lameenc.Encoder()
    encoder.set_bit_rate(128)
    encoder.set_in_sample_rate(jingle.jingle_config["sampleRate"])
    encoder.set_channels(1)
    encoder.set_quality(2)

    # encode one measure at a time
    # this saves memory for long jingles
    with output.open("wb") as file:
        for block in jingle.audio_blocks(seed, measures):
            file.write(encoder.encode(block))
        file.write(encoder.flush())
