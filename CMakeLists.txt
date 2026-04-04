cmake_minimum_required(VERSION 3.14)
project(eapps
    VERSION 2.1.0
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
    add_subdirectory(apps/etrack)
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
    add_subdirectory(apps/eremote)
    add_subdirectory(apps/ewifi)
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

# ═══════════════════════════════════════════════════════════════
# CPack — Per-platform installers with component selection
# Install ALL (Suite) or pick individual app categories
# ═══════════════════════════════════════════════════════════════
set(CPACK_PACKAGE_NAME "eApps-Suite")
set(CPACK_PACKAGE_VERSION "${PROJECT_VERSION}")
set(CPACK_PACKAGE_VENDOR "EmbeddedOS Project")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "eApps Suite — 41 embedded apps in one launcher")
set(CPACK_PACKAGE_HOMEPAGE_URL "https://github.com/embeddedos-org/eApps")
set(CPACK_PACKAGE_CONTACT "embeddedos-org <https://github.com/embeddedos-org>")
set(CPACK_RESOURCE_FILE_LICENSE "${CMAKE_CURRENT_SOURCE_DIR}/LICENSE")
set(CPACK_PACKAGE_INSTALL_DIRECTORY "EoS/eApps Suite")

# ── Selectable components ──
set(CPACK_COMPONENTS_ALL
    suite_launcher productivity media games connectivity security web)

set(CPACK_COMPONENT_SUITE_LAUNCHER_DISPLAY_NAME "eApps Suite Launcher")
set(CPACK_COMPONENT_SUITE_LAUNCHER_DESCRIPTION "Main launcher — all 41 apps in one UI")
set(CPACK_COMPONENT_SUITE_LAUNCHER_REQUIRED ON)

set(CPACK_COMPONENT_PRODUCTIVITY_DISPLAY_NAME "Productivity Apps (14)")
set(CPACK_COMPONENT_PRODUCTIVITY_DESCRIPTION
    "ecal, enote, econverter, ebuffer, efiles, ecleaner, eclock, etools, etimer, epdf, ezip, eviewer, esession, etrack")
set(CPACK_COMPONENT_PRODUCTIVITY_GROUP "Individual Apps")

set(CPACK_COMPONENT_MEDIA_DISPLAY_NAME "Media Apps (5)")
set(CPACK_COMPONENT_MEDIA_DESCRIPTION "emusic, evideo, egallery, eplay, epaint")
set(CPACK_COMPONENT_MEDIA_GROUP "Individual Apps")

set(CPACK_COMPONENT_GAMES_DISPLAY_NAME "Games (11)")
set(CPACK_COMPONENT_GAMES_DESCRIPTION
    "snake, tetris, minesweeper, dice, erunner, esurfer, echess, ebirds, eslice, eblocks, ecrush")
set(CPACK_COMPONENT_GAMES_GROUP "Individual Apps")

set(CPACK_COMPONENT_CONNECTIVITY_DISPLAY_NAME "Connectivity Apps (8)")
set(CPACK_COMPONENT_CONNECTIVITY_DESCRIPTION "eftp, eserial, essh, evnc, etunnel, echat, eremote, ewifi")
set(CPACK_COMPONENT_CONNECTIVITY_GROUP "Individual Apps")

set(CPACK_COMPONENT_SECURITY_DISPLAY_NAME "Security Apps (3)")
set(CPACK_COMPONENT_SECURITY_DESCRIPTION "evpn, eguard, evirustower")
set(CPACK_COMPONENT_SECURITY_GROUP "Individual Apps")

set(CPACK_COMPONENT_WEB_DISPLAY_NAME "Web Apps (1)")
set(CPACK_COMPONENT_WEB_DESCRIPTION "eweb browser")
set(CPACK_COMPONENT_WEB_GROUP "Individual Apps")

set(CPACK_COMPONENT_GROUP_INDIVIDUAL_APPS_DESCRIPTION
    "Install individual app executables — run each app separately")

# ── Windows (NSIS) ──
set(CPACK_NSIS_DISPLAY_NAME "eApps Suite ${PROJECT_VERSION}")
set(CPACK_NSIS_PACKAGE_NAME "eApps Suite")
set(CPACK_NSIS_URL_INFO_ABOUT "https://github.com/embeddedos-org/eApps")
set(CPACK_NSIS_ENABLE_UNINSTALL_BEFORE_INSTALL ON)
set(CPACK_NSIS_MODIFY_PATH OFF)
set(CPACK_NSIS_CREATE_ICONS_EXTRA
    "CreateShortCut '$SMPROGRAMS\\$STARTMENU_FOLDER\\eApps Suite.lnk' '$INSTDIR\\bin\\eapps_suite.exe'")
set(CPACK_NSIS_DELETE_ICONS_EXTRA
    "Delete '$SMPROGRAMS\\$STARTMENU_FOLDER\\eApps Suite.lnk'")
set(CPACK_NSIS_MUI_FINISHPAGE_RUN "eapps_suite.exe")

# ── macOS (DragNDrop → .dmg) ──
set(CPACK_DMG_VOLUME_NAME "eApps Suite ${PROJECT_VERSION}")
set(CPACK_DMG_FORMAT "UDBZ")

# ── Linux DEB ──
set(CPACK_DEBIAN_PACKAGE_MAINTAINER "EmbeddedOS Project")
set(CPACK_DEBIAN_PACKAGE_SECTION "utils")
set(CPACK_DEBIAN_PACKAGE_DEPENDS "libsdl2-2.0-0 (>= 2.0.14)")
set(CPACK_DEBIAN_PACKAGE_HOMEPAGE "https://github.com/embeddedos-org/eApps")
set(CPACK_DEBIAN_FILE_NAME DEB-DEFAULT)

# ── Linux RPM ──
set(CPACK_RPM_PACKAGE_LICENSE "MIT")
set(CPACK_RPM_PACKAGE_GROUP "Applications/System")
set(CPACK_RPM_PACKAGE_URL "https://github.com/embeddedos-org/eApps")
set(CPACK_RPM_PACKAGE_REQUIRES "SDL2 >= 2.0.14")
set(CPACK_RPM_FILE_NAME RPM-DEFAULT)

include(CPack)

# ═══════════════════════════════════════════════════════════════
# CPack — Per-platform Suite installers
# ═══════════════════════════════════════════════════════════════
if(EAPPS_BUILD_SUITE AND TARGET eapps_suite)
    set(CPACK_PACKAGE_NAME "eApps-Suite")
    set(CPACK_PACKAGE_VERSION "${PROJECT_VERSION}")
    set(CPACK_PACKAGE_VENDOR "EmbeddedOS Project")
    set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "eApps Suite — 41 embedded apps in one launcher")
    set(CPACK_PACKAGE_HOMEPAGE_URL "https://github.com/embeddedos-org/eApps")
    set(CPACK_PACKAGE_CONTACT "embeddedos-org <https://github.com/embeddedos-org>")
    set(CPACK_RESOURCE_FILE_LICENSE "${CMAKE_CURRENT_SOURCE_DIR}/LICENSE")
    set(CPACK_PACKAGE_INSTALL_DIRECTORY "EoS/eApps Suite")

    # ── Windows (NSIS) ──
    set(CPACK_NSIS_DISPLAY_NAME "eApps Suite ${PROJECT_VERSION}")
    set(CPACK_NSIS_PACKAGE_NAME "eApps Suite")
    set(CPACK_NSIS_URL_INFO_ABOUT "https://github.com/embeddedos-org/eApps")
    set(CPACK_NSIS_ENABLE_UNINSTALL_BEFORE_INSTALL ON)
    set(CPACK_NSIS_MODIFY_PATH OFF)
    set(CPACK_NSIS_CREATE_ICONS_EXTRA
        "CreateShortCut '$SMPROGRAMS\\\\$STARTMENU_FOLDER\\\\eApps Suite.lnk' '$INSTDIR\\\\bin\\\\eapps_suite.exe'")
    set(CPACK_NSIS_DELETE_ICONS_EXTRA
        "Delete '$SMPROGRAMS\\\\$STARTMENU_FOLDER\\\\eApps Suite.lnk'")
    set(CPACK_NSIS_MUI_FINISHPAGE_RUN "eapps_suite.exe")

    # ── macOS (DragNDrop → .dmg) ──
    set(CPACK_DMG_VOLUME_NAME "eApps Suite ${PROJECT_VERSION}")
    set(CPACK_DMG_FORMAT "UDBZ")

    # ── Linux DEB ──
    set(CPACK_DEBIAN_PACKAGE_MAINTAINER "EmbeddedOS Project")
    set(CPACK_DEBIAN_PACKAGE_SECTION "utils")
    set(CPACK_DEBIAN_PACKAGE_DEPENDS "libsdl2-2.0-0 (>= 2.0.14)")
    set(CPACK_DEBIAN_PACKAGE_HOMEPAGE "https://github.com/embeddedos-org/eApps")
    set(CPACK_DEBIAN_FILE_NAME DEB-DEFAULT)

    # ── Linux RPM ──
    set(CPACK_RPM_PACKAGE_LICENSE "MIT")
    set(CPACK_RPM_PACKAGE_GROUP "Applications/System")
    set(CPACK_RPM_PACKAGE_URL "https://github.com/embeddedos-org/eApps")
    set(CPACK_RPM_PACKAGE_REQUIRES "SDL2 >= 2.0.14")
    set(CPACK_RPM_FILE_NAME RPM-DEFAULT)

    include(CPack)
endif()
