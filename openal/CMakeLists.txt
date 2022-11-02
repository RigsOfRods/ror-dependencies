
ExternalProject_Add(
        openal
        URL https://github.com/kcat/openal-soft/archive/refs/tags/1.22.2.tar.gz
        URL_MD5 2d660bff2a16128bc7e894b1254d3783
        CMAKE_ARGS
        -DCMAKE_INSTALL_PREFIX=${DEPENDENCIES_OUTPUT_DIR}
        -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
        -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
        -DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}
        -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
)