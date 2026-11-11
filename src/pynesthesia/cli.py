import argparse
from pathlib import Path

import pynesthesia.hashseed as hashseed
import pynesthesia.keygen as keygen
import pynesthesia.colors as colors

def hash_file(path):
    # print the hash if the file was read
    digest = hashseed.generate_file_hash(path)
    if digest is not None:
        print(digest)


def jingle_from_seed(seed):
    # create the jingle without replacing an existing file
    song = keygen.create_jingle(seed)
    output = Path.cwd() / "jingle.mid"
    with output.open("xb") as file:
        song.save(file=file)
    print(f"jingle saved to: {output}")


def jingle_from_file(path):
    # hash the file and turn the hash into a jingle
    seed = hashseed.generate_file_hash(path)
    if seed is not None:
        jingle_from_seed(seed)


def colorize_text(text): 
    # print text with a different color for each character
    print(colors.colorize(text))


def main(argv=None):
    # set up the command line options
    parser = argparse.ArgumentParser(
        description="hash a file or create a midi jingle from a file or hash.",
        epilog="file paths must be absolute. jingles are saved as jingle.mid in the current directory.",
    )
    parser.add_argument("path", nargs="?", help="absolute path to a file to hash")
    options = parser.add_mutually_exclusive_group()
    options.add_argument("--file", help="absolute path to a file to turn into a jingle")
    options.add_argument("--seed", help="sha-256 hash to turn into a jingle")
    options.add_argument("--colorize", help="text to print in color")
    args = parser.parse_args(argv)

    # check that one input was provided
    if sum(value is not None for value in (args.path, args.file, args.seed, args.colorize)) != 1:
        parser.error("provide one file path, --file, --seed, or --colorize")

    path = args.path or args.file
    if path is not None and not Path(path).is_absolute():
        parser.error("provide an absolute file path")

    # run the requested command
    try:
        if args.file is not None:
            jingle_from_file(args.file)
        elif args.seed is not None:
            jingle_from_seed(args.seed)
        elif args.colorize is not None:
            colorize_text(args.colorize)
        else:
            hash_file(args.path)
    except ValueError:
        parser.error("provide a valid sha-256 hash")
    except FileExistsError:
        parser.error("jingle.mid already exists in the current directory")
    except OSError as error:
        parser.error(f"could not save jingle: {error}")
