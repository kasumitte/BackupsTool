from src.utils.logger import get_logs
from src.database import get_all_versions, get_watched_folders, remove_watched_folder, add_watched_folder
from src.watcher import find_changed_files
from src.backup import backup_file, restore_file
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from pathlib import Path
import time      
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class App:
    def __init__(self, config):
        self.config = config
        self.console = Console()
        
    def show_menu(self):
        menu = """
        [bold cyan]1 - Add watched folder[/]
        [bold cyan]2 - Remove from watched[/]
        [bold cyan]3 - Show watched folders[/]
        [bold cyan]4 - Start backup[/]
        [bold cyan]5 - Show file history[/]
        [bold cyan]6 - Restore file version[/]
        [bold cyan]7 - Show logs[/]
        [bold cyan]8 - Quit[/]
        """
        self.console.print("Backups Tool", style='bold magenta', justify='center')
        self.console.print(Panel(Align.left(menu)))
    
    def show_watched_folders(self, history: list):
        if not history:
            self.console.print("History is empty", style='bold red')
            return
        
        table = Table(title="Watched folders", header_style="bold cyan")
        table.add_column("ID", style="cyan", width=10)
        table.add_column("PATH", style="cyan", width=60)
        table.add_column("ADDED_AT", style="cyan", width=50)
        
        for row in history:
            table.add_row(
                str(row[0]),
                row[1],
                row[2]
            )
        self.console.print(table)
        
    def show_file_history(self, history: list):
        if not history:
            self.console.print("History is empty", style="bold red")
            return
        
        table = Table(title="Files history", header_style="bold magenta")
        table.add_column("ID", style="cyan", width=5)
        table.add_column("ORIGINAL_PATH", style="cyan", width=30)
        table.add_column("BACKUP_PATH", style="cyan", width=30)
        table.add_column("VERSION_NUM", style="cyan", width=10)
        table.add_column("FILE_HASH", style="cyan", width=30)
        table.add_column("FILE_SIZE", style="cyan", width=10)
        table.add_column("ADDED_AT", style="cyan", width=20)
        
        for row in history:
            table.add_row(
                str(row[0]),
                row[1],
                row[2],
                str(row[3]),
                row[4],
                str(row[5]),
                row[6]
            )
        self.console.print(table)
        
    def show_logs(self, logs: list):
        table = Table(title="Logs", header_style="cyan")
        
        table.add_column("TIMESTAMP", style="cyan", width=15)
        table.add_column("OPERATION", style="bold cyan", width=15)
        table.add_column("ORIGINAL_PATH", style="cyan", width=20)
        table.add_column("BACKUP_PATH", style="cyan", width=20)
        table.add_column("VERSION", style="cyan", width=10)
        table.add_column("FILE SIZE", style="cyan", width=10)
        table.add_column("STATUS", style="cyan", width=10)
        
        for row in logs:
            table.add_row(
                row["timestamp"],
                row["operation"],
                row["original_path"],
                row["backup_path"],
                str(row["version"]),
                str(row["file_size"]),
                row["status"]
            )
        self.console.print(table)
            
    def run(self):
        """ Main workflow """
        self.show_menu()
        while True:
            choice = input("Choose option: ").strip()
            
            match choice:
                case "1":
                    folder_path = Path(input("Enter folder path: ").strip())
                    if not folder_path.is_dir():
                        self.console.print("There is no such directory", style="bold red")
                        continue
                    
                    if add_watched_folder(self.config.db_path, folder_path):
                        self.console.print("Folder was successfully added", style="bold green")

                case "2":
                    folder_path = Path(input("Enter folder path to remove: ").strip())
                    
                    if remove_watched_folder(self.config.db_path, folder_path):
                        self.console.print("Folder was removed", style="bold green")
                    
                case "3":
                    folders = get_watched_folders(self.config.db_path)
                    self.show_watched_folders(folders)
                    
                case "4":
                    """ Backup with polling """
                    while True:
                        logger.info(f"Starting backup...")
                        all_folders = get_watched_folders(self.config.db_path)
                        
                        changed_count = 0
                        for folder in all_folders:
                            changed = find_changed_files(self.config, folder[1])
                            for file in changed:    
                                backup_file(self.config, str(file))
                                changed_count += 1
                        
                        if changed_count > 0:
                            self.console.print(f"{changed_count} files were backed up", style="bold green")
                        else:
                            self.console.print("No changes were found", style="bold red")
                                   
                        time.sleep(self.config.poll_interval)
                        
                        ask_to_continue = input("Do you want to continue Y/n: ").strip()
                        match ask_to_continue:
                            case "Y":
                                continue
                            case "n":
                                logger.info(f"Done!")
                                break
                            case _:
                                self.console.print("Wrong command", style="bold red")
                    
                case "5":
                    folder_path = Path(input("Enter folder path which to show: ").strip())
                    folders = get_all_versions(self.config.db_path, folder_path)  
                    self.show_file_history(folders)
                    
                case "6":
                    version_id = input("Enter version id to restore: ").strip()
                    if not version_id.isdigit():
                        self.console.print("Give a number", style="bold red")
                        continue
                    
                    restore_file(self.config, int(version_id))
                    self.console.print("File was restored", style="bold green")
                    
                case "7":
                    logs = get_logs(self.config.log_path)
                    if logs:
                        self.show_logs(logs)
                    
                case "8":
                    logger.info(f"Done")
                    time.sleep(2)
                    break
                
                case _:
                    self.console.print("Wrong command", style="bold red")
                