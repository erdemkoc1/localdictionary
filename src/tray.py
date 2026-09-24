import os
import sys
import threading
from typing import Optional, Callable
from PIL import Image, ImageDraw, ImageFont
import pystray

def create_tray_image(width=64, height=64) -> Image.Image:
    """Generates a modern, clean tray icon with dark-blue background and LD logo."""
    img = Image.new("RGBA", (width, height), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background rounded rectangle
    draw.rounded_rectangle([2, 2, width - 3, height - 3], radius=14, fill="#1F538D", outline="#4A90E2", width=2)

    # Draw "LD" letters cleanly
    try:
        font = ImageFont.truetype("arial.ttf", 26)
    except Exception:
        font = ImageFont.load_default()

    draw.text((12, 14), "LD", fill="white", font=font)
    return img


class AppTrayIcon:
    """
    Manages the Windows notification tray icon (near the clock),
    providing persistent visibility and quick actions.
    """
    def __init__(self, app, on_show: Callable[[], None], on_settings: Callable[[], None], on_exit: Callable[[], None]):
        self.app = app
        self.on_show = on_show
        self.on_settings = on_settings
        self.on_exit = on_exit
        self.icon: Optional[pystray.Icon] = None
        self._thread: Optional[threading.Thread] = None
        self._is_running = False

    def build_menu(self):
        get_text = getattr(self.app, "gt", lambda k: k)
        return pystray.Menu(
            pystray.MenuItem(get_text("tray_open"), self._action_show, default=True),
            pystray.MenuItem(get_text("tray_settings"), self._action_settings),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(get_text("tray_exit"), self._action_exit)
        )

    def _action_show(self, icon=None, item=None):
        if self.app:
            self.app.after(0, self.on_show)

    def _action_settings(self, icon=None, item=None):
        if self.app:
            self.app.after(0, self.on_settings)

    def _action_exit(self, icon=None, item=None):
        if self.app:
            self.app.after(0, self.on_exit)

    def start(self):
        """Starts the tray icon in a dedicated daemon thread."""
        if self._is_running:
            return
        
        try:
            img = create_tray_image()
            get_text = getattr(self.app, "gt", lambda k: "LocalDictionary (100% Çevrimdışı - Açık)")
            tooltip = get_text("tray_tooltip")
            self.icon = pystray.Icon("LocalDictionary", img, tooltip, menu=self.build_menu())
            self._thread = threading.Thread(target=self.icon.run, daemon=True)
            self._thread.start()
            self._is_running = True
        except Exception as e:
            print(f"Uyarı: Sistem tepsisi simgesi başlatılamadı: {e}")

    def update_language(self):
        """Refreshes menu and tooltip localization when user switches language."""
        if self.icon and self._is_running:
            try:
                get_text = getattr(self.app, "gt", lambda k: k)
                self.icon.title = get_text("tray_tooltip")
                self.icon.menu = self.build_menu()
                self.icon.update_menu()
            except Exception:
                pass

    def stop(self):
        """Stops and removes the tray icon."""
        if self.icon and self._is_running:
            try:
                self.icon.stop()
            except Exception:
                pass
            self._is_running = False
