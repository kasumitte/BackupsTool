from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ValidationError
import logging
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', case_sensitive=False, extra='ignore')
    max_versions: int
    max_file_size_mb: int
    db_path: Path = BASE_DIR / "data" / "versions.db"
    log_path: Path = BASE_DIR / "data" / "actions.csv"
    backup_path: Path = BASE_DIR / "data" / "backups"
    poll_interval: int = 60
    
    @classmethod
    def load_config(cls):
        try:
            config = cls() # type: ignore
            """ Making directories for DB, logs and backups """
            config.db_path.parent.mkdir(parents=True, exist_ok=True)
            config.log_path.parent.mkdir(parents=True, exist_ok=True)
            config.backup_path.parent.mkdir(parents=True, exist_ok=True)
            return config
        except ValidationError as e:
            for error in e.errors():
                logging.error(f"Config error: [{error['msg']}]")
            time.sleep(3)
            sys.exit(1)
