import customtkinter as ctk
import os
import sys
import time
import subprocess
from tkinter import filedialog, Menu
from downloader import MediaDownloader
from history import HistoryManager

# Helper function for PyInstaller resource paths
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Set theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Quick Media Downloader")
        self.geometry("800x600")
        self.minsize(700, 500)
        
        # Set icon
        icon_path = resource_path("icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception as e:
                print(f"Could not set icon: {e}")    

        # Initialize History
        self.history_manager = HistoryManager()

        # Initialize Downloader
        ffmpeg_path = resource_path("ffmpeg")
        if not os.path.exists(ffmpeg_path):
            ffmpeg_path = None
        
        self.downloader = MediaDownloader(ffmpeg_path=ffmpeg_path)
        self.downloading = False

        self.create_layout()

    def create_layout(self):
        # Grid Configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Header
        self.grid_rowconfigure(1, weight=1) # Tabs (Main Content)
        
        # 1. Header
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="Quick Media Downloader", font=ctk.CTkFont(size=28, weight="bold"))
        self.title_label.pack(side="left")

        # 2. Tab View
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        self.tab_download = self.tab_view.add("Download")
        self.tab_history = self.tab_view.add("History")
        
        self.setup_download_tab()
        self.setup_history_tab()

    def setup_download_tab(self):
        self.tab_download.grid_columnconfigure(0, weight=1)
        self.tab_download.grid_rowconfigure(0, weight=0) # Input
        self.tab_download.grid_rowconfigure(1, weight=1) # Status/Spacer
        self.tab_download.grid_rowconfigure(2, weight=0) # Progress
        self.tab_download.grid_rowconfigure(3, weight=0) # Buttons

        # Content Frame (Input)
        self.content_frame = ctk.CTkFrame(self.tab_download, fg_color="transparent")
        self.content_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.content_frame.grid_columnconfigure(1, weight=1)

        # URL Input
        self.url_label = ctk.CTkLabel(self.content_frame, text="Media URL:", font=ctk.CTkFont(weight="bold"))
        self.url_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        self.url_entry = ctk.CTkEntry(self.content_frame, placeholder_text="Paste YouTube or other media link here...", height=35)
        self.url_entry.grid(row=0, column=1, columnspan=2, padx=10, pady=(10, 5), sticky="ew")
        
        # Right-click Paste
        self.context_menu = Menu(self, tearoff=0)
        self.context_menu.add_command(label="Paste", command=self.paste_text)
        self.url_entry.bind("<Button-3>", self.show_context_menu)

        # Output Path
        self.path_label = ctk.CTkLabel(self.content_frame, text="Save to:", font=ctk.CTkFont(weight="bold"))
        self.path_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.path_entry = ctk.CTkEntry(self.content_frame, placeholder_text="Select download folder...", height=35)
        self.path_entry.grid(row=1, column=1, padx=(10, 5), pady=5, sticky="ew")
        
        # Default Path Logic
        default_path = os.path.join(os.path.expanduser("~"), "Downloads", "quick_downloader")
        if not os.path.exists(default_path):
            try:
                os.makedirs(default_path)
            except:
                pass # Fallback to empty or current dir if permission denied
        self.path_entry.insert(0, default_path)

        self.browse_button = ctk.CTkButton(self.content_frame, text="Browse", width=80, height=35, command=self.browse_path)
        self.browse_button.grid(row=1, column=2, padx=10, pady=5)

        # Settings Row
        self.settings_label = ctk.CTkLabel(self.content_frame, text="Settings:", font=ctk.CTkFont(weight="bold"))
        self.settings_label.grid(row=2, column=0, padx=10, pady=20, sticky="nw")

        self.settings_inner_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.settings_inner_frame.grid(row=2, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

        # Format Type
        self.format_var = ctk.StringVar(value="Video")
        self.format_switch = ctk.CTkSegmentedButton(self.settings_inner_frame, values=["Video", "Audio"], variable=self.format_var, command=self.update_quality_options)
        self.format_switch.pack(side="left", padx=(0, 20))

        # Quality Selector
        self.quality_var = ctk.StringVar(value="Best")
        self.quality_menu = ctk.CTkOptionMenu(self.settings_inner_frame, variable=self.quality_var, values=["Best", "4K", "1080p", "720p", "480p"])
        self.quality_menu.pack(side="left", padx=(0, 20))

        # Playlist Checkbox
        self.playlist_var = ctk.BooleanVar(value=False)
        self.playlist_checkbox = ctk.CTkCheckBox(self.settings_inner_frame, text="Download Playlist", variable=self.playlist_var)
        self.playlist_checkbox.pack(side="left")

        # Progress Section
        self.progress_frame = ctk.CTkFrame(self.tab_download, fg_color="transparent")
        self.progress_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.progress_frame.grid_columnconfigure(0, weight=1)

        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, height=15)
        self.progress_bar.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="ew")
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(self.progress_frame, text="Ready", font=ctk.CTkFont(size=12))
        self.status_label.grid(row=1, column=0, padx=10, sticky="w")
        
        self.speed_label = ctk.CTkLabel(self.progress_frame, text="", font=ctk.CTkFont(size=12))
        self.speed_label.grid(row=1, column=1, padx=10, sticky="e")

        # Action Buttons
        self.button_frame = ctk.CTkFrame(self.tab_download, fg_color="transparent")
        self.button_frame.grid(row=3, column=0, padx=20, pady=20, sticky="ew")
        self.button_frame.grid_columnconfigure((0, 1), weight=1)

        self.download_button = ctk.CTkButton(self.button_frame, text="START DOWNLOAD", command=self.start_download, height=50, font=ctk.CTkFont(size=16, weight="bold"))
        self.download_button.grid(row=0, column=0, padx=10, sticky="ew")

        self.cancel_button = ctk.CTkButton(self.button_frame, text="CANCEL", command=self.cancel_download, height=50, fg_color="#C0392B", hover_color="#E74C3C", font=ctk.CTkFont(size=16, weight="bold"))
        self.cancel_button.grid(row=0, column=1, padx=10, sticky="ew")
        self.cancel_button.configure(state="disabled")

    def setup_history_tab(self):
        self.tab_history.grid_columnconfigure(0, weight=1)
        self.tab_history.grid_rowconfigure(0, weight=1)

        self.history_frame = ctk.CTkScrollableFrame(self.tab_history)
        self.history_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.refresh_history()

    def refresh_history(self):
        # Clear existing
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        history = self.history_manager.get_history()
        if not history:
            ctk.CTkLabel(self.history_frame, text="No download history yet.").pack(pady=20)
            return

        for entry in history:
            self.create_history_item(entry)

    def create_history_item(self, entry):
        item_frame = ctk.CTkFrame(self.history_frame)
        item_frame.pack(fill="x", padx=5, pady=5)
        
        # Title and Info
        title_label = ctk.CTkLabel(item_frame, text=entry.get('title', 'Unknown'), font=ctk.CTkFont(weight="bold"))
        title_label.pack(anchor="w", padx=10, pady=(5, 0))
        
        info_label = ctk.CTkLabel(item_frame, text=f"{entry.get('date')} - {entry.get('status')}", font=ctk.CTkFont(size=10))
        info_label.pack(anchor="w", padx=10, pady=(0, 2))
        
        # Button frame
        button_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        button_frame.pack(anchor="w", padx=10, pady=(0, 5))
        
        # Play button
        play_btn = ctk.CTkButton(button_frame, text="▶ Play", width=80, height=25, 
                                 command=lambda: self.play_file(entry))
        play_btn.pack(side="left", padx=(0, 5))
        
        # Show in Explorer button
        explorer_btn = ctk.CTkButton(button_frame, text="📁 Show", width=80, height=25,
                                     command=lambda: self.show_in_explorer(entry))
        explorer_btn.pack(side="left", padx=(0, 5))
        
        # Remove button
        remove_btn = ctk.CTkButton(button_frame, text="🗑 Remove", width=80, height=25,
                                   fg_color="#C0392B", hover_color="#E74C3C",
                                   command=lambda: self.remove_from_history(entry))
        remove_btn.pack(side="left")

    def play_file(self, entry):
        try:
            file_path = os.path.join(entry.get('path', ''), entry.get('title', '') + '.mp3')
            if not os.path.exists(file_path):
                file_path = os.path.join(entry.get('path', ''), entry.get('title', '') + '.mp4')
            if os.path.exists(file_path):
                os.startfile(file_path)
        except Exception as e:
            print(f"Error playing file: {e}")
    
    def show_in_explorer(self, entry):
        try:
            file_path = os.path.join(entry.get('path', ''), entry.get('title', '') + '.mp3')
            if not os.path.exists(file_path):
                file_path = os.path.join(entry.get('path', ''), entry.get('title', '') + '.mp4')
            if os.path.exists(file_path):
                subprocess.run(['explorer', '/select,', os.path.abspath(file_path)])
        except Exception as e:
            print(f"Error showing in explorer: {e}")
    
    def remove_from_history(self, entry):
        try:
            self.history_manager.history.remove(entry)
            self.history_manager.save_history()
            self.refresh_history()
        except Exception as e:
            print(f"Error removing from history: {e}")

    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def paste_text(self):
        try:
            text = self.clipboard_get()
            self.url_entry.delete(0, 'end')
            self.url_entry.insert(0, text)
        except:
            pass

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
        output_path = self.path_entry.get()
        
        if not url:
            self.status_label.configure(text="Error: Please enter a URL", text_color="#E74C3C")
            return
        
        if not output_path:
             self.status_label.configure(text="Error: Please select a download folder", text_color="#E74C3C")
             return

        self.downloading = True
        self.download_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")
        self.progress_bar.set(0)
        self.status_label.configure(text="Starting download...", text_color=("gray10", "#DCE4EE"))
        self.speed_label.configure(text="")

        # Configure Options
        options = {
            'outtmpl': '%(title)s.%(ext)s',
            'noplaylist': not self.playlist_var.get(),
        }

        self.downloader.download(
            url, 
            options,
            output_path,
            self.quality_var.get(),
            self.format_var.get(),
            progress_callback=self.update_progress, 
            completion_callback=self.download_complete, 
            error_callback=self.download_error
        )

    def cancel_download(self):
        if self.downloading:
            self.status_label.configure(text="Cancelling...")
            self.downloader.cancel()

    def update_progress(self, progress, speed, eta):
        # Throttle updates
        current_time = time.time()
        if not hasattr(self, 'last_update_time'):
            self.last_update_time = 0
        
        if current_time - self.last_update_time > 0.05 or progress >= 1.0:
            self.last_update_time = current_time
            self.after(0, lambda: self._update_progress_ui(progress, speed, eta))

    def _update_progress_ui(self, progress, speed, eta):
        try:
            self.progress_bar.set(progress)
            self.status_label.configure(text=f"Downloading... {int(progress*100)}%")
            self.speed_label.configure(text=f"{speed} | ETA: {eta}")
            self.update_idletasks()
        except Exception as e:
            print(f"UI Update Error: {e}")

    def download_complete(self, title="Unknown Title"):
        self.after(0, lambda: self._finish_download("Download Complete!", success=True, title=title))

    def download_error(self, error_msg):
        self.after(0, lambda: self._finish_download(f"Error: {error_msg}", success=False))

    def _finish_download(self, message, success, title=None):
        self.downloading = False
        self.status_label.configure(text=message, text_color="#2ECC71" if success else "#E74C3C")
        self.speed_label.configure(text="")
        self.download_button.configure(state="normal")
        self.cancel_button.configure(state="disabled")
        
        if success:
            self.progress_bar.set(1)
            # Add to history
            self.history_manager.add_entry(
                title=title if title else "Unknown",
                url=self.url_entry.get(),
                status="Completed",
                path=self.path_entry.get()
            )
            self.refresh_history()
        else:
            self.progress_bar.set(0)

if __name__ == "__main__":
    app = App()
    app.mainloop()
