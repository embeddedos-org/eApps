if(EAPPS_PLATFORM_SDL2)
    set(PORT_SOURCES
        sdl2/lv_port_disp_sdl2.c
        sdl2/lv_port_indev_sdl2.c
        sdl2/main_sdl2.c
    )
elseif(EAPPS_PLATFORM_EOS)
    set(PORT_SOURCES
        eos/lv_port_disp_eos.c
        eos/lv_port_indev_eos.c
        eos/main_eos.c
    )
elseif(EAPPS_PLATFORM_WEB)
    set(PORT_SOURCES
        web/lv_port_disp_web.c
        web/lv_port_indev_web.c
        web/main_web.c
    )
elseif(EAPPS_PLATFORM_ANDROID)
    set(PORT_SOURCES
        android/lv_port_disp_android.c
        android/lv_port_indev_android.c
        android/main_android.c
    )
elseif(EAPPS_PLATFORM_IOS)
    set(PORT_SOURCES
        ios/lv_port_disp_ios.c
        ios/lv_port_indev_ios.c
        ios/main_ios.c
    )
elseif(EAPPS_PLATFORM_TV)
    set(PORT_SOURCES
        tv/lv_port_disp_tv.c
        tv/lv_port_indev_tv.c
        tv/main_tv.c
    )
endif()
if(NOT PORT_SOURCES)
    return()
endif()

# LVGL is provided either by the extern/lvgl submodule or by FetchContent, so
# test for the target rather than for the submodule directory.
if(NOT TARGET lvgl)
    message(STATUS "LVGL target unavailable - skipping port layer build")
    return()
endif()

# The SDL2 and EoS ports draw through the EoS display/input HAL
# (<eos/hal_extended.h>), which lives in the sibling `eos` repository rather
# than in this one. Resolve every dependency before declaring the target: the
# port sources include their dependencies unconditionally, so detecting
# afterwards turns a missing optional dependency into a hard build failure.
set(EAPPS_EOS_ROOT "${CMAKE_SOURCE_DIR}/../eos" CACHE PATH
    "Path to an eos repository checkout providing <eos/hal_extended.h>")
find_path(EAPPS_EOS_HAL_INCLUDE_DIR
    NAMES eos/hal_extended.h
    HINTS "${EAPPS_EOS_ROOT}/hal/include")

set(EAPPS_PORT_SKIP_REASON "")

if(EAPPS_PLATFORM_SDL2)
    find_package(SDL2 QUIET)
    if(NOT SDL2_FOUND)
        find_package(PkgConfig QUIET)
        if(PkgConfig_FOUND)
            pkg_check_modules(SDL2 QUIET sdl2)
        endif()
    endif()
    if(NOT SDL2_FOUND)
        set(EAPPS_PORT_SKIP_REASON
            "SDL2 not found - install it (apt install libsdl2-dev | brew install sdl2)")
    endif()
endif()

if(NOT EAPPS_PORT_SKIP_REASON
   AND (EAPPS_PLATFORM_SDL2 OR EAPPS_PLATFORM_EOS)
   AND NOT EAPPS_EOS_HAL_INCLUDE_DIR)
    set(EAPPS_PORT_SKIP_REASON
        "<eos/hal_extended.h> not found - point EAPPS_EOS_ROOT at an eos checkout")
endif()

if(EAPPS_PORT_SKIP_REASON)
    message(STATUS "Skipping eapps_port: ${EAPPS_PORT_SKIP_REASON}")
    return()
endif()

add_library(eapps_port STATIC ${PORT_SOURCES})
target_link_libraries(eapps_port PUBLIC eapps_ui eapps_platform lvgl)

if(EAPPS_PLATFORM_SDL2 OR EAPPS_PLATFORM_EOS)
    target_include_directories(eapps_port PUBLIC ${EAPPS_EOS_HAL_INCLUDE_DIR})
endif()

if(EAPPS_PLATFORM_SDL2)
    if(TARGET SDL2::SDL2)
        target_link_libraries(eapps_port PUBLIC SDL2::SDL2)
    else()
        target_include_directories(eapps_port PUBLIC ${SDL2_INCLUDE_DIRS})
        target_link_libraries(eapps_port PUBLIC ${SDL2_LIBRARIES})
    endif()
endif()

if(EAPPS_PLATFORM_TV)
    target_sources(eapps_port PRIVATE ../core/ui/src/tv_layout.c)
endif()
