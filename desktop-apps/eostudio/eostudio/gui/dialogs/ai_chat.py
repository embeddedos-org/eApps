"""AI Chat panel — the Smart Chat sidebar integrated into every editor."""

from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk
from typing import Any, Callable, Dict, List, Optional

from eostudio.core.ai.smart_chat import SmartChat


class AIChatDialog(tk.Frame):
    """Smart Chat panel embedded in each editor's right sidebar."""

    def __init__(
        self,
        master: tk.Widget,
        editor_context: str = "general",
        bg: str = "#1e1e2e",
        fg: str = "#cdd6f4",
        on_insert_design: Optional[Callable[[Dict[str, Any]], None]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, bg=bg, **kwargs)
        self._bg = bg
        self._fg = fg
        self._editor_context = editor_context
        self._on_insert_design = on_insert_design
        self._messages: List[Dict[str, str]] = []

        try:
            self._chat = SmartChat(context=editor_context)
        except Exception:
            self._chat = None

        self._build_ui()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        header = tk.Frame(self, bg="#181825")
        header.pack(fill=tk.X)

        tk.Label(header, text="🤖 Smart Chat", bg="#181825", fg=self._fg,
                 font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=8, pady=4)

        self._context_label = tk.Label(header, text=f"[{self._editor_context}]",
                                       bg="#181825", fg="#6c7086",
                                       font=("Consolas", 8))
        self._context_label.pack(side=tk.LEFT, padx=4)

        tk.Button(header, text="🗑", bg="#181825", fg="#6c7086",
                  relief=tk.FLAT, font=("Segoe UI", 9), padx=4,
                  command=self._clear_conversation).pack(side=tk.RIGHT, padx=4)

        prompts_frame = tk.Frame(self, bg=self._bg)
        prompts_frame.pack(fill=tk.X, padx=4, pady=4)

        tk.Label(prompts_frame, text="Suggested:", bg=self._bg, fg="#6c7086",
                 font=("Segoe UI", 7)).pack(anchor=tk.W, padx=4)

        self._prompts_row = tk.Frame(prompts_frame, bg=self._bg)
        self._prompts_row.pack(fill=tk.X, padx=2)
        self._populate_sample_prompts()

        gallery_frame = tk.LabelFrame(self, text="Sample Designs", bg=self._bg,
                                      fg="#cba6f7", font=("Segoe UI", 8, "bold"),
                                      bd=1, relief=tk.GROOVE)
        gallery_frame.pack(fill=tk.X, padx=4, pady=2)

        self._gallery_row = tk.Frame(gallery_frame, bg=self._bg)
        self._gallery_row.pack(fill=tk.X, padx=2, pady=2)
        self._populate_gallery()

        self._chat_frame = tk.Frame(self, bg="#181825")
        self._chat_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self._chat_canvas = tk.Canvas(self._chat_frame, bg="#181825",
                                      highlightthickness=0)
        chat_scrollbar = ttk.Scrollbar(self._chat_frame, orient=tk.VERTICAL,
                                       command=self._chat_canvas.yview)
        self._chat_inner = tk.Frame(self._chat_canvas, bg="#181825")

        self._chat_inner.bind("<Configure>",
                              lambda e: self._chat_canvas.configure(
                                  scrollregion=self._chat_canvas.bbox("all")))
        self._chat_canvas.create_window((0, 0), window=self._chat_inner,
                                        anchor=tk.NW, tags="inner")
        self._chat_canvas.configure(yscrollcommand=chat_scrollbar.set)

        self._chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._chat_canvas.bind("<Configure>",
                               lambda e: self._chat_canvas.itemconfigure(
                                   "inner", width=e.width))

        self._add_system_message(
            "Hello! I'm your AI design assistant. "
            f"I'm set up for the {self._editor_context} editor. "
            "Ask me anything about your design!")

        input_frame = tk.Frame(self, bg=self._bg)
        input_frame.pack(fill=tk.X, padx=4, pady=(0, 4))

        self._input_var = tk.StringVar()
        self._input_entry = tk.Entry(input_frame, textvariable=self._input_var,
                                     bg="#313244", fg=self._fg,
                                     insertbackground=self._fg,
                                     font=("Segoe UI", 9), relief=tk.FLAT)
        self._input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4), ipady=4)
        self._input_entry.bind("<Return>", lambda e: self._send_message())

        tk.Button(input_frame, text="Send", bg="#89b4fa", fg="#1e1e2e",
                  relief=tk.FLAT, font=("Segoe UI", 9, "bold"), padx=10, pady=2,
                  command=self._send_message).pack(side=tk.RIGHT)

    # ------------------------------------------------------------------
    # Sample prompts
    # ------------------------------------------------------------------

    def _populate_sample_prompts(self) -> None:
        prompts = self._get_sample_prompts()
        for prompt_text in prompts[:4]:
            btn = tk.Button(self._prompts_row, text=prompt_text[:30] + "…" if len(prompt_text) > 30 else prompt_text,
                            bg="#313244", fg="#89b4fa", relief=tk.FLAT,
                            font=("Segoe UI", 7), padx=4, pady=1, anchor=tk.W,
                            command=lambda p=prompt_text: self._send_prompt(p))  # type: ignore[misc]
            btn.pack(fill=tk.X, pady=1)

    def _get_sample_prompts(self) -> List[str]:
        if self._chat:
            try:
                return self._chat.get_sample_prompts(self._editor_context)
            except Exception:
                pass

        prompts_map = {
            "3d_modeler": [
                "Create a low-poly tree model",
                "How do I add a bevel to edges?",
                "Generate a sci-fi building",
                "Optimize my mesh polygon count",
            ],
            "cad": [
                "Design a bracket with mounting holes",
                "How to add fillet to all edges?",
                "Create a parametric gear profile",
                "Check my sketch for constraints",
            ],
            "image": [
                "Apply a vintage photo filter",
                "How to create a gradient mask?",
                "Generate a texture pattern",
                "Remove background from image",
            ],
            "game": [
                "Create a player controller script",
                "Design a parallax background",
                "Add particle effects to my scene",
                "Generate a tilemap from noise",
            ],
            "ui": [
                "Design a login screen layout",
                "Create a responsive card grid",
                "Generate a navigation flow",
                "Add dark mode to my UI",
            ],
            "product": [
                "Design a phone case with logo cutout",
                "Check my model for 3D printability",
                "Generate a laptop stand design",
                "Create a snap-fit enclosure",
            ],
        }
        return prompts_map.get(self._editor_context, [
            "Help me with my design",
            "Generate a sample object",
            "Explain this tool",
            "Optimize my project",
        ])

    # ------------------------------------------------------------------
    # Gallery
    # ------------------------------------------------------------------

    def _populate_gallery(self) -> None:
        samples = self._get_sample_designs()
        for sample in samples[:4]:
            frame = tk.Frame(self._gallery_row, bg="#313244", width=40, height=40,
                             relief=tk.RAISED, bd=1)
            frame.pack(side=tk.LEFT, padx=2, pady=2)
            frame.pack_propagate(False)
            label = tk.Label(frame, text=sample["icon"], bg="#313244", fg=sample["color"],
                             font=("Segoe UI", 14))
            label.pack(expand=True)
            label.bind("<Button-1>",
                       lambda e, s=sample: self._insert_sample_design(s))  # type: ignore[misc]
            frame.bind("<Button-1>",
                       lambda e, s=sample: self._insert_sample_design(s))  # type: ignore[misc]

    def _get_sample_designs(self) -> List[Dict[str, Any]]:
        designs_map = {
            "3d_modeler": [
                {"name": "Cube", "icon": "□", "color": "#89b4fa", "type": "cube"},
                {"name": "Sphere", "icon": "○", "color": "#a6e3a1", "type": "sphere"},
                {"name": "Cylinder", "icon": "▯", "color": "#f9e2af", "type": "cylinder"},
                {"name": "Torus", "icon": "◎", "color": "#cba6f7", "type": "torus"},
            ],
            "cad": [
                {"name": "Bracket", "icon": "⌐", "color": "#89b4fa", "type": "bracket"},
                {"name": "Gear", "icon": "⚙", "color": "#a6e3a1", "type": "gear"},
                {"name": "Plate", "icon": "▬", "color": "#f9e2af", "type": "plate"},
                {"name": "Tube", "icon": "○", "color": "#cba6f7", "type": "tube"},
            ],
            "ui": [
                {"name": "Login", "icon": "🔐", "color": "#89b4fa", "type": "login_screen"},
                {"name": "Feed", "icon": "📋", "color": "#a6e3a1", "type": "feed_screen"},
                {"name": "Profile", "icon": "👤", "color": "#f9e2af", "type": "profile_screen"},
                {"name": "Settings", "icon": "⚙", "color": "#cba6f7", "type": "settings_screen"},
            ],
        }
        return designs_map.get(self._editor_context, [
            {"name": "Sample A", "icon": "★", "color": "#89b4fa", "type": "sample_a"},
            {"name": "Sample B", "icon": "◆", "color": "#a6e3a1", "type": "sample_b"},
            {"name": "Sample C", "icon": "●", "color": "#f9e2af", "type": "sample_c"},
            {"name": "Sample D", "icon": "▲", "color": "#cba6f7", "type": "sample_d"},
        ])

    def _insert_sample_design(self, sample: Dict[str, Any]) -> None:
        self._add_system_message(f"Inserting sample design: {sample['name']}")
        if self._on_insert_design:
            self._on_insert_design(sample)

    # ------------------------------------------------------------------
    # Chat messaging
    # ------------------------------------------------------------------

    def _send_prompt(self, prompt: str) -> None:
        self._input_var.set(prompt)
        self._send_message()

    def _send_message(self) -> None:
        text = self._input_var.get().strip()
        if not text:
            return

        self._input_var.set("")
        self._add_user_message(text)
        self._messages.append({"role": "user", "content": text})

        response = self._get_ai_response(text)
        self._add_assistant_message(response)
        self._messages.append({"role": "assistant", "content": response})

    def _get_ai_response(self, user_text: str) -> str:
        if self._chat:
            try:
                return self._chat.chat(user_text, context=self._editor_context)
            except Exception:
                pass

        responses = {
            "help": "I can assist with design tasks, generate objects, explain tools, and optimize your work. Just describe what you need!",
            "create": f"I'll create that for you in the {self._editor_context} editor. Processing your request...",
            "how": "Here's how to do that: Select the appropriate tool from the toolbar, then click on the canvas to place or draw. Use the properties panel to fine-tune.",
            "optimize": "To optimize: 1) Reduce polygon count for 3D, 2) Merge duplicate vertices, 3) Use instancing for repeated objects, 4) Simplify materials where possible.",
        }
        lower = user_text.lower()
        for key, resp in responses.items():
            if key in lower:
                return resp
        return (
            f"I understand you're asking about: '{user_text}'. "
            f"In the {self._editor_context} context, I'd suggest using the appropriate "
            "tools from the toolbar. Would you like me to elaborate on any specific aspect?"
        )

    # ------------------------------------------------------------------
    # Message rendering
    # ------------------------------------------------------------------

    def _add_user_message(self, text: str) -> None:
        self._add_bubble(text, side="right", bg="#313244", fg=self._fg, label="You")

    def _add_assistant_message(self, text: str) -> None:
        self._add_bubble(text, side="left", bg="#1e3a5f", fg=self._fg, label="AI")

    def _add_system_message(self, text: str) -> None:
        self._add_bubble(text, side="left", bg="#2a2a3e", fg="#6c7086", label="System")

    def _add_bubble(self, text: str, side: str, bg: str, fg: str, label: str) -> None:
        anchor = tk.E if side == "right" else tk.W

        row = tk.Frame(self._chat_inner, bg="#181825")
        row.pack(fill=tk.X, padx=4, pady=2, anchor=anchor)  # type: ignore[arg-type]

        lbl = tk.Label(row, text=label, bg="#181825", fg="#6c7086",
                       font=("Segoe UI", 7))
        lbl.pack(anchor=anchor, padx=4)  # type: ignore[arg-type]

        bubble = tk.Frame(row, bg=bg, padx=8, pady=4)
        bubble.pack(anchor=anchor, padx=4)  # type: ignore[arg-type]

        msg_label = tk.Label(bubble, text=text, bg=bg, fg=fg,
                             font=("Segoe UI", 9), wraplength=200,
                             justify=tk.LEFT, anchor=tk.W)
        msg_label.pack()

        self._chat_canvas.update_idletasks()
        self._chat_canvas.yview_moveto(1.0)

    # ------------------------------------------------------------------
    # Controls
    # ------------------------------------------------------------------

    def _clear_conversation(self) -> None:
        self._messages.clear()
        for w in self._chat_inner.winfo_children():
            w.destroy()
        self._add_system_message("Conversation cleared. How can I help?")

    def set_editor_context(self, context: str) -> None:
        self._editor_context = context
        self._context_label.config(text=f"[{context}]")
        if self._chat:
            try:
                self._chat.set_context(context)
            except Exception:
                pass

        for w in self._prompts_row.winfo_children():
            w.destroy()
        self._populate_sample_prompts()

        for w in self._gallery_row.winfo_children():
            w.destroy()
        self._populate_gallery()
