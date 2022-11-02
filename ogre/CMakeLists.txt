# First build the required dependencies for Ogre itself. They are provided in a dedicated repository.
ExternalProject_Add(
        ogredeps
        URL https://github.com/AnotherFoxGuy/ogredeps/archive/17f4c583c82559074a96f1436670a4f10961b9d9.tar.gz
        URL_MD5 d5425da9f4ffa9f24dd021e32a8665ad
        CMAKE_ARGS
        -DOGREDEPS_BUILD_AMD_QBS=OFF
        -DOGREDEPS_BUILD_NVIDIA_NVAPI=OFF
        -DOGREDEPS_BUILD_RAPIDJSON=OFF
        -DOGREDEPS_BUILD_REMOTERY=OFF
        -DOGREDEPS_BUILD_SDL2=OFF
        -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
        -DCMAKE_INSTALL_PREFIX=${DEPENDENCIES_OUTPUT_DIR}
        -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
        -DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}
        -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
)

if (WIN32)

    # By default the cg.dll is only installed in the build directory. Therefore manually copy it to the dependency output directory.
    ExternalProject_Add_Step(
            ogredeps copy_cg_dll
            COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_BINARY_DIR}/Build/ogredeps/bin/Release/cg.dll ${DEPENDENCIES_BIN_DIR}/cg.dll
            DEPENDEES build
    )

endif ()
ExternalProject_Add(
        ogre
        DEPENDS ogredeps
        URL https://github.com/OGRECave/ogre/archive/refs/tags/v1.11.6.tar.gz
        URL_MD5 36ca3915aa41a0351bdf08b3953e9ae2
        PATCH_COMMAND git apply ${CMAKE_CURRENT_SOURCE_DIR}/scriptlexer.patch
        CMAKE_ARGS
        -DCMAKE_INSTALL_PREFIX=${DEPENDENCIES_OUTPUT_DIR}
        -DOGRE_DEPENDENCIES_DIR=${DEPENDENCIES_OUTPUT_DIR}
        -DOGRE_BUILD_COMPONENT_BITES=ON
        -DOGRE_BUILD_COMPONENT_CSHARP=OFF
        -DOGRE_BUILD_COMPONENT_JAVA=OFF
        -DOGRE_BUILD_COMPONENT_PYTHON=OFF
        -DOGRE_BUILD_COMPONENT_VOLUME=OFF
        -DOGRE_BUILD_PLUGIN_BSP=OFF
        -DOGRE_BUILD_PLUGIN_PCZ=OFF
        -DOGRE_BUILD_RENDERSYSTEM_GL3PLUS=OFF
        -DOGRE_BUILD_SAMPLES=OFF
        -DOGRE_BUILD_TOOLS=ON
        -DOGRE_RESOURCEMANAGER_STRICT=0
        -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
        -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
        -DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}
        -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
)
