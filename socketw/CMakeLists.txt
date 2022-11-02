set(SOCKETW_SOURCE_DIR ${CMAKE_BINARY_DIR}/Source/socketw)

ExternalProject_Add(
        socketw
        URL https://github.com/RigsOfRods/socketw/archive/refs/tags/3.11.0.tar.gz
        URL_MD5 fc28cf0cc7f3497c4315c0e5fd37eb91
        PATCH_COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_SOURCE_DIR}/sw_config.h ${SOCKETW_SOURCE_DIR}/src/sw_config.h
        CMAKE_ARGS
        -DCMAKE_INSTALL_PREFIX=${DEPENDENCIES_OUTPUT_DIR}
        -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
        -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
        -DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}
        -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
)