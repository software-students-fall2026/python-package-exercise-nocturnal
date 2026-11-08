import sys
import hashlib

def generate_file_hash(filepath):
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

    

if __name__ == "__main__":
    TEST_FILEPATH_1 = "/Users/ajoykumarrishi/Desktop/Resume.docx"
    TEST_FILEPATH_2 = "/Users/ajoykumarrishi/Desktop/Screenshot 2026-11-04 at 09.13.21.png"
    TEST_FILEPATH_3 = "/Users/ajoykumarrishi/Desktop/SA2.pd"

    print(generate_file_hash(TEST_FILEPATH_1))
    print(generate_file_hash(TEST_FILEPATH_2))
    print(generate_file_hash(TEST_FILEPATH_3))

    