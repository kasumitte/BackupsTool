from src.hasher import get_file_hash
from src.database import init_db, save_version, get_oldest_version
from src.backup import backup_file
from src.config import Config

""" Test if all is working as it supposed to """

def test_same_content_same_hash(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("hello")
    hash1 = get_file_hash(file)
    hash2 = get_file_hash(file)
    
    assert hash1 == hash2
    
def test_changed_content_different_hash(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("hello")
    hash_before = get_file_hash(file)
    
    file.write_text("world")
    hash_after = get_file_hash(file)
    
    assert hash_before != hash_after
    
def test_save_and_get_version(tmp_path):
    db = tmp_path / "test.db"
    original_path = tmp_path / "data" / "original.txt"
    backup_path = tmp_path / "backups" / "backups.txt"
    file_hash = 'abc123'
    
    init_db(db)
    save_version(db, str(original_path), str(backup_path), file_hash, 2, 1)
    version = get_oldest_version(db, str(original_path))
    
    assert version['original_path'] == str(original_path)
    assert version['file_hash'] == file_hash

def test_backups(tmp_path):
    test_file = tmp_path / "testing.txt"
    test_file.write_text("Is it working")
    config = Config.model_construct(
        db_path = tmp_path / "tests.db",
        backup_path = tmp_path / "backups",
        log_path = tmp_path / "logs.csv",
        max_versions = 20
    )
    
    init_db(config.db_path)
    backup_file(config, str(test_file))
    backup = get_oldest_version(config.db_path, str(test_file))
    expected_backup = config.backup_path / test_file.parent.name / f"{test_file.stem}_v1{test_file.suffix}"
    
    assert expected_backup.exists()
    assert backup["original_path"] == str(test_file)
