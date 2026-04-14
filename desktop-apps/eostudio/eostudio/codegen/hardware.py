"""Hardware code generation — generates complete embedded firmware projects.

Converts board configuration dictionaries and schematic data into full firmware
projects for multiple target operating systems: EoS, bare-metal, FreeRTOS,
Zephyr, and Linux.  Generates C source files, linker scripts, Makefiles,
CMakeLists.txt, HAL peripheral drivers, device trees, and startup assembly.
"""

from __future__ import annotations

import textwrap
from typing import Any, Dict, List, Optional


class FirmwareGenerator:
    """Generates a complete firmware project from a board configuration."""

    SUPPORTED_TARGETS = ("eos", "baremetal", "freertos", "zephyr", "linux")

    def __init__(self, board_config: dict, target_os: str = "eos") -> None:
        if target_os not in self.SUPPORTED_TARGETS:
            raise ValueError(f"Unsupported target OS {target_os!r}.")
        self.board = board_config
        self.target = target_os
        self.name = board_config.get("name", "board")
        self.arch = board_config.get("arch", "arm-cortex-m")
        self.cpu = board_config.get("cpu", "cortex-m4")
        self.clock_mhz: int = board_config.get("clock_mhz", 168)
        self.memory: List[Dict[str, Any]] = board_config.get("memory", [
            {"name": "FLASH", "base": 0x08000000, "size": 0x100000},
            {"name": "SRAM", "base": 0x20000000, "size": 0x20000},
        ])
        self.peripherals: List[Dict[str, Any]] = board_config.get("peripherals", [])

    # ------------------------------------------------------------------
    # Top-level generation
    # ------------------------------------------------------------------

    def generate(self, app_name: str = "app", peripherals: Optional[List[str]] = None) -> Dict[str, str]:
        files: Dict[str, str] = {}
        active = self._resolve_peripherals(peripherals)
        tc = "arm-none-eabi-" if "arm" in self.arch else "riscv64-unknown-elf-"
        srcs = self._collect_sources(app_name)

        files["board.h"] = self._gen_board_h(app_name)
        files["main.c"] = self._gen_main_c(app_name)
        files["Makefile"] = self.generate_makefile(srcs, ["."], tc)
        files["CMakeLists.txt"] = self.generate_cmake(srcs, ["."], tc)
        files["README.md"] = self._gen_readme(app_name)

        _dispatch = {
            "uart": self.generate_uart_driver, "spi": self.generate_spi_driver,
            "i2c": self.generate_i2c_driver, "gpio": self.generate_gpio_driver,
            "adc": self.generate_adc_driver, "pwm": self.generate_pwm_driver,
            "timer": self.generate_timer_driver, "can": self.generate_can_driver,
            "ethernet": self.generate_ethernet_driver,
        }
        for p in active:
            pt = p.get("type", "gpio")
            pn = p.get("name", pt + "0")
            fn = _dispatch.get(pt)
            if fn:
                files[f"drivers/{pn}.c"] = fn(p)
                files[f"drivers/{pn}.h"] = self._gen_driver_header(pn, pt)

        tgt = {"eos": self._gen_eos, "baremetal": self._gen_baremetal,
               "freertos": self._gen_freertos, "zephyr": self._gen_zephyr,
               "linux": self._gen_linux}
        files.update(tgt[self.target](app_name))
        return files

    def _resolve_peripherals(self, req: Optional[List[str]]) -> List[Dict[str, Any]]:
        if req is None:
            return list(self.peripherals)
        return [p for p in self.peripherals if p.get("type") in req or p.get("name") in req]

    def _collect_sources(self, app_name: str) -> List[str]:
        s = ["main.c"]
        if self.target == "eos":
            s.append("eos_app.c")
        elif self.target == "baremetal":
            s.append("system_init.c")
        elif self.target == "freertos":
            s.append("main_freertos.c")
        elif self.target == "linux":
            s.append(f"{app_name}_module.c")
        for p in self.peripherals:
            s.append(f"drivers/{p.get('name', p.get('type', 'gpio') + '0')}.c")
        return s

    # ------------------------------------------------------------------
    # board.h / main.c / README
    # ------------------------------------------------------------------

    def _gen_board_h(self, app_name: str) -> str:
        g = f"BOARD_{self.name.upper().replace('-', '_')}_H"
        L = [f"#ifndef {g}", f"#define {g}", "",
             f"/* Board: {self.name}  CPU: {self.cpu}  Clock: {self.clock_mhz} MHz */", "",
             f"#define SYSTEM_CLOCK_HZ   ({self.clock_mhz}000000UL)",
             f"#define HSE_VALUE         ({self.board.get('hse_mhz', 8)}000000UL)",
             f"#define HSI_VALUE         (16000000UL)", ""]
        for m in self.memory:
            t = m["name"].upper().replace(" ", "_")
            L += [f"#define {t}_BASE   (0x{m['base']:08X}UL)", f"#define {t}_SIZE   (0x{m['size']:08X}UL)"]
        L.append("")
        for p in self.peripherals:
            n = p.get("name", p["type"] + "0").upper()
            L.append(f"#define {n}_BASE   (0x{p.get('base', 0x40000000):08X}UL)")
            if p.get("irq") is not None:
                L.append(f"#define {n}_IRQn   ({p['irq']})")
        L.append("")
        for p in self.peripherals:
            for pin in p.get("pins", []):
                pn = pin.get("name", "PIN").upper()
                L += [f"#define {pn}_PORT   GPIO{pin.get('port', 'A')}",
                      f"#define {pn}_PIN    ({pin.get('pin', 0)})",
                      f"#define {pn}_AF     ({pin.get('af', 0)})"]
        L += ["", f"#endif /* {g} */", ""]
        return "\n".join(L)

    def _gen_main_c(self, app_name: str) -> str:
        return textwrap.dedent(f"""\
            /* {app_name} — main entry  Board: {self.name}  Target: {self.target} */
            #include "board.h"
            #include <stdint.h>
            int main(void) {{
                SystemInit();
                BSP_Init();
                while (1) {{ /* application code */ }}
                return 0;
            }}
        """)

    def _gen_readme(self, app_name: str) -> str:
        return textwrap.dedent(f"""\
            # {app_name}
            Firmware for **{self.name}** ({self.cpu} @ {self.clock_mhz} MHz).
            Target: {self.target} | Arch: {self.arch}
            ## Build
            ```bash
            make
            cmake -B build && cmake --build build
            ```
        """)

    def _gen_driver_header(self, name: str, ptype: str) -> str:
        g = f"DRV_{name.upper()}_H"
        return f"#ifndef {g}\n#define {g}\n#include <stdint.h>\nvoid {name}_init(uint32_t cfg);\n#endif\n"

    # ------------------------------------------------------------------
    # EoS target
    # ------------------------------------------------------------------

    def _gen_eos(self, app_name: str) -> Dict[str, str]:
        mm = {m["name"]: (m["base"], m["size"]) for m in self.memory}
        return {
            "linker.ld": self.generate_linker_script(mm),
            "eos_config.h": textwrap.dedent(f"""\
                #ifndef EOS_CONFIG_H
                #define EOS_CONFIG_H
                #define EOS_PRODUCT_NAME       "{app_name}"
                #define EOS_PRODUCT_BOARD      "{self.name}"
                #define EOS_PRODUCT_ARCH       "{self.arch}"
                #define EOS_PRODUCT_CLOCK_HZ   ({self.clock_mhz}000000UL)
                #define EOS_TICK_RATE_HZ       (1000U)
                #define EOS_MAX_TASKS          (16U)
                #define EOS_STACK_SIZE_DEFAULT  (1024U)
                #endif
            """),
            "eos_app.c": textwrap.dedent(f"""\
                #include "eos_config.h"
                #include "board.h"
                #include <eos/eos.h>
                #include <eos/task.h>
                static void app_main_task(void *p) {{
                    (void)p;
                    while (1) {{ eos_task_delay(100); }}
                }}
                static void led_blink_task(void *p) {{
                    (void)p;
                    while (1) {{ eos_task_delay(500); }}
                }}
                void eos_app_init(void) {{
                    eos_init();
                    eos_task_create("main", app_main_task, NULL, EOS_STACK_SIZE_DEFAULT, 2);
                    eos_task_create("blink", led_blink_task, NULL, 512, 1);
                    eos_start();
                }}
            """),
        }

    # ------------------------------------------------------------------
    # Baremetal target
    # ------------------------------------------------------------------

    def _gen_baremetal(self, app_name: str) -> Dict[str, str]:
        mm = {m["name"]: (m["base"], m["size"]) for m in self.memory}
        vts = self.board.get("vector_table_size", 128)
        return {
            "linker.ld": self.generate_linker_script(mm),
            "startup.s": self.generate_startup(self.arch, vts),
            "system_init.c": textwrap.dedent(f"""\
                #include "board.h"
                #include <stdint.h>
                void SystemInit(void) {{
                    /* PLL: M=/{self.board.get('pll_m', 8)} N=*{self.board.get('pll_n', 336)} P=/{self.board.get('pll_p', 2)} */
                    /* Target: {self.clock_mhz} MHz */
                }}
                void BSP_Init(void) {{ /* peripheral init */ }}
            """),
        }

    # ------------------------------------------------------------------
    # FreeRTOS target
    # ------------------------------------------------------------------

    def _gen_freertos(self, app_name: str) -> Dict[str, str]:
        mm = {m["name"]: (m["base"], m["size"]) for m in self.memory}
        heap = sum(m.get("size", 0) for m in self.memory if "sram" in m.get("name", "").lower())
        return {
            "linker.ld": self.generate_linker_script(mm),
            "FreeRTOSConfig.h": textwrap.dedent(f"""\
                #ifndef FREERTOS_CONFIG_H
                #define FREERTOS_CONFIG_H
                #define configUSE_PREEMPTION              1
                #define configCPU_CLOCK_HZ                ({self.clock_mhz}000000UL)
                #define configTICK_RATE_HZ                (1000)
                #define configMAX_PRIORITIES              (8)
                #define configMINIMAL_STACK_SIZE          (128)
                #define configTOTAL_HEAP_SIZE             ({heap // 2})
                #define configMAX_TASK_NAME_LEN           (16)
                #define configUSE_MUTEXES                 1
                #define configUSE_COUNTING_SEMAPHORES     1
                #define configUSE_TIMERS                  1
                #define configTIMER_TASK_PRIORITY          (configMAX_PRIORITIES - 1)
                #define configTIMER_QUEUE_LENGTH           10
                #define configTIMER_TASK_STACK_DEPTH       (configMINIMAL_STACK_SIZE * 2)
                #define configPRIO_BITS                   4
                #define configKERNEL_INTERRUPT_PRIORITY    (15 << (8 - configPRIO_BITS))
                #define configMAX_SYSCALL_INTERRUPT_PRIORITY (5 << (8 - configPRIO_BITS))
                #define INCLUDE_vTaskPrioritySet          1
                #define INCLUDE_vTaskDelete               1
                #define INCLUDE_vTaskSuspend              1
                #define INCLUDE_vTaskDelay                1
                #endif
            """),
            "main_freertos.c": textwrap.dedent(f"""\
                #include "board.h"
                #include "FreeRTOSConfig.h"
                #include "FreeRTOS.h"
                #include "task.h"
                static void app_task(void *p) {{
                    (void)p;
                    for (;;) {{ vTaskDelay(pdMS_TO_TICKS(100)); }}
                }}
                static void heartbeat_task(void *p) {{
                    (void)p;
                    for (;;) {{ vTaskDelay(pdMS_TO_TICKS(500)); }}
                }}
                void freertos_app_init(void) {{
                    xTaskCreate(app_task, "app", configMINIMAL_STACK_SIZE*4, NULL, 2, NULL);
                    xTaskCreate(heartbeat_task, "hb", configMINIMAL_STACK_SIZE, NULL, 1, NULL);
                    vTaskStartScheduler();
                }}
            """),
        }

    # ------------------------------------------------------------------
    # Zephyr target
    # ------------------------------------------------------------------

    def _gen_zephyr(self, app_name: str) -> Dict[str, str]:
        conf = [f"# Zephyr config for {app_name}", "CONFIG_PRINTK=y", "CONFIG_LOG=y",
                "CONFIG_GPIO=y", "CONFIG_SERIAL=y"]
        for p in self.peripherals:
            if p.get("type") in ("spi", "i2c", "adc", "pwm", "can"):
                conf.append(f"CONFIG_{p['type'].upper()}=y")
        overlay = [f"/* DT overlay for {self.name} */", ""]
        for p in self.peripherals:
            pn = p.get("name", p["type"] + "0")
            overlay += [f"&{pn} {{", f'\tstatus = "okay";', "};", ""]
        return {
            "prj.conf": "\n".join(conf) + "\n",
            "CMakeLists.txt": textwrap.dedent(f"""\
                cmake_minimum_required(VERSION 3.20.0)
                find_package(Zephyr REQUIRED HINTS $ENV{{ZEPHYR_BASE}})
                project({app_name})
                target_sources(app PRIVATE src/main.c)
            """),
            f"{self.name}.overlay": "\n".join(overlay),
        }

    # ------------------------------------------------------------------
    # Linux target
    # ------------------------------------------------------------------

    def _gen_linux(self, app_name: str) -> Dict[str, str]:
        files: Dict[str, str] = {}
        try:
            from eostudio.codegen.device_tree import DeviceTreeGenerator
            root = DeviceTreeGenerator.from_board_config(self.board)
            files[f"{self.name}.dts"] = DeviceTreeGenerator.to_dts(root)
        except ImportError:
            files[f"{self.name}.dts"] = f"/* DT for {self.name} */\n"

        files[f"{app_name}_module.c"] = textwrap.dedent(f"""\
            #include <linux/module.h>
            #include <linux/kernel.h>
            #include <linux/init.h>
            #include <linux/platform_device.h>
            #include <linux/of.h>
            #define DRIVER_NAME "{app_name}"
            static int {app_name}_probe(struct platform_device *pdev) {{
                dev_info(&pdev->dev, "{app_name} probed\\n");
                return 0;
            }}
            static int {app_name}_remove(struct platform_device *pdev) {{
                dev_info(&pdev->dev, "{app_name} removed\\n");
                return 0;
            }}
            static const struct of_device_id {app_name}_of_match[] = {{
                {{ .compatible = "vendor,{app_name}" }}, {{ }}
            }};
            MODULE_DEVICE_TABLE(of, {app_name}_of_match);
            static struct platform_driver {app_name}_driver = {{
                .probe = {app_name}_probe, .remove = {app_name}_remove,
                .driver = {{ .name = DRIVER_NAME, .of_match_table = {app_name}_of_match }},
            }};
            module_platform_driver({app_name}_driver);
            MODULE_LICENSE("GPL");
            MODULE_DESCRIPTION("{app_name} platform driver");
        """)

        ks = app_name.upper().replace("-", "_")
        files["Kconfig"] = textwrap.dedent(f"""\
            config {ks}
            \ttristate "{app_name} driver"
            \tdepends on OF
            \thelp
            \t  Platform driver for {self.name}.
        """)
        return files

    # ------------------------------------------------------------------
    # Peripheral driver generators
    # ------------------------------------------------------------------

    def generate_uart_driver(self, config: dict) -> str:
        n = config.get("name", "uart0")
        N = n.upper()
        b = config.get("base", 0x40011000)
        return (
            f"/* UART driver — {n} @ 0x{b:08X} */\n"
            f"#include \"board.h\"\n#include <stdint.h>\n#include <stddef.h>\n\n"
            f"#define {N}_BASE  (0x{b:08X}UL)\n"
            f"#define {N}_SR    (*(volatile uint32_t *)({N}_BASE + 0x00))\n"
            f"#define {N}_DR    (*(volatile uint32_t *)({N}_BASE + 0x04))\n"
            f"#define {N}_BRR   (*(volatile uint32_t *)({N}_BASE + 0x08))\n"
            f"#define {N}_CR1   (*(volatile uint32_t *)({N}_BASE + 0x0C))\n\n"
            f"static volatile uint8_t rx_buf[256];\n"
            f"static volatile uint16_t rx_head = 0, rx_tail = 0;\n\n"
            f"void {n}_init(uint32_t baudrate) {{\n"
            f"    uint32_t div = SYSTEM_CLOCK_HZ / baudrate;\n"
            f"    {N}_BRR = div;\n"
            f"    {N}_CR1 = (1<<13)|(1<<3)|(1<<2)|(1<<5);\n}}\n\n"
            f"void {n}_send(const uint8_t *data, uint32_t len) {{\n"
            f"    for (uint32_t i = 0; i < len; i++) {{\n"
            f"        while (!({N}_SR & (1<<7))) {{}}\n"
            f"        {N}_DR = data[i];\n    }}\n"
            f"    while (!({N}_SR & (1<<6))) {{}}\n}}\n\n"
            f"uint32_t {n}_receive(uint8_t *buf, uint32_t max_len) {{\n"
            f"    uint32_t c = 0;\n"
            f"    while (c < max_len && rx_head != rx_tail) {{\n"
            f"        buf[c++] = rx_buf[rx_tail++]; rx_tail &= 0xFF;\n    }}\n"
            f"    return c;\n}}\n\n"
            f"void {n}_isr(void) {{\n"
            f"    if ({N}_SR & (1<<5)) {{\n"
            f"        rx_buf[rx_head++] = (uint8_t){N}_DR; rx_head &= 0xFF;\n    }}\n}}\n"
        )

    def generate_spi_driver(self, config: dict) -> str:
        n = config.get("name", "spi0")
        N = n.upper()
        b = config.get("base", 0x40013000)
        return (
            f"/* SPI driver — {n} @ 0x{b:08X} */\n"
            f"#include \"board.h\"\n#include <stdint.h>\n\n"
            f"#define {N}_BASE  (0x{b:08X}UL)\n"
            f"#define {N}_CR1   (*(volatile uint32_t *)({N}_BASE + 0x00))\n"
            f"#define {N}_SR    (*(volatile uint32_t *)({N}_BASE + 0x08))\n"
            f"#define {N}_DR    (*(volatile uint32_t *)({N}_BASE + 0x0C))\n\n"
            f"void {n}_init(uint32_t prescaler) {{\n"
            f"    {N}_CR1 = (prescaler<<3)|(1<<2)|(1<<6);\n}}\n\n"
            f"uint8_t {n}_transfer(uint8_t tx) {{\n"
            f"    while (!({N}_SR & (1<<1))) {{}}\n"
            f"    {N}_DR = tx;\n"
            f"    while (!({N}_SR & (1<<0))) {{}}\n"
            f"    return (uint8_t){N}_DR;\n}}\n\n"
            f"void {n}_cs_select(void) {{ /* drive CS low */ }}\n"
            f"void {n}_cs_deselect(void) {{ /* drive CS high */ }}\n"
        )

    def generate_i2c_driver(self, config: dict) -> str:
        n = config.get("name", "i2c0")
        N = n.upper()
        b = config.get("base", 0x40005400)
        return (
            f"/* I2C driver — {n} @ 0x{b:08X} */\n"
            f"#include \"board.h\"\n#include <stdint.h>\n\n"
            f"#define {N}_BASE  (0x{b:08X}UL)\n"
            f"#define {N}_CR1   (*(volatile uint32_t *)({N}_BASE + 0x00))\n"
            f"#define {N}_DR    (*(volatile uint32_t *)({N}_BASE + 0x10))\n"
            f"#define {N}_SR1   (*(volatile uint32_t *)({N}_BASE + 0x14))\n"
            f"#define {N}_SR2   (*(volatile uint32_t *)({N}_BASE + 0x18))\n"
            f"#define {N}_CCR   (*(volatile uint32_t *)({N}_BASE + 0x1C))\n\n"
            f"void {n}_init(uint32_t speed_hz) {{\n"
            f"    {N}_CCR = SYSTEM_CLOCK_HZ / (2 * speed_hz);\n"
            f"    {N}_CR1 = (1<<0);\n}}\n\n"
            f"int {n}_write(uint8_t addr, const uint8_t *data, uint32_t len) {{\n"
            f"    {N}_CR1 |= (1<<8);\n"
            f"    while (!({N}_SR1 & (1<<0))) {{}}\n"
            f"    {N}_DR = (addr<<1);\n"
            f"    while (!({N}_SR1 & (1<<1))) {{}}\n"
            f"    (void){N}_SR2;\n"
            f"    for (uint32_t i = 0; i < len; i++) {{\n"
            f"        while (!({N}_SR1 & (1<<7))) {{}}\n"
            f"        {N}_DR = data[i];\n    }}\n"
            f"    while (!({N}_SR1 & (1<<2))) {{}}\n"
            f"    {N}_CR1 |= (1<<9);\n    return 0;\n}}\n\n"
            f"int {n}_read(uint8_t addr, uint8_t *buf, uint32_t len) {{\n"
            f"    {N}_CR1 |= (1<<10)|(1<<8);\n"
            f"    while (!({N}_SR1 & (1<<0))) {{}}\n"
            f"    {N}_DR = (addr<<1)|1;\n"
            f"    while (!({N}_SR1 & (1<<1))) {{}}\n"
            f"    (void){N}_SR2;\n"
            f"    for (uint32_t i = 0; i < len; i++) {{\n"
            f"        if (i == len-1) {N}_CR1 &= ~(1<<10);\n"
            f"        while (!({N}_SR1 & (1<<6))) {{}}\n"
            f"        buf[i] = (uint8_t){N}_DR;\n    }}\n"
            f"    {N}_CR1 |= (1<<9);\n    return 0;\n}}\n\n"
            f"int {n}_scan(uint8_t *found, uint32_t max) {{\n"
            f"    uint32_t cnt = 0;\n"
            f"    for (uint8_t a = 1; a < 128 && cnt < max; a++) {{\n"
            f"        {N}_CR1 |= (1<<8);\n"
            f"        while (!({N}_SR1 & (1<<0))) {{}}\n"
            f"        {N}_DR = (a<<1);\n"
            f"        volatile uint32_t t = 10000;\n"
            f"        while (t-- && !({N}_SR1 & ((1<<1)|(1<<10)))) {{}}\n"
            f"        if ({N}_SR1 & (1<<1)) {{ (void){N}_SR2; found[cnt++] = a; }}\n"
            f"        {N}_CR1 |= (1<<9);\n    }}\n"
            f"    return (int)cnt;\n}}\n"
        )

    def generate_gpio_driver(self, config: dict) -> str:
        n = config.get("name", "gpio0")
        N = n.upper()
        b = config.get("base", 0x40020000)
        return (
            f"/* GPIO driver — {n} @ 0x{b:08X} */\n"
            f"#include \"board.h\"\n#include <stdint.h>\n\n"
            f"#define {N}_BASE   (0x{b:08X}UL)\n"
            f"#define {N}_MODER  (*(volatile uint32_t *)({N}_BASE + 0x00))\n"
            f"#define {N}_ODR    (*(volatile uint32_t *)({N}_BASE + 0x14))\n"
            f"#define {N}_IDR    (*(volatile uint32_t *)({N}_BASE + 0x10))\n"
            f"#define {N}_BSRR   (*(volatile uint32_t *)({N}_BASE + 0x18))\n\n"
            f"void {n}_init(uint32_t pin, uint32_t mode) {{\n"
            f"    {N}_MODER &= ~(0x3U << (pin*2));\n"
            f"    {N}_MODER |= (mode << (pin*2));\n}}\n\n"
            f"void {n}_set(uint32_t pin) {{ {N}_BSRR = (1U << pin); }}\n"
            f"void {n}_clear(uint32_t pin) {{ {N}_BSRR = (1U << (pin+16)); }}\n"
            f"void {n}_toggle(uint32_t pin) {{ {N}_ODR ^= (1U << pin); }}\n"
            f"uint32_t {n}_read(uint32_t pin) {{ return ({N}_IDR >> pin) & 1U; }}\n"
            f"void {n}_isr(void) {{ /* EXTI handler */ }}\n"
        )

    def generate_adc_driver(self, config: dict) -> str:
        n = config.get("name", "adc0")
        N = n.upper()
        b = config.get("base", 0x40012000)
        return (
            f"/* ADC driver — {n} @ 0x{b:08X} */\n"
            f"#include \"board.h\"\n#include <stdint.h>\n\n"
            f"#define {N}_BASE  (0x{b:08X}UL)\n"
            f"#define {N}_SR    (*(volatile uint32_t *)({N}_BASE + 0x00))\n"
            f"#define {N}_CR2   (*(volatile uint32_t *)({N}_BASE + 0x08))\n"
            f"#define {N}_SQR3  (*(volatile uint32_t *)({N}_BASE + 0x34))\n"
            f"#define {N}_DR    (*(volatile uint32_t *)({N}_BASE + 0x4C))\n\n"
            f"void {n}_init(void) {{ {N}_CR2 |= (1<<0); }}\n\n"
            f"uint16_t {n}_read_channel(uint32_t ch) {{\n"
            f"    {N}_SQR3 = ch;\n"
            f"    {N}_CR2 |= (1<<30);\n"
            f"    while (!({N}_SR & (1<<1))) {{}}\n"
            f"    return (uint16_t){N}_DR;\n}}\n\n"
            f"void {n}_start_dma(uint16_t *buf, uint32_t len) {{\n"
            f"    (void)buf; (void)len;\n"
            f"    {N}_CR2 |= (1<<8)|(1<<9);\n}}\n"
        )

    def generate_pwm_driver(self, config: dict) -> str:
        n = config.get("name", "pwm0")
        N = n.upper()
        b = config.get("base", 0x40000000)
        return (
            f"/* PWM driver — {n} @ 0x{b:08X} */\n"
            f"#include \"board.h\"\n#include <stdint.h>\n\n"
            f"#define {N}_BASE  (0x{b:08X}UL)\n"
            f"#define {N}_CR1   (*(volatile uint32_t *)({N}_BASE + 0x00))\n"
            f"#define {N}_ARR   (*(volatile uint32_t *)({N}_BASE + 0x2C))\n"
            f"#define {N}_CCR1  (*(volatile uint32_t *)({N}_BASE + 0x34))\n"
            f"#define {N}_CCER  (*(volatile uint32_t *)({N}_BASE + 0x20))\n\n"
            f"void {n}_init(uint32_t freq_hz) {{\n"
            f"    {N}_ARR = SYSTEM_CLOCK_HZ / freq_hz - 1;\n"
            f"    {N}_CCER |= (1<<0);\n"
            f"    {N}_CR1 |= (1<<0);\n}}\n\n"
            f"void {n}_set_duty(uint32_t duty_pct) {{\n"
            f"    {N}_CCR1 = ({N}_ARR + 1) * duty_pct / 100;\n}}\n\n"
            f"void {n}_set_frequency(uint32_t freq_hz) {{\n"
            f"    {N}_ARR = SYSTEM_CLOCK_HZ / freq_hz - 1;\n}}\n"
        )

    def generate_timer_driver(self, config: dict) -> str:
        n = config.get("name", "timer0")
        N = n.upper()
        b = config.get("base", 0x40000400)
        return (
            f"/* Timer driver — {n} @ 0x{b:08X} */\n"
            f"#include \"board.h\"\n#include <stdint.h>\n\n"
            f"#define {N}_BASE  (0x{b:08X}UL)\n"
            f"#define {N}_CR1   (*(volatile uint32_t *)({N}_BASE + 0x00))\n"
            f"#define {N}_DIER  (*(volatile uint32_t *)({N}_BASE + 0x0C))\n"
            f"#define {N}_SR    (*(volatile uint32_t *)({N}_BASE + 0x10))\n"
            f"#define {N}_PSC   (*(volatile uint32_t *)({N}_BASE + 0x28))\n"
            f"#define {N}_ARR   (*(volatile uint32_t *)({N}_BASE + 0x2C))\n\n"
            f"void {n}_init(uint32_t period_us) {{\n"
            f"    {N}_PSC = (SYSTEM_CLOCK_HZ / 1000000) - 1;\n"
            f"    {N}_ARR = period_us - 1;\n"
            f"    {N}_DIER |= (1<<0);\n}}\n\n"
            f"void {n}_start(void) {{ {N}_CR1 |= (1<<0); }}\n"
            f"void {n}_stop(void)  {{ {N}_CR1 &= ~(1<<0); }}\n\n"
            f"void {n}_isr(void) {{\n"
            f"    if ({N}_SR & (1<<0)) {{\n"
            f"        {N}_SR &= ~(1<<0);\n"
            f"        /* timer overflow callback */\n    }}\n}}\n"
        )

    def generate_can_driver(self, config: dict) -> str:
        n = config.get("name", "can0")
        N = n.upper()
        b = config.get("base", 0x40006400)
        return (
            f"/* CAN driver — {n} @ 0x{b:08X} */\n"
            f"#include \"board.h\"\n#include <stdint.h>\n\n"
            f"#define {N}_BASE  (0x{b:08X}UL)\n"
            f"#define {N}_MCR   (*(volatile uint32_t *)({N}_BASE + 0x00))\n"
            f"#define {N}_MSR   (*(volatile uint32_t *)({N}_BASE + 0x04))\n"
            f"#define {N}_BTR   (*(volatile uint32_t *)({N}_BASE + 0x1C))\n\n"
            f"typedef struct {{ uint32_t id; uint8_t data[8]; uint8_t len; }} {n}_msg_t;\n\n"
            f"void {n}_init(uint32_t bitrate) {{\n"
            f"    {N}_MCR |= (1<<0);\n"
            f"    while (!({N}_MSR & (1<<0))) {{}}\n"
            f"    {N}_BTR = (SYSTEM_CLOCK_HZ / bitrate / 12 - 1)\n"
            f"            | (3<<20) | (4<<16);\n"
            f"    {N}_MCR &= ~(1<<0);\n}}\n\n"
            f"int {n}_send({n}_msg_t *msg) {{\n"
            f"    (void)msg; /* write to TX mailbox */ return 0;\n}}\n\n"
            f"int {n}_receive({n}_msg_t *msg) {{\n"
            f"    (void)msg; /* read from RX FIFO */ return 0;\n}}\n\n"
            f"void {n}_filter_setup(uint32_t id, uint32_t mask) {{\n"
            f"    (void)id; (void)mask; /* configure filter bank */\n}}\n"
        )

    def generate_ethernet_driver(self, config: dict) -> str:
        n = config.get("name", "eth0")
        N = n.upper()
        b = config.get("base", 0x40028000)
        return (
            f"/* Ethernet driver — {n} @ 0x{b:08X} */\n"
            f"#include \"board.h\"\n#include <stdint.h>\n#include <string.h>\n\n"
            f"#define {N}_BASE    (0x{b:08X}UL)\n"
            f"#define {N}_MACCR   (*(volatile uint32_t *)({N}_BASE + 0x00))\n"
            f"#define {N}_MACADDR (*(volatile uint32_t *)({N}_BASE + 0x40))\n\n"
            f"static uint8_t mac_addr[6] = {{0x02,0x00,0x00,0x00,0x00,0x01}};\n\n"
            f"void {n}_init(void) {{\n"
            f"    {N}_MACCR |= (1<<3)|(1<<2);\n}}\n\n"
            f"void {n}_set_mac(const uint8_t mac[6]) {{\n"
            f"    memcpy(mac_addr, mac, 6);\n}}\n\n"
            f"int {n}_send(const uint8_t *data, uint32_t len) {{\n"
            f"    (void)data; (void)len; /* DMA TX descriptor */ return 0;\n}}\n\n"
            f"int {n}_receive(uint8_t *buf, uint32_t max_len) {{\n"
            f"    (void)buf; (void)max_len; /* DMA RX descriptor */ return 0;\n}}\n"
        )

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------

    @staticmethod
    def generate_linker_script(memory_map: dict) -> str:
        """Generate a linker script for ARM Cortex-M from a memory map.

        Args:
            memory_map: ``{region_name: (base_addr, size)}``
        """
        lines = ["/* Linker script — auto-generated by EoStudio */", "MEMORY", "{"]
        for name, (base, size) in memory_map.items():
            n = name.upper().replace(" ", "_")
            attr = "rx" if "flash" in name.lower() else "rwx"
            lines.append(f"    {n} ({attr}) : ORIGIN = 0x{base:08X}, LENGTH = 0x{size:08X}")
        lines += ["}", "", "SECTIONS", "{"]

        flash_name = next((n.upper().replace(" ", "_") for n in memory_map if "flash" in n.lower()), "FLASH")
        sram_name = next((n.upper().replace(" ", "_") for n in memory_map if "sram" in n.lower() or "ram" in n.lower()), "SRAM")

        lines += [
            f"    .isr_vector : {{ KEEP(*(.isr_vector)) }} > {flash_name}",
            f"    .text : {{ *(.text*) *(.rodata*) }} > {flash_name}",
            f"    .data : {{ _sdata = .; *(.data*) _edata = .; }} > {sram_name} AT> {flash_name}",
            f"    .bss (NOLOAD) : {{ _sbss = .; *(.bss*) *(COMMON) _ebss = .; }} > {sram_name}",
            f"    _estack = ORIGIN({sram_name}) + LENGTH({sram_name});",
            "}", "",
        ]
        return "\n".join(lines)

    @staticmethod
    def generate_startup(arch: str, vector_table_size: int = 128) -> str:
        """Generate assembly startup code for ARM or RISC-V."""
        if "riscv" in arch.lower():
            return (
                "/* RISC-V startup — auto-generated by EoStudio */\n"
                ".section .init, \"ax\"\n.global _start\n_start:\n"
                "    la sp, _estack\n"
                "    call SystemInit\n"
                "    call main\n"
                "1:  j 1b\n"
            )
        # ARM Cortex-M
        lines = [
            "/* ARM Cortex-M startup — auto-generated by EoStudio */",
            ".syntax unified", ".cpu cortex-m4", ".thumb", "",
            ".section .isr_vector, \"a\"",
            ".word _estack",
            ".word Reset_Handler",
        ]
        for i in range(2, min(vector_table_size, 256)):
            lines.append(f".word Default_Handler  /* IRQ {i - 2} */")
        lines += [
            "", ".section .text", ".thumb_func", ".global Reset_Handler",
            "Reset_Handler:",
            "    ldr r0, =_sdata", "    ldr r1, =_edata", "    ldr r2, =_sidata",
            "copy_loop:", "    cmp r0, r1", "    bge zero_bss",
            "    ldr r3, [r2], #4", "    str r3, [r0], #4", "    b copy_loop",
            "zero_bss:", "    ldr r0, =_sbss", "    ldr r1, =_ebss",
            "    movs r2, #0",
            "bss_loop:", "    cmp r0, r1", "    bge call_main",
            "    str r2, [r0], #4", "    b bss_loop",
            "call_main:", "    bl SystemInit", "    bl main", "    b .",
            "", ".thumb_func", ".weak Default_Handler",
            "Default_Handler:", "    b .", "",
        ]
        return "\n".join(lines)

    @staticmethod
    def generate_makefile(sources: List[str], includes: List[str], toolchain: str = "arm-none-eabi-") -> str:
        inc_flags = " ".join(f"-I{d}" for d in includes)
        src_str = " \\\n    ".join(sources)
        return textwrap.dedent(f"""\
            # Makefile — auto-generated by EoStudio
            CC      = {toolchain}gcc
            AS      = {toolchain}as
            LD      = {toolchain}ld
            OBJCOPY = {toolchain}objcopy
            SIZE    = {toolchain}size

            CFLAGS  = -mcpu=cortex-m4 -mthumb -O2 -g -Wall -Wextra {inc_flags}
            LDFLAGS = -T linker.ld -nostartfiles -Wl,--gc-sections

            SRCS = {src_str}
            OBJS = $(SRCS:.c=.o)
            TARGET = firmware

            all: $(TARGET).elf $(TARGET).bin
            \t@$(SIZE) $(TARGET).elf

            $(TARGET).elf: $(OBJS)
            \t$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $^

            $(TARGET).bin: $(TARGET).elf
            \t$(OBJCOPY) -O binary $< $@

            %.o: %.c
            \t$(CC) $(CFLAGS) -c -o $@ $<

            clean:
            \trm -f $(OBJS) $(TARGET).elf $(TARGET).bin

            flash: $(TARGET).bin
            \topenocd -f openocd.cfg -c "program $(TARGET).elf verify reset exit"

            .PHONY: all clean flash
        """)

    @staticmethod
    def generate_cmake(sources: List[str], includes: List[str], toolchain: str = "arm-none-eabi-") -> str:
        src_list = "\n    ".join(sources)
        inc_list = "\n    ".join(includes)
        return textwrap.dedent(f"""\
            # CMakeLists.txt — auto-generated by EoStudio
            cmake_minimum_required(VERSION 3.20)
            set(CMAKE_SYSTEM_NAME Generic)
            set(CMAKE_C_COMPILER {toolchain}gcc)
            set(CMAKE_ASM_COMPILER {toolchain}gcc)

            project(firmware C ASM)

            set(SOURCES
                {src_list}
            )

            add_executable(${{PROJECT_NAME}}.elf ${{SOURCES}})

            target_include_directories(${{PROJECT_NAME}}.elf PRIVATE
                {inc_list}
            )

            target_compile_options(${{PROJECT_NAME}}.elf PRIVATE
                -mcpu=cortex-m4 -mthumb -O2 -g -Wall -Wextra
            )

            target_link_options(${{PROJECT_NAME}}.elf PRIVATE
                -T ${{CMAKE_SOURCE_DIR}}/linker.ld -nostartfiles -Wl,--gc-sections
            )

            add_custom_command(TARGET ${{PROJECT_NAME}}.elf POST_BUILD
                COMMAND ${{CMAKE_OBJCOPY}} -O binary ${{PROJECT_NAME}}.elf ${{PROJECT_NAME}}.bin
                COMMENT "Generating binary"
            )
        """)

    @staticmethod
    def generate_openocd_cfg(target: str, interface: str = "stlink") -> str:
        """Generate an OpenOCD configuration file."""
        _TARGETS = {
            "stm32f4": ("stm32f4x", "hla_swd"),
            "stm32h7": ("stm32h7x", "hla_swd"),
            "nrf52": ("nrf52", "cmsis-dap"),
            "rp2040": ("rp2040", "cmsis-dap"),
            "esp32": ("esp32", "esp_usb_jtag"),
        }
        chip, default_transport = _TARGETS.get(target, (target, "hla_swd"))
        return textwrap.dedent(f"""\
            # OpenOCD config — auto-generated by EoStudio
            source [find interface/{interface}.cfg]
            transport select {default_transport}
            source [find target/{chip}.cfg]
            adapter speed 4000
            init
            reset halt
        """)
