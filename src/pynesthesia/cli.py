import argparse
from pathlib import Path

import pynesthesia.output as output_writer
import pynesthesia.colors as colors
import pynesthesia.hashseed as hashseed
import pynesthesia.jingle as jingle


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


def colorize_text(text):
    """print each character in its color"""
    print(colors.colorize(text))


def main(argv=None):
    # set up the command line options
    parser = argparse.ArgumentParser(description="create a jingle or color text")
    parser.add_argument("--colorize", help="text to print in color")
    commands = parser.add_subparsers(dest="command")
    jingle_parser = commands.add_parser("jingle", help="create a jingle from a file")
    jingle_parser.add_argument("path", help="absolute path to a file")

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
            parser.error("choose either colorize or jingle")
        colorize_text(args.colorize)
        return

    if args.command is None:
        parser.error("choose jingle or --colorize")

    if not Path(args.path).is_absolute():
        parser.error("provide an absolute file path")

    try:
        jingle_from_file(args.path, args.measures)
    except OSError as error:
        parser.error(f"could not save jingle: {error}")
