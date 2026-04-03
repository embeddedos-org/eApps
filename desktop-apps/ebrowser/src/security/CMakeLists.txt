add_library(ebowser_security STATIC
    crypto.c
    tls.c
    security.c
    secure_storage.c
    permissions.c
)
target_include_directories(ebowser_security PUBLIC ${CMAKE_SOURCE_DIR}/include)
