"""GTK application code generator for EoStudio UI components.

Supported targets: gtk-python (GTK4 + PyGObject), gtk-c (GTK4 + C).
"""

from __future__ import annotations

import re
from typing import Any, Dict, List


class GTKAppGenerator:
    """Generates GTK4 application source files from EoStudio screens."""

    SUPPORTED_TARGETS = ("gtk-python", "gtk-c")

    def __init__(self, target: str = "gtk-python") -> None:
        if target not in self.SUPPORTED_TARGETS:
            raise ValueError(f"Unknown target {target!r}")
        self._target = target

    def generate(self, screens: List[Dict[str, Any]],
                 app_name: str = "EoStudioApp") -> Dict[str, str]:
        if not screens:
            screens = [{"name": "Home", "components": []}]
        if self._target == "gtk-python":
            return self._gen_python(screens, app_name)
        return self._gen_c(screens, app_name)

    # -- GTK Python ---------------------------------------------------

    def _gen_python(self, screens: List[Dict[str, Any]],
                    app_name: str) -> Dict[str, str]:
        files: Dict[str, str] = {}
        page_methods: List[str] = []
        stack_adds: List[str] = []
        sidebar_rows: List[str] = []

        for s in screens:
            name = self._snake(s.get("name", "Home"))
            label = s.get("name", "Home")
            body = self._py_widgets(s.get("components", []), "box", 2)
            page_methods.append(
                f"    def _build_{name}(self):\n"
                f"        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)\n"
                f"        box.set_margin_top(16)\n"
                f"        box.set_margin_start(16)\n"
                f"        box.set_margin_end(16)\n"
                f"        lbl = Gtk.Label(label='{label}')\n"
                f"        lbl.add_css_class('title-1')\n"
                f"        box.append(lbl)\n"
                f"{body}"
                f"        scroll = Gtk.ScrolledWindow()\n"
                f"        scroll.set_child(box)\n"
                f"        return scroll\n")
            stack_adds.append(
                f"        self.stack.add_titled(self._build_{name}(), '{name}', '{label}')")
            sidebar_rows.append(f"'{label}'")

        files["main.py"] = (
            "import gi\n"
            "gi.require_version('Gtk', '4.0')\n"
            "gi.require_version('Adw', '1')\n"
            "from gi.repository import Gtk, Adw, Gio\n\n\n"
            f"class {self._pascal(app_name)}(Adw.Application):\n"
            "    def __init__(self):\n"
            f"        super().__init__(application_id='com.eostudio.{self._snake(app_name)}')\n\n"
            "    def do_activate(self):\n"
            "        win = MainWindow(application=self)\n"
            "        win.present()\n\n\n"
            "class MainWindow(Adw.ApplicationWindow):\n"
            "    def __init__(self, **kwargs):\n"
            "        super().__init__(**kwargs)\n"
            f"        self.set_title('{app_name}')\n"
            "        self.set_default_size(1200, 800)\n\n"
            "        self.stack = Adw.ViewStack()\n"
            + "\n".join(stack_adds) + "\n\n"
            "        switcher = Adw.ViewSwitcherBar()\n"
            "        switcher.set_stack(self.stack)\n\n"
            "        header = Adw.HeaderBar()\n"
            "        title_switcher = Adw.ViewSwitcherTitle()\n"
            "        title_switcher.set_stack(self.stack)\n"
            "        header.set_title_widget(title_switcher)\n\n"
            "        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)\n"
            "        main_box.append(header)\n"
            "        main_box.append(self.stack)\n"
            "        main_box.append(switcher)\n"
            "        self.set_content(main_box)\n\n"
            + "\n\n".join(page_methods) + "\n\n"
            "if __name__ == '__main__':\n"
            f"    app = {self._pascal(app_name)}()\n"
            "    app.run(None)\n")
        return files

    def _py_widgets(self, components: List[Dict[str, Any]],
                    parent: str, indent: int) -> str:
        lines: List[str] = []
        pad = "    " * indent
        idx = 0
        for c in components:
            ct = c.get("type", "Container")
            lb = c.get("label", c.get("text", ""))
            ch = c.get("children", [])
            if ct == "Button":
                lines.append(f"{pad}btn_{idx} = Gtk.Button(label='{lb}')\n")
                lines.append(f"{pad}{parent}.append(btn_{idx})\n")
            elif ct == "Text":
                lines.append(f"{pad}{parent}.append(Gtk.Label(label='{lb}'))\n")
            elif ct == "Input":
                lines.append(f"{pad}entry_{idx} = Gtk.Entry()\n")
                lines.append(f"{pad}entry_{idx}.set_placeholder_text('{lb}')\n")
                lines.append(f"{pad}{parent}.append(entry_{idx})\n")
            elif ct == "Card":
                bname = f"card_{idx}"
                lines.append(f"{pad}{bname} = Gtk.Frame(label='{lb}')\n")
                lines.append(f"{pad}{bname}_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)\n")
                if ch:
                    lines.append(self._py_widgets(ch, f"{bname}_box", indent))
                else:
                    lines.append(f"{pad}{bname}_box.append(Gtk.Label(label='{lb}'))\n")
                lines.append(f"{pad}{bname}.set_child({bname}_box)\n")
                lines.append(f"{pad}{parent}.append({bname})\n")
            elif ct == "Container" and ch:
                d = c.get("direction", "column")
                orient = "HORIZONTAL" if d == "row" else "VERTICAL"
                bname = f"cont_{idx}"
                lines.append(f"{pad}{bname} = Gtk.Box(orientation=Gtk.Orientation.{orient}, spacing=8)\n")
                lines.append(self._py_widgets(ch, bname, indent))
                lines.append(f"{pad}{parent}.append({bname})\n")
            elif ct == "Image":
                lines.append(f"{pad}{parent}.append(Gtk.Picture())\n")
            else:
                lines.append(f"{pad}{parent}.append(Gtk.Label(label='{lb}'))\n")
            idx += 1
        return "".join(lines)

    # -- GTK C --------------------------------------------------------

    def _gen_c(self, screens: List[Dict[str, Any]],
               app_name: str) -> Dict[str, str]:
        files: Dict[str, str] = {}
        snake = self._snake(app_name)
        page_fns: List[str] = []
        stack_adds: List[str] = []

        for s in screens:
            name = self._snake(s.get("name", "Home"))
            label = s.get("name", "Home")
            body = self._c_widgets(s.get("components", []), "box", 1)
            page_fns.append(
                f"static GtkWidget *build_{name}_page(void) {{\n"
                f"    GtkWidget *box = gtk_box_new(GTK_ORIENTATION_VERTICAL, 12);\n"
                f"    gtk_widget_set_margin_start(box, 16);\n"
                f"    gtk_widget_set_margin_end(box, 16);\n"
                f"    gtk_widget_set_margin_top(box, 16);\n"
                f"    GtkWidget *title = gtk_label_new(\"{label}\");\n"
                f"    gtk_widget_add_css_class(title, \"title-1\");\n"
                f"    gtk_box_append(GTK_BOX(box), title);\n"
                f"{body}"
                f"    GtkWidget *scroll = gtk_scrolled_window_new();\n"
                f"    gtk_scrolled_window_set_child(GTK_SCROLLED_WINDOW(scroll), box);\n"
                f"    return scroll;\n}}\n")
            stack_adds.append(
                f'    adw_view_stack_add_titled(ADW_VIEW_STACK(stack), '
                f'build_{name}_page(), "{name}", "{label}");')

        files["main.c"] = (
            "#include <adwaita.h>\n\n"
            + "\n".join(page_fns) + "\n"
            "static void activate(GtkApplication *app, gpointer data) {\n"
            f"    GtkWidget *win = adw_application_window_new(app);\n"
            f"    gtk_window_set_title(GTK_WINDOW(win), \"{app_name}\");\n"
            "    gtk_window_set_default_size(GTK_WINDOW(win), 1200, 800);\n\n"
            "    GtkWidget *stack = adw_view_stack_new();\n"
            + "\n".join(stack_adds) + "\n\n"
            "    GtkWidget *header = adw_header_bar_new();\n"
            "    GtkWidget *switcher = adw_view_switcher_title_new();\n"
            "    adw_view_switcher_title_set_stack(ADW_VIEW_SWITCHER_TITLE(switcher), ADW_VIEW_STACK(stack));\n"
            "    adw_header_bar_set_title_widget(ADW_HEADER_BAR(header), switcher);\n\n"
            "    GtkWidget *vbox = gtk_box_new(GTK_ORIENTATION_VERTICAL, 0);\n"
            "    gtk_box_append(GTK_BOX(vbox), header);\n"
            "    gtk_box_append(GTK_BOX(vbox), stack);\n"
            "    adw_application_window_set_content(ADW_APPLICATION_WINDOW(win), vbox);\n"
            "    gtk_window_present(GTK_WINDOW(win));\n}\n\n"
            "int main(int argc, char *argv[]) {\n"
            f"    AdwApplication *app = adw_application_new(\"com.eostudio.{snake}\", G_APPLICATION_DEFAULT_FLAGS);\n"
            "    g_signal_connect(app, \"activate\", G_CALLBACK(activate), NULL);\n"
            "    int status = g_application_run(G_APPLICATION(app), argc, argv);\n"
            "    g_object_unref(app);\n"
            "    return status;\n}\n")

        files["meson.build"] = (
            f"project('{snake}', 'c', version: '1.0.0')\n"
            "gnome = import('gnome')\n"
            "deps = [\n"
            "  dependency('gtk4'),\n"
            "  dependency('libadwaita-1'),\n"
            "]\n"
            f"executable('{snake}', 'main.c', dependencies: deps)\n")
        return files

    def _c_widgets(self, components: List[Dict[str, Any]],
                   parent: str, indent: int) -> str:
        lines: List[str] = []
        pad = "    " * indent
        idx = 0
        for c in components:
            ct = c.get("type", "Container")
            lb = c.get("label", c.get("text", ""))
            if ct == "Button":
                lines.append(f'{pad}gtk_box_append(GTK_BOX({parent}), gtk_button_new_with_label("{lb}"));\n')
            elif ct == "Text":
                lines.append(f'{pad}gtk_box_append(GTK_BOX({parent}), gtk_label_new("{lb}"));\n')
            elif ct == "Input":
                lines.append(f'{pad}{{\n{pad}    GtkWidget *e = gtk_entry_new();\n'
                             f'{pad}    gtk_entry_set_placeholder_text(GTK_ENTRY(e), "{lb}");\n'
                             f'{pad}    gtk_box_append(GTK_BOX({parent}), e);\n{pad}}}\n')
            else:
                lines.append(f'{pad}gtk_box_append(GTK_BOX({parent}), gtk_label_new("{lb}"));\n')
            idx += 1
        return "".join(lines)

    @staticmethod
    def _pascal(name: str) -> str:
        return "".join(w.capitalize() for w in re.split(r"[\s_\-]+", name) if w)

    @staticmethod
    def _snake(name: str) -> str:
        return re.sub(r"[\s\-]+", "_", name).lower()
