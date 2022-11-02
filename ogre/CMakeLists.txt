if (WIN32)

    FetchContent_Declare(
            directx
            URL https://prdownloads.sourceforge.net/rigs-of-rods/DirectX-SDK.zip
            URL_MD5 0bcec91bafb4d6727ca538be40ba2c39
    )
    FetchContent_MakeAvailable(directx)

    set(ENV{DXSDK_DIR} ${directx_SOURCE_DIR})
endif ()

# First build the required dependencies for Ogre itself. They are provided in a dedicated repository.
ExternalProject_Add(
        ogredeps
        URL https://github.com/AnotherFoxGuy/ogredeps/archive/9bb6925e815273ce6bee031e06e4df2a588f8cf3.tar.gz
        URL_MD5 0f79899efa51ad1dd45f379525f3f6ad
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
        URL https://github.com/OGRECave/ogre/archive/refs/tags/v13.5.0.tar.gz
        URL_MD5 d97f33be47f8af873c0e82bb70f0f0f6
        PATCH_COMMAND ${PATCH_TOOL_SCRIPT} ${CMAKE_CURRENT_SOURCE_DIR}/scriptlexer.patch
        CMAKE_ARGS
        -DCMAKE_INSTALL_PREFIX=${DEPENDENCIES_OUTPUT_DIR}
        -DOGRE_DEPENDENCIES_DIR=${DEPENDENCIES_OUTPUT_DIR}
        -DDXSDK_DIR=${directx_SOURCE_DIR}
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
