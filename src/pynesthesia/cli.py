import argparse

import pynesthesia.keygen as keygen


def hash_file(argv=None):
    # get file path
    parser = argparse.ArgumentParser(description="calculate the SHA-256 hash of a file.")
    parser.add_argument("path", help="path to the file to hash")
    args = parser.parse_args(argv)

    # hash file
    digest = keygen.generate_file_hash(args.path)

    # print hash if the file was read
    if digest is not None:
        print(digest)
