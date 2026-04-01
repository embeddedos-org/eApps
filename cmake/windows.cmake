set(CMAKE_SYSTEM_NAME Windows)

if(MSVC)
    set(CMAKE_C_FLAGS_INIT "/O2 /W3")
else()
    set(CMAKE_C_COMPILER x86_64-w64-mingw32-gcc)
    set(CMAKE_C_FLAGS_INIT "-O2 -g")
endif()

set(EAPPS_PLATFORM_SDL2 ON CACHE BOOL "" FORCE)
