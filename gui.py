"""Dark-themed tkinter GUI for the auto clicker."""
import os
import sys
import tkinter as tk
from tkinter import ttk

import i18n
from engine import (
    ClickButton,
    ClickerConfig,
    ClickerEngine,
    ClickType,
    CursorMode,
    HotkeyManager,
    PositionPicker,
)
from tray import TrayIcon

THEMES = {
    "dark": {
        "BG": "#1e1f22", "PANEL": "#242529", "FG": "#e8e8e8", "FG_MUTED": "#9a9a9a",
        "ACCENT": "#3ddc84", "ACCENT_STOP": "#e0525a", "ENTRY_BG": "#2c2d30", "BORDER": "#38393d",
    },
    "light": {
        "BG": "#f4f4f5", "PANEL": "#ffffff", "FG": "#1c1c1e", "FG_MUTED": "#6b6b70",
        "ACCENT": "#3ddc84", "ACCENT_STOP": "#e0525a", "ENTRY_BG": "#e7e7ea", "BORDER": "#d6d6da",
    },
}


def _apply_theme_colors(name):
    """Reassign the module-level color constants used throughout widget
    construction, so the next UI (re)build picks up the new palette."""
    global BG, PANEL, FG, FG_MUTED, ACCENT, ACCENT_STOP, ENTRY_BG, BORDER
    p = THEMES[name]
    BG, PANEL, FG, FG_MUTED, ACCENT, ACCENT_STOP, ENTRY_BG, BORDER = (
        p["BG"], p["PANEL"], p["FG"], p["FG_MUTED"],
        p["ACCENT"], p["ACCENT_STOP"], p["ENTRY_BG"], p["BORDER"],
    )


_apply_theme_colors("dark")

FONT = ("Sans", 10)
FONT_BOLD = ("Sans", 11, "bold")
FONT_SMALL = ("Sans", 8)


def _resource_path(relative_path):
    """Resolve a path that works both when run from source and when
    bundled by PyInstaller (which unpacks data files under sys._MEIPASS)."""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def _int(var: tk.StringVar, default=0) -> int:
    try:
        return max(int(var.get()), 0)
    except (ValueError, TypeError):
        return default


class ToggleSwitch(tk.Canvas):
    """A rounded on/off pill switch bound to a BooleanVar."""

    def __init__(self, parent, variable: tk.BooleanVar, command=None, width=42, height=22):
        super().__init__(parent, width=width, height=height, bg=parent["bg"], highlightthickness=0)
        self._var = variable
        self._command = command
        self._width, self._height = width, height
        self.bind("<Button-1>", self._toggle)
        self._var.trace_add("write", lambda *_: self._draw())
        self._draw()

    def set_enabled(self, enabled: bool):
        self.unbind("<Button-1>")
        if enabled:
            self.bind("<Button-1>", self._toggle)
        self._draw(enabled)

    def _toggle(self, _event=None):
        self._var.set(not self._var.get())
        if self._command:
            self._command()

    def _draw(self, enabled=True):
        self.delete("all")
        on = self._var.get()
        color = ACCENT if on else "#4a4b4e"
        r = self._height / 2
        self.create_oval(0, 0, self._height, self._height, fill=color, outline="")
        self.create_rectangle(r, 0, self._width - r, self._height, fill=color, outline="")
        self.create_oval(self._width - self._height, 0, self._width, self._height, fill=color, outline="")
        knob_x = (self._width - r) if on else r
        self.create_oval(knob_x - r + 3, 3, knob_x + r - 3, self._height - 3, fill="#f2f2f2", outline="")


class TranslatedCombo:
    """A readonly ttk.Combobox that shows translated labels while keeping a
    language-independent canonical value in sync on the given StringVar."""

    def __init__(self, parent, canonical_var: tk.StringVar, options, lang, style="Dark.TCombobox", width=10):
        self._canonical_var = canonical_var
        self._options = list(options)
        self._display_var = tk.StringVar()
        self.widget = ttk.Combobox(
            parent, textvariable=self._display_var, values=[], state="readonly",
            width=width, style=style,
        )
        self.widget.bind("<<ComboboxSelected>>", self._on_select)
        self.widget.pack(anchor="w", pady=(2, 0))
        self.refresh(lang)

    def _on_select(self, _event=None):
        idx = self.widget.current()
        if idx >= 0:
            self._canonical_var.set(self._options[idx])

    def refresh(self, lang):
        labels = [i18n.enum_label(o, lang) for o in self._options]
        self.widget["values"] = labels
        current = self._canonical_var.get()
        idx = self._options.index(current) if current in self._options else 0
        self._display_var.set(labels[idx])


class AutoClickerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Auto Clicker")
        self.configure(bg=BG)
        self.resizable(False, False)
        self._set_window_icon()

        self.lang = i18n.LANGUAGES[0]
        self.theme = "dark"
        self._i18n_labels = []  # (widget, string_key)
        self._i18n_enum_labels = []  # (widget, canonical_enum_value)
        self._i18n_combos = []  # [TranslatedCombo, ...]
        self._pick_btn_state = "idle"
        self._record_btn_state = "idle"

        self.engine = ClickerEngine(on_state_change=self._handle_engine_state)
        self.hotkey = HotkeyManager(on_trigger=self._handle_hotkey_trigger)
        self._recording_hotkey = False

        self._init_vars()
        self._build_ui()
        self._update_cps_label()
        self._lock_window_size()
        self._tray_icon = None
        self._start_tray()
        self.protocol("WM_DELETE_WINDOW", self._minimize_to_tray)

    # ------------------------------------------------------------------ tray
    def _start_tray(self):
        icon_path = _resource_path(os.path.join("assets", "AutoClicker.ico"))
        self._tray_icon = TrayIcon(
            icon_path, get_lang=lambda: self.lang,
            on_show=self._restore_from_tray, on_quit=self._quit_app,
        )
        self._tray_icon.start()

    def _minimize_to_tray(self):
        self.withdraw()

    def _restore_from_tray(self):
        self.after(0, self._show_window)

    def _show_window(self):
        self.deiconify()
        self.lift()
        # Some Linux window managers (notably GNOME/Mutter) block programmatic
        # focus-stealing, so the window can come back mapped yet stay behind
        # others with no visible sign it reappeared. Toggling topmost briefly
        # forces it to the front regardless.
        self.attributes("-topmost", True)
        self.after(200, lambda: self.attributes("-topmost", False))
        self.focus_force()

    def _quit_app(self):
        self.after(0, self._do_quit)

    def _do_quit(self):
        self.engine.stop()
        self.hotkey.stop()
        if self._tray_icon:
            self._tray_icon.stop()
        self.destroy()

    def _set_window_icon(self):
        # .ico + iconbitmap only works on Windows; .png + iconphoto is the
        # cross-platform way and covers Linux (and Windows too, as a fallback).
        ico_path = _resource_path(os.path.join("assets", "AutoClicker.ico"))
        if os.path.exists(ico_path):
            try:
                self.iconbitmap(default=ico_path)
            except tk.TclError:
                pass

        png_path = _resource_path(os.path.join("assets", "AutoClicker.png"))
        if os.path.exists(png_path):
            try:
                self._icon_image = tk.PhotoImage(file=png_path)
                self.iconphoto(True, self._icon_image)
            except tk.TclError:
                pass

    def _lock_window_size(self):
        """Fix the window to the largest size any language needs, so
        switching UA/RU/EN never resizes it (translations vary in length)."""
        self.update_idletasks()
        max_w, max_h = self.winfo_reqwidth(), self.winfo_reqheight()
        start_lang = self.lang
        for lang in i18n.LANGUAGES:
            self.lang = lang
            self._apply_language()
            self.update_idletasks()
            max_w = max(max_w, self.winfo_reqwidth())
            max_h = max(max_h, self.winfo_reqheight())
        self.lang = start_lang
        self._apply_language()
        self.geometry(f"{max_w + 8}x{max_h + 4}")

    # ------------------------------------------------------------------ vars
    def _init_vars(self):
        self.var_hours = tk.StringVar(value="0")
        self.var_mins = tk.StringVar(value="0")
        self.var_secs = tk.StringVar(value="0")
        self.var_ms = tk.StringVar(value="100")
        self.var_random = tk.BooleanVar(value=False)
        self.var_random_ms = tk.StringVar(value="0")

        self.var_button = tk.StringVar(value=ClickButton.LEFT.value)
        self.var_click_type = tk.StringVar(value=ClickType.SINGLE.value)

        self.var_repeat_mode = tk.StringVar(value="forever")
        self.var_repeat_count = tk.StringVar(value="1")

        self.var_cursor_mode = tk.StringVar(value=CursorMode.CURRENT.value)
        self.var_fixed_x = tk.StringVar(value="0")
        self.var_fixed_y = tk.StringVar(value="0")

        self.var_cps = tk.StringVar(value="")
        self.var_hotkey_label = tk.StringVar(value=self.hotkey.label())
        self.var_status = tk.StringVar(value=i18n.t("idle", self.lang))

        for v in (self.var_hours, self.var_mins, self.var_secs, self.var_ms):
            v.trace_add("write", lambda *_: self._update_cps_label())

    # ------------------------------------------------------------------- ui
    def _build_ui(self):
        self._section_top_bar()
        self._section_interval()
        self._separator()
        self._section_click_options()
        self._separator()
        self._section_click_repeat()
        self._separator()
        self._section_cursor_position()
        self._separator()
        self._section_bottom_bar()

    def _separator(self):
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=16, pady=10)

    def _header(self, key):
        lbl = tk.Label(self, text=i18n.t(key, self.lang), bg=BG, fg=FG, font=FONT_BOLD)
        lbl.pack(anchor="w", padx=16, pady=(4, 6))
        self._i18n_labels.append((lbl, key))
        return lbl

    def _label(self, parent, key, fg=None, font=FONT, **pack_kwargs):
        lbl = tk.Label(parent, text=i18n.t(key, self.lang), bg=BG, fg=(FG if fg is None else fg), font=font)
        lbl.pack(**pack_kwargs)
        self._i18n_labels.append((lbl, key))
        return lbl

    def _labeled_entry(self, parent, textvariable, width=4):
        e = tk.Entry(
            parent, textvariable=textvariable, width=width, bg=ENTRY_BG, fg=FG,
            insertbackground=FG, relief="flat", justify="center", font=FONT,
        )
        e.pack(side="left", ipady=3)
        return e

    # -- Language & theme switchers -----------------------------------------
    def _section_top_bar(self):
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=16, pady=(12, 0))

        lang_row = tk.Frame(row, bg=BG)
        lang_row.pack(side="left")
        self._lang_buttons = {}
        for code in i18n.LANGUAGES:
            btn = tk.Button(
                lang_row, text=code, command=lambda c=code: self._set_language(c),
                relief="flat", font=FONT_SMALL, padx=8,
            )
            btn.pack(side="left", padx=(0, 4))
            self._lang_buttons[code] = btn

        theme_row = tk.Frame(row, bg=BG)
        theme_row.pack(side="right")
        self._theme_buttons = {}
        for name, key in (("dark", "theme_dark"), ("light", "theme_light")):
            btn = tk.Button(
                theme_row, text=i18n.t(key, self.lang), command=lambda n=name: self._set_theme(n),
                relief="flat", font=FONT_SMALL, padx=8,
            )
            btn.pack(side="left", padx=(4, 0))
            self._i18n_labels.append((btn, key))
            self._theme_buttons[name] = btn

        self._update_lang_buttons()
        self._update_theme_buttons()

    def _set_language(self, lang):
        if lang == self.lang:
            return
        self.lang = lang
        self._apply_language()

    def _update_lang_buttons(self):
        for code, btn in self._lang_buttons.items():
            active = code == self.lang
            btn.config(
                bg=ACCENT if active else ENTRY_BG,
                fg="#0f1a12" if active else FG,
                activebackground=ACCENT if active else BORDER,
            )

    def _set_theme(self, theme):
        if theme == self.theme:
            return
        self.theme = theme
        _apply_theme_colors(theme)
        self._rebuild_ui()

    def _update_theme_buttons(self):
        for name, btn in self._theme_buttons.items():
            active = name == self.theme
            btn.config(
                bg=ACCENT if active else ENTRY_BG,
                fg="#0f1a12" if active else FG,
                activebackground=ACCENT if active else BORDER,
            )

    def _rebuild_ui(self):
        for child in self.winfo_children():
            child.destroy()
        self.configure(bg=BG)
        self._i18n_labels = []
        self._i18n_enum_labels = []
        self._i18n_combos = []
        self._build_ui()
        self._apply_engine_state(self.engine.running)

    def _apply_language(self):
        lang = self.lang
        for widget, key in self._i18n_labels:
            widget.config(text=i18n.t(key, lang))
        for widget, value in self._i18n_enum_labels:
            widget.config(text=i18n.enum_label(value, lang))
        for combo in self._i18n_combos:
            combo.refresh(lang)
        self._update_cps_label()
        self._set_pick_state(self._pick_btn_state == "picking")
        self._set_record_state(self._record_btn_state == "recording")
        self._apply_engine_state(self.engine.running)
        self._update_lang_buttons()

    # -- Interval Configuration -------------------------------------------
    def _section_interval(self):
        self._header("interval_configuration")

        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=16)
        tk.Label(row, textvariable=self.var_cps, bg=BG, fg=FG, font=FONT).pack(side="left")

        fields = tk.Frame(self, bg=BG)
        fields.pack(fill="x", padx=16, pady=(8, 0))
        for var, key in (
            (self.var_hours, "hours"), (self.var_mins, "mins"),
            (self.var_secs, "secs"), (self.var_ms, "milliseconds"),
        ):
            self._labeled_entry(fields, var)
            self._label(fields, key, fg=FG_MUTED, font=FONT, side="left", padx=(4, 12))

        rnd = tk.Frame(self, bg=BG)
        rnd.pack(fill="x", padx=16, pady=(10, 0))
        self._random_switch = ToggleSwitch(rnd, self.var_random, command=self._on_random_toggle)
        self._random_switch.pack(side="left")
        self._label(rnd, "random_offset", side="left", padx=8)
        self._random_entry = self._labeled_entry(rnd, self.var_random_ms)
        self._label(rnd, "ms", fg=FG_MUTED, font=FONT, side="left", padx=4)
        self._random_entry.config(state="disabled")

    def _on_random_toggle(self):
        self._random_entry.config(state="normal" if self.var_random.get() else "disabled")

    def _update_cps_label(self):
        cfg = ClickerConfig(
            hours=_int(self.var_hours), minutes=_int(self.var_mins),
            seconds=_int(self.var_secs), milliseconds=_int(self.var_ms, 100),
        )
        self.var_cps.set(i18n.t("standard_interval", self.lang, cps=cfg.cps()))

    # -- Click Options ------------------------------------------------------
    def _section_click_options(self):
        self._header("click_options")
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=16)

        col1 = tk.Frame(row, bg=BG)
        col1.pack(side="left", padx=(0, 24))
        self._label(col1, "mouse_button", fg=FG_MUTED, font=FONT_SMALL, anchor="w")
        self._combo(col1, self.var_button, [b.value for b in ClickButton])

        col2 = tk.Frame(row, bg=BG)
        col2.pack(side="left")
        self._label(col2, "click_type", fg=FG_MUTED, font=FONT_SMALL, anchor="w")
        self._combo(col2, self.var_click_type, [c.value for c in ClickType])

    def _combo(self, parent, var, values):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Dark.TCombobox", fieldbackground=ENTRY_BG, background=ENTRY_BG,
            foreground=FG, arrowcolor=FG, bordercolor=BORDER, lightcolor=ENTRY_BG,
            darkcolor=ENTRY_BG, selectbackground=ENTRY_BG, selectforeground=FG,
            insertcolor=FG, padding=4,
        )
        style.map(
            "Dark.TCombobox",
            fieldbackground=[("readonly", ENTRY_BG), ("disabled", ENTRY_BG)],
            foreground=[("readonly", FG), ("disabled", FG_MUTED)],
            selectbackground=[("readonly", ENTRY_BG)],
            selectforeground=[("readonly", FG)],
            background=[("readonly", ENTRY_BG)],
        )
        self.option_add("*TCombobox*Listbox.background", ENTRY_BG)
        self.option_add("*TCombobox*Listbox.foreground", FG)
        self.option_add("*TCombobox*Listbox.selectBackground", ACCENT)
        self.option_add("*TCombobox*Listbox.selectForeground", "#0f1a12")
        combo = TranslatedCombo(parent, var, values, self.lang)
        self._i18n_combos.append(combo)
        return combo

    # -- Click Repeat ---------------------------------------------------
    def _section_click_repeat(self):
        self._header("click_repeat")

        row1 = tk.Frame(self, bg=BG)
        row1.pack(fill="x", padx=16, pady=2)
        self._radio(row1, self.var_repeat_mode, "count", "repeat")
        self._labeled_entry(row1, self.var_repeat_count)
        self._label(row1, "times", fg=FG_MUTED, font=FONT, side="left", padx=(4, 0))

        row2 = tk.Frame(self, bg=BG)
        row2.pack(fill="x", padx=16, pady=2)
        self._radio(row2, self.var_repeat_mode, "forever", "repeat_until_stopped")

    def _radio(self, parent, var, value, key):
        rb = tk.Radiobutton(
            parent, text=i18n.t(key, self.lang), variable=var, value=value, bg=BG, fg=FG,
            selectcolor=ENTRY_BG, activebackground=BG, activeforeground=FG,
            font=FONT, highlightthickness=0,
        )
        rb.pack(side="left", padx=(0, 8))
        self._i18n_labels.append((rb, key))
        return rb

    def _radio_enum(self, parent, var, value):
        rb = tk.Radiobutton(
            parent, text=i18n.enum_label(value, self.lang), variable=var, value=value, bg=BG, fg=FG,
            selectcolor=ENTRY_BG, activebackground=BG, activeforeground=FG,
            font=FONT, highlightthickness=0,
        )
        rb.pack(side="left", padx=(0, 8))
        self._i18n_enum_labels.append((rb, value))
        return rb

    # -- Cursor Position --------------------------------------------------
    def _section_cursor_position(self):
        self._header("cursor_position")

        self._radio_full(CursorMode.CURRENT.value)

        fixed_row = tk.Frame(self, bg=BG)
        fixed_row.pack(fill="x", padx=16, pady=2)
        self._radio_enum(fixed_row, self.var_cursor_mode, CursorMode.FIXED.value)
        self._pick_btn = tk.Button(
            fixed_row, command=self._start_position_pick,
            bg=ENTRY_BG, fg=FG, relief="flat", font=FONT_SMALL, activebackground=BORDER,
        )
        self._pick_btn.pack(side="left", padx=8)
        self._set_pick_state(self._pick_btn_state == "picking")
        tk.Label(fixed_row, text="X", bg=BG, fg=FG_MUTED, font=FONT).pack(side="left", padx=(8, 2))
        self._labeled_entry(fixed_row, self.var_fixed_x)
        tk.Label(fixed_row, text="Y", bg=BG, fg=FG_MUTED, font=FONT).pack(side="left", padx=(8, 2))
        self._labeled_entry(fixed_row, self.var_fixed_y)

    def _radio_full(self, value):
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=16, pady=2)
        self._radio_enum(row, self.var_cursor_mode, value)

    def _start_position_pick(self):
        self._set_pick_state(True)

        def captured(pos):
            x, y = pos
            self.after(0, lambda: self._on_position_captured(x, y))

        PositionPicker(on_captured=captured)

    def _on_position_captured(self, x, y):
        self.var_fixed_x.set(str(int(x)))
        self.var_fixed_y.set(str(int(y)))
        self.var_cursor_mode.set(CursorMode.FIXED.value)
        self._set_pick_state(False)

    def _set_pick_state(self, picking: bool):
        self._pick_btn_state = "picking" if picking else "idle"
        key = "move_mouse_enter" if picking else "set_position"
        self._pick_btn.config(text=i18n.t(key, self.lang), state="disabled" if picking else "normal")

    # -- Bottom bar ---------------------------------------------------------
    def _section_bottom_bar(self):
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=16, pady=(0, 16))

        self._start_btn = tk.Button(
            row, textvariable=self._start_button_text(), command=self._toggle_engine,
            bg=ACCENT, fg="#0f1a12", relief="flat", font=FONT_BOLD,
            activebackground=ACCENT, padx=12, pady=6,
        )
        self._start_btn.pack(side="left")

        self._quit_btn = tk.Button(
            row, text=i18n.t("tray_exit", self.lang), command=self._do_quit,
            bg=ENTRY_BG, fg=FG, relief="flat", font=FONT_SMALL, activebackground=BORDER,
        )
        self._quit_btn.pack(side="left", padx=(8, 0))
        self._i18n_labels.append((self._quit_btn, "tray_exit"))

        self._record_btn = tk.Button(
            row, command=self._start_hotkey_record,
            bg=ENTRY_BG, fg=FG, relief="flat", font=FONT_SMALL, activebackground=BORDER,
        )
        self._record_btn.pack(side="right")
        self._set_record_state(self._record_btn_state == "recording")

        tk.Label(row, textvariable=self.var_status, bg=BG, fg=FG_MUTED, font=FONT_SMALL).pack(
            side="right", padx=10
        )

    def _start_button_text(self):
        self._btn_text = tk.StringVar()
        self.var_hotkey_label.trace_add("write", lambda *_: self._refresh_start_label())
        self._refresh_start_label()
        return self._btn_text

    def _refresh_start_label(self):
        running = self.engine.running
        symbol = "■" if running else "▶"
        text = i18n.t("stop" if running else "start", self.lang)
        self._btn_text.set(f"{symbol} {text}  [{self.var_hotkey_label.get()}]")

    def _start_hotkey_record(self):
        self._set_record_state(True)

        def captured(key):
            from engine import key_label
            label = key_label(key)
            self.after(0, lambda: self._on_hotkey_captured(label))

        self.hotkey.record_next(captured)

    def _on_hotkey_captured(self, label):
        self.var_hotkey_label.set(label)
        self._set_record_state(False)

    def _set_record_state(self, recording: bool):
        self._record_btn_state = "recording" if recording else "idle"
        key = "press_any_key" if recording else "record_hotkey"
        self._record_btn.config(text=i18n.t(key, self.lang), state="disabled" if recording else "normal")

    # ------------------------------------------------------------- actions
    def _build_config(self) -> ClickerConfig:
        return ClickerConfig(
            hours=_int(self.var_hours), minutes=_int(self.var_mins),
            seconds=_int(self.var_secs), milliseconds=_int(self.var_ms, 100),
            random_offset_enabled=self.var_random.get(),
            random_offset_ms=_int(self.var_random_ms),
            button=ClickButton(self.var_button.get()),
            click_type=ClickType(self.var_click_type.get()),
            repeat_forever=(self.var_repeat_mode.get() == "forever"),
            repeat_count=max(_int(self.var_repeat_count, 1), 1),
            cursor_mode=CursorMode(self.var_cursor_mode.get()),
            fixed_x=_int(self.var_fixed_x), fixed_y=_int(self.var_fixed_y),
        )

    def _toggle_engine(self):
        self.engine.toggle(self._build_config())

    def _handle_hotkey_trigger(self):
        self.after(0, self._toggle_engine)

    def _handle_engine_state(self, running: bool):
        self.after(0, lambda: self._apply_engine_state(running))

    def _apply_engine_state(self, running: bool):
        self.var_status.set(i18n.t("clicking" if running else "idle", self.lang))
        self._start_btn.config(bg=ACCENT_STOP if running else ACCENT)
        self._refresh_start_label()

