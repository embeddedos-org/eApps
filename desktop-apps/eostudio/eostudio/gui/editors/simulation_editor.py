"""Simulation Editor — MATLAB/Simulink-style block diagram simulation."""
from __future__ import annotations
import math
import tkinter as tk
import tkinter.ttk as ttk
from typing import Any, Dict, List, Optional, Tuple

try:
    from eostudio.core.simulation import SimBlock, SimConnection, SimEngine
except ImportError:
    SimBlock = SimConnection = SimEngine = None  # type: ignore[assignment,misc]

BLOCK_CATALOG = [
    ("sine", "Sine", "Source", "#89b4fa", {"freq": 1.0, "amp": 1.0, "phase": 0.0}),
    ("square", "Square", "Source", "#89b4fa", {"freq": 1.0, "amp": 1.0, "duty": 0.5}),
    ("step", "Step", "Source", "#89b4fa", {"time": 1.0, "amp": 1.0}),
    ("noise", "Noise", "Source", "#89b4fa", {"amp": 0.5}),
    ("constant", "Constant", "Source", "#89b4fa", {"value": 1.0}),
    ("gain", "Gain", "Math", "#a6e3a1", {"gain": 2.0}),
    ("sum", "Sum", "Math", "#a6e3a1", {"signs": "++"}),
    ("product", "Product", "Math", "#a6e3a1", {}),
    ("transfer_fn", "Transfer Fn", "Math", "#cba6f7", {"num": "1", "den": "1 1"}),
    ("integrator", "Integrator", "Math", "#cba6f7", {"ic": 0.0}),
    ("derivative", "Derivative", "Math", "#cba6f7", {}),
    ("delay", "Delay", "Math", "#f9e2af", {"delay": 0.1}),
    ("scope", "Scope", "Sink", "#f38ba8", {}),
    ("comparator", "Compare", "Logic", "#fab387", {"op": ">", "threshold": 0.0}),
    ("switch", "Switch", "Logic", "#fab387", {"threshold": 0.0}),
    ("saturation", "Saturation", "Limit", "#94e2d5", {"lower": -1.0, "upper": 1.0}),
    ("dead_zone", "Dead Zone", "Limit", "#94e2d5", {"lower": -0.1, "upper": 0.1}),
    ("lookup", "Lookup Table", "Misc", "#b4befe", {"x": "0 1 2", "y": "0 1 4"}),
]
_CAT_ORDER = ["Source", "Math", "Logic", "Limit", "Sink", "Misc"]


class SimulationEditor(tk.Frame):
    """MATLAB/Simulink-style block-diagram simulation editor."""
    def __init__(self, master: tk.Widget, bg: str = "#1e1e2e", fg: str = "#cdd6f4", **kw: Any):
        super().__init__(master, bg=bg, **kw)
        self._bg, self._fg = bg, fg
        self._blocks: List[Dict[str, Any]] = []
        self._conns: List[Tuple[int, int]] = []
        self._sel: Optional[int] = None
        self._tool: Optional[str] = None
        self._conn0: Optional[int] = None
        self._doff: Tuple[int, int] = (0, 0)
        self._sim_t = 0.0
        self._sim_dt = 0.01
        self._sim_dur = 5.0
        self._sim_state = "stopped"
        self._sim_data: Dict[int, List[float]] = {}
        self._pw: List[tk.Widget] = []
        self._build_ui()

    def _build_ui(self) -> None:
        # left palette
        left = tk.Frame(self, bg=self._bg, width=160)
        left.pack(side=tk.LEFT, fill=tk.Y)
        left.pack_propagate(False)
        tk.Label(left, text="Blocks", bg=self._bg, fg=self._fg,
                 font=("Segoe UI", 10, "bold"), anchor=tk.W).pack(fill=tk.X, padx=8, pady=(8, 2))
        sf = tk.Frame(left, bg=self._bg)
        sf.pack(fill=tk.BOTH, expand=True)
        cur_cat = ""
        for bid, label, cat, clr, _ in BLOCK_CATALOG:
            if cat != cur_cat:
                cur_cat = cat
                tk.Label(sf, text=cat, bg=self._bg, fg="#6c7086",
                         font=("Segoe UI", 8, "bold"), anchor=tk.W).pack(fill=tk.X, padx=8, pady=(6, 1))
            b = tk.Button(sf, text=label, bg="#313244", fg=clr, relief=tk.FLAT,
                          font=("Segoe UI", 8), anchor=tk.W, padx=6, pady=1)
            b.pack(fill=tk.X, padx=4, pady=0)
            b.bind("<ButtonPress-1>", lambda e, t=bid: self._set_tool(t))
        ttk.Separator(left, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=4, pady=4)
        tk.Button(left, text="Connect Mode", bg="#f9e2af", fg="#1e1e2e", relief=tk.FLAT,
                  font=("Segoe UI", 8), command=lambda: self._set_tool("__connect__")).pack(fill=tk.X, padx=8, pady=2)

        # right props
        right = tk.Frame(self, bg=self._bg, width=210)
        right.pack(side=tk.RIGHT, fill=tk.Y)
        right.pack_propagate(False)
        tk.Label(right, text="Properties", bg=self._bg, fg=self._fg,
                 font=("Segoe UI", 11, "bold"), anchor=tk.W).pack(fill=tk.X, padx=8, pady=(8, 4))
        self._pf = tk.Frame(right, bg=self._bg)
        self._pf.pack(fill=tk.BOTH, expand=True, padx=4)
        self._nsl = tk.Label(self._pf, text="No block selected", bg=self._bg, fg="#6c7086", font=("Segoe UI", 9))
        self._nsl.pack(pady=20)

        # center area (canvas + scope + console)
        center = tk.Frame(self, bg=self._bg)
        center.pack(fill=tk.BOTH, expand=True)

        # sim controls toolbar
        ctrl = tk.Frame(center, bg="#181825")
        ctrl.pack(fill=tk.X)
        for txt, cmd in [("▶ Run", self._run), ("⏸ Pause", self._pause),
                         ("⏹ Stop", self._stop), ("⏭ Step", self._step), ("↺ Reset", self._reset)]:
            tk.Button(ctrl, text=txt, bg="#313244", fg=self._fg, relief=tk.FLAT,
                      font=("Segoe UI", 8), padx=6, command=cmd).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Label(ctrl, text="dt:", bg="#181825", fg=self._fg, font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=(8, 2))
        self._dt_var = tk.StringVar(value=str(self._sim_dt))
        tk.Entry(ctrl, textvariable=self._dt_var, width=6, bg="#313244", fg=self._fg,
                 font=("Consolas", 8), relief=tk.FLAT, insertbackground=self._fg).pack(side=tk.LEFT)
        tk.Label(ctrl, text="dur:", bg="#181825", fg=self._fg, font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=(8, 2))
        self._dur_var = tk.StringVar(value=str(self._sim_dur))
        tk.Entry(ctrl, textvariable=self._dur_var, width=6, bg="#313244", fg=self._fg,
                 font=("Consolas", 8), relief=tk.FLAT, insertbackground=self._fg).pack(side=tk.LEFT)

        # paned: canvas top, scope+console bottom
        pw = tk.PanedWindow(center, orient=tk.VERTICAL, bg=self._bg, sashwidth=4)
        pw.pack(fill=tk.BOTH, expand=True)
        self._canvas = tk.Canvas(pw, bg="#11111b", highlightthickness=0)
        pw.add(self._canvas, minsize=200)
        self._canvas.bind("<ButtonPress-1>", self._click)
        self._canvas.bind("<B1-Motion>", self._drag)
        self._canvas.bind("<Configure>", lambda e: self._redraw())

        bot = tk.Frame(pw, bg=self._bg)
        pw.add(bot, minsize=120)
        bnb = ttk.Notebook(bot)
        bnb.pack(fill=tk.BOTH, expand=True)
        scope_frame = tk.Frame(bnb, bg=self._bg)
        bnb.add(scope_frame, text="Scope")
        self._scope_cv = tk.Canvas(scope_frame, bg="#181825", highlightthickness=0)
        self._scope_cv.pack(fill=tk.BOTH, expand=True)
        console_frame = tk.Frame(bnb, bg=self._bg)
        bnb.add(console_frame, text="Math Console")
        self._console = tk.Text(console_frame, height=6, bg="#181825", fg=self._fg,
                                font=("Consolas", 9), relief=tk.FLAT, insertbackground=self._fg)
        self._console.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self._console.insert("1.0", ">> ")
        self._console.bind("<Return>", self._eval_console)

        # status bar
        self._status = tk.Label(self, text="", bg="#181825", fg="#6c7086",
                                font=("Consolas", 9), anchor=tk.W, padx=8)
        self._status.pack(side=tk.BOTTOM, fill=tk.X)
        self._update_status()

    def _set_tool(self, t: str) -> None:
        self._tool = t
        self._conn0 = None

    # -- mouse --
    def _click(self, ev: tk.Event) -> None:
        if self._tool == "__connect__":
            h = self._hit(ev.x, ev.y)
            if h is not None:
                if self._conn0 is None:
                    self._conn0 = h
                else:
                    if self._conn0 != h:
                        self._conns.append((self._conn0, h))
                    self._conn0 = None
                    self._redraw()
            return
        if self._tool:
            cat = self._cat_lookup(self._tool)
            if cat:
                self._blocks.append({"type": cat[0], "label": cat[1], "x": ev.x, "y": ev.y,
                                     "w": 80, "h": 40, "color": cat[3],
                                     "params": dict(cat[4])})
                self._sel = len(self._blocks) - 1
                self._tool = None
                self._sim_data[self._sel] = []
                self._redraw()
                self._show_props()
                return
        h = self._hit(ev.x, ev.y)
        self._sel = h
        if h is not None:
            b = self._blocks[h]
            self._doff = (ev.x - b["x"], ev.y - b["y"])
            self._show_props()
        else:
            self._clr_props()
        self._redraw()

    def _drag(self, ev: tk.Event) -> None:
        if self._sel is None or self._tool == "__connect__":
            return
        b = self._blocks[self._sel]
        b["x"], b["y"] = ev.x - self._doff[0], ev.y - self._doff[1]
        self._redraw()

    def _hit(self, x: int, y: int) -> Optional[int]:
        for i in range(len(self._blocks) - 1, -1, -1):
            b = self._blocks[i]
            if b["x"] <= x <= b["x"] + b["w"] and b["y"] <= y <= b["y"] + b["h"]:
                return i
        return None

    @staticmethod
    def _cat_lookup(bid: str):
        for c in BLOCK_CATALOG:
            if c[0] == bid:
                return c
        return None

    # -- drawing --
    def _redraw(self) -> None:
        c = self._canvas
        c.delete("all")
        for fi, ti in self._conns:
            if fi < len(self._blocks) and ti < len(self._blocks):
                fb, tb = self._blocks[fi], self._blocks[ti]
                x1, y1 = fb["x"] + fb["w"], fb["y"] + fb["h"] // 2
                x2, y2 = tb["x"], tb["y"] + tb["h"] // 2
                mx = (x1 + x2) // 2
                c.create_line(x1, y1, mx, y1, mx, y2, x2, y2, fill="#585b70", width=2, smooth=False)
                c.create_oval(x1 - 3, y1 - 3, x1 + 3, y1 + 3, fill="#585b70", outline="")
                c.create_polygon(x2, y2, x2 - 6, y2 - 4, x2 - 6, y2 + 4, fill="#585b70")
        for i, b in enumerate(self._blocks):
            sel = i == self._sel
            ol = "#f9e2af" if sel else b["color"]
            lw = 2 if sel else 1
            c.create_rectangle(b["x"], b["y"], b["x"] + b["w"], b["y"] + b["h"],
                               outline=ol, fill="#313244", width=lw)
            c.create_text(b["x"] + b["w"] // 2, b["y"] + b["h"] // 2,
                          text=b["label"], fill=b["color"], font=("Segoe UI", 8, "bold"))
            # ports
            c.create_oval(b["x"] - 4, b["y"] + b["h"] // 2 - 4,
                          b["x"] + 4, b["y"] + b["h"] // 2 + 4, fill="#585b70", outline=ol)
            c.create_oval(b["x"] + b["w"] - 4, b["y"] + b["h"] // 2 - 4,
                          b["x"] + b["w"] + 4, b["y"] + b["h"] // 2 + 4, fill="#585b70", outline=ol)

    # -- properties --
    def _clr_props(self) -> None:
        for w in self._pw:
            w.destroy()
        self._pw.clear()
        self._nsl.pack(pady=20)

    def _show_props(self) -> None:
        self._clr_props()
        self._nsl.pack_forget()
        if self._sel is None:
            self._nsl.pack(pady=20)
            return
        b = self._blocks[self._sel]
        rows = [("Type", b["type"], True), ("Label", b["label"], False),
                ("X", str(b["x"]), False), ("Y", str(b["y"]), False)]
        for pk, pv in b["params"].items():
            rows.append((pk.title(), str(pv), False))
        for lbl, val, ro in rows:
            row = tk.Frame(self._pf, bg=self._bg)
            row.pack(fill=tk.X, padx=4, pady=1)
            self._pw.append(row)
            tk.Label(row, text=lbl, bg=self._bg, fg=self._fg, font=("Segoe UI", 8), width=10, anchor=tk.W).pack(side=tk.LEFT)
            var = tk.StringVar(value=val)
            ent = tk.Entry(row, textvariable=var, width=12, bg="#313244", fg=self._fg, font=("Consolas", 8),
                           relief=tk.FLAT, insertbackground=self._fg, state=tk.DISABLED if ro else tk.NORMAL)
            ent.pack(side=tk.LEFT, fill=tk.X, expand=True)
            if not ro:
                ent.bind("<Return>", lambda e, k=lbl.lower(), v=var: self._pchg(k, v.get()))
        db = tk.Button(self._pf, text="Delete Block", bg="#f38ba8", fg="#1e1e2e", relief=tk.FLAT,
                       font=("Segoe UI", 9), command=self._del_block)
        db.pack(padx=4, pady=8)
        self._pw.append(db)

    def _pchg(self, k: str, v: str) -> None:
        if self._sel is None:
            return
        b = self._blocks[self._sel]
        if k in ("x", "y"):
            try:
                b[k] = int(float(v))
            except ValueError:
                pass
        elif k == "label":
            b["label"] = v
        elif k in b["params"]:
            try:
                b["params"][k] = float(v)
            except ValueError:
                b["params"][k] = v
        self._redraw()

    def _del_block(self) -> None:
        if self._sel is not None:
            idx = self._sel
            self._conns = [(f, t) for f, t in self._conns if f != idx and t != idx]
            self._blocks.pop(idx)
            self._sel = None
            self._redraw()
            self._clr_props()

    # -- simulation --
    def _read_params(self) -> None:
        try:
            self._sim_dt = max(0.001, float(self._dt_var.get()))
        except ValueError:
            pass
        try:
            self._sim_dur = max(0.1, float(self._dur_var.get()))
        except ValueError:
            pass

    def _eval_block(self, b: Dict[str, Any], t: float) -> float:
        bt = b["type"]
        p = b["params"]
        if bt == "sine":
            return float(p.get("amp", 1.0)) * math.sin(2 * math.pi * float(p.get("freq", 1.0)) * t + float(p.get("phase", 0.0)))
        if bt == "square":
            return float(p.get("amp", 1.0)) * (1.0 if (t * float(p.get("freq", 1.0))) % 1.0 < float(p.get("duty", 0.5)) else -1.0)
        if bt == "step":
            return float(p.get("amp", 1.0)) if t >= float(p.get("time", 1.0)) else 0.0
        if bt == "noise":
            return float(p.get("amp", 0.5)) * (2.0 * (hash((t * 10000) % 9999) % 1000) / 1000.0 - 1.0)
        if bt == "constant":
            return float(p.get("value", 1.0))
        if bt == "gain":
            return float(p.get("gain", 1.0))
        return 0.0

    def _run(self) -> None:
        self._read_params()
        self._sim_state = "running"
        self._sim_t = 0.0
        self._sim_data = {i: [] for i in range(len(self._blocks))}
        self._tick()

    def _tick(self) -> None:
        if self._sim_state != "running":
            return
        if self._sim_t >= self._sim_dur:
            self._sim_state = "stopped"
            self._update_status()
            self._draw_scope()
            return
        for i, b in enumerate(self._blocks):
            v = self._eval_block(b, self._sim_t)
            self._sim_data.setdefault(i, []).append(v)
        self._sim_t += self._sim_dt
        self._update_status()
        if int(self._sim_t / self._sim_dt) % max(1, int(0.05 / self._sim_dt)) == 0:
            self._draw_scope()
        self.after(1, self._tick)

    def _pause(self) -> None:
        self._sim_state = "paused"
        self._update_status()

    def _stop(self) -> None:
        self._sim_state = "stopped"
        self._update_status()
        self._draw_scope()

    def _step(self) -> None:
        self._read_params()
        if self._sim_state == "stopped":
            self._sim_t = 0.0
            self._sim_data = {i: [] for i in range(len(self._blocks))}
        for i, b in enumerate(self._blocks):
            self._sim_data.setdefault(i, []).append(self._eval_block(b, self._sim_t))
        self._sim_t += self._sim_dt
        self._sim_state = "paused"
        self._update_status()
        self._draw_scope()

    def _reset(self) -> None:
        self._sim_t = 0.0
        self._sim_state = "stopped"
        self._sim_data = {i: [] for i in range(len(self._blocks))}
        self._update_status()
        self._draw_scope()

    # -- scope --
    def _draw_scope(self) -> None:
        c = self._scope_cv
        c.delete("all")
        cw = c.winfo_width() or 400
        ch = c.winfo_height() or 150
        pad = 40
        c.create_rectangle(pad, 10, cw - 10, ch - 20, outline="#313244", fill="#11111b")
        # axes
        c.create_line(pad, ch - 20, cw - 10, ch - 20, fill="#585b70", width=1)
        c.create_line(pad, 10, pad, ch - 20, fill="#585b70", width=1)
        c.create_text(cw // 2, ch - 8, text="Time (s)", fill="#6c7086", font=("Consolas", 7))
        c.create_text(12, ch // 2, text="Amp", fill="#6c7086", font=("Consolas", 7), angle=90)
        # grid
        for gx in range(pad, cw - 10, max(1, (cw - 50) // 8)):
            c.create_line(gx, 10, gx, ch - 20, fill="#1e1e2e", width=1)
        for gy in range(10, ch - 20, max(1, (ch - 30) // 6)):
            c.create_line(pad, gy, cw - 10, gy, fill="#1e1e2e", width=1)
        # tick labels
        if self._sim_dur > 0:
            for tx in range(5):
                xp = pad + tx * (cw - 50) // 4
                tv = tx * self._sim_dur / 4
                c.create_text(xp, ch - 12, text=f"{tv:.1f}", fill="#6c7086", font=("Consolas", 6))

        colors = ["#89b4fa", "#a6e3a1", "#f9e2af", "#f38ba8", "#cba6f7", "#fab387", "#94e2d5"]
        plot_w = cw - pad - 10
        plot_h = ch - 30
        for idx, data in self._sim_data.items():
            if not data or idx >= len(self._blocks):
                continue
            clr = colors[idx % len(colors)]
            mn, mx = min(data), max(data)
            rng = mx - mn if mx != mn else 1.0
            pts: List[int] = []
            for j, v in enumerate(data):
                px = pad + int(j / max(1, len(data) - 1) * plot_w)
                py = ch - 20 - int((v - mn) / rng * plot_h)
                pts.extend([px, py])
            if len(pts) >= 4:
                c.create_line(*pts, fill=clr, width=1)
            c.create_text(cw - 8, 14 + idx * 12, text=self._blocks[idx]["label"],
                          fill=clr, font=("Consolas", 7), anchor=tk.E)

    # -- console --
    def _eval_console(self, _ev: tk.Event) -> str:
        line = self._console.get("end-2l linestart", "end-1c").strip()
        if line.startswith(">> "):
            line = line[3:]
        result = ""
        try:
            if line.startswith("linspace"):
                parts = line.replace("linspace(", "").rstrip(")").split(",")
                a, b, n = float(parts[0]), float(parts[1]), int(parts[2])
                step = (b - a) / max(1, n - 1)
                result = str([round(a + i * step, 6) for i in range(n)])
            elif line.startswith("fft"):
                result = "[FFT requires numpy — not available in pure tkinter mode]"
            elif line.startswith("polyfit"):
                result = "[polyfit requires numpy — not available in pure tkinter mode]"
            elif line.startswith("solve_ode"):
                result = "[solve_ode requires scipy — not available in pure tkinter mode]"
            else:
                result = str(eval(line, {"__builtins__": {"abs": abs, "round": round, "min": min,
                                                          "max": max, "sum": sum, "len": len, "range": range, "list": list,
                                                          "math": math, "sin": math.sin, "cos": math.cos, "sqrt": math.sqrt,
                                                          "pi": math.pi, "e": math.e, "log": math.log, "exp": math.exp}}))
        except Exception as exc:
            result = f"Error: {exc}"
        self._console.insert(tk.END, f"\n{result}\n>> ")
        self._console.see(tk.END)
        return "break"

    def _update_status(self) -> None:
        self._status.config(text=f"Time: {self._sim_t:.3f}s  |  dt: {self._sim_dt}  |  State: {self._sim_state}  |  Blocks: {len(self._blocks)}")
