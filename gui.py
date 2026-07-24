"""Dark-themed tkinter GUI for the auto clicker."""
import tkinter as tk
from tkinter import ttk, filedialog

from engine import (
    ClickButton,
    ClickerConfig,
    ClickerEngine,
    ClickType,
    CursorMode,
    HotkeyManager,
    PositionPicker,
)

BG = "#1e1f22"
PANEL = "#242529"
FG = "#e8e8e8"
FG_MUTED = "#9a9a9a"
ACCENT = "#3ddc84"
ACCENT_STOP = "#e0525a"
ENTRY_BG = "#2c2d30"
BORDER = "#38393d"

FONT = ("Sans", 10)
FONT_BOLD = ("Sans", 11, "bold")
FONT_SMALL = ("Sans", 8)


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


class AutoClickerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Auto Clicker")
        self.configure(bg=BG)
        self.resizable(False, False)

        self.engine = ClickerEngine(on_state_change=self._handle_engine_state)
        self.hotkey = HotkeyManager(on_trigger=self._handle_hotkey_trigger)
        self._recording_hotkey = False

        self._init_vars()
        self._build_ui()
        self._update_cps_label()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

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
        self.var_image_path = tk.StringVar(value="")

        self.var_cps = tk.StringVar(value="")
        self.var_hotkey_label = tk.StringVar(value=self.hotkey.label())
        self.var_status = tk.StringVar(value="Idle")

        for v in (self.var_hours, self.var_mins, self.var_secs, self.var_ms):
            v.trace_add("write", lambda *_: self._update_cps_label())

    # ------------------------------------------------------------------- ui
    def _build_ui(self):
        pad = dict(padx=16, pady=(10, 4))

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

    def _header(self, text):
        tk.Label(self, text=text, bg=BG, fg=FG, font=FONT_BOLD).pack(
            anchor="w", padx=16, pady=(4, 6)
        )

    def _labeled_entry(self, parent, textvariable, width=4):
        e = tk.Entry(
            parent, textvariable=textvariable, width=width, bg=ENTRY_BG, fg=FG,
            insertbackground=FG, relief="flat", justify="center", font=FONT,
        )
        e.pack(side="left", ipady=3)
        return e

    # -- Interval Configuration -------------------------------------------
    def _section_interval(self):
        self._header("Interval Configuration")

        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=16)
        self._standard_switch = ToggleSwitch(row, tk.BooleanVar(value=True))
        self._standard_switch.set_enabled(False)  # always on; standard mode only
        self._standard_switch.pack(side="left")
        tk.Label(row, textvariable=self.var_cps, bg=BG, fg=FG, font=FONT).pack(side="left", padx=8)

        fields = tk.Frame(self, bg=BG)
        fields.pack(fill="x", padx=16, pady=(8, 0))
        for var, label in (
            (self.var_hours, "hours"), (self.var_mins, "mins"),
            (self.var_secs, "secs"), (self.var_ms, "milliseconds"),
        ):
            self._labeled_entry(fields, var)
            tk.Label(fields, text=label, bg=BG, fg=FG_MUTED, font=FONT).pack(side="left", padx=(4, 12))

        rnd = tk.Frame(self, bg=BG)
        rnd.pack(fill="x", padx=16, pady=(10, 0))
        self._random_switch = ToggleSwitch(rnd, self.var_random, command=self._on_random_toggle)
        self._random_switch.pack(side="left")
        tk.Label(rnd, text="Random Offset ±", bg=BG, fg=FG, font=FONT).pack(side="left", padx=8)
        self._random_entry = self._labeled_entry(rnd, self.var_random_ms)
        tk.Label(rnd, text="ms", bg=BG, fg=FG_MUTED, font=FONT).pack(side="left", padx=4)
        self._random_entry.config(state="disabled")

    def _on_random_toggle(self):
        self._random_entry.config(state="normal" if self.var_random.get() else "disabled")

    def _update_cps_label(self):
        cfg = ClickerConfig(
            hours=_int(self.var_hours), minutes=_int(self.var_mins),
            seconds=_int(self.var_secs), milliseconds=_int(self.var_ms, 100),
        )
        self.var_cps.set(f"Standard Interval (~{cfg.cps():.2f} CPS)")

    # -- Click Options ------------------------------------------------------
    def _section_click_options(self):
        self._header("Click Options")
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=16)

        col1 = tk.Frame(row, bg=BG)
        col1.pack(side="left", padx=(0, 24))
        tk.Label(col1, text="MOUSE BUTTON", bg=BG, fg=FG_MUTED, font=FONT_SMALL).pack(anchor="w")
        self._combo(col1, self.var_button, [b.value for b in ClickButton])

        col2 = tk.Frame(row, bg=BG)
        col2.pack(side="left")
        tk.Label(col2, text="CLICK TYPE", bg=BG, fg=FG_MUTED, font=FONT_SMALL).pack(anchor="w")
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
        cb = ttk.Combobox(
            parent, textvariable=var, values=values, state="readonly",
            width=10, style="Dark.TCombobox",
        )
        cb.pack(anchor="w", pady=(2, 0))
        return cb

    # -- Click Repeat ---------------------------------------------------
    def _section_click_repeat(self):
        self._header("Click Repeat")

        row1 = tk.Frame(self, bg=BG)
        row1.pack(fill="x", padx=16, pady=2)
        self._radio(row1, self.var_repeat_mode, "count", "Repeat")
        self._labeled_entry(row1, self.var_repeat_count)
        tk.Label(row1, text="times", bg=BG, fg=FG_MUTED, font=FONT).pack(side="left", padx=(4, 0))

        row2 = tk.Frame(self, bg=BG)
        row2.pack(fill="x", padx=16, pady=2)
        self._radio(row2, self.var_repeat_mode, "forever", "Repeat until stopped")

    def _radio(self, parent, var, value, text):
        rb = tk.Radiobutton(
            parent, text=text, variable=var, value=value, bg=BG, fg=FG,
            selectcolor=ENTRY_BG, activebackground=BG, activeforeground=FG,
            font=FONT, highlightthickness=0,
        )
        rb.pack(side="left", padx=(0, 8))
        return rb

    # -- Cursor Position --------------------------------------------------
    def _section_cursor_position(self):
        self._header("Cursor Position")

        self._radio_full(CursorMode.CURRENT.value, "Cursor Location")

        fixed_row = tk.Frame(self, bg=BG)
        fixed_row.pack(fill="x", padx=16, pady=2)
        self._radio(fixed_row, self.var_cursor_mode, CursorMode.FIXED.value, "Fixed Location")
        tk.Label(fixed_row, text="X", bg=BG, fg=FG_MUTED, font=FONT).pack(side="left", padx=(8, 2))
        self._labeled_entry(fixed_row, self.var_fixed_x)
        tk.Label(fixed_row, text="Y", bg=BG, fg=FG_MUTED, font=FONT).pack(side="left", padx=(8, 2))
        self._labeled_entry(fixed_row, self.var_fixed_y)
        self._pick_btn = tk.Button(
            fixed_row, text="Set Position", command=self._start_position_pick,
            bg=ENTRY_BG, fg=FG, relief="flat", font=FONT_SMALL, activebackground=BORDER,
        )
        self._pick_btn.pack(side="left", padx=8)

        image_row = tk.Frame(self, bg=BG)
        image_row.pack(fill="x", padx=16, pady=2)
        self._radio(image_row, self.var_cursor_mode, CursorMode.IMAGE.value, "Find Image")
        tk.Button(
            image_row, text="Browse...", command=self._browse_image,
            bg=ENTRY_BG, fg=FG, relief="flat", font=FONT_SMALL, activebackground=BORDER,
        ).pack(side="left", padx=8)
        tk.Label(image_row, textvariable=self.var_image_path, bg=BG, fg=FG_MUTED, font=FONT_SMALL).pack(
            side="left", padx=4
        )

    def _radio_full(self, value, text):
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=16, pady=2)
        self._radio(row, self.var_cursor_mode, value, text)

    def _browse_image(self):
        path = filedialog.askopenfilename(
            title="Select target image",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")],
        )
        if path:
            self.var_image_path.set(path)
            self.var_cursor_mode.set(CursorMode.IMAGE.value)

    def _start_position_pick(self):
        self._pick_btn.config(text="Move mouse, press Enter...", state="disabled")

        def captured(pos):
            x, y = pos
            self.after(0, lambda: self._on_position_captured(x, y))

        PositionPicker(on_captured=captured)

    def _on_position_captured(self, x, y):
        self.var_fixed_x.set(str(int(x)))
        self.var_fixed_y.set(str(int(y)))
        self.var_cursor_mode.set(CursorMode.FIXED.value)
        self._pick_btn.config(text="Set Position", state="normal")

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

        self._record_btn = tk.Button(
            row, text="Record Hotkey", command=self._start_hotkey_record,
            bg=ENTRY_BG, fg=FG, relief="flat", font=FONT_SMALL, activebackground=BORDER,
        )
        self._record_btn.pack(side="right")

        tk.Label(row, textvariable=self.var_status, bg=BG, fg=FG_MUTED, font=FONT_SMALL).pack(
            side="right", padx=10
        )

    def _start_button_text(self):
        self._btn_text = tk.StringVar(value=f"▶ Start  [{self.var_hotkey_label.get()}]")
        self.var_hotkey_label.trace_add("write", lambda *_: self._refresh_start_label())
        return self._btn_text

    def _refresh_start_label(self):
        symbol = "■ Stop " if self.engine.running else "▶ Start"
        self._btn_text.set(f"{symbol}  [{self.var_hotkey_label.get()}]")

    def _start_hotkey_record(self):
        self._record_btn.config(text="Press any key...", state="disabled")

        def captured(key):
            from engine import key_label
            label = key_label(key)
            self.after(0, lambda: self._on_hotkey_captured(label))

        self.hotkey.record_next(captured)

    def _on_hotkey_captured(self, label):
        self.var_hotkey_label.set(label)
        self._record_btn.config(text="Record Hotkey", state="normal")

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
            image_path=self.var_image_path.get(),
        )

    def _toggle_engine(self):
        self.engine.toggle(self._build_config())

    def _handle_hotkey_trigger(self):
        self.after(0, self._toggle_engine)

    def _handle_engine_state(self, running: bool):
        self.after(0, lambda: self._apply_engine_state(running))

    def _apply_engine_state(self, running: bool):
        self.var_status.set("Clicking..." if running else "Idle")
        self._start_btn.config(bg=ACCENT_STOP if running else ACCENT)
        self._refresh_start_label()

    def _on_close(self):
        self.engine.stop()
        self.hotkey.stop()
        self.destroy()
