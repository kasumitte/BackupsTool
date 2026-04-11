from pathlib import Path
from datetime import datetime
import logging
import csv

def log_operation(log_path: Path, operation: str, original_path: str, backup_path: str, version: int, file_size: float, status: str):
    file_exists = log_path.exists()
    
    with open(log_path, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        if not file_exists:
            writer.writerow(['timestamp', 'operation', 'original_path', 'backup_path', 'version', 'file_size', 'status'])
            
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            operation,
            original_path,
            backup_path,
            version,
            round(file_size, 2),
            status
        ])

def get_logs(log_path: Path):
    if not log_path.exists():
        logging.error(f"There is no logs so far")
        return
    
    with open(log_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return list(reader)
