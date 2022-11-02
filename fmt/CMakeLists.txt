ExternalProject_Add(
        fmt 
        URL https://github.com/fmtlib/fmt/releases/download/9.1.0/fmt-9.1.0.zip
        URL_MD5 6133244fe8ef6f75c5601e8069b37b04
        CMAKE_ARGS
        -DFMT_TEST=OFF
        -DCMAKE_INSTALL_PREFIX=${DEPENDENCIES_OUTPUT_DIR}
        -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
        -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
        -DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}
        -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
)