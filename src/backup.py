import shutil
import logging
from pathlib import Path
from src.config import Config
from src.database import save_version, get_last_version, get_version_by_id, get_oldest_version, delete_version
from src.hasher import get_file_hash
from src.utils.logger import log_operation

def backup_file(config: Config, original_path: str):
    original = Path(original_path)
    last = get_last_version(config.db_path, original_path)
    version_num = 1 if last is None else last["version_num"] + 1
    
    """ Check if number of versions bigger than maximum possible """
    if version_num > config.max_versions:
        oldest = get_oldest_version(config.db_path, original_path)
        Path(oldest['backup_path']).unlink()                            # Delete oldest version
        delete_version(config.db_path, oldest["id"])
        
        logging.info(f"You exceeded maximum versions limit (20):  [Oldest version was removed]")
    
    
    backup = config.backup_path / original.parent.name / f"{original.stem}_v{version_num}{original.suffix}"
    backup.parent.mkdir(parents=True, exist_ok=True)
    
    file_hash = get_file_hash(original)
    file_size = original.stat().st_size / (1024 * 1024)
    
    shutil.copy2(original, backup)                                      # Main function of copying file with its metadata
    save_version(config.db_path, str(original), str(backup), file_hash, file_size, version_num)
    
    log_operation(config.log_path, "BACKUP", original_path, str(backup), version_num, file_size, "OK")
    
    
def restore_file(config: Config, version_id: int):
    version = get_version_by_id(config.db_path, version_id)
    
    if version is None:
        logging.error(f"No such version")
        return
    
    backup_path = Path(version["backup_path"])
    original_path = Path(version["original_path"])
    file_size = version["file_size"]
    version = version["version_num"] 
    
    original_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(backup_path, original_path)
    
    log_operation(config.log_path, "RESTORE", str(original_path), str(backup_path), version, file_size, "OK")
