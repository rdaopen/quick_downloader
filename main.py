import customtkinter as ctk
import os
import sys
import time
import subprocess
from tkinter import messagebox
from PIL import Image
from downloader import MediaDownloader
from history import HistoryManager
from config import ConfigManager
from utils import resource_path
from ui.dialogs import AddDownloadDialog, SettingsDialog
from ui.widgets import DownloadItem, HistoryItem
import queue
from server import BackgroundServer
from tray import SystemTrayIcon

# Initialize Config (Global for theme setting before App init)
config_manager = ConfigManager()
ctk.set_appearance_mode(config_manager.get("theme"))
ctk.set_default_color_theme("green")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Quick Media Downloader")
        self.geometry("900x600")
        self.minsize(800, 500)
        
        # Set icon
        icon_path = resource_path("icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception as e:
                print(f"Could not set icon: {e}")    

        self.config_manager = config_manager # Use global instance
        self.history_manager = HistoryManager()
        self.active_downloads = [] 
        self.selected_download = None
        self.selected_history_entries = [] # For history selection
        
        # FFmpeg check
        self.ffmpeg_path = resource_path("ffmpeg")
        if not os.path.exists(self.ffmpeg_path):
            self.ffmpeg_path = None

        self.create_layout()
        self.show_view("Downloads")

        # Background Server for Chrome Extension
        self.url_queue = queue.Queue()
        self.server = BackgroundServer(self.url_queue)
        self.server.start()
        self.check_new_downloads()

        # System Tray
        self.tray_icon = None
        self.protocol("WM_DELETE_WINDOW", self.on_close_window)
        self.init_tray()

    def create_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1. Top Bar
        self.top_bar = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color=("white", "#2b2b2b"))
        self.top_bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.create_top_bar_items()

        # 2. Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=("white", "#2b2b2b"))
        self.sidebar.grid(row=1, column=0, sticky="nsew")
        self.create_sidebar_items()

        # 3. Content Area
        self.content_area = ctk.CTkFrame(self, corner_radius=0, fg_color=("#F5F5F5", "#1a1a1a"))
        self.content_area.grid(row=1, column=1, sticky="nsew")
        
        self.is_running = True
        
    def create_top_bar_items(self):
        # Load Icons
        try:
            self.icon_add = ctk.CTkImage(Image.open(resource_path(os.path.join("icons", "add.png"))), size=(20, 20))
            self.icon_stop = ctk.CTkImage(Image.open(resource_path(os.path.join("icons", "stop.png"))), size=(20, 20))
            self.icon_settings = ctk.CTkImage(Image.open(resource_path(os.path.join("icons", "setting.png"))), size=(20, 20))
        except Exception as e:
            print(f"Error loading icons: {e}")
            self.icon_add = None
            self.icon_stop = None
            self.icon_settings = None

        # Add Download
        self.btn_add = ctk.CTkButton(self.top_bar, text="Add Download", image=self.icon_add, compound="left", width=140, command=self.open_add_dialog)
        self.btn_add.pack(side="left", padx=20, pady=10)
        
        # Cancel
        self.btn_cancel = ctk.CTkButton(self.top_bar, text="Stop", image=self.icon_stop, compound="left", width=100, fg_color="#C0392B", hover_color="#E74C3C", command=self.cancel_selected, state="disabled")
        self.btn_cancel.pack(side="left", padx=10, pady=10)
        
        # Settings
        self.btn_settings = ctk.CTkButton(self.top_bar, text="Settings", image=self.icon_settings, compound="left", width=100, fg_color="transparent", border_width=1, text_color=("gray10", "gray90"), command=self.open_settings)
        self.btn_settings.pack(side="right", padx=20, pady=10)

    def create_sidebar_items(self):
        self.sidebar_buttons = {}
        items = ["Downloads", "Completed", "Videos", "Audios"]
        
        for i, item in enumerate(items):
            btn = ctk.CTkButton(self.sidebar, text=item, height=40, corner_radius=0, fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray90", "gray30"), anchor="w",
                                command=lambda x=item: self.show_view(x))
            btn.pack(fill="x", pady=2)
            self.sidebar_buttons[item] = btn

    def show_view(self, view_name):
        self.current_view = view_name
        self.selected_download = None
        self.selected_history_entries = [] # Clear selection on view change
        self.update_cancel_button_state()
        
        # Update Sidebar Styling
        for name, btn in self.sidebar_buttons.items():
            if name == view_name:
                btn.configure(fg_color=("#E0E0E0", "#3a3a3a"))
            else:
                btn.configure(fg_color="transparent")
        
        # Clear Content
        for widget in self.content_area.winfo_children():
            widget.destroy()
            
        # Populate Content
        if view_name == "Downloads":
            self.show_active_downloads()
        else:
            self.show_history(view_name)

    def show_active_downloads(self):
        if not self.active_downloads:
            ctk.CTkLabel(self.content_area, text="No active downloads.", font=ctk.CTkFont(size=16)).pack(pady=50)
            return
            
        self.scroll_frame = ctk.CTkScrollableFrame(self.content_area)
        self.scroll_frame.pack(fill="both", expand=True)
        
        for download in self.active_downloads:
            DownloadItem(self.scroll_frame, download, self.select_download)

    def select_download(self, download_data):
        self.selected_download = download_data
        self.update_cancel_button_state()
        
        # Visual feedback
        for d in self.active_downloads:
            if 'ui_widgets' in d:
                color = "transparent"
                if d == self.selected_download:
                    color = ("gray85", "gray20") # Highlight color
                
                # Update frame color only if it's not destroyed
                try:
                    d['ui_widgets']['frame'].configure(fg_color=color)
                except:
                    pass

    def update_cancel_button_state(self):
        if self.selected_download and self.current_view == "Downloads":
            self.btn_cancel.configure(state="normal")
        else:
            self.btn_cancel.configure(state="disabled")

    def show_history(self, filter_type):
        self.history_control_bar = ctk.CTkFrame(self.content_area, height=40, fg_color="transparent")
        self.history_control_bar.pack(fill="x", padx=10, pady=5)
        
        self.btn_clear_all = ctk.CTkButton(self.history_control_bar, text="Clear All History", fg_color="#C0392B", hover_color="#E74C3C", height=30, command=self.clear_all_history)
        self.btn_clear_all.pack(side="right", padx=5)

        self.btn_delete_selected = ctk.CTkButton(self.history_control_bar, text="Delete Selected", fg_color="#C0392B", hover_color="#E74C3C", height=30, state="disabled", command=self.delete_selected_history)
        self.btn_delete_selected.pack(side="right", padx=5)

        self.scroll_frame = ctk.CTkScrollableFrame(self.content_area)
        self.scroll_frame.pack(fill="both", expand=True)
        
        history = self.history_manager.get_history()
        
        filtered_history = []
        if filter_type == "Completed":
            filtered_history = history
        elif filter_type == "Videos":
            filtered_history = [h for h in history if h.get('media_type') == 'Video']
        elif filter_type == "Audios":
            filtered_history = [h for h in history if h.get('media_type') == 'Audio']
            
        if not filtered_history:
            ctk.CTkLabel(self.scroll_frame, text="No items found.", font=ctk.CTkFont(size=16)).pack(pady=50)
            return

        callbacks = {
            'play': self.play_file,
            'show': self.show_in_explorer,
            'remove': self.remove_history
        }

        for entry in filtered_history:
            HistoryItem(self.scroll_frame, entry, callbacks, self.on_history_select)

    def on_history_select(self, entry, is_selected):
        if is_selected:
            if entry not in self.selected_history_entries:
                self.selected_history_entries.append(entry)
        else:
            if entry in self.selected_history_entries:
                self.selected_history_entries.remove(entry)
        
        # Update Delete Button State
        if self.selected_history_entries:
            self.btn_delete_selected.configure(state="normal")
        else:
            self.btn_delete_selected.configure(state="disabled")

    def clear_all_history(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the entire history?"):
            self.history_manager.clear_history()
            self.selected_history_entries = []
            self.show_view(self.current_view)

    def delete_selected_history(self):
        if not self.selected_history_entries:
            return
            
        if messagebox.askyesno("Confirm", f"Delete {len(self.selected_history_entries)} selected items?"):
            self.history_manager.remove_items(self.selected_history_entries)
            self.selected_history_entries = []
            self.show_view(self.current_view)

    def open_add_dialog(self):
        AddDownloadDialog(self, self.start_download_task, self.config_manager.get("default_path"))

    def open_settings(self):
        SettingsDialog(self, self.config_manager, self.apply_settings)

    def apply_settings(self):
        ctk.set_appearance_mode(self.config_manager.get("theme"))

    def start_download_task(self, data):
        # Create Downloader Instance
        downloader = MediaDownloader(ffmpeg_path=self.ffmpeg_path)
        
        # Append subfolder based on format
        if data['format'] == 'Video':
            data['path'] = os.path.join(data['path'], 'Videos')
        elif data['format'] == 'Audio':
            data['path'] = os.path.join(data['path'], 'Audios')
            
        # Ensure directory exists
        if not os.path.exists(data['path']):
            os.makedirs(data['path'])
        
        download_obj = {
            'downloader': downloader,
            'data': data,
            'title': data['url'], # Temporary title
            'status': 'queued'
        }
        self.active_downloads.append(download_obj)
        
        # Refresh view if on Downloads
        if self.current_view == "Downloads":
            self.show_view("Downloads")
            
        # Start Download
        options = {
            'outtmpl': '%(title)s.%(ext)s',
            'noplaylist': not data['playlist'],
        }
        
        downloader.download(
            data['url'],
            options,
            data['path'],
            data['quality'],
            data['format'],
            progress_callback=lambda p, s, e: self.update_progress(download_obj, p, s, e),
            completion_callback=lambda t: self.download_complete(download_obj, t),
            error_callback=lambda m: self.download_error(download_obj, m),
            title_callback=lambda t: self.update_title(download_obj, t)
        )

    def update_title(self, download_obj, title):
        self.after(0, lambda: self._update_ui_title(download_obj, title))

    def _update_ui_title(self, download_obj, title):
        if not self.is_running: return
        if 'ui_widgets' in download_obj:
            try:
                # Only update if title changed to avoid flickering/redundancy
                if download_obj.get('title') != title:
                    download_obj['title'] = title
                    download_obj['ui_widgets']['title'].configure(text=title)
            except:
                pass

    def update_progress(self, download_obj, progress, speed, eta):
        # Throttle updates?
        try:
            self.after(0, lambda: self._update_ui_widget(download_obj, progress, speed, eta))
        except:
            pass

    def _update_ui_widget(self, download_obj, progress, speed, eta):
        if not self.is_running: return
        if 'ui_widgets' in download_obj:
            try:
                widgets = download_obj['ui_widgets']
                widgets['progress'].set(progress)
                widgets['status'].configure(text=f"Downloading... {int(progress*100)}%")
                widgets['speed'].configure(text=f"{speed} | ETA: {eta}")
            except:
                pass # Widget might be destroyed if view changed

    def download_complete(self, download_obj, title):
        self.after(0, lambda: self._handle_completion(download_obj, title, True))

    def download_error(self, download_obj, error_msg):
        self.after(0, lambda: self._handle_completion(download_obj, error_msg, False))

    def _handle_completion(self, download_obj, message, success):
        if not self.is_running: return

        if download_obj in self.active_downloads:
            self.active_downloads.remove(download_obj)
        
        if download_obj == self.selected_download:
            self.selected_download = None
            self.update_cancel_button_state()
            
        if success:
            # Add to history
            self.history_manager.add_entry(
                title=message, # message is title on success
                url=download_obj['data']['url'],
                status="Completed",
                path=download_obj['data']['path'],
                media_type=download_obj['data']['format']
            )
            messagebox.showinfo("Download Complete", f"Downloaded: {message}")
        else:
            if message != "Cancelled":
                 messagebox.showerror("Download Error", message)
            
            # --- CLEANUP PART FILES ON ERROR/CANCEL ---
            try:
                base_path = download_obj['data']['path']
                # Search for files that might be leftovers. 
                # Ideally we know the exact filename, but 'message' might not be it.
                # However, downloader can expose 'current_filename'.
                # For now, simplistic cleanup if we can find .part files recently modified?
                # Actually, downloader.py is better for this.
                # BUT, let's trigger a cleanup call on the downloader instance if possible.
                pass 
            except:
                pass
            
        # Refresh current view
        self.show_view(self.current_view)

    def cancel_selected(self):
        if self.selected_download:
            self.selected_download['downloader'].cancel()
            # The error callback will handle the removal and UI update
            self.btn_cancel.configure(state="disabled")

    # --- History Actions ---
    def play_file(self, entry):
        try:
            file_path = os.path.join(entry.get('path', ''), entry.get('title', '') + '.mp3')
            if not os.path.exists(file_path):
                file_path = os.path.join(entry.get('path', ''), entry.get('title', '') + '.mp4')
            if os.path.exists(file_path):
                os.startfile(file_path)
        except Exception as e:
            print(f"Error: {e}")

    def show_in_explorer(self, entry):
        try:
            file_path = os.path.join(entry.get('path', ''), entry.get('title', '') + '.mp3')
            if not os.path.exists(file_path):
                file_path = os.path.join(entry.get('path', ''), entry.get('title', '') + '.mp4')
            if os.path.exists(file_path):
                subprocess.run(['explorer', '/select,', os.path.abspath(file_path)])
        except Exception as e:
            print(f"Error: {e}")

    def remove_history(self, entry):
        self.history_manager.history.remove(entry)
        self.history_manager.save_history()
        self.show_view(self.current_view)

    def check_new_downloads(self):
        try:
            while True:
                url = self.url_queue.get_nowait()
                if url:
                    # Bring window to front (optional but helpful)
                    self.deiconify()
                    self.focus_force()
                    
                    # Open Add Dialog with URL
                    AddDownloadDialog(self, self.start_download_task, self.config_manager.get("default_path"), initial_url=url)
        except queue.Empty:
            pass
        finally:
            if self.is_running:
                self.after(1000, self.check_new_downloads)

    def init_tray(self):
        icon_path = resource_path("icon.ico")
        self.tray_icon = SystemTrayIcon(icon_path, "Quick Media Downloader", self.show_window, self.quit_app)
        self.tray_icon.start()

    def on_close_window(self):
        self.withdraw() # Hide window
        
    def show_window(self):
        self.after(0, self.deiconify)

    def quit_app(self):
        self.is_running = False
        # Stop everything
        if self.tray_icon:
            self.tray_icon.stop()
        if self.server:
            self.server.stop() 
        
        try:
            self.destroy()
        except:
            pass
            
        sys.exit(0)

if __name__ == "__main__":
    app = App()
    app.mainloop()
