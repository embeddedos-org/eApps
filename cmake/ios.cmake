# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Meta Platforms, Inc. and affiliates.
#
# CMake toolchain file for iOS builds

set(CMAKE_SYSTEM_NAME iOS)
set(CMAKE_OSX_DEPLOYMENT_TARGET "15.0" CACHE STRING "Minimum iOS deployment target")
set(CMAKE_OSX_ARCHITECTURES "arm64" CACHE STRING "Target architecture")

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -O2 -Wall -Wextra" CACHE STRING "C flags for iOS" FORCE)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O2 -Wall -Wextra" CACHE STRING "CXX flags for iOS" FORCE)

add_compile_definitions(EAPPS_PLATFORM_IOS=1)
