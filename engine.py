"""Core clicking engine: config model, hotkey capture, and the click loop."""
import random
import threading
from dataclasses import dataclass, field
from enum import Enum

from pynput import keyboard
from pynput.mouse import Button, Controller as MouseController


class ClickButton(Enum):
    LEFT = "Left"
    RIGHT = "Right"
    MIDDLE = "Middle"


class ClickType(Enum):
    SINGLE = "Single"
    DOUBLE = "Double"
    HOLD = "Hold"


class CursorMode(Enum):
    CURRENT = "Cursor Location"
    FIXED = "Fixed Location"


class ActionType(Enum):
    CLICK = "Click"
    SCROLL = "Scroll"
    KEY_PRESS = "Key Press"


class ScrollDirection(Enum):
    UP = "Up"
    DOWN = "Down"


_BUTTON_MAP = {
    ClickButton.LEFT: Button.left,
    ClickButton.RIGHT: Button.right,
    ClickButton.MIDDLE: Button.middle,
}

_KEY_ALIASES = {
    "esc": "esc", "escape": "esc", "ctrl": "ctrl_l", "control": "ctrl_l",
    "alt": "alt_l", "shift": "shift_l", "cmd": "cmd", "win": "cmd",
    "enter": "enter", "return": "enter", "space": "space", "tab": "tab",
    "backspace": "backspace", "delete": "delete", "del": "delete",
}


def parse_key_spec(spec: str):
    """Parse a spec like 'ctrl+c' or 'f5' into a list of pynput key objects."""
    keys = []
    for part in spec.strip().lower().split("+"):
        part = part.strip()
        if not part:
            continue
        name = _KEY_ALIASES.get(part, part)
        key_attr = getattr(keyboard.Key, name, None)
        if key_attr is not None:
            keys.append(key_attr)
        elif len(part) == 1:
            keys.append(part)
    return keys


def hex_to_rgb(hex_str: str):
    hex_str = (hex_str or "").strip().lstrip("#")
    if len(hex_str) != 6:
        return None
    try:
        return tuple(int(hex_str[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return None


def rgb_to_hex(rgb) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


@dataclass
class ClickerConfig:
    hours: int = 0
    minutes: int = 0
    seconds: int = 0
    milliseconds: int = 100
    random_offset_enabled: bool = False
    random_offset_ms: int = 0
    button: ClickButton = ClickButton.LEFT
    click_type: ClickType = ClickType.SINGLE
    repeat_forever: bool = True
    repeat_count: int = 1
    cursor_mode: CursorMode = CursorMode.CURRENT
    fixed_points: list = field(default_factory=list)

    def interval_seconds(self) -> float:
        base = self.hours * 3600 + self.minutes * 60 + self.seconds + self.milliseconds / 1000
        return max(base, 0.001)

    def cps(self) -> float:
        interval = self.interval_seconds()
        return 1 / interval if interval > 0 else 0.0


class ClickerEngine:
    """Runs the click loop on a background thread until stopped."""

    def __init__(self, on_state_change=None):
        self._mouse = MouseController()
        self._thread = None
        self._stop_event = threading.Event()
        self._running = False
        self._on_state_change = on_state_change

    @property
    def running(self):
        return self._running

    def toggle(self, config: ClickerConfig):
        if self._running:
            self.stop()
        else:
            self.start(config)

    def start(self, config: ClickerConfig):
        if self._running:
            return
        self._stop_event.clear()
        self._running = True
        self._notify()
        self._thread = threading.Thread(target=self._run, args=(config,), daemon=True)
        self._thread.start()

    def stop(self):
        if not self._running:
            return
        self._stop_event.set()
        self._running = False
        self._notify()

    def _notify(self):
        if self._on_state_change:
            self._on_state_change(self._running)

    def _run(self, config: ClickerConfig):
        count = 0
        point_index = 0
        while not self._stop_event.is_set():
            target = self._resolve_target(config, point_index)
            if target is not None:
                self._click(target, config)
                count += 1
                if config.cursor_mode == CursorMode.FIXED and config.fixed_points:
                    point_index = (point_index + 1) % len(config.fixed_points)
                if not config.repeat_forever and count >= config.repeat_count:
                    break
            delay = config.interval_seconds()
            if config.random_offset_enabled and config.random_offset_ms:
                jitter = random.uniform(-config.random_offset_ms, config.random_offset_ms) / 1000
                delay = max(delay + jitter, 0.001)
            if self._stop_event.wait(delay):
                break
        self._running = False
        self._notify()

    def _resolve_target(self, config: ClickerConfig, point_index: int = 0):
        if config.cursor_mode == CursorMode.CURRENT:
            return self._mouse.position
        if config.cursor_mode == CursorMode.FIXED:
            if not config.fixed_points:
                return None
            return config.fixed_points[point_index]
        return self._mouse.position

    def _click(self, position, config: ClickerConfig):
        if config.cursor_mode != CursorMode.CURRENT:
            self._mouse.position = position
        button = _BUTTON_MAP[config.button]
        clicks = 2 if config.click_type == ClickType.DOUBLE else 1
        self._mouse.click(button, clicks)


def key_label(key) -> str:
    """Human-readable label for a pynput key, e.g. 'F6', 'A', 'SPACE'."""
    if isinstance(key, keyboard.KeyCode):
        return (key.char or f"VK{key.vk}").upper()
    return str(key).split(".")[-1].upper()


class HotkeyManager:
    """Global keyboard listener: fires on_trigger for the bound key, and
    supports rebinding by capturing the next key press."""

    def __init__(self, on_trigger, initial_key=keyboard.Key.f6):
        self._on_trigger = on_trigger
        self._key = initial_key
        self._recording = False
        self._record_callback = None
        self._listener = keyboard.Listener(on_press=self._on_press)
        self._listener.start()

    @property
    def key(self):
        return self._key

    def label(self) -> str:
        return key_label(self._key)

    def record_next(self, callback):
        """Next key pressed anywhere becomes the new hotkey."""
        self._recording = True
        self._record_callback = callback

    def _on_press(self, key):
        if self._recording:
            self._key = key
            self._recording = False
            cb, self._record_callback = self._record_callback, None
            if cb:
                cb(key)
            return
        if key == self._key:
            self._on_trigger()

    def stop(self):
        self._listener.stop()


class PositionPicker:
    """Captures the next mouse position confirmed by pressing Enter."""

    def __init__(self, on_captured):
        self._on_captured = on_captured
        self._mouse = MouseController()
        self._listener = keyboard.Listener(on_press=self._on_press)
        self._listener.start()

    def _on_press(self, key):
        if key == keyboard.Key.enter:
            self._listener.stop()
            self._on_captured(self._mouse.position)
