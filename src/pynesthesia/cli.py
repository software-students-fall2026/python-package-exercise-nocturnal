import argparse

from .keygen import generate_file_hash


def main(argv=None):
    # get file path
    parser = argparse.ArgumentParser(description="calculate the SHA-256 hash of a file.")
    parser.add_argument("path", help="path to the file to hash")
    args = parser.parse_args(argv)

    # hash file
    digest = generate_file_hash(args.path)
    if digest is None:
        return 1

    # print hash
    print(digest)
    return 0
