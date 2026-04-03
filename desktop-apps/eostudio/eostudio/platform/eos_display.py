"""
EoS Display — Python ctypes bindings to libeos_display shared library.

Provides EosFrameBuffer class for direct framebuffer access from Python,
enabling EoStudio to render its GUI via the EoS display HAL.
"""

import ctypes
import ctypes.util
import os
import sys
from pathlib import Path
from typing import Optional


class EosDisplayError(Exception):
    """Raised when an EoS display operation fails."""
    pass


class EosFrameBuffer:
    """Framebuffer surface backed by EoS HAL display via ctypes."""

    def __init__(self, width: int = 800, height: int = 480,
                 display_id: int = 0, backend: str = "auto"):
        self.width = width
        self.height = height
        self.display_id = display_id
        self._lib: Optional[ctypes.CDLL] = None
        self._initialized = False
        self._backend = backend

    def _find_library(self) -> str:
        """Locate the libeos_display shared library."""
        search_paths = [
            os.environ.get("EOS_LIB_PATH", ""),
            str(Path(__file__).parent.parent.parent.parent / "eos" / "build" / "lib"),
            str(Path(__file__).parent.parent.parent.parent / "eos" / "build"),
            "/usr/local/lib",
            "/usr/lib",
        ]

        if sys.platform == "win32":
            lib_name = "eos_display.dll"
        elif sys.platform == "darwin":
            lib_name = "libeos_display.dylib"
        else:
            lib_name = "libeos_display.so"

        for path in search_paths:
            if not path:
                continue
            full = os.path.join(path, lib_name)
            if os.path.exists(full):
                return full

        found = ctypes.util.find_library("eos_display")
        if found:
            return found

        raise EosDisplayError(
            f"Cannot find {lib_name}. Set EOS_LIB_PATH or build the library."
        )

    def _load_library(self):
        """Load the shared library and set up function prototypes."""
        lib_path = self._find_library()
        self._lib = ctypes.CDLL(lib_path)

        # Backend setup functions
        if hasattr(self._lib, "eos_display_setup_sdl2_backend"):
            self._lib.eos_display_setup_sdl2_backend.restype = ctypes.c_int
            self._lib.eos_display_setup_sdl2_backend.argtypes = []

        if hasattr(self._lib, "eos_display_setup_linux_backend"):
            self._lib.eos_display_setup_linux_backend.restype = ctypes.c_int
            self._lib.eos_display_setup_linux_backend.argtypes = []

        # Display API
        self._lib.eos_display_init.restype = ctypes.c_int
        self._lib.eos_display_deinit.restype = None
        self._lib.eos_display_deinit.argtypes = [ctypes.c_uint8]

        self._lib.eos_display_draw_pixel.restype = ctypes.c_int
        self._lib.eos_display_draw_pixel.argtypes = [
            ctypes.c_uint8, ctypes.c_uint16, ctypes.c_uint16, ctypes.c_uint32
        ]

        self._lib.eos_display_draw_rect.restype = ctypes.c_int
        self._lib.eos_display_draw_rect.argtypes = [
            ctypes.c_uint8, ctypes.c_uint16, ctypes.c_uint16,
            ctypes.c_uint16, ctypes.c_uint16, ctypes.c_uint32
        ]

        self._lib.eos_display_draw_bitmap.restype = ctypes.c_int
        self._lib.eos_display_draw_bitmap.argtypes = [
            ctypes.c_uint8, ctypes.c_uint16, ctypes.c_uint16,
            ctypes.c_uint16, ctypes.c_uint16, ctypes.POINTER(ctypes.c_uint8)
        ]

        self._lib.eos_display_flush.restype = ctypes.c_int
        self._lib.eos_display_flush.argtypes = [ctypes.c_uint8]

        self._lib.eos_display_clear.restype = ctypes.c_int
        self._lib.eos_display_clear.argtypes = [ctypes.c_uint8, ctypes.c_uint32]

        self._lib.eos_display_set_brightness.restype = ctypes.c_int
        self._lib.eos_display_set_brightness.argtypes = [
            ctypes.c_uint8, ctypes.c_uint8
        ]

    def init(self):
        """Initialize the display backend and framebuffer."""
        if self._initialized:
            return

        self._load_library()

        # Register backend
        if self._backend == "sdl2" or (
            self._backend == "auto"
            and os.environ.get("EOS_DISPLAY", "").lower() == "sdl2"
        ):
            if hasattr(self._lib, "eos_display_setup_sdl2_backend"):
                rc = self._lib.eos_display_setup_sdl2_backend()
                if rc != 0:
                    raise EosDisplayError("Failed to register SDL2 backend")
        elif self._backend == "linux" or (
            self._backend == "auto" and os.path.exists("/dev/fb0")
        ):
            if hasattr(self._lib, "eos_display_setup_linux_backend"):
                rc = self._lib.eos_display_setup_linux_backend()
                if rc != 0:
                    raise EosDisplayError("Failed to register Linux FB backend")

        # Initialize display
        class DisplayConfig(ctypes.Structure):
            _fields_ = [
                ("id", ctypes.c_uint8),
                ("width", ctypes.c_uint16),
                ("height", ctypes.c_uint16),
                ("color_mode", ctypes.c_int),
            ]

        cfg = DisplayConfig(
            id=self.display_id,
            width=self.width,
            height=self.height,
            color_mode=2,  # EOS_DISPLAY_COLOR_RGB888
        )

        rc = self._lib.eos_display_init(ctypes.byref(cfg))
        if rc != 0:
            raise EosDisplayError(f"eos_display_init failed: {rc}")

        self._initialized = True

    def deinit(self):
        """Shut down the display."""
        if self._initialized and self._lib:
            self._lib.eos_display_deinit(self.display_id)
            self._initialized = False

    def draw_pixel(self, x: int, y: int, color: int) -> int:
        if not self._initialized:
            return -1
        return int(self._lib.eos_display_draw_pixel(self.display_id, x, y, color))

    def draw_rect(self, x: int, y: int, w: int, h: int, color: int) -> int:
        if not self._initialized:
            return -1
        return int(self._lib.eos_display_draw_rect(
            self.display_id, x, y, w, h, color
        ))

    def draw_bitmap(self, x: int, y: int, w: int, h: int,
                    data: bytes) -> int:
        if not self._initialized:
            return -1
        buf = (ctypes.c_uint8 * len(data)).from_buffer_copy(data)
        return int(self._lib.eos_display_draw_bitmap(
            self.display_id, x, y, w, h, buf
        ))

    def flush(self) -> int:
        if not self._initialized:
            return -1
        return int(self._lib.eos_display_flush(self.display_id))

    def clear(self, color: int = 0) -> int:
        if not self._initialized:
            return -1
        return int(self._lib.eos_display_clear(self.display_id, color))

    def set_brightness(self, pct: int) -> int:
        if not self._initialized:
            return -1
        return int(self._lib.eos_display_set_brightness(self.display_id, pct))

    def __del__(self):
        self.deinit()
