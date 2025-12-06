import customtkinter as ctk
from tkinter import filedialog
import os
from utils import resource_path

class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent, config_manager, callback):
        super().__init__(parent, fg_color=("#F5F5F5", "#1a1a1a"))
        self.config_manager = config_manager
        self.callback = callback
        self.title("Settings")
        self.geometry("400x250")
        self.resizable(False, False)
        
        # Set icon
        self.icon_path = resource_path("icon.ico")
        if os.path.exists(self.icon_path):
            try:
                self.after(200, lambda: self.iconbitmap(self.icon_path))
            except Exception as e:
                print(f"Could not set icon: {e}")

        # Make modal
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        
        # Center
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def create_widgets(self):
        self.grid_columnconfigure(1, weight=1)
        
        # Default Path
        ctk.CTkLabel(self, text="Default Path:", text_color=("gray10", "gray90")).grid(row=0, column=0, padx=10, pady=(20, 5), sticky="e")
        self.path_entry = ctk.CTkEntry(self)
        self.path_entry.grid(row=0, column=1, padx=(10, 5), pady=(20, 5), sticky="ew")
        self.path_entry.insert(0, self.config_manager.get("default_path"))
        
        ctk.CTkButton(self, text="...", width=30, command=self.browse_path).grid(row=0, column=2, padx=(0, 10), pady=(20, 5))

        # Theme
        ctk.CTkLabel(self, text="Theme:", text_color=("gray10", "gray90")).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.theme_var = ctk.StringVar(value=self.config_manager.get("theme"))
        self.theme_menu = ctk.CTkOptionMenu(self, variable=self.theme_var, values=["System", "Dark", "Light"])
        self.theme_menu.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=30)
        
        ctk.CTkButton(btn_frame, text="Save", command=self.save_settings).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancel", fg_color="red", border_width=1, command=self.destroy).pack(side="left", padx=10)

    def browse_path(self):
        path = filedialog.askdirectory()
        if path:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, path)

    def save_settings(self):
        self.config_manager.set("default_path", self.path_entry.get())
        self.config_manager.set("theme", self.theme_var.get())
        self.callback()
        self.destroy()

class AddDownloadDialog(ctk.CTkToplevel):
    def __init__(self, parent, callback, default_path):
        super().__init__(parent, fg_color=("#F5F5F5", "#1a1a1a"))
        self.callback = callback
        self.default_path = default_path
        self.title("Add Download")
        self.geometry("500x350")
        self.resizable(False, False)
        
        # Set icon
        self.icon_path = resource_path("icon.ico")
        if os.path.exists(self.icon_path):
            try:
                self.after(200, lambda: self.iconbitmap(self.icon_path))
            except Exception as e:
                print(f"Could not set icon: {e}")
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def create_widgets(self):
        self.grid_columnconfigure(1, weight=1)
        
        # URL
        ctk.CTkLabel(self, text="Address:", text_color=("gray10", "gray90")).grid(row=0, column=0, padx=10, pady=(20, 5), sticky="e")
        self.url_entry = ctk.CTkEntry(self, width=350)
        self.url_entry.grid(row=0, column=1, padx=10, pady=(20, 5), sticky="ew")
        
        # Auto-paste
        try:
            self.url_entry.insert(0, self.clipboard_get())
        except:
            pass

        # Path
        ctk.CTkLabel(self, text="Save to:", text_color=("gray10", "gray90")).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.path_entry = ctk.CTkEntry(self)
        self.path_entry.grid(row=1, column=1, padx=(10, 5), pady=5, sticky="ew")
        self.path_entry.insert(0, self.default_path)
        
        ctk.CTkButton(self, text="...", width=30, command=self.browse_path).grid(row=1, column=2, padx=(0, 10), pady=5)

        # Settings Frame
        settings_frame = ctk.CTkFrame(self, fg_color="transparent")
        settings_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        
        # Format
        ctk.CTkLabel(settings_frame, text="Format:", text_color=("gray10", "gray90")).pack(side="left", padx=5)
        self.format_var = ctk.StringVar(value="Video")
        self.format_switch = ctk.CTkSegmentedButton(settings_frame, values=["Video", "Audio"], variable=self.format_var, command=self.update_quality_options)
        self.format_switch.pack(side="left", padx=5)
        
        # Quality
        ctk.CTkLabel(settings_frame, text="Quality:", text_color=("gray10", "gray90")).pack(side="left", padx=(15, 5))
        self.quality_var = ctk.StringVar(value="Best")
        self.quality_menu = ctk.CTkOptionMenu(settings_frame, variable=self.quality_var, values=["Best", "4K", "1080p", "720p", "480p"])
        self.quality_menu.pack(side="left", padx=5)
        
        # Playlist
        self.playlist_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self, text="Download Playlist", variable=self.playlist_var, text_color=("gray10", "gray90")).grid(row=3, column=1, padx=10, pady=5, sticky="w")

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=20)
        
        ctk.CTkButton(btn_frame, text="Start Download", command=self.start_download).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancel", fg_color="red", border_width=1, command=self.destroy).pack(side="left", padx=10)

    def browse_path(self):
        path = filedialog.askdirectory()
        if path:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, path)

    def update_quality_options(self, value):
        if value == "Video":
            self.quality_menu.configure(values=["Best", "4K", "1080p", "720p", "480p"])
            self.quality_var.set("Best")
        else:
            self.quality_menu.configure(values=["Best", "High (320kbps)", "Medium (192kbps)", "Low (128kbps)"])
            self.quality_var.set("Best")

    def start_download(self):
        url = self.url_entry.get()
        path = self.path_entry.get()
        
        if not url:
            return
            
        data = {
            "url": url,
            "path": path,
            "format": self.format_var.get(),
            "quality": self.quality_var.get(),
            "playlist": self.playlist_var.get()
        }
        self.callback(data)
        self.destroy()
