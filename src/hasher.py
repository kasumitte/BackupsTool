import hashlib
from pathlib import Path

def get_file_hash(file_path: Path, chunk_size=8192) -> str:
    """ Getting file hash for comparing them """
    
    hasher = hashlib.md5()
    with open(file_path, 'rb') as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()
