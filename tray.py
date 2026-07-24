"""System tray icon: lives in the OS notification area while the main
window is hidden, with a menu to restore it or quit for good."""
import os
import threading

import pystray
from PIL import Image

import i18n


class TrayIcon:
    """Wraps a pystray.Icon so callers don't need to touch pystray directly.

    ``get_lang`` is called each time the menu labels are drawn, so the menu
    stays translated even if the language changes while it's hidden. The
    ``on_show``/``on_quit`` callbacks run on pystray's own thread, not the
    Tk thread — callers must marshal back with ``root.after(0, ...)``.
    """

    def __init__(self, icon_path, get_lang, on_show, on_quit):
        image = (
            Image.open(icon_path).convert("RGBA")
            if os.path.exists(icon_path)
            else Image.new("RGBA", (32, 32), (61, 220, 132, 255))
        )
        menu = pystray.Menu(
            pystray.MenuItem(
                lambda item: i18n.t("tray_show", get_lang()),
                lambda icon, item: on_show(),
                default=True,
            ),
            pystray.MenuItem(
                lambda item: i18n.t("tray_exit", get_lang()),
                lambda icon, item: on_quit(),
            ),
        )
        self._icon = pystray.Icon("AutoClicker", image, "Auto Clicker", menu=menu)

    def start(self):
        threading.Thread(target=self._icon.run, daemon=True).start()

    def stop(self):
        self._icon.stop()
