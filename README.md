# Auto Clicker

A simple auto clicker for Windows with a dark UI: configurable click interval, a start/stop hotkey, fixed cursor position or image-based click targeting, and a UA / RU / EN interface language switcher.

## Installation (Windows)

Grab the installer from the [Releases](https://github.com/to0-young/auto-clicker/releases) page — no Python required.

1. Download **`AutoClickerSetup.exe`** from the latest release.
2. Run it and go through the setup wizard (you can leave the **"Create a desktop shortcut"** box checked).
3. Done — a shortcut will appear on the desktop and in the Start menu, and an uninstaller is included.

> Windows SmartScreen or your antivirus may warn about an unrecognized file — that's normal for an unsigned `.exe`. Click "More info" → "Run anyway".

## Auto clicker not working in a game (e.g. Lineage 2)

Some games run with elevated privileges, and Windows blocks simulated clicks from processes without admin rights. The installed Auto Clicker requests those rights on launch (a UAC prompt will appear) — just confirm it.

## Usage

- **Interval Configuration** — time between clicks (hours/mins/secs/ms) and a random offset.
- **Click Options** — mouse button (left/right/middle) and click type (single/double/hold).
- **Click Repeat** — repeat a fixed number of times, or forever until stopped.
- **Cursor Position** — click at the current cursor location, at a fixed coordinate, or by locating an image on screen.
- The **Start/Stop** button at the bottom, or a hotkey (`F6` by default, rebindable with **Record Hotkey**).
- Three buttons — **UA / RU / EN** — at the top of the window switch the interface language instantly.

## Building from source (for developers)

```
pip install -r requirements.txt
python main.py
```

The Windows installer is built automatically via GitHub Actions whenever a `vX.Y.Z` tag is pushed:

```
git tag v1.0.0
git push --tags
```
