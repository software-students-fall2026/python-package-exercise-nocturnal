import sys
import hashlib

def generate_file_hash(filepath: str) -> str | None:
    """Returns the SHA-256 cryptographic hash of a file.

    Reads the file in binary mode using buffered chunks to handle large files 
    efficiently without consuming too much system memory.

    Args:
        filepath (str): The system path to the file which needs hashing.

    Returns:
        str: The hexadecimal representation of the SHA-256 hash if successful.
        None: If the file cannot be found, read, or opened due to an exception.
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