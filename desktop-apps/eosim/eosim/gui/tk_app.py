# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""TkSimulatorApp — tkinter GUI shell wrapping the SimulatorApp controller.

Provides the full visual interface: toolbar, build sidebar, peripheral
panels with domain-specific rendering, status bar, and scenario selector.
"""
import time
import tkinter as tk
from tkinter import ttk

from eosim.gui.simulator_app import SimulatorApp
from eosim.gui.widgets.build_panel import BuildPanel, PERIPHERAL_CATEGORIES
from eosim.gui.widgets.peripheral_panel import PeripheralPanel
from eosim.gui.widgets.uart_terminal import UARTTerminal
from eosim.gui.widgets.cpu_panel import CPUPanel
from eosim.gui.widgets.gpio_panel import GPIOPanel
from eosim.gui.widgets.memory_view import MemoryView
from eosim.gui.product_templates import PRODUCT_CATALOG
from eosim.gui.widgets.viewer_3d import Viewer3DPanel


class TkBuildPanel(ttk.LabelFrame):
    """Tkinter wrapper for the pure-Python BuildPanel data model."""

    def __init__(self, parent, on_build_callback=None):
        super().__init__(parent, text="Build Configuration", padding=6)
        self._build_panel = BuildPanel()
        self._on_build = on_build_callback
        self._periph_vars = {}
        self._build()

    def _build(self):
        ttk.Label(self, text="Product:", font=("", 9, "bold")).pack(
            anchor=tk.W, pady=(0, 2),
        )
        products = self._build_panel.list_products()
        self._product_names = [p['name'] for p in products]
        self._product_display = [f"{p['icon']} {p['display_name']}" for p in products]
        self.product_var = tk.StringVar()
        self.product_combo = ttk.Combobox(
            self, textvariable=self.product_var,
            values=self._product_display, state="readonly", width=24,
        )
        self.product_combo.pack(fill=tk.X, pady=(0, 4))
        self.product_combo.bind("<<ComboboxSelected>>", self._on_product_select)

        info_frame = ttk.Frame(self)
        info_frame.pack(fill=tk.X, pady=(0, 4))
        self.arch_label = ttk.Label(info_frame, text="Arch: —", font=("Consolas", 9))
        self.arch_label.pack(anchor=tk.W)
        ttk.Label(info_frame, text="RAM (MB):", font=("", 8)).pack(
            anchor=tk.W, pady=(4, 0),
        )
        self.ram_var = tk.IntVar(value=128)
        self.ram_spin = ttk.Spinbox(
            info_frame, from_=8, to=4096, textvariable=self.ram_var,
            width=8, font=("Consolas", 9),
        )
        self.ram_spin.pack(anchor=tk.W)

        sep = ttk.Separator(self, orient=tk.HORIZONTAL)
        sep.pack(fill=tk.X, pady=4)

        ttk.Label(self, text="Peripherals:", font=("", 9, "bold")).pack(
            anchor=tk.W, pady=(0, 2),
        )

        self._periph_canvas = tk.Canvas(self, highlightthickness=0, height=200)
        periph_scrollbar = ttk.Scrollbar(
            self, orient=tk.VERTICAL, command=self._periph_canvas.yview,
        )
        self._periph_inner = ttk.Frame(self._periph_canvas)
        self._periph_inner.bind(
            "<Configure>",
            lambda e: self._periph_canvas.configure(
                scrollregion=self._periph_canvas.bbox("all"),
            ),
        )
        self._periph_canvas.create_window(
            (0, 0), window=self._periph_inner, anchor="nw",
        )
        self._periph_canvas.configure(yscrollcommand=periph_scrollbar.set)
        self._periph_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        periph_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._periph_vars = {}
        for category, periphs in PERIPHERAL_CATEGORIES.items():
            ttk.Label(
                self._periph_inner, text=category, font=("", 8, "bold"),
            ).pack(anchor=tk.W, pady=(4, 0))
            for p in periphs:
                var = tk.BooleanVar(value=False)
                ttk.Checkbutton(
                    self._periph_inner, text=p, variable=var,
                    command=lambda name=p: self._on_periph_toggle(name),
                ).pack(anchor=tk.W, padx=(12, 0))
                self._periph_vars[p] = var

    def _on_product_select(self, event=None):
        idx = self.product_combo.current()
        if idx < 0:
            return
        product_name = self._product_names[idx]
        self._build_panel.select_product(product_name)
        config = self._build_panel.get_build_config()
        self.arch_label.configure(text=f"Arch: {config['arch']}")
        self.ram_var.set(config.get('ram_mb', 128))
        selected = set(config.get('peripherals', []))
        for name, var in self._periph_vars.items():
            var.set(name in selected)

    def _on_periph_toggle(self, name):
        self._build_panel.toggle_peripheral(name)

    def get_build_config(self) -> dict:
        config = self._build_panel.get_build_config()
        config['ram_mb'] = self.ram_var.get()
        return config

    def get_selected_product_name(self) -> str:
        idx = self.product_combo.current()
        if idx < 0:
            return ''
        return self._product_names[idx]


class TkPeripheralPanel(ttk.LabelFrame):
    """Tkinter wrapper for PeripheralPanel with domain-specific sub-panels."""

    def __init__(self, parent):
        super().__init__(parent, text="Peripherals / Domain View", padding=4)
        self._periph_panel = PeripheralPanel()
        self._domain = ''
        self._domain_widgets = {}
        self._generic_text = None
        self._ecg_canvas = None
        self._motor_bars = []
        self._joint_bars = []
        self._build_default()

    def _build_default(self):
        self._domain_frame = ttk.Frame(self)
        self._domain_frame.pack(fill=tk.BOTH, expand=True)
        self._create_generic_panel()

    def configure_for_product(self, vm, domain=''):
        self._domain = domain
        self._periph_panel.configure_for_product(vm, domain)
        self._clear_domain_widgets()
        self._create_domain_widgets(domain)

    def _clear_domain_widgets(self):
        for w in self._domain_widgets.values():
            if isinstance(w, tk.Widget):
                w.destroy()
        self._domain_widgets = {}
        self._motor_bars = []
        self._joint_bars = []
        self._ecg_canvas = None
        if self._generic_text:
            self._generic_text.destroy()
            self._generic_text = None
        for child in self._domain_frame.winfo_children():
            child.destroy()

    def _create_domain_widgets(self, domain):
        if domain == 'automotive':
            self._create_automotive_panel()
        elif domain == 'robotics' and self._has_esc():
            self._create_drone_panel()
        elif domain == 'robotics':
            self._create_robot_panel()
        elif domain == 'medical':
            self._create_medical_panel()
        elif domain == 'aerospace' and self._has_arinc():
            self._create_aircraft_panel()
        elif domain == 'industrial':
            self._create_industrial_panel()
        elif domain in ('aerodynamics', 'physiology', 'finance', 'weather', 'gaming'):
            self._create_generic_panel()
        elif domain == 'aerodynamics':
            self._create_aerodynamics_panel()
        elif domain == 'physiology':
            self._create_physiology_panel()
        elif domain == 'finance':
            self._create_finance_panel()
        elif domain == 'weather':
            self._create_weather_panel()
        elif domain == 'gaming':
            self._create_gaming_panel()
        else:
            self._create_generic_panel()

    def _has_esc(self):
        return any(
            p.device_type == 'ESCController'
            for p in self._periph_panel.sub_panels.values()
        )

    def _has_arinc(self):
        return any(
            p.device_type == 'ARINC429'
            for p in self._periph_panel.sub_panels.values()
        )

    def _make_kv(self, parent, key, row, col=0):
        ttk.Label(parent, text=f"{key}:", font=("", 8)).grid(
            row=row, column=col * 2, sticky=tk.W, padx=(0, 4), pady=1,
        )
        lbl = ttk.Label(parent, text="—", font=("Consolas", 9), width=14, anchor=tk.W)
        lbl.grid(row=row, column=col * 2 + 1, sticky=tk.W, pady=1)
        self._domain_widgets[key] = lbl
        return lbl

    def _create_automotive_panel(self):
        f = ttk.Frame(self._domain_frame)
        f.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        ttk.Label(f, text="\U0001F697 Automotive", font=("", 10, "bold")).grid(
            row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 4))
        self._make_kv(f, "Speed (km/h)", 1, 0)
        self._make_kv(f, "RPM", 1, 1)
        self._make_kv(f, "Steering (\u00b0)", 2, 0)
        self._make_kv(f, "Throttle (%)", 2, 1)
        self._make_kv(f, "Brake (%)", 3, 0)
        self._make_kv(f, "SoC (%)", 3, 1)
        self._make_kv(f, "CAN TX", 4, 0)
        self._make_kv(f, "CAN RX", 4, 1)
        self._make_kv(f, "CAN Errors", 5, 0)
        self._make_kv(f, "Bus Off", 5, 1)

    def _create_drone_panel(self):
        f = ttk.Frame(self._domain_frame)
        f.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        ttk.Label(f, text="\U0001F681 Drone / UAV", font=("", 10, "bold")).pack(
            anchor=tk.W, pady=(0, 4))
        mf = ttk.LabelFrame(f, text="Motor RPM", padding=2)
        mf.pack(fill=tk.X, pady=2)
        self._motor_bars = []
        for i in range(4):
            row = ttk.Frame(mf)
            row.pack(fill=tk.X, pady=1)
            ttk.Label(row, text=f"M{i+1}", width=3).pack(side=tk.LEFT)
            bar = ttk.Progressbar(row, maximum=10000, length=120)
            bar.pack(side=tk.LEFT, padx=4)
            lbl = ttk.Label(row, text="0", font=("Consolas", 8), width=6)
            lbl.pack(side=tk.LEFT)
            self._motor_bars.append((bar, lbl))
        kv = ttk.Frame(f)
        kv.pack(fill=tk.X, pady=2)
        self._make_kv(kv, "Flight Mode", 0, 0)
        self._make_kv(kv, "Altitude (m)", 0, 1)
        self._make_kv(kv, "Roll (\u00b0)", 1, 0)
        self._make_kv(kv, "Pitch (\u00b0)", 1, 1)
        self._make_kv(kv, "Yaw (\u00b0)", 2, 0)
        self._make_kv(kv, "SoC (%)", 2, 1)

    def _create_medical_panel(self):
        f = ttk.Frame(self._domain_frame)
        f.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        ttk.Label(f, text="\U0001FA7A Medical Monitor", font=("", 10, "bold")).pack(
            anchor=tk.W, pady=(0, 4))
        kv = ttk.Frame(f)
        kv.pack(fill=tk.X, pady=2)
        self._make_kv(kv, "Heart Rate", 0, 0)
        self._make_kv(kv, "SpO2 (%)", 0, 1)
        self._make_kv(kv, "Temperature", 1, 0)
        self._make_kv(kv, "Resp Rate", 1, 1)
        self._make_kv(kv, "BP Sys/Dia", 2, 0)
        self._make_kv(kv, "Pump Flow", 2, 1)
        af = ttk.Frame(f)
        af.pack(fill=tk.X, pady=2)
        ttk.Label(af, text="Alarm:", font=("", 8)).pack(side=tk.LEFT)
        self._alarm_label = tk.Label(
            af, text="NONE", font=("Consolas", 10, "bold"),
            bg="#2d2d2d", fg="#4ec9b0", padx=8, pady=2)
        self._alarm_label.pack(side=tk.LEFT, padx=4)
        self._domain_widgets['_alarm_label'] = self._alarm_label
        ef = ttk.LabelFrame(f, text="ECG Waveform", padding=2)
        ef.pack(fill=tk.BOTH, expand=True, pady=4)
        self._ecg_canvas = tk.Canvas(ef, bg="#1e1e1e", height=60, highlightthickness=0)
        self._ecg_canvas.pack(fill=tk.BOTH, expand=True)

    def _create_robot_panel(self):
        f = ttk.Frame(self._domain_frame)
        f.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        ttk.Label(f, text="\U0001F916 Robot Controller", font=("", 10, "bold")).pack(
            anchor=tk.W, pady=(0, 4))
        jf = ttk.LabelFrame(f, text="Joint Angles", padding=2)
        jf.pack(fill=tk.X, pady=2)
        self._joint_bars = []
        for i in range(6):
            row = ttk.Frame(jf)
            row.pack(fill=tk.X, pady=1)
            ttk.Label(row, text=f"J{i+1}", width=3).pack(side=tk.LEFT)
            bar = ttk.Progressbar(row, maximum=360, length=120)
            bar.pack(side=tk.LEFT, padx=4)
            lbl = ttk.Label(row, text="0\u00b0", font=("Consolas", 8), width=6)
            lbl.pack(side=tk.LEFT)
            self._joint_bars.append((bar, lbl))
        kv = ttk.Frame(f)
        kv.pack(fill=tk.X, pady=2)
        self._make_kv(kv, "Gripper", 0, 0)
        self._make_kv(kv, "Obstacle (cm)", 0, 1)
        self._make_kv(kv, "Op Mode", 1, 0)

    def _create_aircraft_panel(self):
        f = ttk.Frame(self._domain_frame)
        f.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        ttk.Label(f, text="\u2708 Aircraft", font=("", 10, "bold")).pack(
            anchor=tk.W, pady=(0, 4))
        kv = ttk.Frame(f)
        kv.pack(fill=tk.X, pady=2)
        self._make_kv(kv, "Altitude (ft)", 0, 0)
        self._make_kv(kv, "Airspeed (kts)", 0, 1)
        self._make_kv(kv, "Heading (\u00b0)", 1, 0)
        self._make_kv(kv, "VS (fpm)", 1, 1)
        self._make_kv(kv, "Gear", 2, 0)
        self._make_kv(kv, "Flaps", 2, 1)
        self._make_kv(kv, "Flight Phase", 3, 0)

    def _create_industrial_panel(self):
        f = ttk.Frame(self._domain_frame)
        f.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        ttk.Label(f, text="\U0001F3ED Industrial PLC", font=("", 10, "bold")).pack(
            anchor=tk.W, pady=(0, 4))
        kv = ttk.Frame(f)
        kv.pack(fill=tk.X, pady=2)
        self._make_kv(kv, "Conveyor Speed", 0, 0)
        self._make_kv(kv, "Motor Status", 0, 1)
        self._make_kv(kv, "Modbus TXN", 1, 0)
        self._make_kv(kv, "Relay States", 1, 1)
        rf = ttk.LabelFrame(f, text="Modbus Registers [0-15]", padding=2)
        rf.pack(fill=tk.X, pady=2)
        self._reg_text = tk.Text(
            rf, wrap=tk.NONE, font=("Consolas", 8),
            bg="#1e1e1e", fg="#d4d4d4", state=tk.DISABLED, height=3, width=50)
        self._reg_text.pack(fill=tk.X)
        self._domain_widgets['_reg_text'] = self._reg_text

    def _create_generic_panel(self):
        self._generic_text = tk.Text(
            self._domain_frame, wrap=tk.WORD, font=("Consolas", 9),
            bg="#1e1e1e", fg="#d4d4d4", state=tk.DISABLED, height=10, width=50)
        self._generic_text.pack(fill=tk.BOTH, expand=True)

    def update_from_state(self, state: dict, vm=None):
        if self._domain == 'automotive':
            self._update_automotive(state, vm)
        elif self._domain == 'robotics' and self._motor_bars:
            self._update_drone(state)
        elif self._domain == 'robotics':
            self._update_robot(state)
        elif self._domain == 'medical':
            self._update_medical(state)
        elif self._domain == 'aerospace' and 'altitude_ft' in state:
            self._update_aircraft(state)
        elif self._domain == 'industrial':
            self._update_industrial(state, vm)
        else:
            self._update_generic(state)
        if vm:
            self._periph_panel.update(vm)

    def _set_kv(self, key, value):
        lbl = self._domain_widgets.get(key)
        if lbl and isinstance(lbl, (ttk.Label, tk.Label)):
            lbl.configure(text=str(value))

    def _update_automotive(self, state, vm=None):
        self._set_kv("Speed (km/h)", state.get('speed_kmh', 0))
        self._set_kv("RPM", state.get('rpm', 0))
        self._set_kv("Steering (\u00b0)", state.get('steering_deg', 0))
        self._set_kv("Throttle (%)", state.get('throttle_pct', 0))
        self._set_kv("Brake (%)", state.get('brake_pct', 0))
        self._set_kv("SoC (%)", state.get('soc_pct', 0))
        if vm:
            can = vm.peripherals.get('can0')
            if can:
                self._set_kv("CAN TX", can.tx_count)
                self._set_kv("CAN RX", can.rx_count)
                self._set_kv("CAN Errors", can.error_count)
                self._set_kv("Bus Off", "YES" if can.bus_off else "No")

    def _update_drone(self, state):
        rpms = state.get('motor_rpm', [0, 0, 0, 0])
        for i, (bar, lbl) in enumerate(self._motor_bars):
            rpm = rpms[i] if i < len(rpms) else 0
            bar['value'] = max(0, rpm)
            lbl.configure(text=str(int(rpm)))
        self._set_kv("Flight Mode", state.get('flight_mode', 'DISARMED'))
        self._set_kv("Altitude (m)", f"{state.get('altitude_m', 0):.1f}")
        self._set_kv("Roll (\u00b0)", state.get('roll_deg', 0))
        self._set_kv("Pitch (\u00b0)", state.get('pitch_deg', 0))
        self._set_kv("Yaw (\u00b0)", state.get('yaw_deg', 0))
        self._set_kv("SoC (%)", state.get('soc_pct', 0))

    def _update_medical(self, state):
        self._set_kv("Heart Rate", state.get('heart_rate', 0))
        self._set_kv("SpO2 (%)", state.get('spo2', 0))
        self._set_kv("Temperature", f"{state.get('temperature', 0):.1f}\u00b0C")
        self._set_kv("Resp Rate", state.get('resp_rate', 0))
        self._set_kv("BP Sys/Dia", f"{state.get('bp_sys', 0)}/{state.get('bp_dia', 0)}")
        self._set_kv("Pump Flow", f"{state.get('pump_flow', 0):.1f} mL/min")
        alarm = state.get('alarm', 'NONE')
        priority = state.get('alarm_priority', 0)
        al = self._domain_widgets.get('_alarm_label')
        if al:
            al.configure(text=alarm)
            if priority >= 3:
                al.configure(bg="#ff4444", fg="white")
            elif priority >= 2:
                al.configure(bg="#ff8800", fg="black")
            elif priority >= 1:
                al.configure(bg="#ffcc00", fg="black")
            else:
                al.configure(bg="#2d2d2d", fg="#4ec9b0")
        if self._ecg_canvas:
            self._draw_ecg(state.get('ecg_waveform', []))

    def _draw_ecg(self, waveform):
        self._ecg_canvas.delete("all")
        if not waveform or len(waveform) < 2:
            return
        w = self._ecg_canvas.winfo_width()
        h = self._ecg_canvas.winfo_height()
        if w < 10 or h < 10:
            return
        n = len(waveform)
        dx = w / max(n - 1, 1)
        mn, mx = min(waveform), max(waveform)
        rng = mx - mn if mx != mn else 1
        pts = []
        for i, v in enumerate(waveform):
            pts.extend([i * dx, h - ((v - mn) / rng) * (h - 4) - 2])
        if len(pts) >= 4:
            self._ecg_canvas.create_line(pts, fill="#4ec9b0", width=1.5, smooth=True)

    def _update_robot(self, state):
        angles = state.get('joint_angles', [0] * 6)
        for i, (bar, lbl) in enumerate(self._joint_bars):
            a = angles[i] if i < len(angles) else 0
            bar['value'] = max(0, a + 180)
            lbl.configure(text=f"{a:.0f}\u00b0")
        self._set_kv("Gripper", state.get('gripper_state', 'open'))
        self._set_kv("Obstacle (cm)", f"{state.get('obstacle_cm', 0):.0f}")
        self._set_kv("Op Mode", state.get('op_mode', 'idle'))

    def _update_aircraft(self, state):
        self._set_kv("Altitude (ft)", f"{state.get('altitude_ft', 0):.0f}")
        self._set_kv("Airspeed (kts)", f"{state.get('airspeed_kts', 0):.0f}")
        self._set_kv("Heading (\u00b0)", f"{state.get('heading_deg', 0):.0f}")
        self._set_kv("VS (fpm)", f"{state.get('vs_fpm', 0):.0f}")
        self._set_kv("Gear", state.get('gear_state', 'UP'))
        self._set_kv("Flaps", f"{state.get('flap_deg', 0)}\u00b0")
        self._set_kv("Flight Phase", state.get('flight_phase', 'ground'))

    def _update_industrial(self, state, vm=None):
        self._set_kv("Conveyor Speed", state.get('conveyor_speed', 0))
        self._set_kv("Motor Status", state.get('motor_status', 'off'))
        if vm:
            mb = vm.peripherals.get('modbus0')
            if mb:
                self._set_kv("Modbus TXN", mb.transaction_count)
                rt = self._domain_widgets.get('_reg_text')
                if rt:
                    regs = mb.registers[:16]
                    lines = []
                    for i in range(0, len(regs), 8):
                        vals = " ".join(f"{v:5d}" for v in regs[i:i+8])
                        lines.append(f"[{i:02d}] {vals}")
                    rt.configure(state=tk.NORMAL)
                    rt.delete("1.0", tk.END)
                    rt.insert("1.0", "\n".join(lines))
                    rt.configure(state=tk.DISABLED)
            relay = vm.peripherals.get('relay0')
            if relay:
                bits = "".join("1" if s else "0" for s in getattr(relay, 'states', []))
                self._set_kv("Relay States", bits or "\u2014")

    def _update_generic(self, state):
        if not self._generic_text:
            return
        lines = [f"{k}: {v}" for k, v in sorted(state.items())]
        self._generic_text.configure(state=tk.NORMAL)
        self._generic_text.delete("1.0", tk.END)
        self._generic_text.insert("1.0", "\n".join(lines))
        self._generic_text.configure(state=tk.DISABLED)

    def reset(self):
        self._periph_panel = PeripheralPanel()
        self._clear_domain_widgets()
        self._create_generic_panel()


class TkSimulatorApp(ttk.Frame):
    """Main tkinter GUI shell — wraps the pure-Python SimulatorApp controller."""

    def __init__(self, parent):
        super().__init__(parent)
        self._app = SimulatorApp()
        self._running = False
        self._paused = False
        self._start_time = 0
        self._elapsed = 0
        self._build_ui()

    def _build_ui(self):
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=4, pady=4)
        self._build_toolbar(toolbar)

        body = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        body.pack(fill=tk.BOTH, expand=True, padx=4)

        self._build_panel = TkBuildPanel(body, on_build_callback=self._on_build)
        body.add(self._build_panel, weight=0)

        right = ttk.PanedWindow(body, orient=tk.VERTICAL)
        body.add(right, weight=1)

        top_right = ttk.PanedWindow(right, orient=tk.HORIZONTAL)
        right.add(top_right, weight=1)

        uart_frame = ttk.LabelFrame(top_right, text="UART", padding=2)
        self.uart_terminal = UARTTerminal(uart_frame)
        self.uart_terminal.pack(fill=tk.BOTH, expand=True)
        top_right.add(uart_frame, weight=1)

        cpu_periph = ttk.PanedWindow(top_right, orient=tk.VERTICAL)
        top_right.add(cpu_periph, weight=1)

        self.cpu_panel = CPUPanel(cpu_periph)
        cpu_periph.add(self.cpu_panel, weight=0)

        self.gpio_panel = GPIOPanel(cpu_periph)
        cpu_periph.add(self.gpio_panel, weight=0)

        mid_right = ttk.PanedWindow(right, orient=tk.HORIZONTAL)
        right.add(mid_right, weight=1)

        self.periph_panel = TkPeripheralPanel(mid_right)
        mid_right.add(self.periph_panel, weight=1)

        self.viewer_3d = Viewer3DPanel(mid_right)
        mid_right.add(self.viewer_3d, weight=1)

        state_frame = ttk.LabelFrame(mid_right, text="Simulator State", padding=2)
        mid_right.add(state_frame, weight=1)
        self._state_text = tk.Text(
            state_frame, wrap=tk.WORD, font=("Consolas", 9),
            bg="#1e1e1e", fg="#d4d4d4", state=tk.DISABLED,
            height=8, width=35,
        )
        state_scroll = ttk.Scrollbar(
            state_frame, orient=tk.VERTICAL, command=self._state_text.yview,
        )
        self._state_text.configure(yscrollcommand=state_scroll.set)
        self._state_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        state_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.memory_view = MemoryView(right)
        right.add(self.memory_view, weight=0)

        status = ttk.Frame(self)
        status.pack(fill=tk.X, padx=4, pady=(2, 4))
        self._build_status_bar(status)

    def _build_toolbar(self, parent):
        ttk.Label(parent, text="Product:", font=("", 9)).pack(
            side=tk.LEFT, padx=(0, 4),
        )
        products = sorted(PRODUCT_CATALOG.keys())
        self._product_display_map = {}
        display_names = []
        for key in products:
            tpl = PRODUCT_CATALOG[key]
            dn = f"{tpl.icon} {tpl.display_name}"
            display_names.append(dn)
            self._product_display_map[dn] = key
        self._toolbar_product_var = tk.StringVar()
        self._toolbar_product_combo = ttk.Combobox(
            parent, textvariable=self._toolbar_product_var,
            values=display_names, state="readonly", width=22,
        )
        self._toolbar_product_combo.pack(side=tk.LEFT, padx=(0, 8))
        self._toolbar_product_combo.bind(
            "<<ComboboxSelected>>", self._on_toolbar_product,
        )

        self._btn_build = ttk.Button(
            parent, text="\u25b6 Build & Run", command=self._on_build, width=12,
        )
        self._btn_build.pack(side=tk.LEFT, padx=2)

        self._btn_pause = ttk.Button(
            parent, text="\u23f8 Pause", command=self._on_pause, width=8,
            state=tk.DISABLED,
        )
        self._btn_pause.pack(side=tk.LEFT, padx=2)

        self._btn_step = ttk.Button(
            parent, text="\u23ed Step", command=self._on_step, width=7,
            state=tk.DISABLED,
        )
        self._btn_step.pack(side=tk.LEFT, padx=2)

        self._btn_stop = ttk.Button(
            parent, text="\u23f9 Stop", command=self._on_stop, width=7,
            state=tk.DISABLED,
        )
        self._btn_stop.pack(side=tk.LEFT, padx=2)

        self._btn_reset = ttk.Button(
            parent, text="\u21ba Reset", command=self._on_reset, width=7,
            state=tk.DISABLED,
        )
        self._btn_reset.pack(side=tk.LEFT, padx=2)

        sep = ttk.Separator(parent, orient=tk.VERTICAL)
        sep.pack(side=tk.LEFT, fill=tk.Y, padx=8)

        ttk.Label(parent, text="Scenario:", font=("", 9)).pack(
            side=tk.LEFT, padx=(0, 4),
        )
        self._scenario_var = tk.StringVar()
        self._scenario_combo = ttk.Combobox(
            parent, textvariable=self._scenario_var,
            values=[], state="readonly", width=20,
        )
        self._scenario_combo.pack(side=tk.LEFT, padx=(0, 4))

        self._btn_load_scenario = ttk.Button(
            parent, text="Load Scenario", command=self._on_load_scenario,
            width=14, state=tk.DISABLED,
        )
        self._btn_load_scenario.pack(side=tk.LEFT, padx=2)

    def _build_status_bar(self, parent):
        self._status_mode = ttk.Label(
            parent, text="Mode: Idle", font=("Consolas", 9),
            relief=tk.SUNKEN, padding=(4, 1),
        )
        self._status_mode.pack(side=tk.LEFT, padx=(0, 4))

        self._status_cycles = ttk.Label(
            parent, text="Cycles: 0", font=("Consolas", 9),
            relief=tk.SUNKEN, padding=(4, 1),
        )
        self._status_cycles.pack(side=tk.LEFT, padx=(0, 4))

        self._status_elapsed = ttk.Label(
            parent, text="Elapsed: 0.0s", font=("Consolas", 9),
            relief=tk.SUNKEN, padding=(4, 1),
        )
        self._status_elapsed.pack(side=tk.LEFT, padx=(0, 4))

        self._status_arch = ttk.Label(
            parent, text="Arch: \u2014", font=("Consolas", 9),
            relief=tk.SUNKEN, padding=(4, 1),
        )
        self._status_arch.pack(side=tk.LEFT, padx=(0, 4))

        self._status_product = ttk.Label(
            parent, text="Product: \u2014", font=("Consolas", 9),
            relief=tk.SUNKEN, padding=(4, 1),
        )
        self._status_product.pack(side=tk.LEFT, padx=(0, 4))

    # --- Toolbar callbacks ---

    def _on_toolbar_product(self, event=None):
        display = self._toolbar_product_var.get()
        product_name = self._product_display_map.get(display, '')
        if not product_name:
            return
        idx = next(
            (i for i, n in enumerate(self._build_panel._product_names)
             if n == product_name), -1,
        )
        if idx >= 0:
            self._build_panel.product_combo.current(idx)
            self._build_panel._on_product_select()

    def _on_build(self):
        product_name = self._build_panel.get_selected_product_name()
        if not product_name:
            display = self._toolbar_product_var.get()
            product_name = self._product_display_map.get(display, '')
        if not product_name:
            return

        config = self._build_panel.get_build_config()
        vm = self._app.build_and_run(
            product_name,
            peripherals=config.get('peripherals', []),
            arch=config.get('arch', ''),
            ram_mb=config.get('ram_mb', 128),
        )
        if not vm:
            return

        tpl = PRODUCT_CATALOG.get(product_name)
        domain = tpl.domain if tpl else ''
        self.periph_panel.configure_for_product(vm, domain)

        self.viewer_3d.set_domain(domain)

        gpio = vm.peripherals.get('gpio0')
        if gpio:
            self.gpio_panel.set_gpio_device(gpio)

        self.uart_terminal.clear()
        self.uart_terminal.set_inject_callback(
            lambda text: vm.inject_uart(text)
            if hasattr(vm, 'inject_uart') else None,
        )

        if vm.bus:
            self.memory_view.set_bus(vm.bus)

        scenarios = list(getattr(self._app.simulator, 'SCENARIOS', {}).keys())
        self._scenario_combo.configure(values=scenarios)
        if scenarios:
            self._scenario_combo.current(0)

        self._running = True
        self._paused = False
        self._start_time = time.time()
        self._elapsed = 0

        self._btn_build.configure(state=tk.DISABLED)
        self._btn_pause.configure(state=tk.NORMAL)
        self._btn_step.configure(state=tk.NORMAL)
        self._btn_stop.configure(state=tk.NORMAL)
        self._btn_reset.configure(state=tk.NORMAL)
        self._btn_load_scenario.configure(state=tk.NORMAL)

        self._status_arch.configure(text=f"Arch: {config.get('arch', 'arm')}")
        self._status_product.configure(
            text=f"Product: {tpl.display_name if tpl else product_name}",
        )

        self._schedule_update()

    def _on_pause(self):
        if self._paused:
            self._paused = False
            self._btn_pause.configure(text="\u23f8 Pause")
            self._schedule_update()
        else:
            self._paused = True
            self._btn_pause.configure(text="\u25b6 Resume")

    def _on_step(self):
        if not self._app.simulator:
            return
        self._app.tick()
        self._update_all_panels()

    def _on_stop(self):
        self._running = False
        self._paused = False
        self._app.stop()
        self._btn_build.configure(state=tk.NORMAL)
        self._btn_pause.configure(state=tk.DISABLED, text="\u23f8 Pause")
        self._btn_step.configure(state=tk.DISABLED)
        self._btn_stop.configure(state=tk.DISABLED)
        self._status_mode.configure(text="Mode: Stopped")

    def _on_reset(self):
        self._on_stop()
        self._app.reset()
        self.cpu_panel.reset()
        self.gpio_panel.reset()
        self.periph_panel.reset()
        self.memory_view.reset()
        self.uart_terminal.clear()
        self._status_cycles.configure(text="Cycles: 0")
        self._status_elapsed.configure(text="Elapsed: 0.0s")
        self._status_mode.configure(text="Mode: Idle")
        self._btn_reset.configure(state=tk.DISABLED)

    def _on_load_scenario(self):
        name = self._scenario_var.get()
        if not name or not self._app.simulator:
            return
        if hasattr(self._app.simulator, 'load_scenario'):
            self._app.simulator.load_scenario(name)
        self._update_all_panels()

    # --- Periodic update loop ---

    def _schedule_update(self):
        if not self._running:
            return
        if not self._paused:
            self._app.tick()
            self._update_all_panels()
        self.after(100, self._schedule_update)

    def _update_all_panels(self):
        if not self._app.simulator or not self._app.vm:
            return

        state = self._app.get_state()
        vm = self._app.vm

        if vm.cpu:
            self.cpu_panel.update_state(vm.cpu.state)

        gpio = vm.peripherals.get('gpio0')
        if gpio:
            self.gpio_panel.update_display(gpio)

        uart_out = vm.get_uart_output()
        if uart_out:
            self.uart_terminal.append(uart_out)

        self.periph_panel.update_from_state(state, vm)

        self.viewer_3d.update_3d(state)

        self.memory_view.refresh()

        self._update_state_panel(state)
        self._update_status_bar()

    def _update_state_panel(self, state):
        lines = []
        for k, v in sorted(state.items()):
            if isinstance(v, list) and len(v) > 8:
                v = v[:8]
            lines.append(f"{k}: {v}")
        self._state_text.configure(state=tk.NORMAL)
        self._state_text.delete("1.0", tk.END)
        self._state_text.insert("1.0", "\n".join(lines))
        self._state_text.configure(state=tk.DISABLED)

    def _update_status_bar(self):
        if self._running and not self._paused:
            mode = "Running"
        elif self._paused:
            mode = "Paused"
        else:
            mode = "Stopped"
        self._status_mode.configure(text=f"Mode: {mode}")
        self._status_cycles.configure(text=f"Cycles: {self._app.tick_count}")
        self._elapsed = time.time() - self._start_time if self._start_time else 0
        self._status_elapsed.configure(text=f"Elapsed: {self._elapsed:.1f}s")

    def on_close(self):
        """Clean up when the window is closed."""
        self._running = False
        self._app.stop()
