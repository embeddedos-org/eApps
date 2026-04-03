# SPDX-License-Identifier: MIT
# Copyright (c) 2024 Meta Platforms, Inc. and affiliates.
#
# Android NDK CMake toolchain file for eApps.

set(CMAKE_SYSTEM_NAME Android)

if(DEFINED ENV{ANDROID_NDK_HOME})
    set(CMAKE_ANDROID_NDK $ENV{ANDROID_NDK_HOME})
else()
    message(FATAL_ERROR "ANDROID_NDK_HOME environment variable is not set. "
                        "Please set it to the path of your Android NDK installation.")
endif()

set(CMAKE_ANDROID_API 26)

if(NOT DEFINED ANDROID_ABI)
    set(ANDROID_ABI "arm64-v8a")
endif()
set(CMAKE_ANDROID_ARCH_ABI ${ANDROID_ABI})

set(CMAKE_ANDROID_STL_TYPE "c++_static")

add_compile_definitions(EAPPS_PLATFORM_ANDROID=1)

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -O2 -Wall -Wextra")
