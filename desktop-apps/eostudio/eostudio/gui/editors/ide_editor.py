"""Full-featured IDE/code editor panel (VS Code-like).

Activity bar, sidebar, tabbed editor, bottom panel, status bar,
command palette, find/replace, syntax highlighting, git integration.
"""

from __future__ import annotations

import datetime
import fnmatch
import os
import re
import subprocess
import threading
import tkinter as tk
import tkinter.font as tkfont
import tkinter.ttk as ttk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

# ---------------------------------------------------------------------------
# Optional integrations (graceful degradation when unavailable)
# ---------------------------------------------------------------------------
try:
    from eostudio.core.ide.syntax import SyntaxHighlighter
except ImportError:
    SyntaxHighlighter = None  # type: ignore[assignment,misc]
try:
    from eostudio.core.ide.language_server import LanguageServer
except ImportError:
    LanguageServer = None  # type: ignore[assignment,misc]
try:
    from eostudio.core.ide.git_integration import GitIntegration
except ImportError:
    GitIntegration = None  # type: ignore[assignment,misc]
try:
    from eostudio.core.ide.extensions import ExtensionManager
except ImportError:
    ExtensionManager = None  # type: ignore[assignment,misc]
try:
    from eostudio.core.ide.project_manager import ProjectManager
except ImportError:
    ProjectManager = None  # type: ignore[assignment,misc]
try:
    from eostudio.core.ide.terminal import TerminalEmulator
except ImportError:
    TerminalEmulator = None  # type: ignore[assignment,misc]
try:
    from eostudio.core.ide.debugger import Debugger
except ImportError:
    Debugger = None  # type: ignore[assignment,misc]
try:
    from eostudio.core.ide.cloud import CloudSync
except ImportError:
    CloudSync = None  # type: ignore[assignment,misc]

# ---------------------------------------------------------------------------
# Keyboard shortcuts
# ---------------------------------------------------------------------------
SHORTCUTS: Dict[str, str] = {
    "<Control-s>": "save", "<Control-Shift-S>": "save_as",
    "<Control-n>": "new_file", "<Control-o>": "open_file",
    "<Control-w>": "close_tab", "<Control-Tab>": "next_tab",
    "<Control-Shift-Tab>": "prev_tab",
    "<Control-f>": "find", "<Control-h>": "find_replace",
    "<Control-g>": "go_to_line", "<Control-Shift-P>": "command_palette",
    "<Control-b>": "toggle_sidebar", "<Control-j>": "toggle_panel",
    "<Control-d>": "duplicate_line", "<Control-slash>": "toggle_comment",
    "<F5>": "run", "<F9>": "toggle_breakpoint",
    "<Control-Shift-grave>": "new_terminal",
}

# ---------------------------------------------------------------------------
# Activity-bar icons (ASCII-safe Unicode)
# ---------------------------------------------------------------------------
ACTIVITY_ICONS: List[Tuple[str, str]] = [
    ("explorer", "\u2630"), ("search", "\u2315"),
    ("git", "\u2387"), ("extensions", "\u29c9"),
    ("debug", "\u2699"), ("run", "\u25b6"),
]

# ---------------------------------------------------------------------------
# File-type icons (short ASCII labels)
# ---------------------------------------------------------------------------
FILE_ICONS: Dict[str, str] = {
    ".py": "Py", ".js": "JS", ".ts": "TS", ".tsx": "Tx",
    ".jsx": "Jx", ".html": "Ht", ".css": "Cs", ".json": "Jn",
    ".md": "Md", ".xml": "Xm", ".yaml": "Ym", ".yml": "Ym",
    ".toml": "Tm", ".c": "C", ".h": "H", ".cpp": "C+",
    ".java": "Jv", ".go": "Go", ".rs": "Rs", ".rb": "Rb",
    ".php": "Ph", ".sh": "Sh", ".sql": "Sq", ".lua": "Lu",
    ".dart": "Dt", ".ini": "In", ".txt": "Tx",
}

# ---------------------------------------------------------------------------
# Extension -> language name mapping
# ---------------------------------------------------------------------------
LANGUAGE_MAP: Dict[str, str] = {
    ".py": "Python", ".pyw": "Python", ".js": "JavaScript",
    ".mjs": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript",
    ".jsx": "JavaScript", ".html": "HTML", ".htm": "HTML",
    ".css": "CSS", ".json": "JSON", ".md": "Markdown",
    ".xml": "XML", ".yaml": "YAML", ".yml": "YAML",
    ".toml": "TOML", ".c": "C", ".h": "C", ".cpp": "C++",
    ".cxx": "C++", ".cc": "C++", ".java": "Java",
    ".go": "Go", ".rs": "Rust", ".rb": "Ruby",
    ".php": "PHP", ".sh": "Shell", ".bash": "Shell",
    ".sql": "SQL", ".lua": "Lua", ".dart": "Dart",
    ".txt": "Plain Text", ".ini": "INI",
}

# ---------------------------------------------------------------------------
# Comment prefixes per language
# ---------------------------------------------------------------------------
COMMENT_PREFIXES: Dict[str, str] = {
    "Python": "# ", "JavaScript": "// ", "TypeScript": "// ",
    "HTML": "<!-- ", "CSS": "/* ", "JSON": "// ",
    "Markdown": "<!-- ", "XML": "<!-- ", "YAML": "# ",
    "TOML": "# ", "C": "// ", "C++": "// ", "Java": "// ",
    "Go": "// ", "Rust": "// ", "Ruby": "# ", "PHP": "// ",
    "Shell": "# ", "SQL": "-- ", "Lua": "-- ", "Dart": "// ",
    "Plain Text": "# ", "INI": "; ",
}

# ---------------------------------------------------------------------------
# Colour themes (Catppuccin Mocha dark, One Light light)
# ---------------------------------------------------------------------------
THEMES: Dict[str, Dict[str, str]] = {
    "dark": {
        "bg": "#1e1e2e", "fg": "#cdd6f4",
        "editor_bg": "#1e1e2e", "editor_fg": "#cdd6f4",
        "gutter_bg": "#181825", "gutter_fg": "#6c7086",
        "sidebar_bg": "#181825", "sidebar_fg": "#cdd6f4",
        "activity_bg": "#11111b", "activity_fg": "#6c7086",
        "activity_active": "#cba6f7",
        "tab_bg": "#181825", "tab_fg": "#6c7086",
        "tab_active_bg": "#1e1e2e", "tab_active_fg": "#cdd6f4",
        "panel_bg": "#181825", "panel_fg": "#cdd6f4",
        "status_bg": "#11111b", "status_fg": "#bac2de",
        "selection": "#45475a", "current_line": "#313244",
        "cursor": "#f5e0dc", "find_hl": "#f9e2af",
        "bracket_match": "#a6e3a1",
        "modified_dot": "#f9e2af", "error": "#f38ba8",
        "warning": "#fab387", "info": "#89b4fa", "success": "#a6e3a1",
        "comment": "#6c7086", "keyword": "#cba6f7",
        "string": "#a6e3a1", "number": "#fab387",
        "function": "#89b4fa", "class_name": "#f9e2af",
        "operator": "#89dceb", "decorator": "#f5c2e7",
        "builtin": "#f2cdcd",
        "minimap_bg": "#11111b", "tree_bg": "#181825",
        "input_bg": "#313244", "input_fg": "#cdd6f4",
        "border": "#313244",
        "button_bg": "#cba6f7", "button_fg": "#1e1e2e",
        "scrollbar": "#45475a",
    },
    "light": {
        "bg": "#fafafa", "fg": "#383a42",
        "editor_bg": "#fafafa", "editor_fg": "#383a42",
        "gutter_bg": "#f0f0f0", "gutter_fg": "#9d9d9f",
        "sidebar_bg": "#f0f0f0", "sidebar_fg": "#383a42",
        "activity_bg": "#e5e5e6", "activity_fg": "#696c77",
        "activity_active": "#a626a4",
        "tab_bg": "#f0f0f0", "tab_fg": "#696c77",
        "tab_active_bg": "#fafafa", "tab_active_fg": "#383a42",
        "panel_bg": "#f0f0f0", "panel_fg": "#383a42",
        "status_bg": "#e5e5e6", "status_fg": "#383a42",
        "selection": "#d7d7d8", "current_line": "#f2f2f2",
        "cursor": "#526fff", "find_hl": "#e5c07b",
        "bracket_match": "#50a14f",
        "modified_dot": "#c18401", "error": "#e45649",
        "warning": "#c18401", "info": "#4078f2", "success": "#50a14f",
        "comment": "#a0a1a7", "keyword": "#a626a4",
        "string": "#50a14f", "number": "#c18401",
        "function": "#4078f2", "class_name": "#c18401",
        "operator": "#0184bc", "decorator": "#a626a4",
        "builtin": "#e45649",
        "minimap_bg": "#e5e5e6", "tree_bg": "#f0f0f0",
        "input_bg": "#ffffff", "input_fg": "#383a42",
        "border": "#d7d7d8",
        "button_bg": "#4078f2", "button_fg": "#ffffff",
        "scrollbar": "#c8c8c9",
    },
}

# ---------------------------------------------------------------------------
# Language keyword / builtin sets
# ---------------------------------------------------------------------------
_PY_KW: Set[str] = {
    "False", "None", "True", "and", "as", "assert", "async", "await",
    "break", "class", "continue", "def", "del", "elif", "else", "except",
    "finally", "for", "from", "global", "if", "import", "in", "is",
    "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try",
    "while", "with", "yield",
}

_PY_BI: Set[str] = {
    "abs", "all", "any", "bin", "bool", "bytes", "callable", "chr",
    "dict", "dir", "enumerate", "eval", "filter", "float", "format",
    "frozenset", "getattr", "globals", "hasattr", "hash", "hex", "id",
    "input", "int", "isinstance", "issubclass", "iter", "len", "list",
    "locals", "map", "max", "min", "next", "object", "open", "ord",
    "pow", "print", "property", "range", "repr", "reversed", "round",
    "set", "setattr", "slice", "sorted", "staticmethod", "str", "sum",
    "super", "tuple", "type", "vars", "zip",
}

_JS_KW: Set[str] = {
    "abstract", "arguments", "async", "await", "boolean", "break", "byte",
    "case", "catch", "class", "const", "continue", "debugger", "default",
    "delete", "do", "else", "enum", "export", "extends", "false", "final",
    "finally", "for", "function", "goto", "if", "implements", "import",
    "in", "instanceof", "interface", "let", "new", "null", "of", "package",
    "private", "protected", "public", "return", "static", "super", "switch",
    "this", "throw", "true", "try", "typeof", "undefined", "var", "void",
    "while", "with", "yield",
}

_C_KW: Set[str] = {
    "auto", "break", "case", "char", "const", "continue", "default", "do",
    "double", "else", "enum", "extern", "float", "for", "goto", "if",
    "inline", "int", "long", "register", "return", "short", "signed",
    "sizeof", "static", "struct", "switch", "typedef", "union", "unsigned",
    "void", "volatile", "while",
}

_LANG_KW: Dict[str, Set[str]] = {
    "Python": _PY_KW, "JavaScript": _JS_KW, "TypeScript": _JS_KW,
    "C": _C_KW, "C++": _C_KW, "Java": _JS_KW, "Go": _C_KW,
    "Rust": _C_KW, "Dart": _JS_KW, "PHP": _JS_KW,
}

# ---------------------------------------------------------------------------
# Helper data classes
# ---------------------------------------------------------------------------


class _FileTab:
    """Metadata for an open editor tab."""

    __slots__ = (
        "path", "title", "content", "modified", "language", "encoding",
        "eol", "indent_size", "use_tabs", "cursor_line", "cursor_col",
        "scroll_y", "undo_stack", "redo_stack", "breakpoints",
    )

    def __init__(
        self,
        path: Optional[str] = None,
        title: str = "Untitled",
        content: str = "",
        language: str = "Plain Text",
    ) -> None:
        self.path: Optional[str] = path
        self.title: str = title
        self.content: str = content
        self.modified: bool = False
        self.language: str = language
        self.encoding: str = "utf-8"
        self.eol: str = "\n"
        self.indent_size: int = 4
        self.use_tabs: bool = False
        self.cursor_line: int = 1
        self.cursor_col: int = 0
        self.scroll_y: float = 0.0
        self.undo_stack: List[str] = []
        self.redo_stack: List[str] = []
        self.breakpoints: Set[int] = set()


class _Diagnostic:
    """Single diagnostic entry."""

    __slots__ = ("file", "line", "col", "severity", "message", "source")

    def __init__(
        self,
        file: str,
        line: int,
        col: int,
        severity: str,
        message: str,
        source: str = "",
    ) -> None:
        self.file: str = file
        self.line: int = line
        self.col: int = col
        self.severity: str = severity
        self.message: str = message
        self.source: str = source


class IDEEditor(tk.Frame):
    """Full-featured IDE/code editor panel comparable to VS Code."""

    def __init__(self, master: tk.Widget, bg: str = "#1e1e2e",
                 fg: str = "#cdd6f4", workspace: Optional[str] = None,
                 theme: str = "dark", **kw: Any) -> None:
        self._theme_name = theme
        self._theme = THEMES.get(theme, THEMES["dark"])
        super().__init__(master, bg=self._theme["bg"], **kw)
        self._bg = self._theme["bg"]
        self._fg = self._theme["fg"]
        self._workspace = workspace or os.getcwd()
        self._tabs: List[_FileTab] = []
        self._active_tab: int = -1
        self._sidebar_visible = True
        self._panel_visible = True
        self._active_activity = "explorer"
        self._diagnostics: List[_Diagnostic] = []
        self._find_bar_visible = False
        self._auto_save_interval = 60_000
        self._auto_save_id: Optional[str] = None
        self._command_palette_open = False
        self._recent_files: List[str] = []
        self._git_branch = "main"
        self._git_files: Dict[str, str] = {}
        self._terminal_history: List[str] = []
        self._terminal_hist_idx = -1
        self._code_font = tkfont.Font(family="Consolas", size=11)
        self._ui_font = tkfont.Font(family="Segoe UI", size=9)
        self._ui_font_bold = tkfont.Font(family="Segoe UI", size=9, weight="bold")
        self._small_font = tkfont.Font(family="Segoe UI", size=8)
        self._icon_font = tkfont.Font(family="Segoe UI", size=14)
        self._syntax_hl: Any = None
        if SyntaxHighlighter is not None:
            try:
                self._syntax_hl = SyntaxHighlighter()
            except Exception:
                pass
        self._lang_server: Any = None
        if LanguageServer is not None:
            try:
                self._lang_server = LanguageServer()
            except Exception:
                pass
        self._git_int: Any = None
        if GitIntegration is not None:
            try:
                self._git_int = GitIntegration(self._workspace)
            except Exception:
                pass
        self._ext_mgr: Any = None
        if ExtensionManager is not None:
            try:
                self._ext_mgr = ExtensionManager()
            except Exception:
                pass
        self._debugger_inst: Any = None
        if Debugger is not None:
            try:
                self._debugger_inst = Debugger()
            except Exception:
                pass
        self._build_ui()
        self._bind_shortcuts()
        self._show_welcome_tab()
        self._start_auto_save()
        self._refresh_git_status()

    # === Layout ==========================================================

    def _build_ui(self) -> None:
        t = self._theme
        self._status_bar = tk.Frame(self, bg=t["status_bg"], height=24)
        self._status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self._status_bar.pack_propagate(False)
        self._build_status_bar()
        self._main_frame = tk.Frame(self, bg=t["bg"])
        self._main_frame.pack(fill=tk.BOTH, expand=True)
        self._activity_bar = tk.Frame(self._main_frame, bg=t["activity_bg"], width=36)
        self._activity_bar.pack(side=tk.LEFT, fill=tk.Y)
        self._activity_bar.pack_propagate(False)
        self._build_activity_bar()
        self._sidebar_frame = tk.Frame(self._main_frame, bg=t["sidebar_bg"], width=250)
        self._sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        self._sidebar_frame.pack_propagate(False)
        self._build_sidebar()
        self._right_pane = tk.PanedWindow(self._main_frame, orient=tk.VERTICAL,
                                          bg=t["bg"], sashwidth=4, sashrelief=tk.FLAT, bd=0)
        self._right_pane.pack(fill=tk.BOTH, expand=True)
        self._editor_area = tk.Frame(self._right_pane, bg=t["bg"])
        self._right_pane.add(self._editor_area, stretch="always")
        self._build_editor_area()
        self._panel_frame = tk.Frame(self._right_pane, bg=t["panel_bg"], height=200)
        self._right_pane.add(self._panel_frame, stretch="never")
        self._build_panel()
        self._palette_toplevel: Optional[tk.Toplevel] = None
        self._find_frame_widget: Optional[tk.Frame] = None

    # === Activity bar ====================================================

    def _build_activity_bar(self) -> None:
        t = self._theme
        self._activity_buttons: Dict[str, tk.Label] = {}
        for act_id, icon in ACTIVITY_ICONS:
            lbl = tk.Label(self._activity_bar, text=icon, bg=t["activity_bg"],
                           fg=t["activity_fg"], font=self._icon_font, width=2, cursor="hand2")
            lbl.pack(pady=2, padx=2)
            lbl.bind("<Button-1>", lambda e, a=act_id: self._on_activity_click(a))
            self._activity_buttons[act_id] = lbl
        self._highlight_activity("explorer")

    def _highlight_activity(self, act_id: str) -> None:
        t = self._theme
        for aid, lbl in self._activity_buttons.items():
            lbl.config(fg=t["activity_active"] if aid == act_id else t["activity_fg"])

    def _on_activity_click(self, act_id: str) -> None:
        if self._active_activity == act_id and self._sidebar_visible:
            self.toggle_sidebar()
            return
        self._active_activity = act_id
        self._highlight_activity(act_id)
        if not self._sidebar_visible:
            self.toggle_sidebar()
        self._refresh_sidebar()

    # === Sidebar ==========================================================

    def _build_sidebar(self) -> None:
        t = self._theme
        self._sidebar_title = tk.Label(self._sidebar_frame, text="EXPLORER", anchor=tk.W,
                                       bg=t["sidebar_bg"], fg=t["sidebar_fg"],
                                       font=self._ui_font_bold, padx=12, pady=6)
        self._sidebar_title.pack(fill=tk.X)
        self._sidebar_content = tk.Frame(self._sidebar_frame, bg=t["sidebar_bg"])
        self._sidebar_content.pack(fill=tk.BOTH, expand=True)
        self._build_explorer_panel()

    def _clear_sidebar(self) -> None:
        for w in self._sidebar_content.winfo_children():
            w.destroy()

    def _refresh_sidebar(self) -> None:
        self._clear_sidebar()
        titles = {"explorer": "EXPLORER", "search": "SEARCH", "git": "SOURCE CONTROL",
                  "extensions": "EXTENSIONS", "debug": "DEBUG", "run": "RUN AND DEBUG"}
        self._sidebar_title.config(text=titles.get(self._active_activity, "EXPLORER"))
        builders: Dict[str, Callable[[], None]] = {
            "explorer": self._build_explorer_panel, "search": self._build_search_panel,
            "git": self._build_git_panel, "extensions": self._build_extensions_panel,
            "debug": self._build_debug_panel, "run": self._build_run_panel}
        builders.get(self._active_activity, self._build_explorer_panel)()

    # -- Explorer --

    def _build_explorer_panel(self) -> None:
        t = self._theme
        s = ttk.Style()
        s.configure("IDE.Treeview", background=t["tree_bg"], foreground=t["sidebar_fg"],
                    fieldbackground=t["tree_bg"], rowheight=22, font=("Segoe UI", 9))
        s.map("IDE.Treeview", background=[("selected", t["selection"])],
              foreground=[("selected", t["fg"])])
        fr = tk.Frame(self._sidebar_content, bg=t["tree_bg"])
        fr.pack(fill=tk.BOTH, expand=True)
        self._file_tree = ttk.Treeview(fr, style="IDE.Treeview", show="tree", selectmode="browse")
        sb = ttk.Scrollbar(fr, orient=tk.VERTICAL, command=self._file_tree.yview)
        self._file_tree.configure(yscrollcommand=sb.set)
        self._file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._file_tree.bind("<Double-1>", self._on_tree_dbl)
        self._file_tree.bind("<Button-3>", self._on_tree_ctx)
        self._populate_tree()

    def _populate_tree(self, root_path: Optional[str] = None) -> None:
        if not hasattr(self, "_file_tree"):
            return
        self._file_tree.delete(*self._file_tree.get_children())
        root = root_path or self._workspace
        if not os.path.isdir(root):
            return
        name = os.path.basename(root) or root
        node = self._file_tree.insert("", tk.END, text=f"[D] {name}", open=True, values=(root,))
        self._insert_tree(node, root, 0)

    def _insert_tree(self, parent: str, directory: str, depth: int) -> None:
        if depth > 8:
            return
        skip = {".git", "__pycache__", "node_modules", ".venv", "venv", "dist", "build"}
        try:
            entries = sorted(os.listdir(directory),
                             key=lambda x: (not os.path.isdir(os.path.join(directory, x)), x.lower()))
        except PermissionError:
            return
        for entry in entries:
            if entry.startswith(".") and entry != ".gitignore":
                continue
            full = os.path.join(directory, entry)
            if os.path.isdir(full):
                if entry in skip:
                    continue
                n = self._file_tree.insert(parent, tk.END, text=f"[D] {entry}", open=False, values=(full,))
                self._insert_tree(n, full, depth + 1)
            else:
                ext = os.path.splitext(entry)[1].lower()
                icon = FILE_ICONS.get(ext, "F")
                gs = self._git_files.get(full, "")
                suf = f" [{gs}]" if gs else ""
                self._file_tree.insert(parent, tk.END, text=f"[{icon}] {entry}{suf}", values=(full,))

    def _on_tree_dbl(self, event: tk.Event) -> None:
        sel = self._file_tree.selection()
        if sel:
            vals = self._file_tree.item(sel[0], "values")
            if vals and os.path.isfile(vals[0]):
                self.open_file(vals[0])

    def _on_tree_ctx(self, event: tk.Event) -> None:
        item = self._file_tree.identify_row(event.y)
        if not item:
            return
        self._file_tree.selection_set(item)
        vals = self._file_tree.item(item, "values")
        path = vals[0] if vals else ""
        m = tk.Menu(self, tearoff=0, bg=self._theme["input_bg"], fg=self._theme["fg"], font=self._ui_font)
        m.add_command(label="New File", command=lambda: self._tree_new_file(path))
        m.add_command(label="New Folder", command=lambda: self._tree_new_folder(path))
        m.add_separator()
        m.add_command(label="Rename", command=lambda: self._tree_rename(path))
        m.add_command(label="Delete", command=lambda: self._tree_delete(path))
        m.add_separator()
        m.add_command(label="Copy Path", command=lambda: self._clip(path))
        m.add_command(label="Copy Relative Path",
                      command=lambda: self._clip(os.path.relpath(path, self._workspace)))
        m.post(event.x_root, event.y_root)

    def _tree_new_file(self, p: str) -> None:
        d = p if os.path.isdir(p) else os.path.dirname(p)
        n = simpledialog.askstring("New File", "File name:", parent=self)
        if n:
            fp = os.path.join(d, n)
            try:
                Path(fp).touch()
                self._populate_tree()
                self.open_file(fp)
            except OSError as e:
                messagebox.showerror("Error", str(e), parent=self)

    def _tree_new_folder(self, p: str) -> None:
        d = p if os.path.isdir(p) else os.path.dirname(p)
        n = simpledialog.askstring("New Folder", "Folder name:", parent=self)
        if n:
            try:
                os.makedirs(os.path.join(d, n), exist_ok=True)
                self._populate_tree()
            except OSError as e:
                messagebox.showerror("Error", str(e), parent=self)

    def _tree_rename(self, p: str) -> None:
        old = os.path.basename(p)
        new = simpledialog.askstring("Rename", "New name:", parent=self, initialvalue=old)
        if new and new != old:
            np = os.path.join(os.path.dirname(p), new)
            try:
                os.rename(p, np)
                self._populate_tree()
                for tab in self._tabs:
                    if tab.path == p:
                        tab.path = np
                        tab.title = new
                self._refresh_tabs()
            except OSError as e:
                messagebox.showerror("Error", str(e), parent=self)

    def _tree_delete(self, p: str) -> None:
        if not messagebox.askyesno("Delete", f"Delete '{os.path.basename(p)}'?", parent=self):
            return
        try:
            if os.path.isdir(p):
                import shutil
                shutil.rmtree(p)
            else:
                os.remove(p)
            self._populate_tree()
        except OSError as e:
            messagebox.showerror("Error", str(e), parent=self)

    def _clip(self, text: str) -> None:
        self.clipboard_clear()
        self.clipboard_append(text)

    # -- Search panel --

    def _build_search_panel(self) -> None:
        t = self._theme
        f = tk.Frame(self._sidebar_content, bg=t["sidebar_bg"])
        f.pack(fill=tk.X, padx=8, pady=4)
        self._srch_var = tk.StringVar()
        self._repl_var = tk.StringVar()
        self._srch_case = tk.BooleanVar(value=False)
        self._srch_regex = tk.BooleanVar(value=False)
        tk.Entry(f, textvariable=self._srch_var, bg=t["input_bg"], fg=t["input_fg"],
                 insertbackground=t["cursor"], font=self._ui_font, relief=tk.FLAT, bd=4).pack(fill=tk.X, pady=2)
        tk.Entry(f, textvariable=self._repl_var, bg=t["input_bg"], fg=t["input_fg"],
                 insertbackground=t["cursor"], font=self._ui_font, relief=tk.FLAT, bd=4).pack(fill=tk.X, pady=2)
        opts = tk.Frame(f, bg=t["sidebar_bg"])
        opts.pack(fill=tk.X, pady=2)
        tk.Checkbutton(opts, text="Aa", variable=self._srch_case, bg=t["sidebar_bg"],
                       fg=t["sidebar_fg"], selectcolor=t["input_bg"], font=self._small_font).pack(side=tk.LEFT)
        tk.Checkbutton(opts, text=".*", variable=self._srch_regex, bg=t["sidebar_bg"],
                       fg=t["sidebar_fg"], selectcolor=t["input_bg"], font=self._small_font).pack(side=tk.LEFT)
        bf = tk.Frame(f, bg=t["sidebar_bg"])
        bf.pack(fill=tk.X, pady=2)
        tk.Button(bf, text="Search", command=self._do_search_files, bg=t["button_bg"],
                  fg=t["button_fg"], relief=tk.FLAT, font=self._small_font, padx=8).pack(side=tk.LEFT, padx=2)
        tk.Button(bf, text="Replace All", command=self._do_replace_files, bg=t["button_bg"],
                  fg=t["button_fg"], relief=tk.FLAT, font=self._small_font, padx=8).pack(side=tk.LEFT, padx=2)
        self._search_results = tk.Listbox(self._sidebar_content, bg=t["tree_bg"], fg=t["sidebar_fg"],
                                          font=self._small_font, selectbackground=t["selection"],
                                          bd=0, highlightthickness=0)
        self._search_results.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self._search_results.bind("<Double-1>", self._on_search_result_click)
        self._search_match_data: List[Tuple[str, int]] = []

    def _do_search_files(self) -> None:
        query = self._srch_var.get()
        if not query:
            return
        self._search_results.delete(0, tk.END)
        self._search_match_data = []
        flags = 0 if self._srch_case.get() else re.IGNORECASE
        try:
            pat = re.compile(query, flags) if self._srch_regex.get() else re.compile(re.escape(query), flags)
        except re.error:
            return
        skip = {".git", "__pycache__", "node_modules", ".venv"}
        for dp, dns, fns in os.walk(self._workspace):
            dns[:] = [d for d in dns if d not in skip and not d.startswith(".")]
            for fn in fns:
                fp = os.path.join(dp, fn)
                try:
                    with open(fp, "r", encoding="utf-8", errors="replace") as fh:
                        for i, line in enumerate(fh, 1):
                            if pat.search(line):
                                rel = os.path.relpath(fp, self._workspace)
                                self._search_results.insert(tk.END, f"  {rel}:{i}  {line.strip()[:60]}")
                                self._search_match_data.append((fp, i))
                except (OSError, UnicodeDecodeError):
                    pass

    def _do_replace_files(self) -> None:
        query = self._srch_var.get()
        repl = self._repl_var.get()
        if not query:
            return
        flags = 0 if self._srch_case.get() else re.IGNORECASE
        try:
            pat = re.compile(query, flags) if self._srch_regex.get() else re.compile(re.escape(query), flags)
        except re.error:
            return
        count = 0
        for dp, dns, fns in os.walk(self._workspace):
            dns[:] = [d for d in dns if d not in {".git", "__pycache__", "node_modules"}]
            for fn in fns:
                fp = os.path.join(dp, fn)
                try:
                    with open(fp, "r", encoding="utf-8") as fh:
                        content = fh.read()
                    new_content, n = pat.subn(repl, content)
                    if n > 0:
                        with open(fp, "w", encoding="utf-8") as fh:
                            fh.write(new_content)
                        count += n
                except (OSError, UnicodeDecodeError):
                    pass
        messagebox.showinfo("Replace", f"Replaced {count} occurrences.", parent=self)

    def _on_search_result_click(self, event: tk.Event) -> None:
        sel = self._search_results.curselection()
        if sel and hasattr(self, "_search_match_data") and sel[0] < len(self._search_match_data):
            fp, line = self._search_match_data[sel[0]]
            self.open_file(fp)
            self._goto_line(line)

    # -- Git panel --

    def _build_git_panel(self) -> None:
        t = self._theme
        p = self._sidebar_content
        bf = tk.Frame(p, bg=t["sidebar_bg"])
        bf.pack(fill=tk.X, padx=8, pady=4)
        tk.Label(bf, text="Branch:", bg=t["sidebar_bg"], fg=t["sidebar_fg"],
                 font=self._small_font).pack(side=tk.LEFT)
        self._branch_var = tk.StringVar(value=self._git_branch)
        tk.Entry(bf, textvariable=self._branch_var, bg=t["input_bg"], fg=t["input_fg"],
                 font=self._small_font, relief=tk.FLAT, bd=2, width=15).pack(side=tk.LEFT, padx=4)
        mf = tk.Frame(p, bg=t["sidebar_bg"])
        mf.pack(fill=tk.X, padx=8, pady=2)
        self._commit_msg = tk.Text(mf, bg=t["input_bg"], fg=t["input_fg"], font=self._ui_font,
                                   height=3, relief=tk.FLAT, bd=4, insertbackground=t["cursor"])
        self._commit_msg.pack(fill=tk.X)
        btf = tk.Frame(p, bg=t["sidebar_bg"])
        btf.pack(fill=tk.X, padx=8, pady=2)
        for txt, cmd in [("Commit", self._git_commit), ("Push", self._git_push),
                         ("Pull", self._git_pull)]:
            tk.Button(btf, text=txt, command=cmd, bg=t["button_bg"], fg=t["button_fg"],
                      relief=tk.FLAT, font=self._small_font, padx=8).pack(side=tk.LEFT, padx=2)
        tk.Label(p, text="Changes", bg=t["sidebar_bg"], fg=t["sidebar_fg"],
                 font=self._ui_font_bold, anchor=tk.W, padx=8).pack(fill=tk.X, pady=(8, 2))
        self._git_list = tk.Listbox(p, bg=t["tree_bg"], fg=t["sidebar_fg"], font=self._small_font,
                                    selectbackground=t["selection"], bd=0, highlightthickness=0)
        self._git_list.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        for path, status in self._git_files.items():
            self._git_list.insert(tk.END, f"  [{status}] {os.path.basename(path)}")

    def _git_commit(self) -> None:
        msg = self._commit_msg.get("1.0", tk.END).strip()
        if not msg:
            messagebox.showwarning("Git", "Enter a commit message.", parent=self)
            return
        try:
            subprocess.run(["git", "add", "."], cwd=self._workspace, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", msg], cwd=self._workspace, check=True, capture_output=True)
            self._commit_msg.delete("1.0", tk.END)
            self._refresh_git_status()
            self._append_output(f"Committed: {msg}\n")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            messagebox.showerror("Git", str(e), parent=self)

    def _git_push(self) -> None:
        try:
            subprocess.run(["git", "push"], cwd=self._workspace, check=True, capture_output=True)
            self._append_output("Pushed successfully.\n")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            messagebox.showerror("Git", str(e), parent=self)

    def _git_pull(self) -> None:
        try:
            subprocess.run(["git", "pull"], cwd=self._workspace, check=True, capture_output=True)
            self._refresh_git_status()
            self._append_output("Pulled successfully.\n")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            messagebox.showerror("Git", str(e), parent=self)

    def _refresh_git_status(self) -> None:
        self._git_files.clear()
        try:
            r = subprocess.run(["git", "status", "--porcelain"], cwd=self._workspace,
                               capture_output=True, text=True)
            if r.returncode == 0:
                for line in r.stdout.strip().splitlines():
                    if len(line) > 3:
                        st = line[:2].strip()
                        fp = os.path.join(self._workspace, line[3:].strip())
                        sm = {"M": "M", "A": "A", "D": "D", "??": "?", "R": "R", "U": "U"}
                        self._git_files[fp] = sm.get(st, st)
            r2 = subprocess.run(["git", "branch", "--show-current"], cwd=self._workspace,
                                capture_output=True, text=True)
            if r2.returncode == 0 and r2.stdout.strip():
                self._git_branch = r2.stdout.strip()
        except FileNotFoundError:
            pass

    # -- Extensions panel --

    def _build_extensions_panel(self) -> None:
        t = self._theme
        p = self._sidebar_content
        tk.Entry(p, bg=t["input_bg"], fg=t["input_fg"], font=self._ui_font,
                 relief=tk.FLAT, bd=4).pack(fill=tk.X, padx=8, pady=4)
        tk.Label(p, text="Installed", bg=t["sidebar_bg"], fg=t["sidebar_fg"],
                 font=self._ui_font_bold, anchor=tk.W, padx=8).pack(fill=tk.X, pady=(8, 2))
        exts = [("Python", "v2024.1", True), ("GitLens", "v14.0", True),
                ("Prettier", "v10.0", True), ("ESLint", "v3.0", False),
                ("Docker", "v1.28", True)]
        for name, ver, enabled in exts:
            f = tk.Frame(p, bg=t["tree_bg"])
            f.pack(fill=tk.X, padx=8, pady=1)
            tk.Label(f, text=f"  {name} {ver}", bg=t["tree_bg"], fg=t["sidebar_fg"],
                     font=self._small_font, anchor=tk.W).pack(side=tk.LEFT, fill=tk.X, expand=True)
            var = tk.BooleanVar(value=enabled)
            tk.Checkbutton(f, variable=var, bg=t["tree_bg"],
                           selectcolor=t["input_bg"]).pack(side=tk.RIGHT)

    # -- Debug panel --

    def _build_debug_panel(self) -> None:
        t = self._theme
        p = self._sidebar_content
        sections = [("Breakpoints", []), ("Variables", []),
                    ("Call Stack", []), ("Watch", [])]
        for title, _ in sections:
            tk.Label(p, text=title, bg=t["sidebar_bg"], fg=t["sidebar_fg"],
                     font=self._ui_font_bold, anchor=tk.W, padx=8).pack(fill=tk.X, pady=(6, 2))
            lb = tk.Listbox(p, bg=t["tree_bg"], fg=t["sidebar_fg"], font=self._small_font,
                            height=4, bd=0, highlightthickness=0, selectbackground=t["selection"])
            lb.pack(fill=tk.X, padx=8, pady=2)

    # -- Run panel --

    def _build_run_panel(self) -> None:
        t = self._theme
        p = self._sidebar_content
        tk.Label(p, text="Run Configuration", bg=t["sidebar_bg"], fg=t["sidebar_fg"],
                 font=self._ui_font_bold, anchor=tk.W, padx=8).pack(fill=tk.X, pady=(8, 4))
        self._run_config = tk.StringVar(value="Python: Current File")
        for cfg in ["Python: Current File", "Python: Module", "Node.js", "Custom Command"]:
            tk.Radiobutton(p, text=cfg, variable=self._run_config, value=cfg,
                           bg=t["sidebar_bg"], fg=t["sidebar_fg"], selectcolor=t["input_bg"],
                           font=self._small_font, anchor=tk.W).pack(fill=tk.X, padx=12)
        bf = tk.Frame(p, bg=t["sidebar_bg"])
        bf.pack(fill=tk.X, padx=8, pady=8)
        tk.Button(bf, text="Run", command=self._run_current, bg=t["success"], fg=t["bg"],
                  relief=tk.FLAT, font=self._ui_font_bold, padx=16).pack(side=tk.LEFT, padx=2)
        tk.Button(bf, text="Debug", command=self._debug_current, bg=t["warning"], fg=t["bg"],
                  relief=tk.FLAT, font=self._ui_font_bold, padx=16).pack(side=tk.LEFT, padx=2)

    # === Editor area =======================================================

    def _build_editor_area(self) -> None:
        t = self._theme
        self._tab_bar = tk.Frame(self._editor_area, bg=t["tab_bg"], height=30)
        self._tab_bar.pack(fill=tk.X)
        self._tab_bar.pack_propagate(False)
        self._tab_widgets: List[tk.Frame] = []
        self._editor_container = tk.Frame(self._editor_area, bg=t["editor_bg"])
        self._editor_container.pack(fill=tk.BOTH, expand=True)
        self._gutter = tk.Text(self._editor_container, width=5, bg=t["gutter_bg"],
                               fg=t["gutter_fg"], font=self._code_font, state=tk.DISABLED,
                               bd=0, padx=4, pady=4, relief=tk.FLAT, cursor="arrow",
                               selectbackground=t["gutter_bg"], selectforeground=t["gutter_fg"],
                               wrap=tk.NONE)
        self._gutter.pack(side=tk.LEFT, fill=tk.Y)
        ef = tk.Frame(self._editor_container, bg=t["editor_bg"])
        ef.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._editor = tk.Text(ef, bg=t["editor_bg"], fg=t["editor_fg"], font=self._code_font,
                               insertbackground=t["cursor"], selectbackground=t["selection"],
                               bd=0, padx=8, pady=4, relief=tk.FLAT, wrap=tk.NONE,
                               undo=True, maxundo=-1,
                               tabs=(self._code_font.measure("    "),))
        vs = ttk.Scrollbar(ef, orient=tk.VERTICAL, command=self._on_editor_yscroll)
        hs = ttk.Scrollbar(ef, orient=tk.HORIZONTAL, command=self._editor.xview)
        self._editor.configure(yscrollcommand=self._on_editor_yscroll_set,
                               xscrollcommand=hs.set)
        vs.pack(side=tk.RIGHT, fill=tk.Y)
        hs.pack(side=tk.BOTTOM, fill=tk.X)
        self._editor.pack(fill=tk.BOTH, expand=True)
        self._minimap = tk.Canvas(self._editor_container, width=60, bg=t["minimap_bg"],
                                  bd=0, highlightthickness=0)
        self._minimap.pack(side=tk.RIGHT, fill=tk.Y)
        self._setup_editor_tags()
        self._editor.bind("<KeyRelease>", self._on_key_release)
        self._editor.bind("<Return>", self._on_return)
        self._editor.bind("<Tab>", self._on_tab)
        self._editor.bind("<ButtonRelease-1>", self._on_cursor_move)
        self._editor.bind("<<Modified>>", self._on_modified)

    def _setup_editor_tags(self) -> None:
        t = self._theme
        for tag, key in [("current_line", "current_line"), ("bracket_match", "bracket_match"),
                         ("find_highlight", "find_hl"), ("keyword", "keyword"),
                         ("builtin", "builtin"), ("string", "string"), ("comment", "comment"),
                         ("number", "number"), ("function", "function"),
                         ("class_name", "class_name"), ("decorator", "decorator"),
                         ("operator", "operator")]:
            if tag == "current_line":
                self._editor.tag_configure(tag, background=t[key])
            else:
                self._editor.tag_configure(tag, foreground=t[key])

    def _on_editor_yscroll(self, *args: Any) -> None:
        self._editor.yview(*args)
        self._gutter.yview(*args)

    def _on_editor_yscroll_set(self, first: str, last: str) -> None:
        self._gutter.yview("moveto", first)
        self._update_minimap()

    # === Tab management ===================================================

    def _refresh_tabs(self) -> None:
        for w in self._tab_widgets:
            w.destroy()
        self._tab_widgets.clear()
        t = self._theme
        for i, tab in enumerate(self._tabs):
            active = i == self._active_tab
            bg = t["tab_active_bg"] if active else t["tab_bg"]
            fg = t["tab_active_fg"] if active else t["tab_fg"]
            frame = tk.Frame(self._tab_bar, bg=bg, padx=8, pady=2)
            frame.pack(side=tk.LEFT, padx=(0, 1))
            dot = " \u25cf" if tab.modified else ""
            lbl = tk.Label(frame, text=f"{tab.title}{dot}", bg=bg, fg=fg,
                           font=self._small_font, cursor="hand2")
            lbl.pack(side=tk.LEFT)
            lbl.bind("<Button-1>", lambda e, idx=i: self._switch_tab(idx))
            cl = tk.Label(frame, text="\u00d7", bg=bg, fg=fg, font=self._small_font, cursor="hand2")
            cl.pack(side=tk.LEFT, padx=(4, 0))
            cl.bind("<Button-1>", lambda e, idx=i: self.close_tab(idx))
            self._tab_widgets.append(frame)

    def _switch_tab(self, idx: int) -> None:
        if idx < 0 or idx >= len(self._tabs):
            return
        if 0 <= self._active_tab < len(self._tabs):
            old = self._tabs[self._active_tab]
            old.content = self._editor.get("1.0", tk.END)
            pos = self._editor.index(tk.INSERT)
            parts = pos.split(".")
            old.cursor_line, old.cursor_col = int(parts[0]), int(parts[1]) + 1
        self._active_tab = idx
        tab = self._tabs[idx]
        self._editor.config(state=tk.NORMAL)
        self._editor.delete("1.0", tk.END)
        self._editor.insert("1.0", tab.content.rstrip("\n"))
        self._editor.mark_set(tk.INSERT, f"{tab.cursor_line}.{tab.cursor_col - 1}")
        self._editor.see(tk.INSERT)
        self._editor.edit_reset()
        self._editor.edit_modified(False)
        self._refresh_tabs()
        self._update_line_numbers()
        self._highlight_current_line()
        self._apply_syntax_highlighting()
        self._update_status_bar()

    def _add_tab(self, tab: _FileTab) -> int:
        self._tabs.append(tab)
        idx = len(self._tabs) - 1
        self._switch_tab(idx)
        return idx

    # === File operations ==================================================

    def open_file(self, path: str) -> None:
        for i, tab in enumerate(self._tabs):
            if tab.path and os.path.normpath(tab.path) == os.path.normpath(path):
                self._switch_tab(i)
                return
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except OSError as e:
            messagebox.showerror("Error", str(e), parent=self)
            return
        ext = os.path.splitext(path)[1].lower()
        lang = LANGUAGE_MAP.get(ext, "Plain Text")
        eol = "CRLF" if "\r\n" in content else "LF"
        tab = _FileTab(path=path, title=os.path.basename(path), content=content, language=lang)
        tab.eol = eol
        if self._tabs and self._tabs[0].title == "Welcome" and not self._tabs[0].path:
            self._tabs.pop(0)
            self._active_tab = -1
            self._refresh_tabs()
        self._add_tab(tab)
        if path not in self._recent_files:
            self._recent_files.insert(0, path)
            self._recent_files = self._recent_files[:20]

    def save(self) -> None:
        if self._active_tab < 0:
            return
        tab = self._tabs[self._active_tab]
        tab.content = self._editor.get("1.0", tk.END).rstrip("\n") + "\n"
        if tab.path:
            try:
                eol = "\r\n" if tab.eol == "CRLF" else "\n"
                with open(tab.path, "w", encoding=tab.encoding.lower(), newline="") as f:
                    f.write(tab.content.replace("\n", eol))
                tab.modified = False
                self._refresh_tabs()
                self._update_status_bar()
            except OSError as e:
                messagebox.showerror("Error", str(e), parent=self)
        else:
            self.save_as()

    def save_as(self) -> None:
        if self._active_tab < 0:
            return
        path = filedialog.asksaveasfilename(parent=self)
        if path:
            tab = self._tabs[self._active_tab]
            tab.path = path
            tab.title = os.path.basename(path)
            tab.language = LANGUAGE_MAP.get(os.path.splitext(path)[1].lower(), "Plain Text")
            self.save()

    def new_file(self) -> None:
        self._add_tab(_FileTab())

    def open_file_dialog(self) -> None:
        path = filedialog.askopenfilename(parent=self)
        if path:
            self.open_file(path)

    def close_tab(self, idx: Optional[int] = None) -> None:
        if idx is None:
            idx = self._active_tab
        if idx < 0 or idx >= len(self._tabs):
            return
        tab = self._tabs[idx]
        if tab.modified:
            r = messagebox.askyesnocancel("Save", f"Save '{tab.title}'?", parent=self)
            if r is None:
                return
            if r:
                self._active_tab = idx
                self.save()
        self._tabs.pop(idx)
        if not self._tabs:
            self._active_tab = -1
            self._editor.delete("1.0", tk.END)
            self._show_welcome_tab()
        elif idx <= self._active_tab:
            self._active_tab = max(0, self._active_tab - 1)
            self._switch_tab(self._active_tab)
        self._refresh_tabs()

    def next_tab(self) -> None:
        if len(self._tabs) > 1:
            self._switch_tab((self._active_tab + 1) % len(self._tabs))

    def prev_tab(self) -> None:
        if len(self._tabs) > 1:
            self._switch_tab((self._active_tab - 1) % len(self._tabs))

    # === Editor features ===================================================

    def _on_key_release(self, event: tk.Event) -> None:
        self._update_line_numbers()
        self._highlight_current_line()
        self._apply_syntax_highlighting()
        self._match_brackets()
        self._update_status_bar()
        self._update_minimap()

    def _on_cursor_move(self, event: tk.Event) -> None:
        self._highlight_current_line()
        self._match_brackets()
        self._update_status_bar()

    def _on_modified(self, event: tk.Event) -> None:
        if self._editor.edit_modified() and 0 <= self._active_tab < len(self._tabs):
            self._tabs[self._active_tab].modified = True
            self._refresh_tabs()
            self._editor.edit_modified(False)

    def _on_return(self, event: tk.Event) -> str:
        line = self._editor.get("insert linestart", "insert")
        indent = ""
        for ch in line:
            if ch in (" ", "\t"):
                indent += ch
            else:
                break
        if line.rstrip().endswith(":") or line.rstrip().endswith("{"):
            indent += "    "
        self._editor.insert("insert", "\n" + indent)
        self._update_line_numbers()
        self._highlight_current_line()
        return "break"

    def _on_tab(self, event: tk.Event) -> str:
        if 0 <= self._active_tab < len(self._tabs):
            tab = self._tabs[self._active_tab]
            self._editor.insert("insert", "\t" if tab.use_tabs else " " * tab.indent_size)
        else:
            self._editor.insert("insert", "    ")
        return "break"

    def _update_line_numbers(self) -> None:
        self._gutter.config(state=tk.NORMAL)
        self._gutter.delete("1.0", tk.END)
        content = self._editor.get("1.0", tk.END)
        line_count = content.count("\n")
        nums = "\n".join(str(i) for i in range(1, line_count + 1))
        self._gutter.insert("1.0", nums)
        self._gutter.config(state=tk.DISABLED)

    def _highlight_current_line(self) -> None:
        self._editor.tag_remove("current_line", "1.0", tk.END)
        ln = self._editor.index(tk.INSERT).split(".")[0]
        self._editor.tag_add("current_line", f"{ln}.0", f"{ln}.end+1c")
        self._editor.tag_lower("current_line")

    def _match_brackets(self) -> None:
        self._editor.tag_remove("bracket_match", "1.0", tk.END)
        pos = self._editor.index(tk.INSERT)
        try:
            char = self._editor.get(pos)
        except tk.TclError:
            return
        pairs = {"(": ")", "[": "]", "{": "}"}
        close_pairs = {v: k for k, v in pairs.items()}
        if char in pairs:
            target = pairs[char]
            depth = 0
            idx = pos
            while True:
                idx = self._editor.search(
                    f"[{re.escape(char)}{re.escape(target)}]",
                    f"{idx}+1c", tk.END, regexp=True)
                if not idx:
                    break
                c = self._editor.get(idx)
                if c == char:
                    depth += 1
                elif c == target:
                    if depth == 0:
                        self._editor.tag_add("bracket_match", pos)
                        self._editor.tag_add("bracket_match", idx)
                        break
                    depth -= 1
        elif char in close_pairs:
            opener = close_pairs[char]
            depth = 0
            idx = pos
            while True:
                idx = self._editor.search(
                    f"[{re.escape(opener)}{re.escape(char)}]",
                    idx, "1.0", backwards=True, regexp=True)
                if not idx:
                    break
                c = self._editor.get(idx)
                if c == char:
                    depth += 1
                elif c == opener:
                    if depth == 0:
                        self._editor.tag_add("bracket_match", pos)
                        self._editor.tag_add("bracket_match", idx)
                        break
                    depth -= 1

    def _apply_syntax_highlighting(self) -> None:
        if self._active_tab < 0:
            return
        lang = self._tabs[self._active_tab].language
        if self._syntax_hl is not None:
            try:
                self._syntax_hl.highlight(self._editor, lang)
                return
            except Exception:
                pass
        for tag in ("keyword", "builtin", "string", "comment", "number",
                    "function", "class_name", "decorator", "operator"):
            self._editor.tag_remove(tag, "1.0", tk.END)
        content = self._editor.get("1.0", tk.END)
        keywords = _LANG_KW.get(lang, set())
        builtins = _PY_BI if lang == "Python" else set()
        comment_pfx = COMMENT_PREFIXES.get(lang, "")
        for i, line in enumerate(content.splitlines(), 1):
            if comment_pfx and comment_pfx not in ("<!--", "/*"):
                cp = line.find(comment_pfx)
                if cp >= 0:
                    self._editor.tag_add("comment", f"{i}.{cp}", f"{i}.end")
            j = 0
            while j < len(line):
                ch = line[j]
                if ch in ('"', "'"):
                    start = j
                    q = ch
                    j += 1
                    while j < len(line) and line[j] != q:
                        if line[j] == "\\" and j + 1 < len(line):
                            j += 1
                        j += 1
                    j += 1
                    self._editor.tag_add("string", f"{i}.{start}", f"{i}.{j}")
                    continue
                j += 1
            for m in re.finditer(r"\b([a-zA-Z_]\w*)\b", line):
                word = m.group(1)
                s, e = m.start(1), m.end(1)
                if word in keywords:
                    self._editor.tag_add("keyword", f"{i}.{s}", f"{i}.{e}")
                elif word in builtins:
                    self._editor.tag_add("builtin", f"{i}.{s}", f"{i}.{e}")
            for m in re.finditer(r"\b\d+\.?\d*\b", line):
                self._editor.tag_add("number", f"{i}.{m.start()}", f"{i}.{m.end()}")
            for m in re.finditer(r"\bdef\s+(\w+)", line):
                self._editor.tag_add("function", f"{i}.{m.start(1)}", f"{i}.{m.end(1)}")
            for m in re.finditer(r"\bclass\s+(\w+)", line):
                self._editor.tag_add("class_name", f"{i}.{m.start(1)}", f"{i}.{m.end(1)}")
            if lang == "Python":
                for m in re.finditer(r"@\w+", line):
                    self._editor.tag_add("decorator", f"{i}.{m.start()}", f"{i}.{m.end()}")

    def _update_minimap(self) -> None:
        self._minimap.delete("all")
        content = self._editor.get("1.0", tk.END)
        lines = content.splitlines()
        h = self._minimap.winfo_height() or 400
        if not lines:
            return
        scale = min(h / max(len(lines), 1), 2.0)
        for i, line in enumerate(lines):
            y = int(i * scale)
            length = min(len(line.rstrip()), 60)
            if length > 0:
                self._minimap.create_line(2, y, 2 + length, y,
                                          fill=self._theme["gutter_fg"], width=1)

    def duplicate_line(self) -> None:
        ln = self._editor.index(tk.INSERT).split(".")[0]
        content = self._editor.get(f"{ln}.0", f"{ln}.end")
        self._editor.insert(f"{ln}.end", "\n" + content)
        self._update_line_numbers()

    def delete_line(self) -> None:
        ln = self._editor.index(tk.INSERT).split(".")[0]
        self._editor.delete(f"{ln}.0", f"{ln}.end+1c")
        self._update_line_numbers()

    def toggle_comment(self) -> None:
        if self._active_tab < 0:
            return
        lang = self._tabs[self._active_tab].language
        prefix = COMMENT_PREFIXES.get(lang, "#")
        if prefix in ("<!--", "/*"):
            return
        ln = self._editor.index(tk.INSERT).split(".")[0]
        content = self._editor.get(f"{ln}.0", f"{ln}.end")
        stripped = content.lstrip()
        if stripped.startswith(prefix):
            idx = content.index(prefix)
            end = idx + len(prefix)
            if end < len(content) and content[end] == " ":
                end += 1
            self._editor.delete(f"{ln}.{idx}", f"{ln}.{end}")
        else:
            indent = len(content) - len(stripped)
            self._editor.insert(f"{ln}.{indent}", prefix + " ")

    # === Bottom panel ======================================================

    def _build_panel(self) -> None:
        t = self._theme
        self._panel_notebook = ttk.Notebook(self._panel_frame)
        s = ttk.Style()
        s.configure("Panel.TNotebook", background=t["panel_bg"])
        s.configure("Panel.TNotebook.Tab", background=t["tab_bg"],
                    foreground=t["tab_fg"], padding=[8, 2])
        s.map("Panel.TNotebook.Tab", background=[("selected", t["tab_active_bg"])],
              foreground=[("selected", t["tab_active_fg"])])
        self._panel_notebook.configure(style="Panel.TNotebook")
        self._terminal_frame = tk.Frame(self._panel_notebook, bg=t["panel_bg"])
        self._panel_notebook.add(self._terminal_frame, text="Terminal")
        self._build_terminal()
        self._problems_frame = tk.Frame(self._panel_notebook, bg=t["panel_bg"])
        self._panel_notebook.add(self._problems_frame, text="Problems")
        self._problems_list = tk.Listbox(self._problems_frame, bg=t["panel_bg"],
                                         fg=t["panel_fg"], font=self._small_font,
                                         selectbackground=t["selection"], bd=0)
        self._problems_list.pack(fill=tk.BOTH, expand=True)
        self._output_frame = tk.Frame(self._panel_notebook, bg=t["panel_bg"])
        self._panel_notebook.add(self._output_frame, text="Output")
        self._output_text = tk.Text(self._output_frame, bg=t["panel_bg"], fg=t["panel_fg"],
                                    font=self._code_font, state=tk.DISABLED, bd=0,
                                    relief=tk.FLAT, wrap=tk.WORD)
        self._output_text.pack(fill=tk.BOTH, expand=True)
        self._debug_frame = tk.Frame(self._panel_notebook, bg=t["panel_bg"])
        self._panel_notebook.add(self._debug_frame, text="Debug Console")
        self._debug_text = tk.Text(self._debug_frame, bg=t["panel_bg"], fg=t["panel_fg"],
                                   font=self._code_font, bd=0, relief=tk.FLAT)
        self._debug_text.pack(fill=tk.BOTH, expand=True)
        self._panel_notebook.pack(fill=tk.BOTH, expand=True)

    def _build_terminal(self) -> None:
        t = self._theme
        self._term_output = tk.Text(self._terminal_frame, bg="#11111b", fg="#a6e3a1",
                                    font=self._code_font, state=tk.DISABLED, bd=0,
                                    relief=tk.FLAT, wrap=tk.WORD)
        self._term_output.pack(fill=tk.BOTH, expand=True)
        inp_frame = tk.Frame(self._terminal_frame, bg=t["panel_bg"])
        inp_frame.pack(fill=tk.X)
        tk.Label(inp_frame, text="$", bg=t["panel_bg"], fg="#a6e3a1",
                 font=self._code_font).pack(side=tk.LEFT, padx=(4, 2))
        self._term_input = tk.Entry(inp_frame, bg="#11111b", fg="#a6e3a1",
                                    font=self._code_font, relief=tk.FLAT, bd=4,
                                    insertbackground="#a6e3a1")
        self._term_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._term_input.bind("<Return>", self._on_terminal_enter)
        self._term_input.bind("<Up>", self._on_terminal_history_up)
        self._term_input.bind("<Down>", self._on_terminal_history_down)

    def _on_terminal_enter(self, event: tk.Event) -> None:
        cmd = self._term_input.get().strip()
        if not cmd:
            return
        self._terminal_history.append(cmd)
        self._terminal_hist_idx = len(self._terminal_history)
        self._term_input.delete(0, tk.END)
        self._term_append(f"$ {cmd}\n")

        def run() -> None:
            try:
                result = subprocess.run(cmd, shell=True, cwd=self._workspace,
                                        capture_output=True, text=True, timeout=30)
                output = result.stdout + result.stderr
            except subprocess.TimeoutExpired:
                output = "[timeout]\n"
            except Exception as e:
                output = f"[error: {e}]\n"
            self.after(0, lambda: self._term_append(output))
        threading.Thread(target=run, daemon=True).start()

    def _on_terminal_history_up(self, event: tk.Event) -> None:
        if self._terminal_history and self._terminal_hist_idx > 0:
            self._terminal_hist_idx -= 1
            self._term_input.delete(0, tk.END)
            self._term_input.insert(0, self._terminal_history[self._terminal_hist_idx])

    def _on_terminal_history_down(self, event: tk.Event) -> None:
        if self._terminal_hist_idx < len(self._terminal_history) - 1:
            self._terminal_hist_idx += 1
            self._term_input.delete(0, tk.END)
            self._term_input.insert(0, self._terminal_history[self._terminal_hist_idx])
        else:
            self._terminal_hist_idx = len(self._terminal_history)
            self._term_input.delete(0, tk.END)

    def _term_append(self, text: str) -> None:
        self._term_output.config(state=tk.NORMAL)
        self._term_output.insert(tk.END, text)
        self._term_output.see(tk.END)
        self._term_output.config(state=tk.DISABLED)

    def _append_output(self, text: str) -> None:
        self._output_text.config(state=tk.NORMAL)
        self._output_text.insert(tk.END, text)
        self._output_text.see(tk.END)
        self._output_text.config(state=tk.DISABLED)

    # === Status bar ========================================================

    def _build_status_bar(self) -> None:
        t = self._theme
        self._status_left = tk.Label(self._status_bar, bg=t["status_bg"], fg=t["status_fg"],
                                     font=self._small_font, anchor=tk.W, padx=8)
        self._status_left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._status_right = tk.Label(self._status_bar, bg=t["status_bg"], fg=t["status_fg"],
                                      font=self._small_font, anchor=tk.E, padx=8)
        self._status_right.pack(side=tk.RIGHT)
        self._update_status_bar()

    def _update_status_bar(self) -> None:
        errs = sum(1 for d in self._diagnostics if d.severity == "error")
        warns = sum(1 for d in self._diagnostics if d.severity == "warning")
        modified = "*" if (0 <= self._active_tab < len(self._tabs)
                           and self._tabs[self._active_tab].modified) else ""
        self._status_left.config(text=f"  {self._git_branch}  {modified}  "
                                 f"Errors: {errs}  Warnings: {warns}")
        if 0 <= self._active_tab < len(self._tabs):
            tab = self._tabs[self._active_tab]
            try:
                pos = self._editor.index(tk.INSERT)
                ln, col = pos.split(".")
                tab.cursor_line = int(ln)
                tab.cursor_col = int(col) + 1
            except (tk.TclError, ValueError):
                pass
            indent = f"Tab Size: {tab.indent_size}"
            self._status_right.config(
                text=f"Ln {tab.cursor_line}, Col {tab.cursor_col}   "
                     f"{tab.encoding}   {tab.language}   {indent}   {tab.eol}")
        else:
            self._status_right.config(text="")

    # === Keyboard shortcuts ================================================

    def _bind_shortcuts(self) -> None:
        for seq, action in SHORTCUTS.items():
            handler = getattr(self, action, None) or getattr(self, f"_{action}", None)
            if handler:
                self.winfo_toplevel().bind(seq, lambda e, h=handler: (h(), "break"))

    # === Command palette ===================================================

    def command_palette(self) -> None:
        if self._command_palette_open:
            return
        self._command_palette_open = True
        top = tk.Toplevel(self)
        top.title("Command Palette")
        top.geometry("500x300")
        top.transient(self)
        top.grab_set()
        t = self._theme
        top.config(bg=t["bg"])
        top.protocol("WM_DELETE_WINDOW", lambda: self._close_palette(top))
        sv = tk.StringVar()
        ent = tk.Entry(top, textvariable=sv, bg=t["input_bg"], fg=t["input_fg"],
                       insertbackground=t["cursor"], font=self._ui_font, relief=tk.FLAT, bd=8)
        ent.pack(fill=tk.X, padx=4, pady=4)
        ent.focus_set()
        lb = tk.Listbox(top, bg=t["tree_bg"], fg=t["fg"], font=self._ui_font,
                        selectbackground=t["selection"], bd=0, highlightthickness=0)
        lb.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        commands = [
            ("Save", self.save), ("Save As...", self.save_as),
            ("New File", self.new_file), ("Open File...", self.open_file_dialog),
            ("Close Tab", lambda: self.close_tab()),
            ("Toggle Sidebar", self.toggle_sidebar),
            ("Toggle Panel", self.toggle_panel),
            ("Find", self.find), ("Find and Replace", self.find_replace),
            ("Go to Line...", self.go_to_line),
            ("Duplicate Line", self.duplicate_line),
            ("Delete Line", self.delete_line),
            ("Toggle Comment", self.toggle_comment),
            ("Switch Theme", self.switch_theme),
            ("Run", self._run_current), ("New Terminal", self.new_terminal),
        ]
        for name, _ in commands:
            lb.insert(tk.END, f"  > {name}")

        def on_filter(*_: Any) -> None:
            q = sv.get().lower()
            lb.delete(0, tk.END)
            for name, _ in commands:
                if q in name.lower():
                    lb.insert(tk.END, f"  > {name}")

        def on_select(event: tk.Event) -> None:
            sel = lb.curselection()
            if sel:
                text = lb.get(sel[0]).strip().lstrip("> ").strip()
                for name, cmd in commands:
                    if name == text:
                        self._close_palette(top)
                        cmd()
                        return

        sv.trace_add("write", on_filter)
        lb.bind("<Double-1>", on_select)
        ent.bind("<Return>", lambda e: on_select(e))
        ent.bind("<Escape>", lambda e: self._close_palette(top))

    def _close_palette(self, top: tk.Toplevel) -> None:
        self._command_palette_open = False
        top.destroy()

    # === Find / Replace ====================================================

    def find(self) -> None:
        self._show_find_bar(replace=False)

    def find_replace(self) -> None:
        self._show_find_bar(replace=True)

    def _show_find_bar(self, replace: bool = False) -> None:
        if hasattr(self, "_find_frame_widget") and self._find_frame_widget is not None:
            self._find_frame_widget.destroy()
        t = self._theme
        f = tk.Frame(self._editor_area, bg=t["input_bg"])
        f.pack(fill=tk.X, side=tk.TOP, before=self._editor_container)
        self._find_frame_widget = f
        self._find_var = tk.StringVar()
        self._replace_var = tk.StringVar()
        tk.Label(f, text="Find:", bg=t["input_bg"], fg=t["input_fg"],
                 font=self._small_font).pack(side=tk.LEFT, padx=4)
        fe = tk.Entry(f, textvariable=self._find_var, bg=t["bg"], fg=t["fg"],
                      insertbackground=t["cursor"], font=self._ui_font, width=25, relief=tk.FLAT, bd=2)
        fe.pack(side=tk.LEFT, padx=2)
        fe.focus_set()
        fe.bind("<Return>", lambda e: self._find_next())
        tk.Button(f, text="Next", command=self._find_next, bg=t["button_bg"],
                  fg=t["button_fg"], relief=tk.FLAT, font=self._small_font).pack(side=tk.LEFT, padx=2)
        tk.Button(f, text="Prev", command=self._find_prev, bg=t["button_bg"],
                  fg=t["button_fg"], relief=tk.FLAT, font=self._small_font).pack(side=tk.LEFT, padx=2)
        if replace:
            tk.Label(f, text="Replace:", bg=t["input_bg"], fg=t["input_fg"],
                     font=self._small_font).pack(side=tk.LEFT, padx=(8, 4))
            tk.Entry(f, textvariable=self._replace_var, bg=t["bg"], fg=t["fg"],
                     insertbackground=t["cursor"], font=self._ui_font, width=25,
                     relief=tk.FLAT, bd=2).pack(side=tk.LEFT, padx=2)
            tk.Button(f, text="Replace", command=self._replace_one, bg=t["button_bg"],
                      fg=t["button_fg"], relief=tk.FLAT, font=self._small_font).pack(side=tk.LEFT, padx=2)
            tk.Button(f, text="All", command=self._replace_all, bg=t["button_bg"],
                      fg=t["button_fg"], relief=tk.FLAT, font=self._small_font).pack(side=tk.LEFT, padx=2)
        tk.Button(f, text="\u00d7", command=self._hide_find_bar, bg=t["input_bg"],
                  fg=t["input_fg"], relief=tk.FLAT, font=self._small_font).pack(side=tk.RIGHT, padx=4)

    def _hide_find_bar(self) -> None:
        if self._find_frame_widget is not None:
            self._find_frame_widget.destroy()
            self._find_frame_widget = None
        self._editor.tag_remove("find_highlight", "1.0", tk.END)

    def _find_next(self) -> None:
        query = self._find_var.get()
        if not query:
            return
        self._editor.tag_remove("find_highlight", "1.0", tk.END)
        start = self._editor.index(tk.INSERT + "+1c")
        pos = self._editor.search(query, start, nocase=True, stopindex=tk.END)
        if not pos:
            pos = self._editor.search(query, "1.0", nocase=True, stopindex=start)
        if pos:
            end = f"{pos}+{len(query)}c"
            self._editor.tag_add("find_highlight", pos, end)
            self._editor.mark_set(tk.INSERT, pos)
            self._editor.see(pos)

    def _find_prev(self) -> None:
        query = self._find_var.get()
        if not query:
            return
        self._editor.tag_remove("find_highlight", "1.0", tk.END)
        start = self._editor.index(tk.INSERT)
        pos = self._editor.search(query, start, nocase=True, backwards=True, stopindex="1.0")
        if not pos:
            pos = self._editor.search(query, tk.END, nocase=True, backwards=True, stopindex=start)
        if pos:
            end = f"{pos}+{len(query)}c"
            self._editor.tag_add("find_highlight", pos, end)
            self._editor.mark_set(tk.INSERT, pos)
            self._editor.see(pos)

    def _replace_one(self) -> None:
        query = self._find_var.get()
        repl = self._replace_var.get()
        if not query:
            return
        pos = self._editor.search(query, tk.INSERT, nocase=True)
        if pos:
            end = f"{pos}+{len(query)}c"
            self._editor.delete(pos, end)
            self._editor.insert(pos, repl)
            self._find_next()

    def _replace_all(self) -> None:
        query = self._find_var.get()
        repl = self._replace_var.get()
        if not query:
            return
        content = self._editor.get("1.0", tk.END)
        new_content = content.replace(query, repl)
        self._editor.delete("1.0", tk.END)
        self._editor.insert("1.0", new_content.rstrip("\n"))
        self._update_line_numbers()

    # === Go to line ========================================================

    def go_to_line(self) -> None:
        line = simpledialog.askinteger("Go to Line", "Line number:", parent=self, minvalue=1)
        if line:
            self._goto_line(line)

    def _goto_line(self, line: int) -> None:
        self._editor.mark_set(tk.INSERT, f"{line}.0")
        self._editor.see(f"{line}.0")
        self._highlight_current_line()
        self._update_status_bar()

    # === Welcome tab =======================================================

    def _show_welcome_tab(self) -> None:
        lines = [
            "Welcome to EoStudio IDE",
            "========================",
            "",
            "Quick Actions:",
            "  Ctrl+N       New File",
            "  Ctrl+O       Open File",
            "  Ctrl+Shift+P Command Palette",
            "  Ctrl+B       Toggle Sidebar",
            "  Ctrl+J       Toggle Panel",
            "",
            "Recent Files:",
        ]
        for fp in self._recent_files[:10]:
            lines.append(f"  {fp}")
        if not self._recent_files:
            lines.append("  (none)")
        lines.extend(["", "Open a file from the Explorer to get started."])
        tab = _FileTab(title="Welcome", content="\n".join(lines), language="Plain Text")
        self._add_tab(tab)

    # === Auto-save =========================================================

    def _start_auto_save(self) -> None:
        def auto_save() -> None:
            for tab in self._tabs:
                if tab.modified and tab.path:
                    try:
                        eol = "\r\n" if tab.eol == "CRLF" else "\n"
                        with open(tab.path, "w", encoding=tab.encoding.lower(), newline="") as f:
                            f.write(tab.content.replace("\n", eol))
                        tab.modified = False
                    except OSError:
                        pass
            self._refresh_tabs()
            self._auto_save_id = self.after(self._auto_save_interval, auto_save)
        self._auto_save_id = self.after(self._auto_save_interval, auto_save)

    # === Theme switching ===================================================

    def switch_theme(self) -> None:
        new_theme = "light" if self._theme_name == "dark" else "dark"
        self._theme_name = new_theme
        self._theme = THEMES[new_theme]
        self._bg = self._theme["bg"]
        self._fg = self._theme["fg"]
        self.config(bg=self._bg)
        for widget in self.winfo_children():
            widget.destroy()
        self._build_ui()
        self._bind_shortcuts()
        if self._tabs:
            self._switch_tab(self._active_tab)
        else:
            self._show_welcome_tab()

    # === Toggle methods ====================================================

    def toggle_sidebar(self) -> None:
        if self._sidebar_visible:
            self._sidebar_frame.pack_forget()
            self._sidebar_visible = False
        else:
            self._sidebar_frame.pack(side=tk.LEFT, fill=tk.Y,
                                     before=self._right_pane)
            self._sidebar_visible = True

    def toggle_panel(self) -> None:
        if self._panel_visible:
            self._right_pane.forget(self._panel_frame)
            self._panel_visible = False
        else:
            self._right_pane.add(self._panel_frame, stretch="never")
            self._panel_visible = True

    def toggle_breakpoint(self) -> None:
        if self._active_tab < 0:
            return
        tab = self._tabs[self._active_tab]
        line = int(self._editor.index(tk.INSERT).split(".")[0])
        if line in tab.breakpoints:
            tab.breakpoints.discard(line)
        else:
            tab.breakpoints.add(line)

    # === Run / Debug =======================================================

    def _run_current(self) -> None:
        if self._active_tab < 0:
            return
        tab = self._tabs[self._active_tab]
        if not tab.path:
            messagebox.showinfo("Run", "Save the file first.", parent=self)
            return
        self.save()
        lang = tab.language
        if lang == "Python":
            cmd = f"python \"{tab.path}\""
        elif lang in ("JavaScript", "TypeScript"):
            cmd = f"node \"{tab.path}\""
        else:
            self._append_output(f"No run configuration for {lang}\n")
            return
        self._append_output(f"$ {cmd}\n")

        def run() -> None:
            try:
                r = subprocess.run(cmd, shell=True, cwd=self._workspace,
                                   capture_output=True, text=True, timeout=60)
                out = r.stdout + r.stderr
            except subprocess.TimeoutExpired:
                out = "[timeout]\n"
            except Exception as e:
                out = f"[error: {e}]\n"
            self.after(0, lambda: self._append_output(out))
        threading.Thread(target=run, daemon=True).start()

    def _debug_current(self) -> None:
        if self._debugger_inst:
            try:
                self._debugger_inst.start(self._tabs[self._active_tab].path)
            except Exception as e:
                self._append_output(f"Debug error: {e}\n")
        else:
            self._append_output("Debugger not available.\n")

    def new_terminal(self) -> None:
        self._panel_notebook.select(self._terminal_frame)
        self._term_input.focus_set()

    # === Workspace =========================================================

    def set_workspace(self, path: str) -> None:
        self._workspace = path
        if hasattr(self, "_file_tree"):
            self._populate_tree()
        self._refresh_git_status()
