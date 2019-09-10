# The MIT License (MIT)
#
# Copyright (c) 2016 Fabian Killus
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

cmake_minimum_required(VERSION 3.2)


# ------------------------------------------------------------------------------------------------#
# The intention of this script is to provide a simple solution for building all dependencies
# required for Rigs of Rods. It is in fact a super- or meta-build project which makes use of
# the ExternalProject module of CMake to build the individual dependencies.
# ------------------------------------------------------------------------------------------------#

project(ror-dependencies VERSION 30)


# ------------------------------------------------------------------------------------------------#
# Options to enable/disable building specific dependencies
# ------------------------------------------------------------------------------------------------#

# Options with same default value on all platforms
option(BUILD_OGRE "Build Ogre3D graphics library" ON)
option(BUILD_MYGUI "Build MyGUI graphical UI library" ON)
option(BUILD_OPENAL "Build OpenAL audio library" ON)
option(BUILD_ANGELSCRIPT "Build AngelScript scripting library" ON)
option(BUILD_SOCKETW "Build SocketW networking library" ON)
option(BUILD_CAELUM "Build Caelum library" ON)
option(BUILD_RAPIDJSON "Build RapidJSON library" ON)
option(BUILD_MOFILEREADER "Build MofileReader" ON)

# Options with different default values on Windows and Linux
include(CMakeDependentOption)
cmake_dependent_option(BUILD_CURL "Build cURL library" ON WIN32 OFF)

# ------------------------------------------------------------------------------------------------#
# General setup and initialization
# ------------------------------------------------------------------------------------------------#

include(ExternalProject)

# Set the EP_BASE directory property to setup the build directory structure (see the
# ExternalProject documentation for more information)
set_property(DIRECTORY PROPERTY EP_BASE ${CMAKE_BINARY_DIR})


# Determine the name for the output directory where dependencies are going to be installed
if (WIN32)
    set(DEPENDENCIES_OUTPUT_DIR ${CMAKE_BINARY_DIR}/Dependencies_${CMAKE_SYSTEM_NAME}_${CMAKE_GENERATOR})
    string(REPLACE " " "-" DEPENDENCIES_OUTPUT_DIR ${DEPENDENCIES_OUTPUT_DIR})
else ()
    set(DEPENDENCIES_OUTPUT_DIR ${CMAKE_BINARY_DIR}/Dependencies_${CMAKE_SYSTEM_NAME})
endif ()

if (MSVC)
    set(DEPENDENCIES_INCLUDE_DIR ${DEPENDENCIES_OUTPUT_DIR}/include)
    set(DEPENDENCIES_LIB_DIR ${DEPENDENCIES_OUTPUT_DIR}/lib)
    set(DEPENDENCIES_BIN_DIR ${DEPENDENCIES_OUTPUT_DIR}/bin)
else ()
    set(DEPENDENCIES_INCLUDE_DIR ${DEPENDENCIES_OUTPUT_DIR}/include)
    set(DEPENDENCIES_LIB_DIR ${DEPENDENCIES_OUTPUT_DIR}/lib/${CMAKE_BUILD_TYPE})
    set(DEPENDENCIES_BIN_DIR ${DEPENDENCIES_OUTPUT_DIR}/bin/${CMAKE_BUILD_TYPE})
endif ()

file(MAKE_DIRECTORY ${DEPENDENCIES_INCLUDE_DIR})
file(MAKE_DIRECTORY ${DEPENDENCIES_LIB_DIR})
file(MAKE_DIRECTORY ${DEPENDENCIES_BIN_DIR})


# Compile flags
if (MSVC)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /bigobj /w")
endif ()

if (UNIX)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O2 -Wno-deprecated-declarations -Wno-attributes")
endif ()


# On Linux some packages rely on pkgconfig to be found correctly. Therefore the environment variable
# needs to be set up accordingly. In addition when building depedencies which need to find other
# dependencies (e.g. MyGUI searching for OGRE) PKG_CONFIG_USE_CMAKE_PREFIX_PATH needs to be set to TRUE.
if (UNIX)
    set(ENV{PKG_CONFIG_PATH} "$ENV{PKG_CONFIG_PATH}:${DEPENDENCIES_LIB_DIR}/pkgconfig")
endif ()


# ------------------------------------------------------------------------------------------------#
#  OpenAL
# ------------------------------------------------------------------------------------------------#

if (BUILD_OPENAL)

    ExternalProject_Add(
            openal
            GIT_REPOSITORY https://github.com/kcat/openal-soft.git
            CMAKE_ARGS
            -DCMAKE_INSTALL_PREFIX=${DEPENDENCIES_OUTPUT_DIR}
            -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
            -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
            -DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}
            -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
    )

endif ()


# ------------------------------------------------------------------------------------------------#
#  cURL
# ------------------------------------------------------------------------------------------------#

if (BUILD_CURL)

    ExternalProject_Add(
            curl
            GIT_REPOSITORY https://github.com/bagder/curl.git
            GIT_TAG curl-7_46_0
            GIT_SHALLOW TRUE
            GIT_PROGRESS TRUE
            CMAKE_ARGS
            -DCMAKE_INSTALL_PREFIX=${DEPENDENCIES_OUTPUT_DIR}
            -DBUILD_CURL_TESTS=OFF
            -DCMAKE_USE_OPENSSL=OFF
            -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
            -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
            -DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}
            -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
    )

endif ()


# ------------------------------------------------------------------------------------------------#
#  RapidJSON
# ------------------------------------------------------------------------------------------------#
if (BUILD_RAPIDJSON)
    ExternalProject_Add(
            RapidJSON
            GIT_REPOSITORY https://github.com/miloyip/rapidjson
            CMAKE_ARGS
            -DCMAKE_INSTALL_PREFIX=${DEPENDENCIES_OUTPUT_DIR}
            -DINCLUDE_INSTALL_DIR=${DEPENDENCIES_OUTPUT_DIR}/include # rapidjson will add "rapidjson" subdirectory
            -DRAPIDJSON_BUILD_DOC=NO
            -DRAPIDJSON_BUILD_EXAMPLES=NO
            -DRAPIDJSON_BUILD_TESTS=NO
            -DRAPIDJSON_BUILD_THIRDPARTY_GTEST=NO
            -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
            -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
            -DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}
            -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
    )
endif ()

# ------------------------------------------------------------------------------------------------#
#  Ogre3D
# ------------------------------------------------------------------------------------------------#

if (BUILD_OGRE)

    # First build the required dependencies for Ogre itself. They are provided in a dedicated repository.
    ExternalProject_Add(
            ogredeps
            URL https://bitbucket.org/cabalistic/ogredeps/get/default.zip
            CMAKE_ARGS
            -DOGREDEPS_BUILD_AMD_QBS=OFF
            -DOGREDEPS_BUILD_NVIDIA_NVAPI=OFF
            -DOGREDEPS_BUILD_RAPIDJSON=OFF
            -DOGREDEPS_BUILD_REMOTERY=OFF
            -DOGREDEPS_BUILD_SDL2=OFF
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

        ExternalProject_Add(
                ogre
                DEPENDS ogredeps
                GIT_REPOSITORY https://github.com/OGRECave/ogre.git
                GIT_TAG v1.11.6
                PATCH_COMMAND patch --strip=1 --input=${CMAKE_SOURCE_DIR}/patches/scriptlexer.patch
                CMAKE_ARGS
                -DCMAKE_INSTALL_PREFIX=${DEPENDENCIES_OUTPUT_DIR}
                -DOGRE_DEPENDENCIES_DIR=${DEPENDENCIES_OUTPUT_DIR}
                -DFREETYPE_LIBRARY=${DEPENDENCIES_OUTPUT_DIR}/lib/Release/freetype.lib
                -DZLIB_LIBRARY=${DEPENDENCIES_OUTPUT_DIR}/lib/Release/zlib.lib
                -DOGRE_BUILD_SAMPLES=OFF
                -DOGRE_BUILD_TOOLS=ON
                -DOGRE_BUILD_COMPONENT_BITES=ON
                -DOGRE_BUILD_COMPONENT_VOLUME=OFF
                -DOGRE_BUILD_PLUGIN_BSP=OFF
                -DOGRE_BUILD_PLUGIN_PCZ=OFF
                -DOGRE_BUILD_RENDERSYSTEM_D3D9=ON
                -DOGRE_BUILD_RENDERSYSTEM_D3D11=OFF  # TODO
                -DOGRE_BUILD_RENDERSYSTEM_GL3PLUS=OFF
                -DOGRE_RESOURCEMANAGER_STRICT=0
                -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
                -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
                -DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}
                -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
                -DDirectX9_D3DX9_LIBRARY=${CMAKE_SOURCE_DIR}/win32-directx/lib/x86/d3dx9.lib  # Add bundled DirectX libs
                -DDirectX9_DXERR_LIBRARY=${CMAKE_SOURCE_DIR}/win32-directx/lib/x86/DxErr.lib  # Add bundled DirectX libs
                -DDirectX9_BUNDLED_INCLUDE_DIR=${CMAKE_SOURCE_DIR}/win32-directx/include      # Add bundled DirectX headers; requires modified CMakeLists.txt
        )
    else ()
        ExternalProject_Add(
                ogre
                DEPENDS ogredeps
                GIT_REPOSITORY https://github.com/OGRECave/ogre.git
                GIT_TAG v1.11.6
                PATCH_COMMAND patch -p1 < ${CMAKE_SOURCE_DIR}/patches/scriptlexer.patch
                CMAKE_ARGS
                -DCMAKE_INSTALL_PREFIX=${DEPENDENCIES_OUTPUT_DIR}
                -DOGRE_DEPENDENCIES_DIR=${DEPENDENCIES_OUTPUT_DIR}
                -DOGRE_BUILD_SAMPLES=OFF
                -DOGRE_BUILD_TOOLS=ON
                -DOGRE_BUILD_COMPONENT_BITES=ON
                -DOGRE_BUILD_COMPONENT_VOLUME=OFF
                -DOGRE_BUILD_PLUGIN_BSP=OFF
                -DOGRE_BUILD_PLUGIN_PCZ=OFF
                -DOGRE_BUILD_RENDERSYSTEM_GL3PLUS=OFF
                -DOGRE_RESOURCEMANAGER_STRICT=0
                -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
                -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
                -DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}
                -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
        )
    endif ()


endif ()


# ------------------------------------------------------------------------------------------------#
#  MyGUI
# ------------------------------------------------------------------------------------------------#

if (BUILD_MYGUI)

    ExternalProject_Add(
            mygui
            DEPENDS ogre
            GIT_REPOSITORY https://github.com/MyGUI/mygui.git
            GIT_TAG 07da0620e0d835346452b02b7b1ba7c583429736
            CMAKE_ARGS
            -DPKG_CONFIG_USE_CMAKE_PREFIX_PATH=ON
            -DCMAKE_PREFIX_PATH=${DEPENDENCIES_OUTPUT_DIR}
            -DCMAKE_INSTALL_PREFIX=${DEPENDENCIES_OUTPUT_DIR}
            -DMYGUI_DEPENDENCIES_DIR=${DEPENDENCIES_OUTPUT_DIR}
            -DOGRE_SOURCE_DIR=${CMAKE_BINARY_DIR}/Source/ogre
            -DOGRE_BUILD=${DEPENDENCIES_OUTPUT_DIR}
            -DCMAKE_MODULE_PATH=${CMAKE_MODULE_PATH}
            -DMYGUI_BUILD_DEMOS=OFF
            -DMYGUI_BUILD_DOCS=OFF
            -DMYGUI_BUILD_TEST_APP=OFF
            -DMYGUI_BUILD_TOOLS=OFF
            -DMYGUI_BUILD_PLUGINS=NO
            -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
            -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
            -DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}
            -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
    )

endif ()


# ------------------------------------------------------------------------------------------------#
#  Caelum
# ------------------------------------------------------------------------------------------------#

if (BUILD_CAELUM)

    if (WIN32)
        # Set paths to help find Ogre on Windows
        set(CAELUM_CMAKE_ARGS
                -DOgre_INCLUDE_DIRS=${DEPENDENCIES_INCLUDE_DIR}/OGRE
                -DOgre_LIBRARY_DIRS=${DEPENDENCIES_LIB_DIR}
                -DOgre_LIBRARIES=${DEPENDENCIES_LIB_DIR}/OgreMain
                )
    elseif (UNIX)
        # Set pkgconfig path on Linux
        set(CAELUM_CMAKE_ARGS
                -DPKG_CONFIG_USE_CMAKE_PREFIX_PATH=ON
                )
    endif ()

    ExternalProject_Add(
            caelum
            DEPENDS ogre
            GIT_REPOSITORY https://github.com/RigsOfRods/ogre-caelum
            CMAKE_ARGS
            -DCaelum_BUILD_SAMPLES=FALSE
            -DINSTALL_OGRE_PLUGIN=OFF
            -DCMAKE_PREFIX_PATH=${DEPENDENCIES_OUTPUT_DIR}
            -DCMAKE_INSTALL_PREFIX=${DEPENDENCIES_OUTPUT_DIR}
            ${CAELUM_CMAKE_ARGS}
            -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
            -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
            -DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}
            -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
    )

    if (WIN32)
        ExternalProject_Add_Step(
                caelum patch_pluginscfg
                COMMAND ${CMAKE_COMMAND} -E echo Plugin=Caelum >> ${DEPENDENCIES_BIN_DIR}/release/plugins.cfg
                DEPENDEES install
        )
    endif ()

endif ()

# ------------------------------------------------------------------------------------------------#
#  SocketW
# ------------------------------------------------------------------------------------------------#

if (BUILD_SOCKETW)

    set(SOCKETW_SOURCE_DIR ${CMAKE_BINARY_DIR}/Source/socketw)

    ExternalProject_Add(
            socketw
            GIT_REPOSITORY https://github.com/RigsOfRods/socketw.git
            PATCH_COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_SOURCE_DIR}/patches/sw_config.h ${SOCKETW_SOURCE_DIR}/src/sw_config.h
            CMAKE_ARGS
            -DCMAKE_INSTALL_PREFIX=${DEPENDENCIES_OUTPUT_DIR}
            -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
            -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
            -DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}
            -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
    )

endif ()


# ------------------------------------------------------------------------------------------------#
#  Angelscript
# ------------------------------------------------------------------------------------------------#

if (BUILD_ANGELSCRIPT)

    set(ANGELSCRIPT_BUILD_DIR ${CMAKE_BINARY_DIR}/Build/angelscript)
    set(ANGELSCRIPT_SOURCE_DIR ${CMAKE_BINARY_DIR}/Source/angelscript)

    ExternalProject_Add(
            angelscript
            GIT_REPOSITORY https://github.com/AnotherFoxGuy/angelscript.git
            GIT_TAG c0e460930d4cb73bcfbeb253cd5611d7156b1cce
            CMAKE_ARGS
            -DCMAKE_INSTALL_PREFIX=${DEPENDENCIES_OUTPUT_DIR}
            -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
            -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
            -DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}
            -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
    )

endif ()


# ------------------------------------------------------------------------------------------------#
#  Mofilereader
# ------------------------------------------------------------------------------------------------#

if (BUILD_MOFILEREADER)

    set(MOFILEREADER_SOURCE_DIR ${CMAKE_BINARY_DIR}/Source/mofilereader)

    ExternalProject_Add(
            mofilereader-download
            GIT_REPOSITORY https://github.com/AnotherFoxGuy/MofileReader
            SOURCE_DIR ${MOFILEREADER_SOURCE_DIR}
            CONFIGURE_COMMAND ""
            BUILD_COMMAND ""
            INSTALL_COMMAND ""
    )

    if (WIN32)

        ExternalProject_Add(
            mofilereader
            DEPENDS mofilereader-download
            DOWNLOAD_COMMAND ""
            SOURCE_DIR ${MOFILEREADER_SOURCE_DIR}
            BUILD_IN_SOURCE 1
            CMAKE_ARGS
            -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
            -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
            -DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}
            -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
            INSTALL_COMMAND ${CMAKE_COMMAND} -E copy_directory ${MOFILEREADER_SOURCE_DIR}/include ${DEPENDENCIES_INCLUDE_DIR}
            COMMAND ${CMAKE_COMMAND} -E copy_directory ${MOFILEREADER_SOURCE_DIR}/${CMAKE_BUILD_TYPE} ${DEPENDENCIES_LIB_DIR}
        )

    else ()
 
       ExternalProject_Add(
            mofilereader
            DEPENDS mofilereader-download
            DOWNLOAD_COMMAND ""
            SOURCE_DIR ${MOFILEREADER_SOURCE_DIR}
            BUILD_IN_SOURCE 1
            CMAKE_ARGS
            -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
            -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
            -DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}
            -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
            INSTALL_COMMAND ${CMAKE_COMMAND} -E copy_directory ${MOFILEREADER_SOURCE_DIR}/include ${DEPENDENCIES_INCLUDE_DIR}
            COMMAND ${CMAKE_COMMAND} -E copy ${MOFILEREADER_SOURCE_DIR}/libmoFileReader.a ${DEPENDENCIES_OUTPUT_DIR}/lib
            COMMAND ${CMAKE_COMMAND} -E copy ${MOFILEREADER_SOURCE_DIR}/moReader ${DEPENDENCIES_OUTPUT_DIR}/bin
        )

     endif ()

endif ()
