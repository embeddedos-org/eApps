#!/usr/bin/env bash
# eBrowser — Zero-Prerequisite Setup Script (Linux / macOS)
# Usage: ./setup.sh [URL]
# Example: ./setup.sh https://google.com

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
URL="${1:-}"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log()  { echo -e "${GREEN}[eBrowser]${NC} $1"; }
warn() { echo -e "${YELLOW}[eBrowser]${NC} $1"; }
fail() { echo -e "${RED}[eBrowser]${NC} $1"; exit 1; }

# --- Detect OS ---
OS="$(uname -s)"
ARCH="$(uname -m)"
log "Detected: $OS $ARCH"

# --- Detect package manager ---
detect_pkg_manager() {
    if command -v apt-get &>/dev/null; then echo "apt"
    elif command -v dnf &>/dev/null; then echo "dnf"
    elif command -v yum &>/dev/null; then echo "yum"
    elif command -v pacman &>/dev/null; then echo "pacman"
    elif command -v zypper &>/dev/null; then echo "zypper"
    elif command -v apk &>/dev/null; then echo "apk"
    elif command -v brew &>/dev/null; then echo "brew"
    else echo "unknown"
    fi
}

install_macos() {
    if ! command -v brew &>/dev/null; then
        log "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi

    if ! command -v cmake &>/dev/null; then
        log "Installing CMake..."
        brew install cmake
    fi

    if ! command -v gcc &>/dev/null && ! command -v clang &>/dev/null; then
        log "Installing Xcode Command Line Tools..."
        xcode-select --install 2>/dev/null || true
    fi

    if ! brew list sdl2 &>/dev/null; then
        log "Installing SDL2..."
        brew install sdl2
    fi
}

install_linux() {
    local PKG="$(detect_pkg_manager)"
    log "Package manager: $PKG"

    case "$PKG" in
        apt)
            log "Installing dependencies via apt..."
            sudo apt-get update -qq
            sudo apt-get install -y -qq cmake gcc g++ libsdl2-dev git
            ;;
        dnf)
            log "Installing dependencies via dnf..."
            sudo dnf install -y cmake gcc gcc-c++ SDL2-devel git
            ;;
        yum)
            log "Installing dependencies via yum..."
            sudo yum install -y cmake gcc gcc-c++ SDL2-devel git
            ;;
        pacman)
            log "Installing dependencies via pacman..."
            sudo pacman -Sy --noconfirm cmake gcc sdl2 git make
            ;;
        zypper)
            log "Installing dependencies via zypper..."
            sudo zypper install -y cmake gcc gcc-c++ libSDL2-devel git
            ;;
        apk)
            log "Installing dependencies via apk..."
            sudo apk add cmake gcc g++ sdl2-dev git make musl-dev
            ;;
        brew)
            install_macos
            ;;
        *)
            fail "Unknown package manager. Please install cmake, gcc, and libsdl2-dev manually."
            ;;
    esac
}

# --- Install dependencies ---
log "Checking dependencies..."

NEED_INSTALL=false
command -v cmake &>/dev/null || NEED_INSTALL=true
command -v gcc &>/dev/null || command -v cc &>/dev/null || command -v clang &>/dev/null || NEED_INSTALL=true

if [ "$NEED_INSTALL" = true ]; then
    log "Some dependencies missing — installing..."
    if [ "$OS" = "Darwin" ]; then
        install_macos
    else
        install_linux
    fi
else
    # Still check SDL2
    if [ "$OS" = "Darwin" ]; then
        if ! brew list sdl2 &>/dev/null 2>&1; then
            log "Installing SDL2..."
            brew install sdl2
        fi
    else
        PKG="$(detect_pkg_manager)"
        case "$PKG" in
            apt)
                dpkg -s libsdl2-dev &>/dev/null 2>&1 || { log "Installing SDL2..."; sudo apt-get install -y -qq libsdl2-dev; }
                ;;
            dnf|yum)
                rpm -q SDL2-devel &>/dev/null 2>&1 || { log "Installing SDL2..."; sudo $PKG install -y SDL2-devel; }
                ;;
            pacman)
                pacman -Qi sdl2 &>/dev/null 2>&1 || { log "Installing SDL2..."; sudo pacman -Sy --noconfirm sdl2; }
                ;;
        esac
    fi
fi

log "All dependencies satisfied ✓"

# --- Initialize LVGL submodule if needed ---
if [ ! -f "$SCRIPT_DIR/extern/lvgl/CMakeLists.txt" ]; then
    if [ -f "$SCRIPT_DIR/.gitmodules" ]; then
        log "Initializing LVGL submodule..."
        cd "$SCRIPT_DIR" && git submodule update --init --recursive
    else
        log "LVGL will be auto-downloaded by CMake FetchContent..."
    fi
fi

# --- Build ---
log "Configuring build..."
cd "$SCRIPT_DIR"
cmake -B build -DeBrowser_BUILD_STANDALONE=ON -DBUILD_TESTING=ON 2>&1 | tail -5

log "Building eBrowser (this may take a minute on first build)..."
cmake --build build --parallel "$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)" 2>&1 | tail -5

if [ ! -f build/port/eBrowser ]; then
    fail "Build failed — eBrowser binary not found"
fi

log "Build successful ✓"

# --- Run tests ---
log "Running tests..."
cd build
ctest --output-on-failure 2>&1 | tail -3
cd "$SCRIPT_DIR"

# --- Launch ---
log "Launching eBrowser..."
if [ -n "$URL" ]; then
    exec build/port/eBrowser "$URL"
else
    exec build/port/eBrowser
fi
