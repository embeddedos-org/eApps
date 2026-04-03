add_library(eBrowser_render STATIC render.c)
target_include_directories(eBrowser_render PUBLIC ${CMAKE_SOURCE_DIR}/include)
target_link_libraries(eBrowser_render PUBLIC eBrowser_engine lvgl)
