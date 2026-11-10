import argparse
from pathlib import Path

import pynesthesia.colors as colors
import pynesthesia.hashseed as hashseed
import pynesthesia.jingle as jingle


def jingle_from_file(path):
    # hash the file and create a jingle
    seed = hashseed.generate_file_hash(path)
    if seed is not None:
        song = jingle.create_jingle(seed)
        output = Path.cwd() / "jingle.mid"

        # save without replacing an existing file
        with output.open("xb") as file:
            song.save(file=file)
        print(f"jingle saved to: {output}")


def colorize_text(text):
    # print each character in its color
    print(colors.colorize(text))


def main(argv=None):
    # set up the command line options
    parser = argparse.ArgumentParser(
        description="create a midi jingle from a file.",
        epilog="jingles are saved as jingle.mid in the current directory.",
    )
    parser.add_argument("--colorize", help="text to print in color")
    commands = parser.add_subparsers(dest="command")
    jingle_parser = commands.add_parser("jingle", help="create a jingle from a file")
    jingle_parser.add_argument("path", help="absolute path to a file")
    args = parser.parse_args(argv)

    if args.colorize is not None:
        if args.command is not None:
            parser.error("choose either colorize or jingle")
        colorize_text(args.colorize)
        return

    if args.command is None:
        parser.error("choose jingle or --colorize")

    if not Path(args.path).is_absolute():
        parser.error("provide an absolute file path")

    # create the requested jingle
    try:
        jingle_from_file(args.path)
    except FileExistsError:
        parser.error("jingle.mid already exists in the current directory")
    except OSError as error:
        parser.error(f"could not save jingle: {error}")
