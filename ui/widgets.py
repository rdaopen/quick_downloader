import customtkinter as ctk

class DownloadItem(ctk.CTkFrame):
    def __init__(self, parent, download_data, select_callback):
        super().__init__(parent, fg_color=("white", "#2b2b2b"))
        self.download_data = download_data
        self.select_callback = select_callback
        self.pack(fill="x", padx=5, pady=5)
        
        self.create_widgets()
        self.bind_events()
        
        # Store widget references in data for updates (legacy support for main.py logic)
        download_data['ui_widgets'] = {
            'frame': self,
            'title': self.title_label,
            'progress': self.progress_bar,
            'status': self.status_label,
            'speed': self.speed_label
        }

    def create_widgets(self):
        self.title_label = ctk.CTkLabel(self, text=self.download_data.get('title', 'Initializing...'), font=ctk.CTkFont(weight="bold"), text_color=("gray10", "gray90"))
        self.title_label.pack(anchor="w", padx=10, pady=(5, 0))
        
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.pack(fill="x", padx=10, pady=5)
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(self, text="Starting...", font=ctk.CTkFont(size=12), text_color=("gray40", "gray60"))
        self.status_label.pack(side="left", padx=10, pady=(0, 5))
        
        self.speed_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12), text_color=("gray40", "gray60"))
        self.speed_label.pack(side="right", padx=10, pady=(0, 5))

    def bind_events(self):
        self.bind("<Button-1>", lambda e: self.select_callback(self.download_data))
        for child in self.winfo_children():
            child.bind("<Button-1>", lambda e: self.select_callback(self.download_data))

class HistoryItem(ctk.CTkFrame):
    def __init__(self, parent, entry, callbacks, selection_callback):
        super().__init__(parent, fg_color=("white", "#2b2b2b"))
        self.entry = entry
        self.callbacks = callbacks # {'play': func, 'show': func, 'remove': func}
        self.selection_callback = selection_callback
        self.pack(fill="x", padx=5, pady=5)
        
        self.create_widgets()

    def create_widgets(self):
        # Checkbox
        self.checkbox_var = ctk.BooleanVar(value=False)
        self.checkbox = ctk.CTkCheckBox(self, text="", width=24, checkbox_width=20, checkbox_height=20, variable=self.checkbox_var, command=self.on_toggle)
        self.checkbox.pack(side="left", padx=(10, 0), pady=10)

        # Info Frame
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)

        # Info
        ctk.CTkLabel(info_frame, text=self.entry.get('title', 'Unknown'), font=ctk.CTkFont(weight="bold"), text_color=("gray10", "gray90")).pack(anchor="w", padx=10, pady=(5, 0))
        ctk.CTkLabel(info_frame, text=f"{self.entry.get('media_type', 'Unknown')} | {self.entry.get('date')}", font=ctk.CTkFont(size=10), text_color=("gray40", "gray60")).pack(anchor="w", padx=10, pady=(0, 2))
        
        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(side="right", padx=10)
        
        ctk.CTkButton(btn_frame, text="▶ Play", width=60, height=24, command=lambda: self.callbacks['play'](self.entry)).pack(side="left", padx=(0, 5))
        ctk.CTkButton(btn_frame, text="📁 Show", width=60, height=24, command=lambda: self.callbacks['show'](self.entry)).pack(side="left", padx=(0, 5))
        ctk.CTkButton(btn_frame, text="🗑", width=30, height=24, fg_color="#C0392B", hover_color="#E74C3C", command=lambda: self.callbacks['remove'](self.entry)).pack(side="left")

    def on_toggle(self):
        if self.selection_callback:
            self.selection_callback(self.entry, self.checkbox_var.get())
