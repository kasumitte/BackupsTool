from pathlib import Path
from src.hasher import get_file_hash
from src.database import get_last_version
from src.config import Config
import logging

def scan_folder(folder_path: str):
    return [f for f in Path(folder_path).rglob('*') if f.is_file()]

def find_changed_files(config: Config, folder_path: str):
    changed = []
    logging.info(f"Scanning files...")
    
    for file in scan_folder(folder_path):
        current_hash = get_file_hash(file)
        last = get_last_version(config.db_path, str(file))
        
        size_mb = file.stat().st_size / (1024 * 1024)
        
        """ Check if current file bigger than maximum size """
        if size_mb > config.max_file_size_mb:
            logging.error(f"File is bigger than maximum size of file")
            continue
        
        if last is None or last["file_hash"] != current_hash:
            changed.append(file)
            
    return changed
