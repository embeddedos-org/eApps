add_library(eapps_ui STATIC
    src/theme.c
    src/widgets.c
    src/canvas.c
    src/game_engine.c
)

target_include_directories(eapps_ui PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_link_libraries(eapps_ui PUBLIC eapps_common lvgl)
target_link_libraries(eapps_ui PRIVATE m)
