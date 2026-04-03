add_library(eBrowser_platform STATIC platform.c)
target_include_directories(eBrowser_platform PUBLIC ${CMAKE_SOURCE_DIR}/include)
