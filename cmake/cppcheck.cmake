# cmake/cppcheck.cmake
# Optional cppcheck integration for static analysis
#
# Usage:
#   cmake -B build -DEAPPS_ENABLE_CPPCHECK=ON
#   cmake --build build --target cppcheck

option(EAPPS_ENABLE_CPPCHECK "Enable cppcheck static analysis target" OFF)

if(EAPPS_ENABLE_CPPCHECK)
    find_program(CPPCHECK_EXECUTABLE cppcheck)

    if(CPPCHECK_EXECUTABLE)
        message(STATUS "cppcheck found: ${CPPCHECK_EXECUTABLE}")

        set(CPPCHECK_ARGS
            --enable=all
            --suppress=missingIncludeSystem
            --suppress=constVariablePointer
            --suppress=constParameterPointer
            --suppress=variableScope
            --suppress=unusedFunction
            --error-exitcode=1
            --inline-suppr
            --std=c11
            -I ${CMAKE_SOURCE_DIR}/core/common/include
            -I ${CMAKE_SOURCE_DIR}/core/ui/include
            -I ${CMAKE_SOURCE_DIR}/core/storage/include
            -I ${CMAKE_SOURCE_DIR}/core/network/include
            -I ${CMAKE_SOURCE_DIR}/core/platform/include
            -I ${CMAKE_SOURCE_DIR}/extern
            ${CMAKE_SOURCE_DIR}/core/
            ${CMAKE_SOURCE_DIR}/apps/
        )

        add_custom_target(cppcheck
            COMMAND ${CPPCHECK_EXECUTABLE} ${CPPCHECK_ARGS}
            WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
            COMMENT "Running cppcheck static analysis..."
        )
    else()
        message(WARNING "cppcheck not found — 'cppcheck' target will not be available")
    endif()
endif()
