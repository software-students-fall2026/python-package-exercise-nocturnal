![CI](https://github.com/software-students-fall2026/python-package-exercise-nocturnal/actions/workflows/ci.yml/badge.svg?branch=main)
![CD](https://github.com/software-students-fall2026/python-package-exercise-nocturnal/actions/workflows/cd.yml/badge.svg?branch=main)

# pynesthesia

# Description
Pynesthesia is inspired by the condition "synesthesia," which refers to when one sense triggers other senses. An example of this would be seeing colors when hearing music or being able to taste words. Our python package reads a given file's SHA-256 hash and is able to turn it into colored text, a jingle (MP3), chiptune (WAV), a page of fortune cards (HTML), or a flower drawing (SVG).  

## PyPI Page and Install

Our package is on PyPI at [pynesthesia](https://pypi.org/project/pynesthesia/)
```bash
pip install pynesthesia 
```

## How It Works
A SHA-256 hash consists of 32 numbers from 0 to 255. Each of our features use these numbers to determine qualities like tempo, notes, words, colors, and flower type. 

## Using Pynesthesia
Begin by generating a hash for a given file: 

```python
from pynesthesia import hashseed

seed = hashseed.generate_file_hash("/absolute/path/to/file.txt")
# Return the file's SHA-256 hash, or None if it cannot be read.
```

**Colored text**
```python
from pynesthesia import colors

print(colors.colorize(seed))
# add a color for each character of the text in terminal
```

**Jingle**
```python
from pathlib import Path
from pynesthesia import jingle, output

output.save_mp3(seed, Path("jingle.mp3"), measures=4)
# encode the generated electronic audio as an mp3

for block in jingle.audio_blocks(seed, measures=2):
   print(len(block))
# make one measure of audio at a time
```

**Chiptune**
```python
from pynesthesia import chiptune

wav_bytes = chiptune.create_chiptune(seed, bpm=140, bars=4, wave_type="square")
# Turn a SHA-256 hash (64 hex characters) into WAV bytes. Same hash -> same song.

chiptune.save_chiptune(seed, "chiptune.wav", bars=8, wave_type="saw")
# Create the chiptune and write it to `path` as a .wav file.
# Refuses to replace a file that already exists (raises FileExistsError).
```

**8-BIT**
```python
from pynesthesia import retro8bit

wav_bytes = retro8bit.create_retro(seed, bpm=150, bars=4, wave_type="pulse25")
# Turn a SHA-256 hash (64 hex characters) into 8-bit WAV bytes. Same hash -> same tune.

retro8bit.save_retro(seed, "retro.wav", bars=8, wave_type="pulse12")
# Create the 8-bit tune and write it to `path` as a .wav file.
# Refuses to replace a file that already exists (raises FileExistsError).
```

**Fortune cards**
```python
from pynesthesia import htmlgen

cards = htmlgen.generate_cards(seed)
htmlgen.write_html(cards, "fortunes.html")
```

**Flower**
```python
from pynesthesia import flower

species, style = flower.choose_flower(seed)
# turn a sha-256 hash into name of flower species and art style

svg_text = flower.render_flower_svg(seed)
# turn a sha-256 hash into flower drawn as svg text

flower.svg_to_file(seed, "flower.svg")
# save svg text of hash into a .svg file
```

## Example program
[examples/demo.py](examples/demo.py) uses every function above. Run it from a clone of this repo with: 
```bash
pipenv run python examples/demo.py
```

## Run from Command Line
Make sure file paths are absolute. Output can be found in the 'pynesthesia_output' folder. 

- `jingle`: create a jingle from a file
    - `--measures`: number of measures (1-112, default 8)

```bash
pynesthesia jingle /absolute/path/to/file.txt --measures 4
```

- `chiptune`: create a chiptune wav from a file
    - `--bars`: length in bars (1-32, default 4)
    - `--wave`: melody sound (square, triangle, saw or pulse; default square)
```bash
pynesthesia chiptune /absolute/path/to/file.txt --bars 8 --wave saw
```

- `html`: Create a html fortune page from a file
```bash
pynesthesia html /absolute/path/to/file.txt
```

- `--colorize`: text to print in color
```bash
pynesthesia --colorize 2cf24dba5fb0a30e
```

## Configuration

### Environment variables

pynesthesia doesn't use any environment variables.

### Starter data

pynesthesia doesn't use a database or need any starter data.

### Secret configuration files

There is no `.env` or other secret file. 

### Optional settings

Jingle tempos, scales, rhythms, sounds and length limits are in `src/pynesthesia/jingleConfig.json`.

## Contributing

- Set up:

```bash
git clone https://github.com/software-students-fall2026/python-package-exercise-nocturnal.git
cd python-package-exercise-nocturnal
pip install pipenv
pipenv install --dev
```

- Test:

```bash
pipenv run python -m pytest --cov=pynesthesia --cov-report=term-missing --cov-fail-under=100
```

- Build and check:
```bash
pipenv run python -m build
pipenv run twine check dist/*
```

## Team

- [Christina Lin](https://github.com/christinalin06)
- [Daniel Zhang](https://github.com/danielzhang04)
- [Jason Wang](https://github.com/TirpitzS128)
- [Rishi Ajoykumar](https://github.com/ajoykumarrishi)
- [Matthew Chen](https://github.com/23matthewc)
