add_library(eapps_storage STATIC src/prefs.c)
target_include_directories(eapps_storage PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_link_libraries(eapps_storage PUBLIC eapps_common)
