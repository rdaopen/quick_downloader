import json
import os
from datetime import datetime

class HistoryManager:
    def __init__(self, filename="history.json"):
        self.filename = filename
        self.history = self.load_history()

    def load_history(self):
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except:
            return []

    def add_entry(self, title, url, status, path):
        entry = {
            "title": title,
            "url": url,
            "status": status,
            "path": path,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history.insert(0, entry) # Add to top
        self.save_history()

    def save_history(self):
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.history, f, indent=4)
        except Exception as e:
            print(f"Error saving history: {e}")

    def get_history(self):
        return self.history
