#!/usr/bin/env bash
# Build eApps Suite installers for the current platform.
# Usage: ./scripts/build-installers.sh [linux|windows|macos|all]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="${ROOT_DIR}/build-installer"

platform="${1:-auto}"

echo "═══════════════════════════════════════════"
echo "  eApps Suite Installer Builder"
echo "═══════════════════════════════════════════"

# Detect platform if auto
if [ "$platform" = "auto" ]; then
    case "$(uname -s)" in
        Linux*)  platform="linux" ;;
        Darwin*) platform="macos" ;;
        MINGW*|MSYS*|CYGWIN*) platform="windows" ;;
        *) echo "Unknown platform: $(uname -s)"; exit 1 ;;
    esac
    echo "Detected platform: $platform"
fi

# Configure
echo ""
echo "── Configuring ──"
cmake -B "$BUILD_DIR" -S "$ROOT_DIR" \
    -DCMAKE_BUILD_TYPE=Release \
    -DEAPPS_BUILD_SUITE=ON

# Build
echo ""
echo "── Building ──"
cmake --build "$BUILD_DIR" --parallel

# Package
echo ""
echo "── Packaging ──"
cd "$BUILD_DIR"

case "$platform" in
    linux)
        echo "Building DEB..."
        cpack -G DEB
        echo "Building RPM..."
        cpack -G RPM 2>/dev/null || echo "(RPM skipped — rpmbuild not found)"
        ;;
    macos)
        echo "Building DMG..."
        cpack -G DragNDrop
        ;;
    windows)
        echo "Building NSIS..."
        cpack -G NSIS
        ;;
    all)
        echo "Building all available generators..."
        cpack -G DEB 2>/dev/null || echo "(DEB skipped)"
        cpack -G RPM 2>/dev/null || echo "(RPM skipped)"
        cpack -G DragNDrop 2>/dev/null || echo "(DMG skipped)"
        cpack -G NSIS 2>/dev/null || echo "(NSIS skipped)"
        ;;
    *)
        echo "Unknown platform: $platform"
        echo "Usage: $0 [linux|windows|macos|all]"
        exit 1
        ;;
esac

# Summary
echo ""
echo "═══════════════════════════════════════════"
echo "  Installers created in: $BUILD_DIR"
echo "═══════════════════════════════════════════"
ls -lh *.deb *.rpm *.dmg *.exe 2>/dev/null || echo "(no installer files found)"
