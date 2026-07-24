# Auto Clicker

A simple auto clicker for Windows and Linux: configurable click interval, a start/stop hotkey, fixed or current cursor position, a UA / RU / EN interface language switcher, and a dark/light theme.

## Installation

Grab a build from the [Releases](https://github.com/to0-young/auto-clicker/releases) page — no Python required. Each release has three files: `AutoClickerSetup-windows.exe`, `AutoClicker.deb`, and `AutoClicker-linux`.

### Windows

1. Download **`AutoClickerSetup-windows.exe`** from the latest release.
2. Run it and go through the setup wizard:
   - Choose an install location (or keep the default).
   - Leave **"Create a desktop shortcut"** checked if you want one.
3. Done. "Auto Clicker" is now in the Start menu (and on the desktop, if you kept the checkbox), with a proper uninstaller registered in "Add or Remove Programs".

The app requests administrator rights on launch (a UAC prompt) — this is required so it can send clicks into other elevated applications (e.g. games running as admin). Confirm the prompt.

> Windows SmartScreen or your antivirus may warn about an unrecognized file — that's normal for an unsigned `.exe`. Click "More info" → "Run anyway".

### Linux

**Debian / Ubuntu / Mint and similar (recommended):**
```
wget https://github.com/to0-young/auto-clicker/releases/latest/download/AutoClicker.deb
sudo apt install ./AutoClicker.deb
```
(Or just double-click the downloaded `.deb` in a file manager that supports package installs, e.g. GNOME Software / Ubuntu Software.)

This installs the binary to `/opt/autoclicker` and adds an "Auto Clicker" entry with its icon to your applications menu. To remove it later:
```
sudo apt remove autoclicker
```

**Any other distro (Fedora, Arch, openSUSE, ...):**
```
wget https://github.com/to0-young/auto-clicker/releases/latest/download/AutoClicker-linux
chmod +x AutoClicker-linux
./AutoClicker-linux
```
There's no installer for this path — it's a single portable binary you run directly, from wherever you put it.

> **Tray icon:** needs a tray host to actually show up in. Most X11 desktop environments (XFCE, KDE, Cinnamon, MATE...) provide one out of the box; vanilla GNOME needs the "AppIndicator and KStatusNotifierItem Support" extension installed. Without a tray host, the app still runs — you just won't see the tray icon, and closing the window will hide it with no way to reopen it until you relaunch.
>
> **Wayland:** on a pure Wayland session (no XWayland), global hotkeys and simulated clicks may not work at all — this is a Wayland security restriction, not a bug in the app. If clicks/hotkeys don't register, check whether your session is Wayland or X11 (`echo $XDG_SESSION_TYPE`).

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

The Windows installer and Linux package are built automatically via GitHub Actions whenever a `vX.Y.Z` tag is pushed:

```
git push
git tag v1.0.0
git push --tags
```

> `git push` only pushes commits on a branch — it does **not** push tags. If you tag a release and only run `git push`, the workflow never triggers and no new release appears. Push the tag explicitly with `git push --tags` (all tags) or `git push origin v1.0.0` (a single tag).
