enable_testing()

add_executable(test_dom test_dom.c)
target_link_libraries(test_dom PRIVATE eBrowser_engine)
add_test(NAME test_dom COMMAND test_dom)

add_executable(test_html_parser test_html_parser.c)
target_link_libraries(test_html_parser PRIVATE eBrowser_engine)
add_test(NAME test_html_parser COMMAND test_html_parser)

add_executable(test_css_parser test_css_parser.c)
target_link_libraries(test_css_parser PRIVATE eBrowser_engine)
add_test(NAME test_css_parser COMMAND test_css_parser)

add_executable(test_layout test_layout.c)
target_link_libraries(test_layout PRIVATE eBrowser_engine)
add_test(NAME test_layout COMMAND test_layout)

add_executable(test_url test_url.c)
target_link_libraries(test_url PRIVATE eBrowser_network)
add_test(NAME test_url COMMAND test_url)

add_executable(test_input test_input.c)
target_link_libraries(test_input PRIVATE eBrowser_input)
add_test(NAME test_input COMMAND test_input)

add_executable(test_platform test_platform.c)
target_link_libraries(test_platform PRIVATE eBrowser_platform)
add_test(NAME test_platform COMMAND test_platform)

add_executable(test_crypto test_crypto.c)
target_link_libraries(test_crypto PRIVATE eBrowser_security)
add_test(NAME test_crypto COMMAND test_crypto)

add_executable(test_tls test_tls.c)
target_link_libraries(test_tls PRIVATE eBrowser_security)
add_test(NAME test_tls COMMAND test_tls)

add_executable(test_security test_security.c)
target_link_libraries(test_security PRIVATE eBrowser_security)
add_test(NAME test_security COMMAND test_security)

add_executable(test_svg test_svg.c)
target_link_libraries(test_svg PRIVATE eBrowser_engine)
add_test(NAME test_svg COMMAND test_svg)

add_executable(test_modules test_modules.c)
target_link_libraries(test_modules PRIVATE eBrowser_engine eBrowser_network eBrowser_telemetry eBrowser_plugin eBrowser_security)
add_test(NAME test_modules COMMAND test_modules)
