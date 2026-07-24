# Auto Clicker

A simple auto clicker for Windows: configurable click interval, a start/stop hotkey, fixed or current cursor position, a UA / RU / EN interface language switcher, and a dark/light theme.

## Installation (Windows)

Grab the installer from the [Releases](https://github.com/to0-young/auto-clicker/releases) page — no Python required.

1. Download **`AutoClickerSetup.exe`** from the latest release.
2. Run it and go through the setup wizard (you can leave the **"Create a desktop shortcut"** box checked).
3. Done — a shortcut will appear on the desktop and in the Start menu, and an uninstaller is included.

> Windows SmartScreen or your antivirus may warn about an unrecognized file — that's normal for an unsigned `.exe`. Click "More info" → "Run anyway".

## Usage

- **Interval Configuration** — time between clicks (hours/mins/secs/ms) and a random offset.
- **Click Options** — mouse button (left/right/middle) and click type (single/double/hold).
- **Click Repeat** — repeat a fixed number of times, or forever until stopped.
- **Cursor Position** — click at the current cursor location, or at a fixed coordinate.
- The **Start/Stop** button at the bottom, or a hotkey (`F6` by default, rebindable with **Record Hotkey**).
- Three buttons — **UA / RU / EN** — at the top of the window switch the interface language instantly.
- **Dark / Light** buttons next to the language switcher toggle the color theme.
- Closing the window (the X button) minimizes it to the system tray instead of quitting; use the tray icon's menu to show the window again or exit for good.

## Building from source (for developers)

```
pip install -r requirements.txt
python main.py
```

The Windows installer is built automatically via GitHub Actions whenever a `vX.Y.Z` tag is pushed:

```
git push
git tag v1.0.0
git push --tags
```

> `git push` only pushes commits on a branch — it does **not** push tags. If you tag a release and only run `git push`, the workflow never triggers and no new release appears. Push the tag explicitly with `git push --tags` (all tags) or `git push origin v1.0.0` (a single tag).
