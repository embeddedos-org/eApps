add_library(eBrowser_browser STATIC browser.c)
target_include_directories(eBrowser_browser PUBLIC ${CMAKE_SOURCE_DIR}/include)
target_link_libraries(eBrowser_browser PUBLIC
    eBrowser_engine
    eBrowser_render
    eBrowser_network
    eBrowser_input
    eBrowser_platform
    lvgl
)
