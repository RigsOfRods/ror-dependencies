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

if (${CMAKE_VERSION} VERSION_GREATER_EQUAL "3.24")
    cmake_policy(SET CMP0135 NEW)
endif ()


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
option(BUILD_PAGEDGEOMETRY "Build PagedGeometry library" ON)
option(BUILD_CAELUM "Build Caelum library" ON)
option(BUILD_RAPIDJSON "Build RapidJSON library" ON)
option(BUILD_FMT "Build fmt" ON)

# Options with different default values on Windows and Linux
include(CMakeDependentOption)
cmake_dependent_option(BUILD_CURL "Build cURL library" ON WIN32 OFF)

# ------------------------------------------------------------------------------------------------#
# General setup and initialization
# ------------------------------------------------------------------------------------------------#

if (WIN32)
    set(PATCH_TOOL_SCRIPT python ${CMAKE_SOURCE_DIR}/tools/patch.py --verbose)
else ()
    set(PATCH_TOOL_SCRIPT patch -p1 <)
endif ()

include(ExternalProject)
include(FetchContent)

set(FETCHCONTENT_QUIET FALSE)

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
    set(CMAKE_CXX_FLAGS "-std=c++11 ${CMAKE_CXX_FLAGS}")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O2 -Wno-deprecated-declarations -Wno-attributes")
endif ()


# On Linux some packages rely on pkgconfig to be found correctly. Therefore the environment variable
# needs to be set up accordingly. In addition when building depedencies which need to find other
# dependencies (e.g. MyGUI searching for OGRE) PKG_CONFIG_USE_CMAKE_PREFIX_PATH needs to be set to TRUE.
if (UNIX)
    set(ENV{PKG_CONFIG_PATH} "$ENV{PKG_CONFIG_PATH}:${DEPENDENCIES_LIB_DIR}/pkgconfig")
endif ()

if (BUILD_OPENAL)
    add_subdirectory(openal)
endif ()

if (BUILD_CURL)
    add_subdirectory(curl)
endif ()

if (BUILD_RAPIDJSON)
    add_subdirectory(rapidjson)
endif ()

if (BUILD_OGRE)
    add_subdirectory(ogre)
endif ()

if (BUILD_MYGUI)
    add_subdirectory(mygui)
endif ()

if (BUILD_PAGEDGEOMETRY)
    add_subdirectory(pagedgeometry)
endif ()

if (BUILD_CAELUM)
    add_subdirectory(caelum)
endif ()

if (BUILD_SOCKETW)
    add_subdirectory(socketw)
endif ()

if (BUILD_ANGELSCRIPT)
    add_subdirectory(angelscript)
endif ()

if (BUILD_FMT)
    add_subdirectory(fmt)
endif ()
