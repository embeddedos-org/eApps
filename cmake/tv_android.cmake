# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Meta Platforms, Inc. and affiliates.
#
# CMake toolchain file for Android TV builds (based on Android NDK)

set(CMAKE_SYSTEM_NAME Android)
set(CMAKE_ANDROID_API 26 CACHE STRING "Minimum Android API level for TV")
set(CMAKE_ANDROID_ARCH_ABI "arm64-v8a" CACHE STRING "Target ABI")

if(DEFINED ENV{ANDROID_NDK_HOME})
    set(CMAKE_ANDROID_NDK $ENV{ANDROID_NDK_HOME} CACHE PATH "Android NDK path")
elseif(DEFINED ENV{ANDROID_NDK})
    set(CMAKE_ANDROID_NDK $ENV{ANDROID_NDK} CACHE PATH "Android NDK path")
endif()

set(CMAKE_ANDROID_STL_TYPE "c++_shared" CACHE STRING "Android STL type")

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -O2 -Wall -Wextra" CACHE STRING "C flags for TV Android" FORCE)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O2 -Wall -Wextra" CACHE STRING "CXX flags for TV Android" FORCE)

add_compile_definitions(
    EAPPS_PLATFORM_TV=1
    TV_RESOLUTION_1080P=1
)
