add_library(eBrowser_plugin STATIC
    plugin.c
)
target_include_directories(eBrowser_plugin PUBLIC
    ${CMAKE_SOURCE_DIR}/include
)
