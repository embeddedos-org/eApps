# SPDX-License-Identifier: MIT
cmake_minimum_required(VERSION 3.16)
add_library(esettings STATIC esettings.c)
target_include_directories(esettings PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(esettings PUBLIC eapps_core lvgl)
