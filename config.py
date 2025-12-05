import json
import os
import customtkinter as ctk

class ConfigManager:
    def __init__(self, filename="config.json"):
        self.filename = filename
        self.config = self.load_config()

    def load_config(self):
        default_config = {
            "default_path": os.path.join(os.path.expanduser("~"), "Downloads", "quick_downloader"),
            "theme": "System"
        }
        
        if not os.path.exists(self.filename):
            return default_config
            
        try:
            with open(self.filename, 'r') as f:
                return {**default_config, **json.load(f)}
        except:
            return default_config

    def save_config(self):
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key):
        return self.config.get(key)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()
