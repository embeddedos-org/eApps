set(HTTP_COMMON_SRC src/http.c)

if(EAPPS_PLATFORM_EOS OR (UNIX AND NOT EMSCRIPTEN))
    set(HTTP_PLATFORM_SRC src/http_posix.c)
elseif(WIN32)
    set(HTTP_PLATFORM_SRC src/http_win32.c)
elseif(EMSCRIPTEN)
    set(HTTP_PLATFORM_SRC src/http_web.c)
else()
    set(HTTP_PLATFORM_SRC src/http_posix.c)
endif()

add_library(eapps_network STATIC ${HTTP_COMMON_SRC} ${HTTP_PLATFORM_SRC})
target_include_directories(eapps_network PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_link_libraries(eapps_network PUBLIC eapps_common)

if(WIN32)
    target_link_libraries(eapps_network PRIVATE winhttp)
endif()
