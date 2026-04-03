cmake_minimum_required(VERSION 3.16)
project(eBrowser
    VERSION 0.1.0
    DESCRIPTION "eBrowser — lightweight web browser for embedded and IoT devices"
    LANGUAGES C
)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

# --- Feature flags ---
option(eBrowser_BUILD_ENGINE    "Build HTML/CSS/Layout engine"           ON)
option(eBrowser_BUILD_RENDER    "Build rendering backend"                ON)
option(eBrowser_BUILD_NETWORK   "Build HTTP/HTTPS network stack"        ON)
option(eBrowser_BUILD_INPUT     "Build input abstraction layer"         ON)
option(eBrowser_BUILD_BROWSER   "Build browser UI application"         ON)
option(eBrowser_BUILD_JS        "Build optional JavaScript engine"     OFF)
option(eBrowser_BUILD_SECURITY  "Build security and crypto layer"      ON)
option(eBrowser_BUILD_STANDALONE "Build standalone executable"          ON)

# --- Platform detection ---
if(CMAKE_TOOLCHAIN_FILE MATCHES "eos\\.cmake$")
    set(eBrowser_PLATFORM_EOS ON)
    add_definitions(-DeBrowser_PLATFORM_EOS=1)
elseif(EMSCRIPTEN)
    set(eBrowser_PLATFORM_WEB ON)
    add_definitions(-DeBrowser_PLATFORM_WEB=1)
else()
    set(eBrowser_PLATFORM_SDL2 ON)
    add_definitions(-DeBrowser_PLATFORM_SDL2=1)
endif()

# --- Compiler warnings ---
if(MSVC)
    add_compile_options(/W3)
    add_compile_definitions(_CRT_SECURE_NO_WARNINGS)
else()
    add_compile_options(-Wall -Wextra -Wno-unused-parameter)
endif()

# --- LVGL ---
set(LV_CONF_PATH "${CMAKE_CURRENT_SOURCE_DIR}/extern/lv_conf.h" CACHE STRING "" FORCE)
add_definitions(-DLV_CONF_INCLUDE_SIMPLE=1)
add_definitions(-DLV_USE_DRAW_SW_COMPLEX=0)
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/extern/lvgl/CMakeLists.txt")
    message(STATUS "Using LVGL from extern/lvgl/ submodule")
    set(LV_USE_DRAW_SW_ASM "none" CACHE STRING "" FORCE)
    add_subdirectory(extern/lvgl)
else()
    message(STATUS "LVGL submodule not found — auto-downloading via FetchContent...")
    include(FetchContent)
    FetchContent_Declare(lvgl
        GIT_REPOSITORY https://github.com/lvgl/lvgl.git
        GIT_TAG        release/v9.2
        GIT_SHALLOW    TRUE
    )
    set(LV_USE_DRAW_SW_ASM "none" CACHE STRING "" FORCE)
    FetchContent_MakeAvailable(lvgl)
endif()

# --- Core engine ---
if(eBrowser_BUILD_ENGINE)
    add_subdirectory(src/engine)
endif()

# --- Rendering backend ---
if(eBrowser_BUILD_RENDER)
    add_subdirectory(src/render)
endif()

# --- Network stack ---
if(eBrowser_BUILD_NETWORK)
    add_subdirectory(src/network)
endif()

# --- Input layer ---
if(eBrowser_BUILD_INPUT)
    add_subdirectory(src/input)
endif()

# --- Security & Crypto ---
if(eBrowser_BUILD_SECURITY)
    add_subdirectory(src/security)
endif()

# --- Telemetry ---
add_subdirectory(src/telemetry)

# --- Plugin System ---
add_subdirectory(src/plugin)

# --- Platform abstraction ---
add_subdirectory(platform)

# --- Browser UI ---
if(eBrowser_BUILD_BROWSER)
    add_subdirectory(src/browser)
endif()

# --- Port layer ---
add_subdirectory(port)

# --- Tests ---
if(BUILD_TESTING)
    enable_testing()
    add_subdirectory(tests)
endif()
