ExternalProject_Add(
        curl
        URL https://github.com/curl/curl/releases/download/curl-7_86_0/curl-7.86.0.tar.gz
        URL_MD5 f44246e7c13cd91f07095fe63c06353c
        CMAKE_ARGS
        -DCMAKE_INSTALL_PREFIX=${DEPENDENCIES_OUTPUT_DIR}
        -DBUILD_CURL_TESTS=OFF
        -DCMAKE_USE_OPENSSL=OFF
        -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
        -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
        -DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}
        -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
)