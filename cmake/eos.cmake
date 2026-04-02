set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR ${EOS_TARGET_ARCH})

# Allow the compiler to be set from the command line (-DCMAKE_C_COMPILER=...)
if(NOT CMAKE_C_COMPILER)
    set(EOS_TOOLCHAIN_PREFIX "arm-none-eabi-" CACHE STRING "Cross-compiler prefix")
    set(CMAKE_C_COMPILER   "${EOS_TOOLCHAIN_PREFIX}gcc")
    set(CMAKE_CXX_COMPILER "${EOS_TOOLCHAIN_PREFIX}g++")
    set(CMAKE_ASM_COMPILER "${EOS_TOOLCHAIN_PREFIX}gcc")
    set(CMAKE_OBJCOPY      "${EOS_TOOLCHAIN_PREFIX}objcopy")
    set(CMAKE_SIZE         "${EOS_TOOLCHAIN_PREFIX}size")
endif()

# Skip linker test during compiler check (cross-compilers may lack crt0)
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)

set(CMAKE_C_FLAGS_INIT   "-ffunction-sections -fdata-sections -fno-common")
set(CMAKE_EXE_LINKER_FLAGS_INIT "-Wl,--gc-sections")

set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

set(EAPPS_PLATFORM_EOS ON CACHE BOOL "" FORCE)
