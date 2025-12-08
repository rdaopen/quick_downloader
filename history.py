import json
import os
from datetime import datetime
from utils import get_user_data_dir

class HistoryManager:
    def __init__(self, filename="history.json"):
        self.filename = os.path.join(get_user_data_dir(), filename)
        self.history = self.load_history()

    def load_history(self):
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except:
            return []

    def add_entry(self, title, url, status, path, media_type="Unknown"):
        entry = {
            "title": title,
            "url": url,
            "status": status,
            "path": path,
            "media_type": media_type,
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

    def clear_history(self):
        self.history = []
        self.save_history()

    def remove_items(self, items_to_remove):
        # items_to_remove should be a list of entry objects
        self.history = [h for h in self.history if h not in items_to_remove]
        self.save_history()
