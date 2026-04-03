"""HardwareEditor — GUI for schematic capture, PCB layout, board config, and BOM."""
from __future__ import annotations
import csv
import io
import os
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox, simpledialog
from typing import Any, Dict, List, Optional, Tuple
try:
    from eostudio.codegen.hardware import FirmwareGenerator
except ImportError:
    FirmwareGenerator = None  # type: ignore[assignment,misc]
try:
    from eostudio.plugins import PluginHook, PluginManager
except ImportError:
    PluginHook = PluginManager = None  # type: ignore[assignment,misc]

_CL = [
    {"cat": "Passive", "name": "Resistor", "sym": "R", "pkg": "0402", "val": "10k"},
    {"cat": "Passive", "name": "Capacitor", "sym": "C", "pkg": "0402", "val": "100nF"},
    {"cat": "Passive", "name": "Inductor", "sym": "L", "pkg": "0603", "val": "10uH"},
    {"cat": "Semi", "name": "LED", "sym": "D", "pkg": "0603", "val": "Red"},
    {"cat": "Semi", "name": "Diode", "sym": "D", "pkg": "SOD-323", "val": "1N4148"},
    {"cat": "Semi", "name": "MOSFET N", "sym": "Q", "pkg": "SOT-23", "val": "2N7002"},
    {"cat": "IC", "name": "MCU STM32F4", "sym": "U", "pkg": "LQFP-64", "val": "STM32F407VG"},
    {"cat": "IC", "name": "MCU ESP32", "sym": "U", "pkg": "QFN-48", "val": "ESP32-S3"},
    {"cat": "IC", "name": "MCU nRF52", "sym": "U", "pkg": "QFN-48", "val": "nRF52840"},
    {"cat": "IC", "name": "MCU RP2040", "sym": "U", "pkg": "QFN-56", "val": "RP2040"},
    {"cat": "IC", "name": "LDO 3.3V", "sym": "U", "pkg": "SOT-223", "val": "AMS1117"},
    {"cat": "IC", "name": "Op-Amp", "sym": "U", "pkg": "SOT-23-5", "val": "MCP6001"},
    {"cat": "IC", "name": "EEPROM", "sym": "U", "pkg": "SOT-23-5", "val": "24LC256"},
    {"cat": "Conn", "name": "USB-C", "sym": "J", "pkg": "USB-C", "val": "USB-C"},
    {"cat": "Conn", "name": "Header 2x20", "sym": "J", "pkg": "2.54mm", "val": "40P"},
    {"cat": "Xtal", "name": "Crystal 8M", "sym": "Y", "pkg": "HC-49S", "val": "8MHz"},
    {"cat": "Xtal", "name": "Crystal 32k", "sym": "Y", "pkg": "2012", "val": "32.768kHz"},
]
_PL = ["STM32F4", "STM32H7", "ESP32", "nRF52840", "nRF5340", "RP2040", "iMX8M", "K64F"]
_OL = ["eos", "baremetal", "freertos", "zephyr", "linux"]
_LY = ["Top Copper", "Bottom Copper", "Top Silk", "Bottom Silk", "Top Mask", "Bottom Mask", "Edge Cuts"]


class HardwareEditor(tk.Frame):
    def __init__(self, master: tk.Widget, bg: str = "#1e1e2e", fg: str = "#cdd6f4", **kw: Any):
        super().__init__(master, bg=bg, **kw)
        self._bg, self._fg = bg, fg
        self._comps: List[Dict[str, Any]] = []
        self._wires: List[Tuple[int, int, int, int]] = []
        self._nets: List[Dict[str, Any]] = []
        self._sel: Optional[int] = None
        self._tool: Optional[str] = None
        self._drag: Optional[Tuple[int, int]] = None
        self._rc: Dict[str, int] = {}
        self._pcbt: List[Tuple[int, int, int, int]] = []
        self._ptool: Optional[str] = None
        self._player: str = _LY[0]
        self._yaml: str = self._dyaml()
        self._tplat: str = "STM32F4"
        self._tos: str = "eos"
        self._bom: List[Dict[str, Any]] = []
        self._pmgr: Any = None
        self._eosim: Any = None
        self._build_ui()

    def _build_ui(self) -> None:
        s = ttk.Style()
        s.configure("HW.TNotebook", background=self._bg)
        s.configure("HW.TNotebook.Tab", background="#313244", foreground=self._fg, padding=[8, 4])
        self._nb = ttk.Notebook(self, style="HW.TNotebook")
        self._nb.pack(fill=tk.BOTH, expand=True)
        self._mk_sch()
        self._mk_pcb()
        self._mk_cfg()
        self._mk_bom()

    def _mk_sch(self) -> None:
        tab = tk.Frame(self._nb, bg=self._bg)
        self._nb.add(tab, text="  Schematic  ")
        left = tk.Frame(tab, bg=self._bg, width=170)
        left.pack(side=tk.LEFT, fill=tk.Y)
        left.pack_propagate(False)
        tk.Label(left, text="Components", bg=self._bg, fg=self._fg, font=("Segoe UI", 10, "bold")).pack(fill=tk.X, padx=6, pady=(6, 2))
        sf = tk.Frame(left, bg=self._bg)
        sf.pack(fill=tk.BOTH, expand=True)
        cur = ""
        for c in _CL:
            if c["cat"] != cur:
                cur = c["cat"]
                tk.Label(sf, text=cur, bg=self._bg, fg="#6c7086", font=("Segoe UI", 8, "bold")).pack(fill=tk.X, padx=6, pady=(4, 0))
            b = tk.Button(sf, text=c["name"], bg="#313244", fg="#89b4fa", relief=tk.FLAT, font=("Segoe UI", 8), anchor=tk.W, padx=4)
            b.pack(fill=tk.X, padx=4)
            b.bind("<ButtonPress-1>", lambda e, cc=c: self._sset(cc))
        ttk.Separator(left).pack(fill=tk.X, padx=4, pady=4)
        tk.Button(left, text="Wire Mode", bg="#f9e2af", fg="#1e1e2e", relief=tk.FLAT, font=("Segoe UI", 8), command=lambda: setattr(self, '_tool', '__wire__')).pack(fill=tk.X, padx=6, pady=1)
        tk.Button(left, text="Net Label", bg="#a6e3a1", fg="#1e1e2e", relief=tk.FLAT, font=("Segoe UI", 8), command=self._anet).pack(fill=tk.X, padx=6, pady=1)
        tk.Button(left, text="Run ERC", bg="#f38ba8", fg="#1e1e2e", relief=tk.FLAT, font=("Segoe UI", 8), command=self._erc).pack(fill=tk.X, padx=6, pady=4)
        self._cv = tk.Canvas(tab, bg="#181825", highlightthickness=0)
        self._cv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._cv.bind("<Button-1>", self._sclk)
        self._cv.bind("<B1-Motion>", self._smov)
        self._cv.bind("<ButtonRelease-1>", self._srel)
        right = tk.Frame(tab, bg=self._bg, width=200)
        right.pack(side=tk.RIGHT, fill=tk.Y)
        right.pack_propagate(False)
        tk.Label(right, text="Properties", bg=self._bg, fg=self._fg, font=("Segoe UI", 10, "bold")).pack(fill=tk.X, padx=6, pady=(6, 2))
        self._pf = tk.Frame(right, bg=self._bg)
        self._pf.pack(fill=tk.BOTH, expand=True, padx=4)
        tk.Label(self._pf, text="No selection", bg=self._bg, fg="#6c7086", font=("Segoe UI", 9)).pack(pady=20)

    def _mk_pcb(self) -> None:
        tab = tk.Frame(self._nb, bg=self._bg)
        self._nb.add(tab, text="  PCB Layout  ")
        tb = tk.Frame(tab, bg="#313244", height=32)
        tb.pack(fill=tk.X)
        tb.pack_propagate(False)
        tk.Label(tb, text="Layer:", bg="#313244", fg=self._fg, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(6, 2))
        self._lv = tk.StringVar(value=_LY[0])
        lc = ttk.Combobox(tb, textvariable=self._lv, values=_LY, state="readonly", width=16)
        lc.pack(side=tk.LEFT, padx=2)
        lc.bind("<<ComboboxSelected>>", lambda e: setattr(self, '_player', self._lv.get()))
        for l, t in [("Route", "route"), ("Via", "via"), ("Zone", "zone"), ("Select", None)]:
            tk.Button(tb, text=l, bg="#45475a", fg=self._fg, relief=tk.FLAT, font=("Segoe UI", 8), padx=6, command=lambda tt=t: setattr(self, '_ptool', tt)).pack(side=tk.LEFT, padx=2, pady=3)
        tk.Button(tb, text="Run DRC", bg="#f38ba8", fg="#1e1e2e", relief=tk.FLAT, font=("Segoe UI", 8), padx=6, command=self._drc).pack(side=tk.RIGHT, padx=6, pady=3)
        self._pcv = tk.Canvas(tab, bg="#11111b", highlightthickness=0)
        self._pcv.pack(fill=tk.BOTH, expand=True)
        self._pcv.create_rectangle(50, 50, 550, 400, outline="#585b70", width=2, dash=(4, 2))
        self._pcv.bind("<Button-1>", self._pclk)
        self._pcv.bind("<B1-Motion>", self._pdrg)

    def _mk_cfg(self) -> None:
        tab = tk.Frame(self._nb, bg=self._bg)
        self._nb.add(tab, text="  Board Config  ")
        tb = tk.Frame(tab, bg="#313244", height=36)
        tb.pack(fill=tk.X)
        tb.pack_propagate(False)
        tk.Label(tb, text="Platform:", bg="#313244", fg=self._fg, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(6, 2))
        self._pv = tk.StringVar(value=self._tplat)
        ttk.Combobox(tb, textvariable=self._pv, values=_PL, state="readonly", width=14).pack(side=tk.LEFT, padx=2)
        tk.Button(tb, text="Gen from Schematic", bg="#89b4fa", fg="#1e1e2e", relief=tk.FLAT, font=("Segoe UI", 8), padx=6, command=self._gcfg).pack(side=tk.LEFT, padx=6, pady=4)
        tk.Button(tb, text="Generate Code", bg="#a6e3a1", fg="#1e1e2e", relief=tk.FLAT, font=("Segoe UI", 8), padx=6, command=self._cgen).pack(side=tk.LEFT, padx=4, pady=4)
        tk.Button(tb, text="\u25b6 Simulate", bg="#f9e2af", fg="#1e1e2e", relief=tk.FLAT, font=("Segoe UI", 8), padx=6, command=self._sim).pack(side=tk.RIGHT, padx=6, pady=4)
        ef = tk.Frame(tab, bg=self._bg)
        ef.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self._yt = tk.Text(ef, bg="#181825", fg="#cdd6f4", insertbackground="#cdd6f4", font=("Consolas", 10), wrap=tk.NONE, undo=True)
        ys = ttk.Scrollbar(ef, command=self._yt.yview)
        xs = ttk.Scrollbar(ef, orient=tk.HORIZONTAL, command=self._yt.xview)
        self._yt.configure(yscrollcommand=ys.set, xscrollcommand=xs.set)
        ys.pack(side=tk.RIGHT, fill=tk.Y)
        xs.pack(side=tk.BOTTOM, fill=tk.X)
        self._yt.pack(fill=tk.BOTH, expand=True)
        self._yt.insert("1.0", self._yaml)
        rf = tk.LabelFrame(tab, text="Simulation Result", bg=self._bg, fg="#6c7086", font=("Segoe UI", 9))
        rf.pack(fill=tk.X, padx=6, pady=(0, 6))
        self._sl = tk.Label(rf, text="No simulation run yet.", bg=self._bg, fg="#6c7086", font=("Segoe UI", 9), anchor=tk.W)
        self._sl.pack(fill=tk.X, padx=6, pady=4)

    def _mk_bom(self) -> None:
        tab = tk.Frame(self._nb, bg=self._bg)
        self._nb.add(tab, text="  BOM  ")
        tb = tk.Frame(tab, bg="#313244", height=36)
        tb.pack(fill=tk.X)
        tb.pack_propagate(False)
        tk.Button(tb, text="Refresh BOM", bg="#89b4fa", fg="#1e1e2e", relief=tk.FLAT, font=("Segoe UI", 8), padx=6, command=self._rbom).pack(side=tk.LEFT, padx=6, pady=4)
        tk.Button(tb, text="Export CSV", bg="#a6e3a1", fg="#1e1e2e", relief=tk.FLAT, font=("Segoe UI", 8), padx=6, command=self._ecsv).pack(side=tk.LEFT, padx=4, pady=4)
        self._cl = tk.Label(tb, text="Total: $0.00", bg="#313244", fg="#f9e2af", font=("Segoe UI", 9, "bold"))
        self._cl.pack(side=tk.RIGHT, padx=8)
        cols = ("ref", "value", "package", "qty", "manufacturer", "price")
        self._tv = ttk.Treeview(tab, columns=cols, show="headings", height=20)
        for c, w in zip(cols, (80, 120, 100, 50, 160, 70)):
            self._tv.heading(c, text=c.capitalize())
            self._tv.column(c, width=w)
        sb = ttk.Scrollbar(tab, command=self._tv.yview)
        self._tv.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._tv.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

    # ---- Schematic logic ----
    def _sset(self, c: Dict[str, Any]) -> None:
        self._tool = c.get("sym", "R")
        self._cur = dict(c)

    def _anet(self) -> None:
        n = simpledialog.askstring("Net Label", "Net name:", parent=self)
        if n:
            self._tool = "__net__"
            self._nname = n

    def _sclk(self, e: tk.Event) -> None:
        x, y = e.x, e.y
        if self._tool == "__wire__":
            self._drag = (x, y)
            return
        if self._tool == "__net__":
            nl = getattr(self, "_nname", "NET")
            self._nets.append({"x": x, "y": y, "name": nl})
            self._cv.create_text(x, y, text=nl, fill="#a6e3a1", font=("Consolas", 9), anchor=tk.W)
            self._tool = None
            return
        if self._tool and hasattr(self, "_cur"):
            c = dict(self._cur)
            sym = c.get("sym", "R")
            self._rc.setdefault(sym, 0)
            self._rc[sym] += 1
            c.update({"ref": f"{sym}{self._rc[sym]}", "x": x, "y": y})
            self._comps.append(c)
            self._dc(c, len(self._comps) - 1)
            self._ssel(len(self._comps) - 1)
            return
        h = next((i for i, c in enumerate(self._comps) if abs(x - c.get("x", 0)) < 30 and abs(y - c.get("y", 0)) < 20), None)
        if h is not None:
            self._sel = h
            self._drag = (x, y)
            self._ssel(h)
        else:
            self._sdsel()

    def _smov(self, e: tk.Event) -> None:
        if self._tool == "__wire__":
            return
        if self._sel is not None and self._drag:
            c = self._comps[self._sel]
            c["x"] += e.x - self._drag[0]
            c["y"] += e.y - self._drag[1]
            self._drag = (e.x, e.y)
            self._rdraw()

    def _srel(self, e: tk.Event) -> None:
        if self._tool == "__wire__" and self._drag:
            w = (*self._drag, e.x, e.y)
            self._wires.append(w)
            self._cv.create_line(*w, fill="#cdd6f4", width=2)
            self._drag = None
            return
        self._drag = None

    def _dc(self, c: Dict[str, Any], i: int) -> None:
        x, y = c["x"], c["y"]
        t = f"c{i}"
        self._cv.create_rectangle(x - 25, y - 12, x + 25, y + 12, fill="#313244", outline="#89b4fa", tags=t)
        self._cv.create_text(x, y - 2, text=c.get("ref", "?"), fill="#89b4fa", font=("Consolas", 8, "bold"), tags=t)
        self._cv.create_text(x, y + 8, text=c.get("val", ""), fill="#6c7086", font=("Consolas", 7), tags=t)

    def _rdraw(self) -> None:
        self._cv.delete("all")
        for i, c in enumerate(self._comps):
            self._dc(c, i)
        for w in self._wires:
            self._cv.create_line(*w, fill="#cdd6f4", width=2)
        for n in self._nets:
            self._cv.create_text(n["x"], n["y"], text=n["name"], fill="#a6e3a1", font=("Consolas", 9), anchor=tk.W)
        if self._sel is not None and self._sel < len(self._comps):
            c = self._comps[self._sel]
            self._cv.create_rectangle(c["x"] - 27, c["y"] - 14, c["x"] + 27, c["y"] + 14, outline="#f9e2af", width=2)

    def _ssel(self, i: int) -> None:
        self._sel = i
        self._rdraw()
        for w in self._pf.winfo_children():
            w.destroy()
        c = self._comps[i]
        for lb, k in [("Reference", "ref"), ("Value", "val"), ("Package", "pkg"), ("Name", "name")]:
            tk.Label(self._pf, text=lb, bg=self._bg, fg="#6c7086", font=("Segoe UI", 8)).pack(fill=tk.X, padx=4, pady=(4, 0))
            v = tk.StringVar(value=c.get(k, ""))
            en = tk.Entry(self._pf, textvariable=v, bg="#313244", fg=self._fg, insertbackground=self._fg, font=("Segoe UI", 9))
            en.pack(fill=tk.X, padx=4)
            en.bind("<Return>", lambda ev, kk=k, vv=v: self._sprop(i, kk, vv.get()))

    def _sdsel(self) -> None:
        self._sel = None
        self._rdraw()
        for w in self._pf.winfo_children():
            w.destroy()
        tk.Label(self._pf, text="No selection", bg=self._bg, fg="#6c7086", font=("Segoe UI", 9)).pack(pady=20)

    def _sprop(self, i: int, k: str, v: str) -> None:
        if i < len(self._comps):
            self._comps[i][k] = v
            self._rdraw()

    def _erc(self) -> None:
        errs: List[str] = []
        refs = [c.get("ref", "") for c in self._comps]
        dupes = [r for r in set(refs) if refs.count(r) > 1]
        if dupes:
            errs.append(f"Duplicate refs: {', '.join(dupes)}")
        for c in self._comps:
            if not c.get("val"):
                errs.append(f"{c.get('ref', '?')}: missing value")
        if not self._comps:
            errs.append("Empty schematic")
        if errs:
            messagebox.showwarning("ERC Errors", "\n".join(errs), parent=self)
        else:
            messagebox.showinfo("ERC", "Electrical Rules Check passed.", parent=self)

    # ---- PCB logic ----
    def _pclk(self, e: tk.Event) -> None:
        if self._ptool == "via":
            self._pcv.create_oval(e.x - 6, e.y - 6, e.x + 6, e.y + 6, fill="#f9e2af", outline="#f9e2af")
            self._pcv.create_oval(e.x - 2, e.y - 2, e.x + 2, e.y + 2, fill="#11111b", outline="#11111b")
        elif self._ptool == "route":
            self._pstart = (e.x, e.y)

    def _pdrg(self, e: tk.Event) -> None:
        if self._ptool == "route" and hasattr(self, "_pstart"):
            x0, y0 = self._pstart
            clr = "#f38ba8" if "Bottom" in self._player else "#89b4fa"
            self._pcv.create_line(x0, y0, e.x, e.y, fill=clr, width=3, capstyle=tk.ROUND)
            self._pcbt.append((x0, y0, e.x, e.y))
            self._pstart = (e.x, e.y)

    def _drc(self) -> None:
        errs: List[str] = []
        if not self._pcbt:
            errs.append("No traces placed")
        for i, t in enumerate(self._pcbt):
            if ((t[2] - t[0])**2 + (t[3] - t[1])**2)**0.5 < 2:
                errs.append(f"Trace {i}: too short")
        if errs:
            messagebox.showwarning("DRC Errors", "\n".join(errs), parent=self)
        else:
            messagebox.showinfo("DRC", "Design Rule Check passed.", parent=self)

    # ---- Board config / codegen ----
    def _dyaml(self) -> str:
        return ("name: my_board\narch: arm-cortex-m\ncpu: cortex-m4\nclock_mhz: 168\nhse_mhz: 8\nmemory:\n"
                "  - name: FLASH\n    base: 0x08000000\n    size: 0x100000\n"
                "  - name: SRAM\n    base: 0x20000000\n    size: 0x20000\nperipherals:\n"
                "  - type: uart\n    name: uart0\n    base: 0x40011000\n    irq: 37\n"
                "  - type: gpio\n    name: gpioa\n    base: 0x40020000\n"
                "  - type: spi\n    name: spi1\n    base: 0x40013000\n    irq: 35\n"
                "  - type: i2c\n    name: i2c1\n    base: 0x40005400\n    irq: 31\n")

    def _pyaml(self) -> Dict[str, Any]:
        try:
            import yaml  # type: ignore[import-untyped]
            return yaml.safe_load(self._yt.get("1.0", tk.END)) or {}
        except Exception as e:
            messagebox.showerror("YAML Error", str(e), parent=self)
            return {}

    def _gcfg(self) -> None:
        try:
            import yaml  # type: ignore[import-untyped]
        except ImportError:
            messagebox.showerror("Error", "PyYAML required", parent=self)
            return
        cfg: Dict[str, Any] = {"name": "my_board", "arch": "arm-cortex-m", "cpu": "cortex-m4",
                               "clock_mhz": 168, "memory": [{"name": "FLASH", "base": 0x08000000, "size": 0x100000},
                                                            {"name": "SRAM", "base": 0x20000000, "size": 0x20000}], "peripherals": []}
        pm = {"MCU STM32F4": "cortex-m4", "MCU ESP32": "xtensa-lx7", "MCU nRF52": "cortex-m4", "MCU RP2040": "cortex-m0plus"}
        for c in self._comps:
            if c.get("name", "") in pm:
                cfg["cpu"] = pm[c["name"]]
        self._yt.delete("1.0", tk.END)
        self._yt.insert("1.0", yaml.dump(cfg, default_flow_style=False, sort_keys=False))

    def _cgen(self) -> None:
        dlg = tk.Toplevel(self)
        dlg.title("Generate Firmware")
        dlg.geometry("360x240")
        dlg.configure(bg=self._bg)
        dlg.transient(self)
        tk.Label(dlg, text="Generate Firmware", bg=self._bg, fg=self._fg, font=("Segoe UI", 12, "bold")).pack(pady=(12, 8))
        tk.Label(dlg, text="Target OS:", bg=self._bg, fg="#6c7086", font=("Segoe UI", 9)).pack(anchor=tk.W, padx=16)
        ov = tk.StringVar(value=self._tos)
        ttk.Combobox(dlg, textvariable=ov, values=_OL, state="readonly", width=20).pack(padx=16, pady=4)
        tk.Label(dlg, text="App Name:", bg=self._bg, fg="#6c7086", font=("Segoe UI", 9)).pack(anchor=tk.W, padx=16)
        nv = tk.StringVar(value="app")
        tk.Entry(dlg, textvariable=nv, bg="#313244", fg=self._fg, insertbackground=self._fg, font=("Segoe UI", 10)).pack(fill=tk.X, padx=16, pady=4)

        def gen():
            self._tos = ov.get()
            cfg = self._pyaml()
            if not cfg:
                return
            od = filedialog.askdirectory(title="Output", parent=dlg)
            if not od:
                return
            self._dogen(cfg, nv.get() or "app", od)
            dlg.destroy()
        tk.Button(dlg, text="Generate", bg="#a6e3a1", fg="#1e1e2e", relief=tk.FLAT, font=("Segoe UI", 10, "bold"), padx=12, command=gen).pack(pady=16)

    def _dogen(self, cfg: Dict[str, Any], app: str, od: str) -> None:
        if FirmwareGenerator is None:
            messagebox.showerror("Error", "FirmwareGenerator unavailable.", parent=self)
            return
        try:
            g = FirmwareGenerator(cfg, target_os=self._tos)
            fs = g.generate(app_name=app)
            for f, c in fs.items():
                p = os.path.join(od, f)
                os.makedirs(os.path.dirname(p) or od, exist_ok=True)
                with open(p, "w", encoding="utf-8") as fh:
                    fh.write(c)
            messagebox.showinfo("Done", f"{len(fs)} files \u2192 {od}", parent=self)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)

    # ---- EoSim integration ----
    def set_plugin_manager(self, mgr: Any) -> None:
        self._pmgr = mgr
        if mgr:
            self._eosim = mgr.get_plugin("eosim")

    def _sim(self) -> None:
        cfg = self._pyaml()
        if not cfg:
            return
        if self._pmgr and PluginHook is not None:
            res = self._pmgr.fire_hook(PluginHook.ON_SIMULATE, {"design": cfg, "platform": self._tplat})
            if res:
                r = res[0]
                ok = r.get("success", False)
                t = ("PASS" if ok else "FAIL") + f"  Platform: {r.get('platform', '?')}"
                if r.get("duration_ms"):
                    t += f"  {r['duration_ms']:.1f}ms"
                if r.get("errors"):
                    t += "\nErrors: " + "; ".join(r["errors"])
                self._sl.config(text=t, fg="#a6e3a1" if ok else "#f38ba8")
                return
        messagebox.showinfo("Simulate", "EoSim plugin not available.", parent=self)

    # ---- BOM ----
    def _rbom(self) -> None:
        for r in self._tv.get_children():
            self._tv.delete(r)
        grouped: Dict[str, Dict[str, Any]] = {}
        for c in self._comps:
            k = f"{c.get('val', '')}|{c.get('pkg', '')}"
            if k not in grouped:
                grouped[k] = {"ref": c.get("ref", "?"), "value": c.get("val", ""), "package": c.get("pkg", ""), "qty": 0, "manufacturer": "", "price": 0.0}
            grouped[k]["qty"] += 1
            if grouped[k]["qty"] > 1:
                grouped[k]["ref"] += f", {c.get('ref', '?')}"
        self._bom = list(grouped.values())
        total = 0.0
        for b in self._bom:
            self._tv.insert("", "end", values=(b["ref"], b["value"], b["package"], b["qty"], b["manufacturer"], f"${b['price']:.2f}"))
            total += b["price"] * b["qty"]
        self._cl.config(text=f"Total: ${total:.2f}")

    def _ecsv(self) -> None:
        if not self._bom:
            self._rbom()
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")], parent=self)
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Reference", "Value", "Package", "Qty", "Manufacturer", "Price"])
            for b in self._bom:
                w.writerow([b["ref"], b["value"], b["package"], b["qty"], b["manufacturer"], b["price"]])
