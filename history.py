import json
import os
from datetime import datetime

HISTORY_FILE = "download_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(channel_name, folder, count):
    history = load_history()
    history.append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "channel": channel_name,
        "folder": folder,
        "files": count
    })
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)
