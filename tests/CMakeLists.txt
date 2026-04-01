enable_testing()

set(TEST_SOURCES
    test_expr_parser
    test_math_utils
    test_string_utils
    test_date_utils
    test_registry
    test_game_engine
    test_prefs
)

foreach(test ${TEST_SOURCES})
    add_executable(${test} ${test}.c)
    target_link_libraries(${test} PRIVATE eapps_common eapps_ui eapps_storage)
    if(NOT MSVC)
        target_link_libraries(${test} PRIVATE m)
    endif()
    add_test(NAME ${test} COMMAND ${test})
endforeach()
