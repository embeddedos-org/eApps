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
endif()

if(NOT PORT_SOURCES)
    return()
endif()

if(NOT PORT_SOURCES)
    return()
endif()

add_library(eapps_port STATIC ${PORT_SOURCES})

target_link_libraries(eapps_port PUBLIC eapps_ui eapps_platform lvgl)

if(EAPPS_PLATFORM_SDL2)
    find_package(SDL2 QUIET)
    if(SDL2_FOUND)
        target_link_libraries(eapps_port PUBLIC SDL2::SDL2)
    endif()
endif()
