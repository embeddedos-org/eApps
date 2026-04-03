cmake_minimum_required(VERSION 3.14)
project(eapps
    VERSION 0.1.0
    DESCRIPTION "EoS Application Suite — productivity, media, games, networking tools"
    LANGUAGES C
)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

# --- Feature flags (all ON by default) ---
option(EAPPS_BUILD_PRODUCTIVITY "Build productivity apps (ecal, enote, econverter, etc.)" ON)
option(EAPPS_BUILD_MEDIA        "Build media apps (emusic, evideo, egallery, etc.)"       ON)
option(EAPPS_BUILD_GAMES        "Build game apps (snake, tetris, echess, etc.)"            ON)
option(EAPPS_BUILD_CONNECTIVITY "Build connectivity apps (eftp, essh, eserial, etc.)"     ON)
option(EAPPS_BUILD_SECURITY     "Build security apps (evpn, evirustower, eguard)"         ON)
option(EAPPS_BUILD_WEB          "Build web apps (eweb, echat)"                             ON)
option(EAPPS_BUILD_SUITE        "Build the suite launcher"                                 ON)
option(EAPPS_BUILD_STANDALONE   "Build standalone executables per app"                    OFF)

# --- Platform detection ---
if(CMAKE_TOOLCHAIN_FILE MATCHES "eos\\.cmake$")
    set(EAPPS_PLATFORM_EOS ON)
    add_definitions(-DEAPPS_PLATFORM_EOS=1)
elseif(EMSCRIPTEN)
    set(EAPPS_PLATFORM_WEB ON)
    add_definitions(-DEAPPS_PLATFORM_WEB=1)
else()
    set(EAPPS_PLATFORM_SDL2 ON)
    add_definitions(-DEAPPS_PLATFORM_SDL2=1)
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
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/extern/lvgl/CMakeLists.txt")
    add_subdirectory(extern/lvgl)
else()
    message(STATUS "LVGL submodule not found — using stub target")
    add_library(lvgl INTERFACE)
    target_include_directories(lvgl INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/extern)
endif()

# --- Core libraries ---
add_subdirectory(core/common)
add_subdirectory(core/ui)
add_subdirectory(core/storage)
add_subdirectory(core/network)
add_subdirectory(core/platform)

# --- Port layer ---
add_subdirectory(port)

# --- Apps ---
if(EAPPS_BUILD_PRODUCTIVITY)
    add_subdirectory(apps/ecal)
    add_subdirectory(apps/enote)
    add_subdirectory(apps/econverter)
    add_subdirectory(apps/ebuffer)
    add_subdirectory(apps/efiles)
    add_subdirectory(apps/ecleaner)
    add_subdirectory(apps/eclock)
    add_subdirectory(apps/etools)
    add_subdirectory(apps/etimer)
    add_subdirectory(apps/epdf)
    add_subdirectory(apps/ezip)
    add_subdirectory(apps/eviewer)
    add_subdirectory(apps/esession)
endif()

if(EAPPS_BUILD_MEDIA)
    add_subdirectory(apps/emusic)
    add_subdirectory(apps/evideo)
    add_subdirectory(apps/egallery)
    add_subdirectory(apps/eplay)
    add_subdirectory(apps/epaint)
endif()

if(EAPPS_BUILD_GAMES)
    add_subdirectory(apps/snake)
    add_subdirectory(apps/tetris)
    add_subdirectory(apps/minesweeper)
    add_subdirectory(apps/dice)
    add_subdirectory(apps/erunner)
    add_subdirectory(apps/esurfer)
    add_subdirectory(apps/echess)
    add_subdirectory(apps/ebirds)
    add_subdirectory(apps/eslice)
    add_subdirectory(apps/eblocks)
    add_subdirectory(apps/ecrush)
endif()

if(EAPPS_BUILD_CONNECTIVITY)
    add_subdirectory(apps/eftp)
    add_subdirectory(apps/eserial)
    add_subdirectory(apps/essh)
    add_subdirectory(apps/evnc)
    add_subdirectory(apps/etunnel)
    add_subdirectory(apps/echat)
endif()

if(EAPPS_BUILD_SECURITY)
    add_subdirectory(apps/evpn)
    add_subdirectory(apps/eguard)
    add_subdirectory(apps/evirustower)
    add_subdirectory(apps/ebot)
endif()

if(EAPPS_BUILD_WEB)
    add_subdirectory(apps/eweb)
endif()

if(EAPPS_BUILD_SUITE)
    add_subdirectory(apps/suite)
endif()

# --- Tests ---
if(BUILD_TESTING)
    enable_testing()
    add_subdirectory(tests)
endif()
