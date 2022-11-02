ExternalProject_Add(
        angelscript
        URL https://github.com/AnotherFoxGuy/angelscript/archive/39d73b9e5e728c997019ec02cbbfa5bef9cf59e0.tar.gz
        URL_MD5 ffe9a7552d9b188318b270cb8b483bb9
        CMAKE_ARGS
        -DCMAKE_INSTALL_PREFIX=${DEPENDENCIES_OUTPUT_DIR}
        -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
        -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
        -DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}
        -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
)
