set(SUITE_LINK_LIBS eapps_ui eapps_storage eapps_network eapps_platform)

if(TARGET eapps_port)
    list(APPEND SUITE_LINK_LIBS eapps_port)
endif()

# Link all enabled app libraries
if(EAPPS_BUILD_PRODUCTIVITY)
    list(APPEND SUITE_LINK_LIBS ecal enote econverter ebuffer efiles ecleaner eclock etools etimer epdf ezip eviewer esession etrack)
endif()
if(EAPPS_BUILD_MEDIA)
    list(APPEND SUITE_LINK_LIBS emusic evideo egallery eplay epaint)
endif()
if(EAPPS_BUILD_GAMES)
    list(APPEND SUITE_LINK_LIBS snake tetris minesweeper dice erunner esurfer echess ebirds eslice eblocks ecrush)
endif()
if(EAPPS_BUILD_CONNECTIVITY)
    list(APPEND SUITE_LINK_LIBS eftp eserial essh evnc etunnel echat eremote ewifi)
endif()
if(EAPPS_BUILD_SECURITY)
    list(APPEND SUITE_LINK_LIBS evpn eguard evirustower)
endif()
if(EAPPS_BUILD_WEB)
    list(APPEND SUITE_LINK_LIBS eweb)
endif()

add_library(suite STATIC suite.c)
target_include_directories(suite PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(suite PUBLIC ${SUITE_LINK_LIBS})

if(TARGET eapps_port)
    add_executable(eapps_suite suite.c)
    target_link_libraries(eapps_suite PRIVATE suite eapps_port)
endif()

# ═══════════════════════════════════════════════════════════════
# Install rules — Suite launcher + individual app components
# ═══════════════════════════════════════════════════════════════

# Suite launcher (always installed as core component)
if(TARGET eapps_suite)
    install(TARGETS eapps_suite
            RUNTIME DESTINATION bin
            COMPONENT suite_launcher)
endif()

# Individual standalone app install (per-category components)
# Users choose categories via NSIS checkboxes or:
#   cmake --install build --component games
if(EAPPS_BUILD_STANDALONE AND TARGET eapps_port)
    foreach(app ecal enote econverter ebuffer efiles ecleaner eclock etools etimer epdf ezip eviewer esession etrack)
        if(TARGET ${app}_standalone)
            install(TARGETS ${app}_standalone RUNTIME DESTINATION bin COMPONENT productivity)
        endif()
    endforeach()

    foreach(app emusic evideo egallery eplay epaint)
        if(TARGET ${app}_standalone)
            install(TARGETS ${app}_standalone RUNTIME DESTINATION bin COMPONENT media)
        endif()
    endforeach()

    foreach(app snake tetris minesweeper dice erunner esurfer echess ebirds eslice eblocks ecrush)
        if(TARGET ${app}_standalone)
            install(TARGETS ${app}_standalone RUNTIME DESTINATION bin COMPONENT games)
        endif()
    endforeach()

    foreach(app eftp eserial essh evnc etunnel echat eremote ewifi)
        if(TARGET ${app}_standalone)
            install(TARGETS ${app}_standalone RUNTIME DESTINATION bin COMPONENT connectivity)
        endif()
    endforeach()

    foreach(app evpn eguard evirustower)
        if(TARGET ${app}_standalone)
            install(TARGETS ${app}_standalone RUNTIME DESTINATION bin COMPONENT security)
        endif()
    endforeach()

    if(TARGET eweb_standalone)
        install(TARGETS eweb_standalone RUNTIME DESTINATION bin COMPONENT web)
    endif()
endif()

# Linux desktop integration
if(UNIX AND NOT APPLE)
    install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/../../installer/linux/eapps-suite.desktop
            DESTINATION share/applications
            COMPONENT suite_launcher)
    install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/../../installer/linux/eapps-suite.png
            DESTINATION share/icons/hicolor/256x256/apps
            COMPONENT suite_launcher
            OPTIONAL)
endif()
