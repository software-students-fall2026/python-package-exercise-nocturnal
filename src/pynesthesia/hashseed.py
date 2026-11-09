import sys
import hashlib

def generate_file_hash(filepath: str) -> str | None:
    """Return the file's SHA-256 hash, or None if it cannot be read.

    Reads the file in chunks to limit memory use.
    """
    buffer_size = 131072 # 128 KB buffer
    sha256 = hashlib.sha256()

    try:
        # open file in binary mode to read raw bytes
        with open(filepath, 'rb') as file:
            while True:
                chunk = file.read(buffer_size)

                # file end reached when chunk is empty
                if not chunk:
                    break

                # chunk fed into hash state
                sha256.update(chunk)

        return sha256.hexdigest()
    
    except Exception as e:
        print(f"Error processing file: {e}")
        return None