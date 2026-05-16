#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MARIE Calculator Simulator — Professional GUI Edition
Ports all C logic to Python and wraps it in an animated dark-themed interface.
"""

import tkinter as tk
from tkinter import ttk
import threading
import queue
import time

# ── Palette (Phosphor Green / CRT Terminal) ───────────────────────────────────
BG       = "#040c04"
PANEL    = "#071207"
PANEL2   = "#0a1a0a"
BORDER   = "#0f3316"
ACCENT   = "#00ff41"
GREEN    = "#00ff41"
YELLOW   = "#ffaa00"
RED      = "#ff4444"
ORANGE   = "#ffaa00"
PURPLE   = "#cc44ff"
CYAN     = "#00ccff"
TEXT     = "#008829"
MUTED    = "#004d14"
WHITE    = "#00ff41"
FLASH    = "#00ff41"

MONO     = ("Courier New", 11)
MONO_SM  = ("Courier New", 9)
MONO_LG  = ("Courier New", 13, "bold")
HEAD     = ("Courier New", 9, "bold")
REG_FONT = ("Courier New", 30, "bold")
BTN_FONT = ("Courier New", 10, "bold")
TITLE_F  = ("Courier New", 14, "bold")
LABEL_F  = ("Courier New", 9)

# ── MARIE Machine State ───────────────────────────────────────────────────────
AC_val  = 0
MAR_val = 0
MBR_val = 0
memory  = [0] * 16
MEM_OPERAND = 5
MEM_TEMP    = 6

# Queue for thread → UI communication
ui_queue: queue.Queue = queue.Queue()


def _q(*args):
    ui_queue.put(args)


# ── MARIE Primitive Instructions ──────────────────────────────────────────────

def exec_input(value):
    global AC_val
    _q("trace", "inst", f"  [EXECUTE  INPUT]")
    AC_val = value
    _q("trace", "reg",  f"    AC  ← input        AC  = {AC_val}")
    _q("reg", "AC", AC_val)


def exec_store(addr):
    global MAR_val, MBR_val
    _q("trace", "inst", f"  [EXECUTE  STORE {addr}]")
    MAR_val = addr
    _q("trace", "reg",  f"    MAR ← {addr:<12}    MAR = {MAR_val}")
    _q("reg", "MAR", MAR_val)
    MBR_val = AC_val
    _q("trace", "reg",  f"    MBR ← AC           MBR = {MBR_val}")
    _q("reg", "MBR", MBR_val)
    memory[MAR_val] = MBR_val
    _q("trace", "mem",  f"    M[MAR] ← MBR       M[{MAR_val}] = {memory[MAR_val]}")
    _q("mem", MAR_val, MBR_val)


def exec_load(addr):
    global MAR_val, MBR_val, AC_val
    _q("trace", "inst", f"  [EXECUTE  LOAD {addr}]")
    MAR_val = addr
    _q("trace", "reg",  f"    MAR ← {addr:<12}    MAR = {MAR_val}")
    _q("reg", "MAR", MAR_val)
    MBR_val = memory[MAR_val]
    _q("trace", "reg",  f"    MBR ← M[MAR]       MBR = {MBR_val}")
    _q("reg", "MBR", MBR_val)
    AC_val = MBR_val
    _q("trace", "reg",  f"    AC  ← MBR          AC  = {AC_val}")
    _q("reg", "AC", AC_val)


def exec_add(addr):
    global MAR_val, MBR_val, AC_val
    _q("trace", "inst", f"  [EXECUTE  ADD {addr}]")
    MAR_val = addr
    _q("trace", "reg",  f"    MAR ← {addr:<12}    MAR = {MAR_val}")
    _q("reg", "MAR", MAR_val)
    MBR_val = memory[MAR_val]
    _q("trace", "reg",  f"    MBR ← M[MAR]       MBR = {MBR_val}")
    _q("reg", "MBR", MBR_val)
    old = AC_val
    AC_val = AC_val + MBR_val
    _q("trace", "result", f"    AC  ← AC + MBR     {old} + {MBR_val} = {AC_val}")
    _q("reg", "AC", AC_val)


def exec_subt(addr):
    global MAR_val, MBR_val, AC_val
    _q("trace", "inst", f"  [EXECUTE  SUBT {addr}]")
    MAR_val = addr
    _q("trace", "reg",  f"    MAR ← {addr:<12}    MAR = {MAR_val}")
    _q("reg", "MAR", MAR_val)
    MBR_val = memory[MAR_val]
    _q("trace", "reg",  f"    MBR ← M[MAR]       MBR = {MBR_val}")
    _q("reg", "MBR", MBR_val)
    old = AC_val
    AC_val = AC_val - MBR_val
    _q("trace", "result", f"    AC  ← AC − MBR     {old} − {MBR_val} = {AC_val}")
    _q("reg", "AC", AC_val)


def exec_clear():
    global AC_val
    _q("trace", "inst", "  [EXECUTE  CLEAR]")
    AC_val = 0
    _q("trace", "reg",  f"    AC  ← 0            AC  = {AC_val}")
    _q("reg", "AC", AC_val)


def exec_halt():
    _q("trace", "inst",  "  [EXECUTE  HALT]")
    _q("trace", "muted", "    Processor HALTED.")


# ── MARIE High-Level Operations ───────────────────────────────────────────────

def do_add(x):
    _q("trace", "op", f"  ▶ ADD {x}")
    exec_store(MEM_TEMP)
    exec_input(x)
    exec_store(MEM_OPERAND)
    exec_load(MEM_TEMP)
    exec_add(MEM_OPERAND)


def do_subt(x):
    _q("trace", "op", f"  ▶ SUBT {x}")
    exec_store(MEM_TEMP)
    exec_input(x)
    exec_store(MEM_OPERAND)
    exec_load(MEM_TEMP)
    exec_subt(MEM_OPERAND)


def do_clear():
    _q("trace", "op", "  ▶ CLEAR")
    exec_clear()


def marie_set_AC(value):
    do_clear()
    do_add(value)


def marie_sum(data):
    do_clear()
    for v in data:
        do_add(v)
    return AC_val


def marie_average(data):
    global AC_val
    if not data:
        do_clear()
        return AC_val
    marie_sum(data)
    avg = AC_val // len(data)
    _q("trace", "op", f"  ▶ Integer division: {AC_val} ÷ {len(data)} = {avg}")
    marie_set_AC(avg)
    return AC_val


def marie_max(data):
    global AC_val
    if not data:
        do_clear()
        return AC_val
    marie_set_AC(data[0])
    max_val = data[0]
    for v in data[1:]:
        exec_store(MEM_TEMP)
        exec_input(v)
        exec_store(MEM_OPERAND)
        exec_load(MEM_TEMP)
        exec_subt(MEM_OPERAND)
        if AC_val < 0:
            max_val = v
        marie_set_AC(max_val)
    return AC_val


def marie_sort(data):
    global AC_val
    n = len(data)
    if n <= 1:
        if n == 1:
            marie_set_AC(data[0])
        else:
            do_clear()
        return
    for i in range(n - 1):
        for j in range(n - 1 - i):
            marie_set_AC(data[j])
            exec_store(MEM_TEMP)
            exec_input(data[j + 1])
            exec_store(MEM_OPERAND)
            exec_load(MEM_TEMP)
            exec_subt(MEM_OPERAND)
            if AC_val > 0:
                data[j], data[j + 1] = data[j + 1], data[j]
                _q("trace", "op", f"    ↕ Swapped → {data}")
    marie_set_AC(data[0])


# ── GUI Application ───────────────────────────────────────────────────────────

class MARIEApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("MARIE Calculator Simulator")
        self.root.configure(bg=BG)
        self.root.geometry("1160x740")
        self.root.resizable(True, True)
        self.root.minsize(960, 620)

        self._busy        = False
        self._halted      = False
        self._reg_widgets = {}   # name → (border_frame, value_label)
        self._mem_widgets = {}   # index → (inner_frame, val_label)
        self._flash_jobs  = {}
        self._proc_buttons = []  # disabled while halted

        self._build_ui()
        self._poll()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_header()
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x")

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=14, pady=14)

        # Left sidebar --------------------------------------------------------
        sidebar = tk.Frame(body, bg=BG, width=268)
        sidebar.pack(side="left", fill="y", padx=(0, 14))
        sidebar.pack_propagate(False)
        self._build_registers(sidebar)
        self._build_memory(sidebar)

        # Right pane ----------------------------------------------------------
        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True)
        self._build_trace(right)
        self._build_buttons(right)
        self._build_statusbar(right)

    def _build_header(self):
        bar = tk.Frame(self.root, bg=PANEL, height=58)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        # left: logo + title
        lf = tk.Frame(bar, bg=PANEL)
        lf.pack(side="left", fill="y", padx=18)

        tk.Label(lf, text="◈", font=("Segoe UI", 18), fg=ACCENT, bg=PANEL
                 ).pack(side="left", padx=(0, 8))
        tk.Label(lf, text="MARIE Calculator Simulator",
                 font=TITLE_F, fg=WHITE, bg=PANEL
                 ).pack(side="left")

        # right: subtitle
        tk.Label(bar,
                 text="Machine Architecture Really Intuitive and Educational  ·  v2.0",
                 font=LABEL_F, fg=MUTED, bg=PANEL
                 ).pack(side="right", padx=18)

    def _section_label(self, parent, text):
        row = tk.Frame(parent, bg=BG)
        row.pack(fill="x", pady=(10, 5))
        tk.Label(row, text=text, font=HEAD, fg=MUTED, bg=BG
                 ).pack(side="left")
        tk.Frame(row, bg=BORDER, height=1
                 ).pack(side="left", fill="x", expand=True, padx=(8, 0))

    # ── Registers panel ───────────────────────────────────────────────────────

    def _build_registers(self, parent):
        self._section_label(parent, "REGISTERS")
        for name in ("AC", "MAR", "MBR"):
            self._make_reg_card(parent, name)

    def _make_reg_card(self, parent, name):
        reg_color = {"AC": GREEN, "MAR": YELLOW, "MBR": CYAN}[name]

        border = tk.Frame(parent, bg=BORDER, padx=1, pady=1)
        border.pack(fill="x", pady=3)

        inner = tk.Frame(border, bg=PANEL, padx=14, pady=10)
        inner.pack(fill="x")

        tk.Label(inner, text=name, font=LABEL_F, fg=MUTED, bg=PANEL
                 ).pack(anchor="w")

        val = tk.Label(inner, text="0", font=REG_FONT, fg=reg_color, bg=PANEL,
                       anchor="e")
        val.pack(fill="x")

        self._reg_widgets[name] = (border, inner, val)

    # ── Memory grid ───────────────────────────────────────────────────────────

    def _build_memory(self, parent):
        self._section_label(parent, "MEMORY  ·  16 words")

        outer = tk.Frame(parent, bg=BORDER, padx=1, pady=1)
        outer.pack(fill="x", pady=(0, 4))

        grid = tk.Frame(outer, bg=PANEL, padx=8, pady=8)
        grid.pack(fill="x")

        for i in range(16):
            row, col = divmod(i, 4)

            cell_bg = tk.Frame(grid, bg=BORDER, padx=1, pady=1)
            cell_bg.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")

            inner = tk.Frame(cell_bg, bg=PANEL2, padx=4, pady=3)
            inner.pack(fill="both")

            # Address label
            addr_txt = f"[{i:02d}]"
            addr_fg  = MUTED
            if i == MEM_OPERAND:
                addr_txt = f"[{i:02d}]*"
                addr_fg  = ACCENT
            elif i == MEM_TEMP:
                addr_txt = f"[{i:02d}]†"
                addr_fg  = YELLOW

            tk.Label(inner, text=addr_txt, font=MONO_SM, fg=addr_fg,
                     bg=PANEL2, width=6).pack()

            val_lbl = tk.Label(inner, text="0", font=MONO_SM, fg=TEXT,
                                bg=PANEL2, width=6)
            val_lbl.pack()

            self._mem_widgets[i] = (cell_bg, inner, val_lbl)

        tk.Label(parent, text="* addr 5 = OPERAND   † addr 6 = TEMP",
                 font=MONO_SM, fg=MUTED, bg=BG
                 ).pack(anchor="w")

    # ── Trace panel ───────────────────────────────────────────────────────────

    def _build_trace(self, parent):
        self._section_label(parent, "EXECUTION TRACE")

        wrap = tk.Frame(parent, bg=BORDER, padx=1, pady=1)
        wrap.pack(fill="both", expand=True, pady=(0, 10))

        inner = tk.Frame(wrap, bg=PANEL)
        inner.pack(fill="both", expand=True)

        self.trace = tk.Text(
            inner,
            bg=PANEL, fg=TEXT,
            font=MONO,
            relief="flat", bd=0,
            state="disabled",
            selectbackground=FLASH,
            insertbackground=WHITE,
            wrap="none",
            padx=12, pady=8,
        )

        vsb = tk.Scrollbar(inner, orient="vertical",
                           command=self.trace.yview, bg=PANEL2,
                           troughcolor=PANEL2, activebackground=BORDER)
        vsb.pack(side="right", fill="y")
        self.trace.pack(side="left", fill="both", expand=True)
        self.trace.configure(yscrollcommand=vsb.set)

        hsb = tk.Scrollbar(parent, orient="horizontal",
                            command=self.trace.xview, bg=PANEL2,
                            troughcolor=PANEL2)
        hsb.pack(fill="x")
        self.trace.configure(xscrollcommand=hsb.set)

        # Color tags
        self.trace.tag_config("op",     foreground=ACCENT,  font=("Consolas", 11, "bold"))
        self.trace.tag_config("inst",   foreground=CYAN)
        self.trace.tag_config("reg",    foreground=TEXT)
        self.trace.tag_config("result", foreground=GREEN,   font=("Consolas", 11, "bold"))
        self.trace.tag_config("mem",    foreground=ORANGE)
        self.trace.tag_config("muted",  foreground=MUTED)
        self.trace.tag_config("sep",    foreground=BORDER)
        self.trace.tag_config("final",  foreground=PURPLE,  font=("Consolas", 11, "bold"))
        self.trace.tag_config("error",  foreground=RED,     font=("Consolas", 11, "bold"))

        self._trace_add("op",    "  MARIE Calculator Simulator — Ready\n")
        self._trace_add("muted", "  AC = MAR = MBR = 0  ·  Memory zeroed\n")
        self._trace_add("sep",   "  " + "─" * 62 + "\n")

    # ── Button bar ────────────────────────────────────────────────────────────

    def _build_buttons(self, parent):
        self._section_label(parent, "OPERATIONS")

        row = tk.Frame(parent, bg=BG)
        row.pack(fill="x")

        ops = [
            ("ADD",     ACCENT,  self._op_add),
            ("SUBT",    RED,     self._op_subt),
            ("CLEAR",   YELLOW,  self._op_clear),
            ("SUM",     GREEN,   self._op_sum),
            ("AVERAGE", CYAN,    self._op_average),
            ("MAX",     ORANGE,  self._op_max),
            ("SORT",    PURPLE,  self._op_sort),
            ("HALT",    RED,     self._op_halt),
            ("RESET",   MUTED,   self._op_reset),
            ("EXIT",    RED,     self.root.quit),
        ]

        # Processor ops get disabled on HALT; RESET and EXIT stay live
        _proc_op_names = {"ADD", "SUBT", "CLEAR", "SUM", "AVERAGE", "MAX", "SORT", "HALT"}

        self._op_buttons = []
        for name, color, cmd in ops:
            btn = tk.Button(
                row, text=name,
                font=BTN_FONT,
                fg=color, bg=PANEL2,
                activebackground=PANEL, activeforeground=WHITE,
                relief="flat", bd=0,
                padx=14, pady=8,
                cursor="hand2",
                command=cmd,
            )
            btn.pack(side="left", padx=3)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=PANEL,  fg=WHITE))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=PANEL2, fg=c))
            self._op_buttons.append(btn)
            if name in _proc_op_names:
                self._proc_buttons.append(btn)

    def _build_statusbar(self, parent):
        bar = tk.Frame(parent, bg=BG)
        bar.pack(fill="x", pady=(6, 0))

        self.status_lbl = tk.Label(
            bar, text="Ready.",
            font=LABEL_F, fg=MUTED, bg=BG, anchor="w"
        )
        self.status_lbl.pack(side="left")

        self.ac_badge = tk.Label(
            bar, text="AC = 0",
            font=MONO_LG, fg=ACCENT, bg=BG, anchor="e"
        )
        self.ac_badge.pack(side="right", padx=6)

    # ── Trace helpers ─────────────────────────────────────────────────────────

    def _trace_add(self, tag, text):
        self.trace.configure(state="normal")
        self.trace.insert("end", text, tag)
        self.trace.see("end")
        self.trace.configure(state="disabled")

    def _trace_clear(self):
        self.trace.configure(state="normal")
        self.trace.delete("1.0", "end")
        self.trace.configure(state="disabled")

    # ── Register flash animation ──────────────────────────────────────────────

    def _flash_reg(self, name):
        border, inner, val = self._reg_widgets[name]
        border.configure(bg=FLASH)
        inner.configure(bg=PANEL2)
        val.configure(bg=PANEL2, fg=WHITE)
        if name in self._flash_jobs:
            self.root.after_cancel(self._flash_jobs[name])
        self._flash_jobs[name] = self.root.after(
            420, lambda: self._restore_reg(name)
        )

    def _restore_reg(self, name):
        reg_color = {"AC": GREEN, "MAR": YELLOW, "MBR": CYAN}[name]
        border, inner, val = self._reg_widgets[name]
        border.configure(bg=BORDER)
        inner.configure(bg=PANEL)
        val.configure(bg=PANEL, fg=reg_color)

    def _set_reg(self, name, value):
        _, _, val = self._reg_widgets[name]
        val.configure(text=str(value))
        self._flash_reg(name)
        if name == "AC":
            self.ac_badge.configure(text=f"AC = {value}")

    # ── Memory flash animation ────────────────────────────────────────────────

    def _flash_mem(self, addr, value):
        border, inner, val = self._mem_widgets[addr]
        val.configure(text=str(value))
        inner.configure(bg=FLASH)
        val.configure(bg=FLASH, fg=WHITE)
        self.root.after(500, lambda: self._restore_mem(addr))

    def _restore_mem(self, addr):
        _, inner, val = self._mem_widgets[addr]
        inner.configure(bg=PANEL2)
        val.configure(bg=PANEL2, fg=TEXT)

    # ── Queue consumer (runs every 25 ms on main thread) ─────────────────────

    def _poll(self):
        try:
            while True:
                item = ui_queue.get_nowait()
                kind = item[0]

                if kind == "trace":
                    _, tag, text = item
                    self._trace_add(tag, text + "\n")

                elif kind == "reg":
                    _, name, value = item
                    self._set_reg(name, value)

                elif kind == "mem":
                    _, addr, val = item
                    self._flash_mem(addr, val)

                elif kind == "done":
                    _, msg = item
                    self._trace_add("final", f"\n  ✓  {msg}\n")
                    self._trace_add("sep",   "  " + "─" * 62 + "\n")
                    self._set_status(f"Done — {msg}", GREEN)
                    self._busy = False
                    self._set_buttons_state("normal")

                elif kind == "status":
                    _, msg, color = item
                    self._set_status(msg, color)

                elif kind == "error":
                    _, msg = item
                    self._trace_add("error", f"\n  ✗  {msg}\n")
                    self._trace_add("sep",   "  " + "─" * 62 + "\n")
                    self._set_status(f"Error: {msg}", RED)
                    self._busy = False
                    self._set_buttons_state("normal")

        except queue.Empty:
            pass

        self.root.after(25, self._poll)

    def _set_status(self, msg, color=MUTED):
        self.status_lbl.configure(text=msg, fg=color)

    def _set_buttons_state(self, state):
        for btn in self._op_buttons:
            btn.configure(state=state)

    def _set_proc_buttons(self, state):
        for btn in self._proc_buttons:
            btn.configure(state=state)

    # ── Thread runner ─────────────────────────────────────────────────────────

    def _run(self, func, result_fn):
        if self._halted:
            self._set_status("Processor HALTED — press RESET to restart.", RED)
            return
        if self._busy:
            self._set_status("Busy — wait for the current operation to finish.", YELLOW)
            return

        self._busy = True
        self._set_status("Running…", ACCENT)
        self._set_buttons_state("disabled")

        def worker():
            try:
                func()
                ui_queue.put(("done", result_fn()))
            except Exception as exc:
                ui_queue.put(("error", str(exc)))

        threading.Thread(target=worker, daemon=True).start()

    # ── Input dialogs ─────────────────────────────────────────────────────────

    def _ask_int(self, prompt):
        return _IntDialog(self.root, prompt).result

    def _ask_array(self):
        return _ArrayDialog(self.root).result

    # ── Operation handlers ────────────────────────────────────────────────────

    def _sep(self):
        self._trace_add("sep", "  " + "─" * 62 + "\n")

    def _op_add(self):
        x = self._ask_int("Enter integer to ADD to AC:")
        if x is None:
            return
        self._sep()
        self._run(
            lambda: do_add(x),
            lambda: f"ADD {x}  →  AC = {AC_val}"
        )

    def _op_subt(self):
        x = self._ask_int("Enter integer to SUBTRACT from AC:")
        if x is None:
            return
        self._sep()
        self._run(
            lambda: do_subt(x),
            lambda: f"SUBT {x}  →  AC = {AC_val}"
        )

    def _op_clear(self):
        self._sep()
        self._run(
            do_clear,
            lambda: "CLEAR  →  AC = 0"
        )

    def _op_sum(self):
        data = self._ask_array()
        if data is None:
            return
        self._sep()
        self._run(
            lambda: marie_sum(data),
            lambda: f"SUM{data}  =  {AC_val}"
        )

    def _op_average(self):
        data = self._ask_array()
        if data is None:
            return
        self._sep()
        self._run(
            lambda: marie_average(data),
            lambda: f"AVERAGE{data}  =  {AC_val}"
        )

    def _op_max(self):
        data = self._ask_array()
        if data is None:
            return
        self._sep()
        self._run(
            lambda: marie_max(data),
            lambda: f"MAX{data}  =  {AC_val}"
        )

    def _op_sort(self):
        data = self._ask_array()
        if data is None:
            return
        arr = data[:]
        self._sep()
        self._run(
            lambda: marie_sort(arr),
            lambda: f"SORT  →  {arr}"
        )

    def _op_halt(self):
        if self._busy or self._halted:
            return
        self._halted = True
        self._sep()
        self._trace_add("inst",  "  [EXECUTE  HALT]\n")
        self._trace_add("muted", "    Processor HALTED.\n")
        self._trace_add("final", "\n  ■  PROCESSOR HALTED\n")
        self._trace_add("sep",   "  " + "─" * 62 + "\n")
        self._set_proc_buttons("disabled")
        self._set_status("■  PROCESSOR HALTED  —  press RESET to restart", RED)

    def _op_reset(self):
        global AC_val, MAR_val, MBR_val, memory
        if self._busy:
            return
        self._halted = False
        self._set_proc_buttons("normal")
        AC_val = MAR_val = MBR_val = 0
        memory = [0] * 16

        self._trace_clear()
        self._trace_add("op",    "  System RESET — all registers and memory zeroed\n")
        self._trace_add("sep",   "  " + "─" * 62 + "\n")

        for name in ("AC", "MAR", "MBR"):
            _, _, val = self._reg_widgets[name]
            val.configure(text="0")
            self._restore_reg(name)

        for i in range(16):
            _, inner, val = self._mem_widgets[i]
            val.configure(text="0", fg=TEXT, bg=PANEL2)
            inner.configure(bg=PANEL2)

        self.ac_badge.configure(text="AC = 0")
        self._set_status("Reset complete.", MUTED)


# ── Custom dialogs ────────────────────────────────────────────────────────────

class _BaseDialog:
    """Shared dark-themed dialog base."""

    def __init__(self, master, title, width, height):
        self.result = None
        self.top = tk.Toplevel(master)
        self.top.title(title)
        self.top.configure(bg=PANEL)
        self.top.geometry(f"{width}x{height}")
        self.top.resizable(False, False)
        self.top.grab_set()
        self.top.transient(master)
        self.top.focus_force()

    def _entry(self, parent, var):
        e = tk.Entry(parent, textvariable=var, font=MONO,
                     fg=WHITE, bg=PANEL2, insertbackground=WHITE,
                     relief="flat", bd=0, highlightthickness=1,
                     highlightcolor=ACCENT, highlightbackground=BORDER)
        return e

    def _btn(self, parent, text, color, cmd):
        b = tk.Button(parent, text=text, font=BTN_FONT,
                      fg=WHITE, bg=color,
                      activebackground=PANEL, activeforeground=WHITE,
                      relief="flat", bd=0, padx=18, pady=6,
                      cursor="hand2", command=cmd)
        b.bind("<Enter>", lambda e: b.config(bg=PANEL))
        b.bind("<Leave>", lambda e: b.config(bg=color))
        return b

    def _flash_error(self, widget):
        orig = widget.cget("highlightbackground")
        widget.configure(highlightbackground=RED, highlightcolor=RED)
        self.top.after(400, lambda: widget.configure(
            highlightbackground=BORDER, highlightcolor=ACCENT))

    def wait(self):
        self.top.wait_window()


class _IntDialog(_BaseDialog):
    def __init__(self, master, prompt):
        super().__init__(master, "Enter Value", 360, 148)
        tk.Label(self.top, text=prompt, font=HEAD, fg=TEXT, bg=PANEL,
                 wraplength=320, justify="left"
                 ).pack(padx=20, pady=(18, 6), anchor="w")

        var = tk.StringVar()
        self._e = self._entry(self.top, var)
        self._e.pack(padx=20, fill="x")
        self._e.focus()

        row = tk.Frame(self.top, bg=PANEL)
        row.pack(fill="x", padx=20, pady=12)
        self._btn(row, "OK",     ACCENT, lambda: self._ok(var)).pack(side="right", padx=(6, 0))
        self._btn(row, "Cancel", PANEL2, self.top.destroy).pack(side="right")

        self._e.bind("<Return>",  lambda e: self._ok(var))
        self.top.bind("<Escape>", lambda e: self.top.destroy())
        self.wait()

    def _ok(self, var):
        try:
            self.result = int(var.get())
            self.top.destroy()
        except ValueError:
            self._flash_error(self._e)


class _ArrayDialog(_BaseDialog):
    def __init__(self, master):
        super().__init__(master, "Enter Array Values", 420, 170)
        tk.Label(self.top,
                 text="Enter integers separated by spaces or commas:",
                 font=HEAD, fg=TEXT, bg=PANEL
                 ).pack(padx=20, pady=(18, 4), anchor="w")
        tk.Label(self.top,
                 text="Example:   3   7   1   9   4",
                 font=MONO_SM, fg=MUTED, bg=PANEL
                 ).pack(padx=20, anchor="w")

        var = tk.StringVar()
        self._e = self._entry(self.top, var)
        self._e.pack(padx=20, fill="x", pady=8)
        self._e.focus()

        row = tk.Frame(self.top, bg=PANEL)
        row.pack(fill="x", padx=20, pady=4)
        self._btn(row, "Run",    GREEN,  lambda: self._ok(var)).pack(side="right", padx=(6, 0))
        self._btn(row, "Cancel", PANEL2, self.top.destroy).pack(side="right")

        self._e.bind("<Return>",  lambda e: self._ok(var))
        self.top.bind("<Escape>", lambda e: self.top.destroy())
        self.wait()

    def _ok(self, var):
        try:
            nums = [int(t) for t in var.get().replace(",", " ").split() if t]
            if not nums:
                raise ValueError
            self.result = nums
            self.top.destroy()
        except ValueError:
            self._flash_error(self._e)


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    root = tk.Tk()
    try:
        root.iconbitmap("")
    except Exception:
        pass
    MARIEApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
