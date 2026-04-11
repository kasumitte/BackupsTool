from src.config import Config
from src.app import App
from src.database import init_db

def main():
    config = Config.load_config()
    init_db(config.db_path)
    app = App(config=config)
    app.run()
    
if __name__ == "__main__":
    main()