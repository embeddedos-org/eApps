add_library(ehmi STATIC ehmi.c)
target_include_directories(ehmi PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(ehmi PUBLIC eapps_ui)
