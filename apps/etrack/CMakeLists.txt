add_library(etrack STATIC etrack.c)
target_include_directories(etrack PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(etrack PUBLIC eapps_ui eapps_storage eapps_network)

if(EAPPS_BUILD_STANDALONE AND TARGET eapps_port)
    add_executable(etrack_standalone etrack.c)
    target_link_libraries(etrack_standalone PRIVATE etrack eapps_port)
endif()
