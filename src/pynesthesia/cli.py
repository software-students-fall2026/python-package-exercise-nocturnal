import argparse
from pathlib import Path

import pynesthesia.output as output_writer
import pynesthesia.colors as colors
import pynesthesia.hashseed as hashseed
import pynesthesia.jingle as jingle
import pynesthesia.htmlgen as htmlgen
import pynesthesia.chiptune as chiptune

def jingle_from_file(path, measures=jingle.jingle_config["measuresDefault"]):
    """create an mp3 from a file"""
    seed = hashseed.generate_file_hash(path)
    if seed is not None:
        directory = Path.cwd() / "pynesthesia" / "jingles"
        directory.mkdir(parents=True, exist_ok=True)

        # add new options to the filename here
        options = {"measures": measures}
        option_names = "_".join(f"{name}-{value}" for name, value in options.items())
        output = directory / f"{seed}_{option_names}.mp3"
        output_writer.save_mp3(seed, output, **options)
        print(f"jingle saved to: {output}")

def html_from_file(path):
    """Create an HTML fortune page from a file"""
    seed = hashseed.generate_file_hash(path)
    if seed is not None:
        cards = htmlgen.generate_cards(seed)
        directory = Path.cwd() / "pynesthesia" / "fortunes"
        directory.mkdir(parents=True, exist_ok=True)

        output = directory / f"{seed[:12]}.html"
        htmlgen.write_html(cards, output)
        print(f"HTML page saved to: {output}")

def chiptune_from_file(path, bars=4, wave="square"):
    """create a wav chiptune from a file"""
    seed = hashseed.generate_file_hash(path)
    if seed is not None:
        directory = Path.cwd() / "pynesthesia" / "chiptunes"
        directory.mkdir(parents=True, exist_ok=True)

        # the options are part of the filename, the same way the jingle does it
        output = directory / f"{seed}_bars-{bars}_wave-{wave}.wav"
        output.write_bytes(chiptune.create_chiptune(seed, bars=bars, wave_type=wave))
        print(f"chiptune saved to: {output}")

def colorize_text(text):
    """print each character in its color"""
    print(colors.colorize(text))

def run_jingle(args):
    jingle_from_file(args.path, args.measures)

def run_html(args):
    html_from_file(args.path)

def run_chiptune(args):
    chiptune_from_file(args.path, args.bars, args.wave)

def main(argv=None):
    # set up the command line options
    parser = argparse.ArgumentParser(description="create a jingle or color text")
    parser.add_argument("--colorize", help="text to print in color")
    commands = parser.add_subparsers(dest="command")\

    jingle_parser = commands.add_parser("jingle", help="create a jingle from a file")
    jingle_parser.add_argument("path", help="absolute path to a file")
    jingle_parser.set_defaults(handler = run_jingle)

    html_parser = commands.add_parser("html", help="Create a html fortune page from a file")
    html_parser.add_argument("path", help="Absolute path to a file")
    html_parser.set_defaults(handler = run_html)

    chiptune_parser = commands.add_parser("chiptune", help="create a chiptune wav from a file")
    chiptune_parser.add_argument("path", help="absolute path to a file")
    chiptune_parser.add_argument(
        "--bars", type=int, choices=range(1, 33), default=4, metavar="1-32",
        help="length in bars (default: %(default)s)",
    )
    chiptune_parser.add_argument(
        "--wave", choices=chiptune.WAVES, default="square",
        help="melody sound (default: %(default)s)",
    )
    chiptune_parser.set_defaults(handler = run_chiptune)

    # limit the jingle to five minutes
    minimum, maximum = jingle.jingle_config["measuresLimits"]
    jingle_parser.add_argument(
        "--measures", type=int, choices=range(minimum, maximum + 1),
        default=jingle.jingle_config["measuresDefault"], metavar=f"{minimum}-{maximum}",
        help="number of measures (default: %(default)s)",
    )

    args = parser.parse_args(argv)

    if args.colorize is not None:
        if args.command is not None:
            parser.error("choose either --colorize or a command")
        colorize_text(args.colorize)
        return

    if args.command is None:
        parser.error("choose a command or --colorize")

    if hasattr(args, "path") and not Path(args.path).is_absolute():
        parser.error("provide an absolute file path")

    try:
        args.handler(args)
    except OSError as error:
        parser.error(f"could not save output: {error}")
