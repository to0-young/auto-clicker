#!/usr/bin/env python3
"""Entry point for the Auto Clicker utility."""
import sys

from gui import AutoClickerApp


def _make_dpi_aware():
    # Without this, Windows virtualizes coordinates for a non-DPI-aware
    # process on scaled displays, so positions captured via pynput (Set
    # Position) don't match where a later click via pynput actually lands.
    if sys.platform != "win32":
        return
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # per-monitor DPI aware
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def main():
    _make_dpi_aware()
    app = AutoClickerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
