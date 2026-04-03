@echo off
REM eBrowser — Zero-Prerequisite Setup Script (Windows)
REM Usage: setup.bat [URL]
REM Example: setup.bat https://google.com

setlocal enabledelayedexpansion
set "SCRIPT_DIR=%~dp0"
set "URL=%~1"
set "MINGW=C:\msys64\mingw64\bin"

echo [eBrowser] Starting eBrowser zero-prerequisite setup...

REM --- Check for MSYS2 ---
if not exist "C:\msys64\usr\bin\bash.exe" (
    echo [eBrowser] MSYS2 not found — installing via winget...
    where winget >nul 2>&1
    if errorlevel 1 (
        echo [eBrowser] ERROR: winget not found. Please install MSYS2 manually from https://www.msys2.org/
        exit /b 1
    )
    winget install MSYS2.MSYS2 --accept-package-agreements --accept-source-agreements --silent
    if errorlevel 1 (
        echo [eBrowser] MSYS2 may already be installed or needs admin. Checking...
        if not exist "C:\msys64\usr\bin\bash.exe" (
            echo [eBrowser] ERROR: MSYS2 installation failed. Install manually from https://www.msys2.org/
            exit /b 1
        )
    )
)
echo [eBrowser] MSYS2 found at C:\msys64 ✓

REM --- Install GCC, CMake, SDL2, Make via pacman ---
echo [eBrowser] Checking MinGW toolchain...
if not exist "%MINGW%\gcc.exe" (
    echo [eBrowser] Installing GCC, CMake, SDL2, Make...
    C:\msys64\usr\bin\bash.exe -lc "pacman -S --noconfirm --needed mingw-w64-x86_64-gcc mingw-w64-x86_64-cmake mingw-w64-x86_64-SDL2 mingw-w64-x86_64-make"
) else (
    echo [eBrowser] GCC found ✓
    REM Still ensure SDL2 and cmake are present
    if not exist "%MINGW%\sdl2-config.exe" (
        if not exist "%MINGW%\lib\libSDL2.a" (
            echo [eBrowser] Installing SDL2...
            C:\msys64\usr\bin\bash.exe -lc "pacman -S --noconfirm --needed mingw-w64-x86_64-SDL2"
        )
    )
    if not exist "%MINGW%\cmake.exe" (
        echo [eBrowser] Installing CMake...
        C:\msys64\usr\bin\bash.exe -lc "pacman -S --noconfirm --needed mingw-w64-x86_64-cmake"
    )
)

REM --- Verify toolchain ---
if not exist "%MINGW%\gcc.exe" (
    echo [eBrowser] ERROR: GCC not found after installation.
    exit /b 1
)
echo [eBrowser] All dependencies satisfied ✓

REM --- Set PATH ---
set "PATH=%MINGW%;%PATH%"

REM --- Remove old build if corrupt ---
if exist "%SCRIPT_DIR%build\CMakeCache.txt" (
    findstr /C:"MinGW" "%SCRIPT_DIR%build\CMakeCache.txt" >nul 2>&1
    if errorlevel 1 (
        echo [eBrowser] Clearing incompatible build directory...
        rmdir /S /Q "%SCRIPT_DIR%build" 2>nul
    )
)

REM --- Configure ---
echo [eBrowser] Configuring build...
"%MINGW%\cmake.exe" -G "MinGW Makefiles" -B "%SCRIPT_DIR%build" -S "%SCRIPT_DIR%" -DeBrowser_BUILD_STANDALONE=ON -DBUILD_TESTING=ON
if errorlevel 1 (
    echo [eBrowser] ERROR: CMake configuration failed.
    exit /b 1
)

REM --- Build ---
echo [eBrowser] Building eBrowser (this may take a minute on first build)...
"%MINGW%\mingw32-make.exe" -C "%SCRIPT_DIR%build" -j4
if errorlevel 1 (
    echo [eBrowser] ERROR: Build failed.
    exit /b 1
)

echo [eBrowser] Build successful ✓

REM --- Find executable ---
set "EXE="
if exist "%SCRIPT_DIR%build\port\eBrowser.exe" set "EXE=%SCRIPT_DIR%build\port\eBrowser.exe"
if exist "%SCRIPT_DIR%build\eBrowser.exe" set "EXE=%SCRIPT_DIR%build\eBrowser.exe"

if "%EXE%"=="" (
    echo [eBrowser] ERROR: eBrowser.exe not found after build.
    exit /b 1
)

REM --- Run tests ---
echo [eBrowser] Running tests...
cd "%SCRIPT_DIR%build"
"%MINGW%\cmake.exe" --build . --target test 2>nul
cd "%SCRIPT_DIR%"

REM --- Launch ---
echo [eBrowser] Launching eBrowser...
if not "%URL%"=="" (
    start "" "%EXE%" "%URL%"
) else (
    start "" "%EXE%"
)
