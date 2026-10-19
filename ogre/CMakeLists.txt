set(OGRE_GL3PLUS OFF)
set(OGRE_TOOLS ON)
set(OGRE_MACOS_ARGS)
set(OGRE_PATCH_COMMAND ${PATCH_TOOL_SCRIPT} ${CMAKE_CURRENT_SOURCE_DIR}/scriptlexer.patch
    COMMAND ${PATCH_TOOL_SCRIPT} ${CMAKE_CURRENT_SOURCE_DIR}/fixsamples.patch)
if(ROR_MACOS_GL3)
    set(OGRE_GL3PLUS ON)
    set(OGRE_TOOLS OFF)
    set(OGRE_PATCH_COMMAND ${ROR_PATCH_COMMAND} ${CMAKE_CURRENT_SOURCE_DIR}/scriptlexer.patch
        ${CMAKE_CURRENT_SOURCE_DIR}/patches/macos/arm64-sdk.patch)
    set(OGRE_MACOS_ARGS
        -DOGRE_BUILD_RENDERSYSTEM_GL=OFF
        -DOGRE_BUILD_PLUGIN_CG=OFF
        -DOGRE_BUILD_PLUGIN_STBI=ON
        -DOGRE_BUILD_PLUGIN_FREEIMAGE=OFF
        -DOGRE_CONFIG_ENABLE_ZIP=ON
        -DOGRE_BUILD_LIBS_AS_FRAMEWORKS=OFF
        -DOGRE_BUILD_COMPONENT_OVERLAY=ON
        -DOGRE_BUILD_COMPONENT_PAGING=ON
        -DOGRE_BUILD_COMPONENT_RTSHADERSYSTEM=ON
        -DOGRE_BUILD_COMPONENT_MESHLODGENERATOR=ON
        -DOGRE_BUILD_COMPONENT_TERRAIN=ON
        -DOGRE_BUILD_COMPONENT_PROPERTY=OFF
        -DOGRE_BUILD_COMPONENT_BITES=ON
        -DOGRE_INSTALL_SAMPLES=OFF -DOGRE_INSTALL_DOCS=OFF
        -DOGRE_INSTALL_SAMPLES_SOURCE=OFF -DOGRE_INSTALL_TOOLS=OFF
        -DCMAKE_DISABLE_FIND_PACKAGE_SDL2=TRUE
        -DOGRE_BUILD_DEPENDENCIES=OFF
        -DFREETYPE_INCLUDE_DIRS=${DEPENDENCIES_OUTPUT_DIR}/include/freetype2
        -DFREETYPE_LIBRARY_RELEASE=${DEPENDENCIES_OUTPUT_DIR}/lib/libfreetype.dylib
        -DZLIB_LIBRARY=${DEPENDENCIES_OUTPUT_DIR}/lib/libz.dylib
        -DZLIB_INCLUDE_DIR=${DEPENDENCIES_OUTPUT_DIR}/include)
endif()


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

ror_add_dependency(
        ogre
        DEPENDS ${OGRE_DEPS}
        URL https://github.com/OGRECave/ogre/archive/refs/tags/v1.11.6.tar.gz
        URL_MD5 36ca3915aa41a0351bdf08b3953e9ae2
        PATCH_COMMAND ${OGRE_PATCH_COMMAND}
        CMAKE_ARGS
        -DCMAKE_INSTALL_PREFIX=${DEPENDENCIES_OUTPUT_DIR}
        -DOGRE_DEPENDENCIES_DIR=${DEPENDENCIES_OUTPUT_DIR}
        -DDXSDK_DIR=${directx_SOURCE_DIR}
        -DCg_HOME=${DEPENDENCIES_OUTPUT_DIR}
        -DCMAKE_POLICY_VERSION_MINIMUM=3.5
        -DOGRE_BUILD_COMPONENT_BITES=ON
        -DOGRE_BUILD_COMPONENT_CSHARP=OFF
        -DOGRE_BUILD_COMPONENT_JAVA=OFF
        -DOGRE_BUILD_COMPONENT_PYTHON=OFF
        -DOGRE_BUILD_COMPONENT_VOLUME=OFF
        -DOGRE_BUILD_PLUGIN_BSP=OFF
        -DOGRE_BUILD_PLUGIN_PCZ=OFF
        -DOGRE_BUILD_RENDERSYSTEM_GL3PLUS=${OGRE_GL3PLUS}
        -DOGRE_BUILD_SAMPLES=OFF
        -DOGRE_BUILD_TOOLS=${OGRE_TOOLS}
        -DOGRE_RESOURCEMANAGER_STRICT=0
        -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
        -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
        -DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}
        -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
        -DCMAKE_C_COMPILER_LAUNCHER=${CMAKE_C_COMPILER_LAUNCHER}
        -DCMAKE_CXX_COMPILER_LAUNCHER=${CMAKE_CXX_COMPILER_LAUNCHER}
        ${OGRE_MACOS_ARGS}
)


if (WIN32)
    # By default the cg.dll is only installed in the build directory. Therefore manually copy it to the dependency output directory.
    ExternalProject_Add_Step(
            ogre copy_cg
            COMMAND ${CMAKE_COMMAND} -E copy_directory ${cgtoolkit_SOURCE_DIR}/bin64/ ${DEPENDENCIES_BIN_DIR}
            COMMAND ${CMAKE_COMMAND} -E copy_directory ${cgtoolkit_SOURCE_DIR}/include/ ${DEPENDENCIES_INCLUDE_DIR}
            COMMAND ${CMAKE_COMMAND} -E copy_directory ${cgtoolkit_SOURCE_DIR}/lib64/ ${DEPENDENCIES_LIB_DIR}
            DEPENDEES configure
    )
endif ()
if(ROR_MACOS_GL3)
    ExternalProject_Add_Step(ogre rtshader-resources
        COMMAND ${CMAKE_COMMAND} -E copy_directory <SOURCE_DIR>/Samples/Media/RTShaderLib/GLSL
            ${DEPENDENCIES_OUTPUT_DIR}/share/OGRE/Media/RTShaderLib/GLSL
        DEPENDEES install)
endif()

if(ROR_MACOS_GL3)
    ExternalProject_Add_Step(ogre verify-macos-profile
        COMMAND ${CMAKE_COMMAND} -DOGRE_BINARY_DIR=<BINARY_DIR>
            -P ${CMAKE_CURRENT_SOURCE_DIR}/verify-macos.cmake
        DEPENDEES configure DEPENDERS build)
endif()
