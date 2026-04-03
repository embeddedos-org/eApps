add_library(eBrowser_engine STATIC
    dom.c
    html_parser.c
    css_parser.c
    layout.c
    svg_parser.c
    gpu_renderer.c
    js_engine.c
)
target_include_directories(eBrowser_engine PUBLIC
    ${CMAKE_SOURCE_DIR}/include
)
