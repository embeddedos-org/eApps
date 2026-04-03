# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""CPU state display panel for EoSim simulation UI."""
import tkinter as tk
from tkinter import ttk


class CPUPanel(ttk.LabelFrame):
    """Displays real-time CPU register state with change highlighting."""

    def __init__(self, parent):
        super().__init__(parent, text="CPU State", padding=4)
        self._prev_regs = [0] * 16
        self._prev_pc = 0
        self._prev_sp = 0
        self._prev_lr = 0
        self._prev_cpsr = 0
        self._reg_labels = []
        self._flag_labels = {}
        self._build()

    def _build(self):
        special_frame = ttk.Frame(self)
        special_frame.pack(fill=tk.X, pady=(0, 4))

        self.pc_label = ttk.Label(
            special_frame, text="PC: 0x00000000", font=("Consolas", 9),
        )
        self.pc_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 8))

        self.sp_label = ttk.Label(
            special_frame, text="SP: 0x00000000", font=("Consolas", 9),
        )
        self.sp_label.grid(row=0, column=1, sticky=tk.W, padx=(0, 8))

        self.lr_label = ttk.Label(
            special_frame, text="LR: 0x00000000", font=("Consolas", 9),
        )
        self.lr_label.grid(row=1, column=0, sticky=tk.W, padx=(0, 8))

        self.cpsr_label = ttk.Label(
            special_frame, text="CPSR: 0x00000000", font=("Consolas", 9),
        )
        self.cpsr_label.grid(row=1, column=1, sticky=tk.W, padx=(0, 8))

        flags_frame = ttk.Frame(self)
        flags_frame.pack(fill=tk.X, pady=(0, 4))
        for i, flag_name in enumerate(["N", "Z", "C", "V"]):
            lbl = tk.Label(
                flags_frame, text=f" {flag_name} ", font=("Consolas", 9, "bold"),
                bg="#555555", fg="white", width=3, relief=tk.RAISED,
            )
            lbl.grid(row=0, column=i, padx=2)
            self._flag_labels[flag_name] = lbl

        info_frame = ttk.Frame(self)
        info_frame.pack(fill=tk.X, pady=(0, 4))
        self.mode_label = ttk.Label(
            info_frame, text="Mode: supervisor", font=("Consolas", 9),
        )
        self.mode_label.pack(side=tk.LEFT, padx=(0, 12))
        self.cycle_label = ttk.Label(
            info_frame, text="Cycles: 0", font=("Consolas", 9),
        )
        self.cycle_label.pack(side=tk.LEFT, padx=(0, 12))
        self.halted_label = ttk.Label(
            info_frame, text="", font=("Consolas", 9), foreground="red",
        )
        self.halted_label.pack(side=tk.LEFT)

        sep = ttk.Separator(self, orient=tk.HORIZONTAL)
        sep.pack(fill=tk.X, pady=4)

        reg_frame = ttk.Frame(self)
        reg_frame.pack(fill=tk.X)
        self._reg_labels = []
        for i in range(16):
            r, c = divmod(i, 4)
            lbl = ttk.Label(
                reg_frame,
                text=f"R{i:<2d}: 0x00000000",
                font=("Consolas", 9),
            )
            lbl.grid(row=r, column=c, sticky=tk.W, padx=(0, 6), pady=1)
            self._reg_labels.append(lbl)

    def update_state(self, cpu_state):
        """Update display from a CPUState object or dict."""
        if hasattr(cpu_state, 'regs'):
            regs = cpu_state.regs[:16]
            pc = cpu_state.pc
            sp = cpu_state.sp
            lr = getattr(cpu_state, 'lr', 0)
            cpsr = getattr(cpu_state, 'cpsr', 0)
            cycles = cpu_state.cycles
            mode = getattr(cpu_state, 'mode', 'supervisor')
            halted = getattr(cpu_state, 'halted', False)
        elif isinstance(cpu_state, dict):
            regs = cpu_state.get('regs', [0] * 16)[:16]
            pc = cpu_state.get('pc', 0)
            sp = cpu_state.get('sp', 0)
            lr = cpu_state.get('lr', 0)
            cpsr = cpu_state.get('cpsr', 0)
            cycles = cpu_state.get('cycles', 0)
            mode = cpu_state.get('mode', 'supervisor')
            halted = cpu_state.get('halted', False)
        else:
            return

        self._update_label(self.pc_label, f"PC: 0x{pc:08X}", pc != self._prev_pc)
        self._update_label(self.sp_label, f"SP: 0x{sp:08X}", sp != self._prev_sp)
        self._update_label(self.lr_label, f"LR: 0x{lr:08X}", lr != self._prev_lr)
        self._update_label(
            self.cpsr_label, f"CPSR: 0x{cpsr:08X}", cpsr != self._prev_cpsr
        )

        flag_bits = {
            "N": bool(cpsr & (1 << 31)),
            "Z": bool(cpsr & (1 << 30)),
            "C": bool(cpsr & (1 << 29)),
            "V": bool(cpsr & (1 << 28)),
        }
        for name, active in flag_bits.items():
            lbl = self._flag_labels[name]
            if active:
                lbl.configure(bg="#4ec9b0", fg="black")
            else:
                lbl.configure(bg="#555555", fg="white")

        self.mode_label.configure(text=f"Mode: {mode}")
        self.cycle_label.configure(text=f"Cycles: {cycles}")
        self.halted_label.configure(text="HALTED" if halted else "")

        for i in range(min(16, len(regs))):
            changed = (
                i < len(self._prev_regs) and regs[i] != self._prev_regs[i]
            )
            self._update_label(
                self._reg_labels[i],
                f"R{i:<2d}: 0x{regs[i]:08X}",
                changed,
            )

        self._prev_regs = list(regs)
        self._prev_pc = pc
        self._prev_sp = sp
        self._prev_lr = lr
        self._prev_cpsr = cpsr

    def _update_label(self, label, text, changed):
        label.configure(text=text)
        if changed:
            label.configure(foreground="#dcdcaa")
            label.after(500, lambda: label.configure(foreground=""))
        else:
            label.configure(foreground="")

    def reset(self):
        self._prev_regs = [0] * 16
        self._prev_pc = 0
        self._prev_sp = 0
        self._prev_lr = 0
        self._prev_cpsr = 0
        for lbl in self._reg_labels:
            lbl.configure(text="R??: 0x00000000", foreground="")
        self.pc_label.configure(text="PC: 0x00000000", foreground="")
        self.sp_label.configure(text="SP: 0x00000000", foreground="")
        self.lr_label.configure(text="LR: 0x00000000", foreground="")
        self.cpsr_label.configure(text="CPSR: 0x00000000", foreground="")
        self.mode_label.configure(text="Mode: supervisor")
        self.cycle_label.configure(text="Cycles: 0")
        self.halted_label.configure(text="")
        for lbl in self._flag_labels.values():
            lbl.configure(bg="#555555", fg="white")
