"""UML Diagram Editor — class, sequence, state, use-case, and activity diagrams."""
from __future__ import annotations
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from typing import Any, Dict, List, Optional, Tuple

try:
    from eostudio.core.uml import UMLClass, UMLRelation, UMLDiagram
except ImportError:
    UMLClass = UMLRelation = UMLDiagram = None  # type: ignore[assignment,misc]

CLASS_TOOLS = [("class", "Class", "#89b4fa"), ("interface", "Interface", "#cba6f7"),
               ("abstract", "Abstract Class", "#a6e3a1"), ("enum", "Enum", "#f9e2af"),
               ("note", "Note", "#6c7086")]
RELATION_TOOLS = [("association", "Association ——►", "#cdd6f4"), ("aggregation", "Aggregation ◇——", "#cdd6f4"),
                  ("composition", "Composition ◆——", "#cdd6f4"), ("inheritance", "Inheritance △——", "#cdd6f4"),
                  ("implementation", "Implementation △⋯", "#cdd6f4"), ("dependency", "Dependency ⋯►", "#cdd6f4")]
SEQUENCE_TOOLS = [("actor", "Actor", "#89b4fa"), ("lifeline", "Lifeline", "#a6e3a1"),
                  ("sync_msg", "Sync Message", "#f9e2af"), ("async_msg", "Async Message", "#f38ba8"),
                  ("return_msg", "Return", "#6c7086"), ("self_msg", "Self Call", "#cba6f7")]
STATE_TOOLS = [("state", "State", "#89b4fa"), ("initial", "Initial", "#a6e3a1"),
               ("final", "Final", "#f38ba8"), ("transition", "Transition", "#f9e2af"),
               ("choice", "Choice", "#cba6f7")]
USECASE_TOOLS = [("actor_uc", "Actor", "#89b4fa"), ("usecase", "Use Case", "#a6e3a1"),
                 ("include", "«include»", "#f9e2af"), ("extend", "«extend»", "#f38ba8"),
                 ("boundary", "System Boundary", "#6c7086")]
ACTIVITY_TOOLS = [("action", "Action", "#89b4fa"), ("decision", "Decision", "#f9e2af"),
                  ("fork", "Fork / Join", "#a6e3a1"), ("start", "Start", "#a6e3a1"),
                  ("end", "End", "#f38ba8"), ("flow", "Flow Arrow", "#6c7086")]
LANGUAGES = ["Python", "Java", "Kotlin", "TypeScript", "C++", "C#"]
_TAB_TOOLS: Dict[str, list] = {"Class": CLASS_TOOLS + RELATION_TOOLS, "Sequence": SEQUENCE_TOOLS,
                               "State Machine": STATE_TOOLS, "Use Case": USECASE_TOOLS, "Activity": ACTIVITY_TOOLS}
_REL_IDS = {r[0] for r in RELATION_TOOLS}
_CONN_IDS = {"transition", "flow", "include", "extend", "sync_msg", "async_msg", "return_msg", "self_msg"}


def _uml_field(a: str, lang: str) -> str:
    parts = a.split(":")
    name = parts[0].lstrip("+-# ").strip()
    tp = parts[1].strip() if len(parts) > 1 else ("str" if lang == "Python" else "String")
    return name, tp


class UMLEditor(tk.Frame):
    """Full UML diagram editor with code generation and export."""
    def __init__(self, master: tk.Widget, bg: str = "#1e1e2e", fg: str = "#cdd6f4", **kw: Any):
        super().__init__(master, bg=bg, **kw)
        self._bg, self._fg = bg, fg
        self._elements: Dict[str, List[Dict[str, Any]]] = {k: [] for k in _TAB_TOOLS}
        self._relations: Dict[str, List[Dict[str, Any]]] = {k: [] for k in _TAB_TOOLS}
        self._sel: Optional[int] = None
        self._tool: Optional[str] = None
        self._conn0: Optional[int] = None
        self._doff: Tuple[int, int] = (0, 0)
        self._tab: str = "Class"
        self._pw: List[tk.Widget] = []
        self._build_ui()

    def _build_ui(self) -> None:
        left = tk.Frame(self, bg=self._bg, width=175)
        left.pack(side=tk.LEFT, fill=tk.Y)
        left.pack_propagate(False)
        tk.Label(left, text="Tools", bg=self._bg, fg=self._fg,
                 font=("Segoe UI", 10, "bold"), anchor=tk.W).pack(fill=tk.X, padx=8, pady=(8, 2))
        self._tframe = tk.Frame(left, bg=self._bg)
        self._tframe.pack(fill=tk.BOTH, expand=True)
        ttk.Separator(left, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=4, pady=4)
        ef = tk.LabelFrame(left, text="Export", bg=self._bg, fg="#f9e2af",
                           font=("Segoe UI", 9, "bold"), bd=1, relief=tk.GROOVE)
        ef.pack(fill=tk.X, padx=4, pady=4)
        for fmt in ("PlantUML", "Mermaid"):
            tk.Button(ef, text=f"Export {fmt}", bg="#313244", fg=self._fg, relief=tk.FLAT,
                      font=("Segoe UI", 8), command=lambda f=fmt: self._export(f)).pack(fill=tk.X, padx=4, pady=1)
        tk.Button(ef, text="Generate Code…", bg="#89b4fa", fg="#1e1e2e", relief=tk.FLAT,
                  font=("Segoe UI", 9), command=self._codegen_dlg).pack(fill=tk.X, padx=4, pady=(4, 4))
        right = tk.Frame(self, bg=self._bg, width=220)
        right.pack(side=tk.RIGHT, fill=tk.Y)
        right.pack_propagate(False)
        tk.Label(right, text="Properties", bg=self._bg, fg=self._fg,
                 font=("Segoe UI", 11, "bold"), anchor=tk.W).pack(fill=tk.X, padx=8, pady=(8, 4))
        self._pf = tk.Frame(right, bg=self._bg)
        self._pf.pack(fill=tk.BOTH, expand=True, padx=4)
        self._nsl = tk.Label(self._pf, text="No element selected", bg=self._bg, fg="#6c7086", font=("Segoe UI", 9))
        self._nsl.pack(pady=20)
        center = tk.Frame(self, bg=self._bg)
        center.pack(fill=tk.BOTH, expand=True)
        self._nb = ttk.Notebook(center)
        self._nb.pack(fill=tk.BOTH, expand=True)
        self._cvs: Dict[str, tk.Canvas] = {}
        for tn in _TAB_TOOLS:
            fr = tk.Frame(self._nb, bg=self._bg)
            self._nb.add(fr, text=tn)
            cv = tk.Canvas(fr, bg="#11111b", highlightthickness=0)
            cv.pack(fill=tk.BOTH, expand=True)
            cv.bind("<ButtonPress-1>", lambda e, t=tn: self._click(e, t))
            cv.bind("<B1-Motion>", lambda e, t=tn: self._drag(e, t))
            cv.bind("<Double-Button-1>", lambda e, t=tn: self._dbl(e, t))
            self._cvs[tn] = cv
        self._nb.bind("<<NotebookTabChanged>>", self._tab_chg)
        self._refresh_tools()

    def _refresh_tools(self) -> None:
        for w in self._tframe.winfo_children():
            w.destroy()
        for tid, lbl, clr in _TAB_TOOLS.get(self._tab, []):
            b = tk.Button(self._tframe, text=lbl, bg="#313244", fg=clr, relief=tk.FLAT,
                          font=("Segoe UI", 9), anchor=tk.W, padx=6, pady=2)
            b.pack(fill=tk.X, padx=4, pady=1)
            b.bind("<ButtonPress-1>", lambda e, t=tid: setattr(self, '_tool', t) or setattr(self, '_conn0', None))

    def _tab_chg(self, _e: tk.Event) -> None:
        self._tab = list(_TAB_TOOLS.keys())[self._nb.index(self._nb.select())]
        self._sel = self._conn0 = self._tool = None
        self._refresh_tools()
        self._clr_props()

    def _click(self, ev: tk.Event, tab: str) -> None:
        t = self._tool
        if t and (t in _REL_IDS or t in _CONN_IDS):
            h = self._hit(ev.x, ev.y, tab)
            if h is not None:
                if self._conn0 is None:
                    self._conn0 = h
                else:
                    self._relations[tab].append({"type": t, "from": self._conn0, "to": h,
                                                 "label": t.replace("_", " ").title()})
                    self._conn0 = self._tool = None
                    self._redraw(tab)
            return
        if t:
            self._elements[tab].append(self._mk(t, ev.x, ev.y))
            self._sel = len(self._elements[tab]) - 1
            self._tool = None
            self._redraw(tab)
            self._show_props(tab)
            return
        h = self._hit(ev.x, ev.y, tab)
        self._sel = h
        if h is not None:
            el = self._elements[tab][h]
            self._doff = (ev.x - el["x"], ev.y - el["y"])
            self._show_props(tab)
        else:
            self._clr_props()
        self._redraw(tab)

    def _drag(self, ev: tk.Event, tab: str) -> None:
        if self._sel is None:
            return
        el = self._elements[tab][self._sel]
        el["x"], el["y"] = ev.x - self._doff[0], ev.y - self._doff[1]
        self._redraw(tab)

    def _dbl(self, ev: tk.Event, tab: str) -> None:
        h = self._hit(ev.x, ev.y, tab)
        if h is not None and tab == "Class":
            self._cls_edit(tab, h)

    def _hit(self, x: int, y: int, tab: str) -> Optional[int]:
        for i in range(len(self._elements[tab]) - 1, -1, -1):
            e = self._elements[tab][i]
            if e["x"] <= x <= e["x"] + e["w"] and e["y"] <= y <= e["y"] + e["h"]:
                return i
        return None

    def _mk(self, t: str, x: int, y: int) -> Dict[str, Any]:
        b: Dict[str, Any] = {"type": t, "x": x, "y": y, "name": t.title()}
        if t in ("class", "interface", "abstract", "enum"):
            b.update(w=160, h=120, name=f"My{t.title()}", stereotype=f"«{t}»" if t != "class" else "",
                     attributes=["+name: String", "+id: int"], methods=["+toString(): String"])
        elif t == "note":
            b.update(w=120, h=60, text="…")
        elif t == "state":
            b.update(w=120, h=50)
        elif t in ("initial", "start"):
            b.update(w=24, h=24)
        elif t in ("final", "end"):
            b.update(w=24, h=24)
        elif t in ("choice", "decision"):
            b.update(w=40, h=40)
        elif t == "fork":
            b.update(w=120, h=8)
        elif t in ("actor", "actor_uc"):
            b.update(w=40, h=70, name="Actor")
        elif t == "lifeline":
            b.update(w=80, h=30, name="Object")
        elif t == "usecase":
            b.update(w=140, h=50, name="Use Case")
        elif t == "boundary":
            b.update(w=300, h=250, name="System")
        elif t == "action":
            b.update(w=120, h=40, name="Action")
        else:
            b.update(w=100, h=40)
        return b

    def _redraw(self, tab: str) -> None:
        c = self._cvs[tab]
        c.delete("all")
        els = self._elements[tab]
        for rel in self._relations[tab]:
            fi, ti = rel["from"], rel["to"]
            if fi >= len(els) or ti >= len(els):
                continue
            fe, te = els[fi], els[ti]
            x1, y1 = fe["x"] + fe["w"] // 2, fe["y"] + fe["h"] // 2
            x2, y2 = te["x"] + te["w"] // 2, te["y"] + te["h"] // 2
            rt = rel["type"]
            dash = None
            clr = "#585b70"
            if rt in ("dependency", "implementation"):
                dash = (6, 3)
            if rt in ("inheritance", "implementation"):
                clr = "#89b4fa"
            elif rt in ("sync_msg", "async_msg", "return_msg", "self_msg"):
                clr = "#f9e2af"
                if rt == "async_msg":
                    dash = (8, 4)
                elif rt == "return_msg":
                    dash = (4, 4)
                    clr = "#6c7086"
            c.create_line(x1, y1, x2, y2, fill=clr, width=2, arrow=tk.LAST,
                          arrowshape=(10, 12, 5), dash=dash)
            mx, my = (x1 + x2) // 2, (y1 + y2) // 2
            if rt == "aggregation":
                c.create_polygon(x1, y1 - 8, x1 + 8, y1, x1, y1 + 8, x1 - 8, y1, fill="", outline=clr)
            elif rt == "composition":
                c.create_polygon(x1, y1 - 8, x1 + 8, y1, x1, y1 + 8, x1 - 8, y1, fill=clr, outline=clr)
            c.create_text(mx, my - 10, text=rel.get("label", ""), fill="#6c7086", font=("Segoe UI", 7))
        for i, el in enumerate(els):
            self._draw_el(c, el, i == self._sel, tab)

    def _draw_el(self, c: tk.Canvas, el: Dict[str, Any], sel: bool, tab: str) -> None:
        x, y, w, h, t = el["x"], el["y"], el["w"], el["h"], el["type"]
        ol = "#f9e2af" if sel else "#585b70"
        lw = 2 if sel else 1
        if t in ("class", "interface", "abstract", "enum"):
            self._draw_cls(c, el, ol, lw)
        elif t == "note":
            c.create_rectangle(x, y, x + w, y + h, outline=ol, fill="#313244", width=lw)
            c.create_text(x + w // 2, y + h // 2, text=el.get("text", ""), fill="#6c7086", font=("Segoe UI", 8))
        elif t in ("state", "action"):
            c.create_rectangle(x, y, x + w, y + h, outline=ol, fill="#313244", width=lw)
            c.create_text(x + w // 2, y + h // 2, text=el["name"], fill="#89b4fa", font=("Segoe UI", 9, "bold"))
        elif t in ("initial", "start"):
            c.create_oval(x, y, x + w, y + h, fill="#a6e3a1", outline=ol, width=lw)
        elif t in ("final", "end"):
            c.create_oval(x, y, x + w, y + h, fill="", outline=ol, width=lw)
            c.create_oval(x + 4, y + 4, x + w - 4, y + h - 4, fill="#f38ba8", outline="")
        elif t in ("choice", "decision"):
            c.create_polygon(x + w // 2, y, x + w, y + h // 2, x + w // 2, y + h, x, y + h // 2, fill="#313244", outline=ol, width=lw)
        elif t == "fork":
            c.create_rectangle(x, y, x + w, y + h, fill="#585b70", outline=ol, width=lw)
        elif t in ("actor", "actor_uc"):
            cx_a = x + w // 2
            c.create_oval(cx_a - 8, y, cx_a + 8, y + 16, outline=ol, fill="#313244", width=lw)
            c.create_line(cx_a, y + 16, cx_a, y + 44, fill=ol, width=lw)
            c.create_line(cx_a - 14, y + 28, cx_a + 14, y + 28, fill=ol, width=lw)
            c.create_line(cx_a, y + 44, cx_a - 10, y + 60, fill=ol, width=lw)
            c.create_line(cx_a, y + 44, cx_a + 10, y + 60, fill=ol, width=lw)
            c.create_text(cx_a, y + h + 8, text=el["name"], fill=self._fg, font=("Segoe UI", 8))
        elif t == "lifeline":
            c.create_rectangle(x, y, x + w, y + h, outline=ol, fill="#313244", width=lw)
            c.create_text(x + w // 2, y + h // 2, text=el["name"], fill="#a6e3a1", font=("Segoe UI", 9))
            ch_h = self._cvs[tab].winfo_height() or 600
            c.create_line(x + w // 2, y + h, x + w // 2, ch_h - 20, fill="#585b70", width=1, dash=(4, 4))
        elif t == "usecase":
            c.create_oval(x, y, x + w, y + h, outline=ol, fill="#313244", width=lw)
            c.create_text(x + w // 2, y + h // 2, text=el["name"], fill="#a6e3a1", font=("Segoe UI", 9))
        elif t == "boundary":
            c.create_rectangle(x, y, x + w, y + h, outline=ol, fill="", width=lw, dash=(8, 4))
            c.create_text(x + w // 2, y + 14, text=el["name"], fill="#6c7086", font=("Segoe UI", 10, "bold"))
        else:
            c.create_rectangle(x, y, x + w, y + h, outline=ol, fill="#313244", width=lw)
            c.create_text(x + w // 2, y + h // 2, text=el["name"], fill=self._fg, font=("Segoe UI", 9))

    def _draw_cls(self, c: tk.Canvas, el: Dict[str, Any], ol: str, lw: int) -> None:
        x, y, w = el["x"], el["y"], el["w"]
        at, mt, st = el.get("attributes", []), el.get("methods", []), el.get("stereotype", "")
        lh = 16
        ns = 30 + (14 if st else 0)
        ats = max(20, len(at) * lh + 8)
        ms = max(20, len(mt) * lh + 8)
        th = ns + ats + ms
        el["h"] = th
        c.create_rectangle(x, y, x + w, y + th, outline=ol, fill="#313244", width=lw)
        ty = y + 6
        if st:
            c.create_text(x + w // 2, ty + 6, text=st, fill="#6c7086", font=("Segoe UI", 7, "italic"))
            ty += 14
        c.create_text(x + w // 2, ty + 10, text=el["name"], fill="#89b4fa", font=("Segoe UI", 10, "bold"))
        s1 = y + ns
        c.create_line(x, s1, x + w, s1, fill=ol, width=1)
        for j, a in enumerate(at):
            c.create_text(x + 8, s1 + 6 + j * lh, text=a, fill="#a6e3a1", font=("Consolas", 8), anchor=tk.NW)
        s2 = s1 + ats
        c.create_line(x, s2, x + w, s2, fill=ol, width=1)
        for j, m in enumerate(mt):
            c.create_text(x + 8, s2 + 6 + j * lh, text=m, fill="#f9e2af", font=("Consolas", 8), anchor=tk.NW)

    def _clr_props(self) -> None:
        for w in self._pw:
            w.destroy()
        self._pw.clear()
        self._nsl.pack(pady=20)

    def _show_props(self, tab: str) -> None:
        self._clr_props()
        self._nsl.pack_forget()
        if self._sel is None:
            self._nsl.pack(pady=20)
            return
        el = self._elements[tab][self._sel]
        flds = [("Type", el["type"], True), ("Name", el["name"], False),
                ("X", str(el["x"]), False), ("Y", str(el["y"]), False),
                ("Width", str(el["w"]), False), ("Height", str(el["h"]), False)]
        if "stereotype" in el:
            flds.append(("Stereotype", el["stereotype"], False))
        for lbl, val, ro in flds:
            row = tk.Frame(self._pf, bg=self._bg)
            row.pack(fill=tk.X, padx=4, pady=1)
            self._pw.append(row)
            tk.Label(row, text=lbl, bg=self._bg, fg=self._fg, font=("Segoe UI", 8), width=10, anchor=tk.W).pack(side=tk.LEFT)
            var = tk.StringVar(value=val)
            ent = tk.Entry(row, textvariable=var, width=14, bg="#313244", fg=self._fg, font=("Consolas", 8),
                           relief=tk.FLAT, insertbackground=self._fg, state=tk.DISABLED if ro else tk.NORMAL)
            ent.pack(side=tk.LEFT, fill=tk.X, expand=True)
            if not ro:
                ent.bind("<Return>", lambda e, k=lbl.lower(), v=var, t=tab: self._pchg(k, v.get(), t))
        if el["type"] in ("class", "interface", "abstract", "enum"):
            b = tk.Button(self._pf, text="Edit Class…", bg="#89b4fa", fg="#1e1e2e", relief=tk.FLAT,
                          font=("Segoe UI", 9), command=lambda: self._cls_edit(tab, self._sel))
            b.pack(padx=4, pady=4)
            self._pw.append(b)
        db = tk.Button(self._pf, text="Delete", bg="#f38ba8", fg="#1e1e2e", relief=tk.FLAT,
                       font=("Segoe UI", 9), command=lambda: self._del(tab))
        db.pack(padx=4, pady=4)
        self._pw.append(db)

    def _pchg(self, k: str, v: str, tab: str) -> None:
        if self._sel is None:
            return
        el = self._elements[tab][self._sel]
        if k in ("x", "y", "width", "height"):
            try:
                val = int(float(v))
            except ValueError:
                return
            el[{"width": "w", "height": "h"}.get(k, k)] = val
        else:
            el[k] = v
        self._redraw(tab)

    def _del(self, tab: str) -> None:
        if self._sel is not None:
            self._elements[tab].pop(self._sel)
            self._sel = None
            self._redraw(tab)
            self._clr_props()

    def _cls_edit(self, tab: str, idx: int) -> None:
        el = self._elements[tab][idx]
        win = tk.Toplevel(self, bg=self._bg)
        win.title(f"Edit {el['name']}")
        win.geometry("480x520")
        win.transient(self)
        tk.Label(win, text="Class Name:", bg=self._bg, fg=self._fg, font=("Segoe UI", 9)).pack(anchor=tk.W, padx=8, pady=(8, 2))
        nv = tk.StringVar(value=el["name"])
        tk.Entry(win, textvariable=nv, bg="#313244", fg=self._fg, font=("Consolas", 10), relief=tk.FLAT, insertbackground=self._fg).pack(fill=tk.X, padx=8)
        tk.Label(win, text="Stereotype:", bg=self._bg, fg=self._fg, font=("Segoe UI", 9)).pack(anchor=tk.W, padx=8, pady=(8, 2))
        sv = tk.StringVar(value=el.get("stereotype", ""))
        tk.Entry(win, textvariable=sv, bg="#313244", fg=self._fg, font=("Consolas", 10), relief=tk.FLAT, insertbackground=self._fg).pack(fill=tk.X, padx=8)
        tk.Label(win, text="Attributes (one per line):", bg=self._bg, fg=self._fg, font=("Segoe UI", 9)).pack(anchor=tk.W, padx=8, pady=(8, 2))
        at = tk.Text(win, height=8, bg="#313244", fg="#a6e3a1", font=("Consolas", 9), relief=tk.FLAT, insertbackground=self._fg)
        at.pack(fill=tk.X, padx=8)
        at.insert("1.0", "\n".join(el.get("attributes", [])))
        tk.Label(win, text="Methods (one per line):", bg=self._bg, fg=self._fg, font=("Segoe UI", 9)).pack(anchor=tk.W, padx=8, pady=(8, 2))
        mt = tk.Text(win, height=8, bg="#313244", fg="#f9e2af", font=("Consolas", 9), relief=tk.FLAT, insertbackground=self._fg)
        mt.pack(fill=tk.X, padx=8)
        mt.insert("1.0", "\n".join(el.get("methods", [])))

        def _apply():
            el["name"] = nv.get()
            el["stereotype"] = sv.get()
            el["attributes"] = [l for l in at.get("1.0", tk.END).strip().split("\n") if l.strip()]
            el["methods"] = [l for l in mt.get("1.0", tk.END).strip().split("\n") if l.strip()]
            self._redraw(tab)
            win.destroy()
        tk.Button(win, text="Apply", bg="#89b4fa", fg="#1e1e2e", relief=tk.FLAT, font=("Segoe UI", 10, "bold"), command=_apply).pack(pady=8)

    def _export(self, fmt: str) -> None:
        els = self._elements.get(self._tab, [])
        rels = self._relations.get(self._tab, [])
        lines: List[str] = []
        arw = {"association": "-->", "aggregation": "o--", "composition": "*--",
               "inheritance": "--|>", "implementation": "..|>", "dependency": "..>"}
        if fmt == "PlantUML":
            lines.append("@startuml")
            for el in els:
                if el["type"] in ("class", "interface", "abstract", "enum"):
                    lines.append(f'{el["type"]} {el["name"]} {{')
                    for a in el.get("attributes", []):
                        lines.append(f"  {a}")
                    for m in el.get("methods", []):
                        lines.append(f"  {m}")
                    lines.append("}")
            for r in rels:
                if r["from"] < len(els) and r["to"] < len(els):
                    lines.append(f'{els[r["from"]]["name"]} {arw.get(r["type"], "-->")} {els[r["to"]]["name"]}')
            lines.append("@enduml")
        else:
            lines.append("classDiagram")
            for el in els:
                if el["type"] in ("class", "interface", "abstract", "enum"):
                    lines.append(f'  class {el["name"]} {{')
                    for a in el.get("attributes", []):
                        lines.append(f"    {a}")
                    for m in el.get("methods", []):
                        lines.append(f"    {m}")
                    lines.append("  }")
            for r in rels:
                if r["from"] < len(els) and r["to"] < len(els):
                    lines.append(f'  {els[r["from"]]["name"]} {arw.get(r["type"], "-->")} {els[r["to"]]["name"]}')
        self._code_win(f"Export — {fmt}", "\n".join(lines))

    def _codegen_dlg(self) -> None:
        win = tk.Toplevel(self, bg=self._bg)
        win.title("Generate Code")
        win.geometry("360x200")
        win.transient(self)
        tk.Label(win, text="Target Language:", bg=self._bg, fg=self._fg, font=("Segoe UI", 10)).pack(anchor=tk.W, padx=12, pady=(12, 4))
        lv = tk.StringVar(value=LANGUAGES[0])
        ttk.Combobox(win, textvariable=lv, values=LANGUAGES, state="readonly", width=20).pack(padx=12)
        tk.Label(win, text="Output Directory:", bg=self._bg, fg=self._fg, font=("Segoe UI", 10)).pack(anchor=tk.W, padx=12, pady=(12, 4))
        dv = tk.StringVar(value="./generated")
        r = tk.Frame(win, bg=self._bg)
        r.pack(fill=tk.X, padx=12)
        tk.Entry(r, textvariable=dv, bg="#313244", fg=self._fg, font=("Consolas", 9), relief=tk.FLAT, insertbackground=self._fg).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(r, text="…", bg="#313244", fg=self._fg, relief=tk.FLAT,
                  command=lambda: dv.set(filedialog.askdirectory() or dv.get())).pack(side=tk.LEFT, padx=(4, 0))

        def _gen():
            code = self._gen_code(lv.get())
            win.destroy()
            self._code_win(f"Generated {lv.get()}", code)
        tk.Button(win, text="Generate", bg="#89b4fa", fg="#1e1e2e", relief=tk.FLAT, font=("Segoe UI", 10, "bold"), command=_gen).pack(pady=12)

    def _gen_code(self, lang: str) -> str:
        els = [e for e in self._elements.get("Class", []) if e["type"] in ("class", "interface", "abstract", "enum")]
        L: List[str] = []
        for el in els:
            n, at, mt = el["name"], el.get("attributes", []), el.get("methods", [])
            if lang == "Python":
                L += [f"class {n}:", "    def __init__(self):"]
                for a in at:
                    nm, _ = _uml_field(a, lang)
                    L.append(f"        self.{nm} = None")
                if not at:
                    L.append("        pass")
                for m in mt:
                    mn = m.split("(")[0].lstrip("+-# ").strip()
                    L += [f"    def {mn}(self):", "        pass"]
                L.append("")
            elif lang == "Java":
                L.append(f"public class {n} {{")
                for a in at:
                    nm, tp = _uml_field(a, lang)
                    L.append(f"    private {tp} {nm};")
                for m in mt:
                    mn = m.split("(")[0].lstrip("+-# ").strip()
                    L += [f"    public void {mn}() {{", "    }"]
                L += ["}", ""]
            elif lang == "Kotlin":
                L.append(f"class {n} {{")
                for a in at:
                    nm, tp = _uml_field(a, lang)
                    L.append(f"    var {nm}: {tp}? = null")
                for m in mt:
                    mn = m.split("(")[0].lstrip("+-# ").strip()
                    L += [f"    fun {mn}() {{", "    }"]
                L += ["}", ""]
            elif lang == "TypeScript":
                L.append(f"class {n} {{")
                for a in at:
                    nm, tp = _uml_field(a, lang)
                    L.append(f"    {nm}: {tp};")
                for m in mt:
                    mn = m.split("(")[0].lstrip("+-# ").strip()
                    L += [f"    {mn}(): void {{", "    }"]
                L += ["}", ""]
            elif lang == "C++":
                L += [f"class {n} {{", "public:"]
                for a in at:
                    nm, tp = _uml_field(a, lang)
                    L.append(f"    {tp} {nm};")
                for m in mt:
                    mn = m.split("(")[0].lstrip("+-# ").strip()
                    L.append(f"    void {mn}();")
                L += ["};", ""]
            elif lang == "C#":
                L.append(f"public class {n} {{")
                for a in at:
                    nm, tp = _uml_field(a, lang)
                    L.append(f"    public {tp} {nm} {{ get; set; }}")
                for m in mt:
                    mn = m.split("(")[0].lstrip("+-# ").strip()
                    L += [f"    public void {mn}() {{", "    }"]
                L += ["}", ""]
        return "\n".join(L)

    def _code_win(self, title: str, code: str) -> None:
        win = tk.Toplevel(self, bg=self._bg)
        win.title(title)
        win.geometry("600x400")
        win.transient(self)
        t = tk.Text(win, bg="#181825", fg=self._fg, insertbackground=self._fg, font=("Consolas", 10), wrap=tk.NONE, relief=tk.FLAT)
        t.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        t.insert("1.0", code)
        t.config(state=tk.DISABLED)
