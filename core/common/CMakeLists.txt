add_library(eapps_common STATIC
    src/registry.c
    src/math_utils.c
    src/string_utils.c
    src/date_utils.c
    src/expr_parser.c
)

target_include_directories(eapps_common PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

if(NOT MSVC)
    target_link_libraries(eapps_common PRIVATE m)
endif()
    target_link_libraries(eapps_common PRIVATE m)
endif()
