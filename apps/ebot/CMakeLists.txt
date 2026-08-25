# LVGL is provided either by the extern/lvgl submodule or by FetchContent, so
# test for the target rather than for the submodule directory.
if(NOT TARGET lvgl)
    message(STATUS "LVGL target unavailable - skipping ebot build")
    return()
endif()

add_library(ebot STATIC ebot.c)
target_include_directories(ebot PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(ebot PUBLIC eapps_ui eapps_network)
if(EAPPS_BUILD_STANDALONE AND TARGET eapps_port)
    add_executable(ebot_standalone ebot.c)
    target_link_libraries(ebot_standalone PRIVATE ebot eapps_port)
endif()