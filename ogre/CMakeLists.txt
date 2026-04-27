
if (WIN32)
        FetchContent_Declare(
                cgtoolkit
                URL https://github.com/AnotherFoxGuy/cg-toolkit/archive/refs/tags/3.1.tar.gz
                URL_MD5 15d596a54850ba786fe5102f25870801
        )
        FetchContent_MakeAvailable(cgtoolkit)
        FetchContent_Declare(
                directx
                URL https://prdownloads.sourceforge.net/rigs-of-rods/DirectX-SDK.zip
                URL_MD5 0bcec91bafb4d6727ca538be40ba2c39
        )
        FetchContent_MakeAvailable(directx)
endif ()

ExternalProject_Add(
        ogre
        DEPENDS ${OGRE_DEPS}
        URL https://github.com/OGRECave/ogre/archive/refs/tags/v1.11.6.tar.gz
        URL_MD5 36ca3915aa41a0351bdf08b3953e9ae2
        PATCH_COMMAND ${PATCH_TOOL_SCRIPT} ${CMAKE_CURRENT_SOURCE_DIR}/scriptlexer.patch
        CMAKE_ARGS
        -DCMAKE_INSTALL_PREFIX=${DEPENDENCIES_OUTPUT_DIR}
        -DOGRE_DEPENDENCIES_DIR=${DEPENDENCIES_OUTPUT_DIR}
        -DDXSDK_DIR=${directx_SOURCE_DIR}
        -DCg_HOME=${cgtoolkit_SOURCE_DIR}
        -DCMAKE_POLICY_VERSION_MINIMUM=3.5
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
        -DCMAKE_C_COMPILER_LAUNCHER=${CMAKE_C_COMPILER_LAUNCHER}
        -DCMAKE_CXX_COMPILER_LAUNCHER=${CMAKE_CXX_COMPILER_LAUNCHER}
)


if (WIN32)
    # By default the cg.dll is only installed in the build directory. Therefore manually copy it to the dependency output directory.
    ExternalProject_Add_Step(
            ogre copy_cg
            COMMAND ${CMAKE_COMMAND} -E copy_directory ${cgtoolkit_SOURCE_DIR}/bin/ ${DEPENDENCIES_BIN_DIR}
            DEPENDEES build
    )
endif ()