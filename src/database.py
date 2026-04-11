import sqlite3
from datetime import datetime
from pathlib import Path
import logging
""" Versions control """

def init_db(db_path: Path):
    with sqlite3.connect(db_path) as db:
        db.execute(""" CREATE TABLE IF NOT EXISTS watched_folders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT UNIQUE,
            added_at TIMESTAMP) """)
        db.execute(""" CREATE TABLE IF NOT EXISTS versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_path TEXT,
            backup_path TEXT,
            version_num INTEGER,
            file_hash TEXT,
            file_size INTEGER,
            added_at TIMESTAMP) """)
        db.commit()

        
def add_watched_folder(db_path: Path, folder_path: Path):    
    try:
        with sqlite3.connect(db_path) as db:
            db.execute(""" INSERT INTO watched_folders(path, added_at) VALUES (?, ?)""",
                   (str(folder_path), datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            db.commit()
            return True
    
    except sqlite3.IntegrityError:
        logging.warning(f"Path is already in database")
        return False
    except sqlite3.Error:
        logging.error(f"Database error")
        return False
        
def get_watched_folders(db_path: Path):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(""" SELECT * FROM watched_folders ORDER BY added_at DESC LIMIT 40 """)
        return cursor.fetchall()

def get_last_version(db_path: Path, original_path: str):
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(""" SELECT * FROM versions
                              WHERE original_path = ?
                              ORDER BY version_num DESC
                              LIMIT 1 """, 
                              (original_path,))
        row = cursor.fetchone()
        return dict(row) if row is not None else None
    
def save_version(db_path: Path, original_path: str, backup_path: str, file_hash: str, file_size: float, version_num: int):
    with sqlite3.connect(db_path) as conn:
        conn.execute(""" INSERT INTO versions 
                     (original_path, backup_path, file_hash, file_size, version_num, added_at) VALUES (?, ?, ?, ?, ?, ?)""", 
                     (original_path, backup_path, file_hash, file_size, version_num, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        
def get_all_versions(db_path: Path, original_path: Path):                
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(""" SELECT * FROM versions 
                              WHERE original_path = ? 
                              ORDER BY added_at DESC LIMIT 40""", (str(original_path),))
        return cursor.fetchall()
    
def remove_watched_folder(db_path: Path, folder_path: Path):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(""" DELETE FROM watched_folders WHERE path = ? """, (str(folder_path),))
        if cursor.rowcount == 0:
            logging.info(f"No such directory was found")
            return False
        conn.commit()
        return True

def get_version_by_id(db_path: Path, version_id: int):
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(""" SELECT * FROM versions WHERE id = ? """, (version_id,))
        row = cursor.fetchone()
        return dict(row) if row is not None else None

def get_oldest_version(db_path: Path, original_path: str):
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(""" SELECT * FROM versions 
                     WHERE original_path = ?
                     ORDER BY version_num ASC LIMIT 1 """, (original_path,))
        row = cursor.fetchone()
        return dict(row) 

def delete_version(db_path: Path, version_id: int):
    with sqlite3.connect(db_path) as conn:
        conn.execute(""" DELETE FROM versions WHERE id = ? """, (version_id,))
        conn.commit()
        