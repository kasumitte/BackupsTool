# Backups Tool
Backup your files, thats it

## How it works
Every specified amount of time it checks for changes by comparing current hash of files with one's that saved in database  

## Setup
> You can change settings based on your preferences in config.py (allegedly "shutil" library that i used here might not work on macos, so check if it works by using tests)

**Requirements:** Python 3.13, uv 

```bash
# 1. Install uv (if you dont have it)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install dependencies
uv sync

# 3. Run setup file
uv run setup.py
```
 

<div align="center">
    <figure style="border: 1px solid #6806a8; padding: 10px; display: inline-block;">
        <img src="assets/readme_pic.JPG" width=300 height=200>
        <figcaption align="center"><i></i></figcaption>
    </figure>    
</div>