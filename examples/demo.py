from pathlib import Path

from pynesthesia import chiptune, colors, flower, hashseed, htmlgen, jingle, output

folder = Path("pynesthesia_output/demo")
folder.mkdir(parents=True, exist_ok=True)

# turn the file into a hash
seed = hashseed.generate_file_hash(__file__)
print(colors.colorize(seed))

# jingle
print(len(next(jingle.audio_blocks(seed, measures=1))))
output.save_mp3(seed, folder / "jingle.mp3", measures=4)

# chiptune
print(len(chiptune.create_chiptune(seed, bars=2)))
(folder / "chiptune.wav").unlink(missing_ok=True)  # save_chiptune won't overwrite
chiptune.save_chiptune(seed, folder / "chiptune.wav", bars=4, wave_type="saw")

# fortunes
cards = htmlgen.generate_cards(seed)
print(cards[1]["body"])
htmlgen.write_html(cards, folder / "fortunes.html")

# flower
print(flower.choose_flower(seed))
print(len(flower.render_flower_svg(seed)))
flower.svg_to_file(seed, folder / "flower.svg")

