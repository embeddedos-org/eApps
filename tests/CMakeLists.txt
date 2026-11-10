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

# eRemote and eWiFi are connectivity apps: the top-level CMakeLists.txt only
# adds apps/eremote and apps/ewifi when EAPPS_BUILD_CONNECTIVITY is ON, so their
# tests can only be built then. Otherwise the linker is handed the bare names
# "eremote" and "ewifi" and fails with "library not found".
if(EAPPS_BUILD_CONNECTIVITY)
    # eRemote engine tests
    add_executable(test_eremote test_eremote.c)
    target_link_libraries(test_eremote PRIVATE eapps_common eapps_ui eremote)
    if(NOT MSVC)
        target_link_libraries(test_eremote PRIVATE m)
    endif()
    add_test(NAME test_eremote COMMAND test_eremote)

    # eWiFi engine + vault + validation tests
    add_executable(test_ewifi test_ewifi.c)
    target_link_libraries(test_ewifi PRIVATE eapps_common eapps_ui ewifi)
    if(NOT MSVC)
        target_link_libraries(test_ewifi PRIVATE m)
    endif()
    add_test(NAME test_ewifi COMMAND test_ewifi)

    # eWiFi shell-argument hardening — SSIDs reach system()/popen()
    add_executable(test_ewifi_shellsafe test_ewifi_shellsafe.c)
    target_link_libraries(test_ewifi_shellsafe PRIVATE eapps_common eapps_ui ewifi)
    if(NOT MSVC)
        target_link_libraries(test_ewifi_shellsafe PRIVATE m)
    endif()
    add_test(NAME test_ewifi_shellsafe COMMAND test_ewifi_shellsafe)
else()
    message(STATUS "test_eremote, test_ewifi, test_ewifi_shellsafe skipped: EAPPS_BUILD_CONNECTIVITY is OFF")
endif()

# App lifecycle tests — needs all app libraries
# test_app_lifecycle.c checks each category only under #ifdef EAPPS_BUILD_<CATEGORY>,
# so every enabled category must also be passed as a compile definition. Without
# them the test compiled to an empty main() and passed with 0 assertions.
# esettings is a system app (always built, top-level CMakeLists.txt), so it is
# linked whenever the productivity checks that reference it are compiled.
# LIFECYCLE_EXPECTED counts the enabled categories straight from the options, not
# from LIFECYCLE_DEFS, so the test fails if a category's define is ever dropped.
set(LIFECYCLE_LIBS eapps_common eapps_ui)
set(LIFECYCLE_DEFS)
set(LIFECYCLE_EXPECTED 0)
foreach(category PRODUCTIVITY MEDIA GAMES CONNECTIVITY SECURITY WEB)
    if(EAPPS_BUILD_${category})
        math(EXPR LIFECYCLE_EXPECTED "${LIFECYCLE_EXPECTED} + 1")
    endif()
endforeach()
if(EAPPS_BUILD_PRODUCTIVITY)
    list(APPEND LIFECYCLE_LIBS ecal enote econverter ebuffer efiles ecleaner eclock etools etimer epdf ezip eviewer esession esettings)
    list(APPEND LIFECYCLE_DEFS EAPPS_BUILD_PRODUCTIVITY)
endif()
if(EAPPS_BUILD_MEDIA)
    list(APPEND LIFECYCLE_LIBS emusic evideo egallery eplay epaint)
    list(APPEND LIFECYCLE_DEFS EAPPS_BUILD_MEDIA)
endif()
if(EAPPS_BUILD_GAMES)
    list(APPEND LIFECYCLE_LIBS snake tetris minesweeper dice erunner esurfer echess ebirds eslice eblocks ecrush)
    list(APPEND LIFECYCLE_DEFS EAPPS_BUILD_GAMES)
endif()
if(EAPPS_BUILD_CONNECTIVITY)
    list(APPEND LIFECYCLE_LIBS eftp eserial essh evnc etunnel echat eremote ewifi)
    list(APPEND LIFECYCLE_DEFS EAPPS_BUILD_CONNECTIVITY)
endif()
if(EAPPS_BUILD_SECURITY)
    list(APPEND LIFECYCLE_LIBS evpn eguard evirustower ebot)
    list(APPEND LIFECYCLE_DEFS EAPPS_BUILD_SECURITY)
endif()
if(EAPPS_BUILD_WEB)
    list(APPEND LIFECYCLE_LIBS eweb)
    list(APPEND LIFECYCLE_DEFS EAPPS_BUILD_WEB)
endif()
# With every category switched off there is nothing to check, so no test.
if(LIFECYCLE_EXPECTED GREATER 0)
    add_executable(test_app_lifecycle test_app_lifecycle.c)
    target_link_libraries(test_app_lifecycle PRIVATE ${LIFECYCLE_LIBS})
    target_compile_definitions(test_app_lifecycle PRIVATE ${LIFECYCLE_DEFS}
        EAPPS_LIFECYCLE_EXPECTED_CATEGORIES=${LIFECYCLE_EXPECTED})
    if(NOT MSVC)
        target_link_libraries(test_app_lifecycle PRIVATE m)
    endif()
    add_test(NAME test_app_lifecycle COMMAND test_app_lifecycle)
else()
    message(STATUS "test_app_lifecycle skipped: every EAPPS_BUILD_<CATEGORY> option is OFF")
endif()
