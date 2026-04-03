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

# App lifecycle tests — needs all app libraries
set(LIFECYCLE_LIBS eapps_common eapps_ui)
if(EAPPS_BUILD_PRODUCTIVITY)
    list(APPEND LIFECYCLE_LIBS ecal enote econverter ebuffer efiles ecleaner eclock etools etimer epdf ezip eviewer esession)
endif()
if(EAPPS_BUILD_MEDIA)
    list(APPEND LIFECYCLE_LIBS emusic evideo egallery eplay epaint)
endif()
if(EAPPS_BUILD_GAMES)
    list(APPEND LIFECYCLE_LIBS snake tetris minesweeper dice erunner esurfer echess ebirds eslice eblocks ecrush)
endif()
if(EAPPS_BUILD_CONNECTIVITY)
    list(APPEND LIFECYCLE_LIBS eftp eserial essh evnc etunnel echat eremote ewifi)
endif()
if(EAPPS_BUILD_SECURITY)
    list(APPEND LIFECYCLE_LIBS evpn eguard evirustower)
endif()
if(EAPPS_BUILD_WEB)
    list(APPEND LIFECYCLE_LIBS eweb)
endif()
add_executable(test_app_lifecycle test_app_lifecycle.c)
target_link_libraries(test_app_lifecycle PRIVATE ${LIFECYCLE_LIBS})
if(NOT MSVC)
    target_link_libraries(test_app_lifecycle PRIVATE m)
endif()
add_test(NAME test_app_lifecycle COMMAND test_app_lifecycle)
