
import pystray
from PIL import Image
import threading

class SystemTrayIcon:
    def __init__(self, icon_path, app_name, on_open, on_quit):
        self.icon_path = icon_path
        self.app_name = app_name
        self.on_open = on_open
        self.on_quit = on_quit
        self.icon = None
        self.thread = None

    def create_image(self):
        return Image.open(self.icon_path)

    def run(self):
        image = self.create_image()
        menu = pystray.Menu(
            pystray.MenuItem("Open", self.on_open_action, default=True),
            pystray.MenuItem("Quit", self.on_quit_action)
        )
        self.icon = pystray.Icon("name", image, self.app_name, menu)
        self.icon.run()

    def start(self):
        # Run in a separate thread to not block main loop if needed, 
        # BUT pystray usually wants to be on main thread or have its own loop.
        # Since Tkinter is on MainThread, we run this in a thread.
        # Note: on some platforms this might be an issue, but usually fine on Windows.
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def stop(self):
        if self.icon:
            self.icon.stop()

    def on_open_action(self, icon, item):
        self.on_open()

    def on_quit_action(self, icon, item):
        self.stop()
        self.on_quit()
