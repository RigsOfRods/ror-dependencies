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

project( ror-dependencies VERSION 27 )


# ------------------------------------------------------------------------------------------------#
# Options to enable/disable building specific dependencies
# ------------------------------------------------------------------------------------------------#

# Options with same default value on all platforms
option( BUILD_OGRE         "Build Ogre3D graphics library"        ON )
option( BUILD_MYGUI        "Build MyGUI graphical UI library"     ON )
option( BUILD_OPENAL       "Build OpenAL audio library"           ON )
option( BUILD_ANGELSCRIPT  "Build AngelScript scripting library"  ON )
option( BUILD_SOCKETW      "Build SocketW networking library"     ON )
option( BUILD_PAGEDGEOMETRY "Build PagedGeometry library"         ON )
option( BUILD_CAELUM       "Build Caelum library"                 ON )

# Options with different default values on Windows and Linux
include(CMakeDependentOption)
cmake_dependent_option( BUILD_CURL  "Build cURL library"                 ON WIN32 OFF )

# Build options available for Windows only
if( WIN32 )
  option( BUILD_MOFILEREADER "Build MofileReader"                 ON )
  option( BUILD_WXWIDGETS    "Build WxWidgets"                    ON )
endif()



# ------------------------------------------------------------------------------------------------#
# General setup and initialization
# ------------------------------------------------------------------------------------------------#

include(ExternalProject)

# Set the EP_BASE directory property to setup the build directory structure (see the
# ExternalProject documentation for more information)
set_property(DIRECTORY PROPERTY EP_BASE ${CMAKE_BINARY_DIR})


# Determine the name for the output directory where dependencies are going to be installed
if( WIN32 )
  set( DEPENDENCIES_OUTPUT_DIR ${CMAKE_BINARY_DIR}/Dependencies_${CMAKE_SYSTEM_NAME}_${CMAKE_GENERATOR} )
  string( REPLACE " " "-" DEPENDENCIES_OUTPUT_DIR ${DEPENDENCIES_OUTPUT_DIR} )
else()
  set( DEPENDENCIES_OUTPUT_DIR ${CMAKE_BINARY_DIR}/Dependencies_${CMAKE_SYSTEM_NAME} )
endif()

if( MSVC )
  set( DEPENDENCIES_INCLUDE_DIR ${DEPENDENCIES_OUTPUT_DIR}/include )
  set( DEPENDENCIES_LIB_DIR ${DEPENDENCIES_OUTPUT_DIR}/lib )
  set( DEPENDENCIES_BIN_DIR ${DEPENDENCIES_OUTPUT_DIR}/bin )
else()
  set( DEPENDENCIES_INCLUDE_DIR ${DEPENDENCIES_OUTPUT_DIR}/include )
  set( DEPENDENCIES_LIB_DIR ${DEPENDENCIES_OUTPUT_DIR}/lib/${CMAKE_BUILD_TYPE} )
  set( DEPENDENCIES_BIN_DIR ${DEPENDENCIES_OUTPUT_DIR}/bin/${CMAKE_BUILD_TYPE} )
endif()

file( MAKE_DIRECTORY ${DEPENDENCIES_INCLUDE_DIR} )
file( MAKE_DIRECTORY ${DEPENDENCIES_LIB_DIR} )
file( MAKE_DIRECTORY ${DEPENDENCIES_BIN_DIR} )


# Compile flags
if( MSVC )
  set( CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /bigobj" )
endif()

if( UNIX )
  #set( CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -march=native" )
endif()


# On Linux some packages rely on pkgconfig to be found correctly. Therefore the environment variable
# needs to be set up accordingly. In addition when building depedencies which need to find other
# dependencies (e.g. MyGUI searching for OGRE) PKG_CONFIG_USE_CMAKE_PREFIX_PATH needs to be set to TRUE.
if( UNIX )
  set( ENV{PKG_CONFIG_PATH} "$ENV{PKG_CONFIG_PATH}:${DEPENDENCIES_LIB_DIR}/pkgconfig" )
endif()



# ------------------------------------------------------------------------------------------------#
#  cURL
# ------------------------------------------------------------------------------------------------#

if( BUILD_CURL )

  ExternalProject_Add(
    curl
    GIT_REPOSITORY https://github.com/bagder/curl.git
    GIT_TAG curl-7_46_0
    UPDATE_COMMAND ""
    CMAKE_ARGS
      -DCMAKE_INSTALL_PREFIX=${DEPENDENCIES_OUTPUT_DIR}
      -DBUILD_CURL_TESTS=OFF
      -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
      -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
  )

endif()


# ------------------------------------------------------------------------------------------------#
#  Ogre3D
# ------------------------------------------------------------------------------------------------#
# Patching is needed for the D3D9 plugin when compiling with VS2015.
# See http://www.ogre3d.org/forums/viewtopic.php?f=2&t=84008

if( BUILD_OGRE )

  # First build the required dependencies for Ogre itself. They are provided in a dedicated repository.
  ExternalProject_Add(
    ogredeps
    URL https://bitbucket.org/cabalistic/ogredeps/get/7168c50f9d04.zip
    CMAKE_ARGS
      -DOGREDEPS_BUILD_SDL2=OFF
      -DCMAKE_INSTALL_PREFIX=${CMAKE_BINARY_DIR}/OgreDependencies
  )

  if( WIN32 )
    # By default the cg.dll is only installed in the build directory. Therefore manually copy it to the dependency output directory.
    ExternalProject_Add_Step(
      ogredeps copy_cg_dll
      COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_BINARY_DIR}/Build/ogredeps/bin/Release/cg.dll ${DEPENDENCIES_BIN_DIR}/cg.dll
      DEPENDEES build
      )
  endif()

  ExternalProject_Add(
    ogre
    DEPENDS ogredeps
    HG_REPOSITORY https://bitbucket.org/sinbad/ogre
    HG_TAG v1-9
    UPDATE_COMMAND ""
    PATCH_COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_SOURCE_DIR}/patches/OgreTerrain.cpp ${CMAKE_BINARY_DIR}/Source/ogre/Components/Terrain/src/OgreTerrain.cpp  # Fix stackoverflow on terrain load (PR #336)
    COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_SOURCE_DIR}/patches/OgreD3D9Prerequisites.h ${CMAKE_BINARY_DIR}/Source/ogre/RenderSystems/Direct3D9/include/OgreD3D9Prerequisites.h # workaround for VS2015
    CMAKE_ARGS
      -DCMAKE_INSTALL_PREFIX=${DEPENDENCIES_OUTPUT_DIR}
      -DOGRE_DEPENDENCIES_DIR=${CMAKE_BINARY_DIR}/OgreDependencies
      -DOGRE_BUILD_SAMPLES=OFF
      -DOGRE_BUILD_TOOLS=OFF
      -DOGRE_BUILD_RENDERSYSTEM_D3D9=ON
      -DOGRE_BUILD_RENDERSYSTEM_D3D11=OFF  # TODO
      -DOGRE_BUILD_RENDERSYSTEM_GL3PLUS=ON
      -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
      -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
  )

endif()



# ------------------------------------------------------------------------------------------------#
#  MyGUI
# ------------------------------------------------------------------------------------------------#

if( BUILD_MYGUI )

  ExternalProject_Add(
    mygui
    DEPENDS ogre
    GIT_REPOSITORY https://github.com/MyGUI/mygui
    GIT_TAG MyGUI3.2.2
    UPDATE_COMMAND ""
    CMAKE_ARGS
      -DPKG_CONFIG_USE_CMAKE_PREFIX_PATH=ON
      -DCMAKE_PREFIX_PATH=${DEPENDENCIES_OUTPUT_DIR}
      -DCMAKE_INSTALL_PREFIX=${DEPENDENCIES_OUTPUT_DIR}
      -DMYGUI_DEPENDENCIES_DIR=${CMAKE_BINARY_DIR}/OgreDependencies
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
  )

endif()



# ------------------------------------------------------------------------------------------------#
#  OpenAL
# ------------------------------------------------------------------------------------------------#

if( BUILD_OPENAL )

  ExternalProject_Add(
    openal
    GIT_REPOSITORY https://github.com/kcat/openal-soft
    GIT_TAG openal-soft-1.17.1
    UPDATE_COMMAND ""
    CMAKE_ARGS
      -DCMAKE_INSTALL_PREFIX=${DEPENDENCIES_OUTPUT_DIR}
      -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
      -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
  )

endif()



# ------------------------------------------------------------------------------------------------#
#  PagedGeometry
# ------------------------------------------------------------------------------------------------#


if( BUILD_PAGEDGEOMETRY )

	if( WIN32 )
	  # Set paths to help find Ogre on Windows
	  set( PAGEDGEOMETRY_CMAKE_ARGS
		-DOgre_INCLUDE_DIRS=${DEPENDENCIES_INCLUDE_DIR}/OGRE
		-DOgre_LIBRARY_DIRS=${DEPENDENCIES_LIB_DIR}
	  )
	elseif( UNIX )
	  # Set pkgconfig path to find Ogre on Linux
	  set( PAGEDGEOMETRY_CMAKE_ARGS
		  -DPKG_CONFIG_USE_CMAKE_PREFIX_PATH=ON
	  )
	endif()

	ExternalProject_Add(
    paged-geometry
    DEPENDS ogre
    GIT_REPOSITORY https://github.com/RigsOfRods/ogre-pagedgeometry.git
    GIT_TAG v1.2.0
    UPDATE_COMMAND ""
    CMAKE_ARGS
      -DCMAKE_PREFIX_PATH=${DEPENDENCIES_OUTPUT_DIR}
      -DCMAKE_INSTALL_PREFIX=${DEPENDENCIES_OUTPUT_DIR}
	  ${PAGEDGEOMETRY_CMAKE_ARGS}
      -DPAGEDGEOMETRY_BUILD_SAMPLES=OFF
      -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
      -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
    )

endif()



# ------------------------------------------------------------------------------------------------#
#  Caelum
# ------------------------------------------------------------------------------------------------#

if( BUILD_CAELUM )

  if( WIN32 )
    # Set paths to help find Ogre on Windows
    set( PAGEDGEOMETRY_CMAKE_ARGS
	  -DOgre_INCLUDE_DIRS=${DEPENDENCIES_INCLUDE_DIR}/OGRE
	  -DOgre_LIBRARY_DIRS=${DEPENDENCIES_LIB_DIR}
	  -DOgre_LIBRARIES=${DEPENDENCIES_LIB_DIR}/OgreMain
    )
  elseif( UNIX )
    # Set pkgconfig path on Linux
    set( PAGEDGEOMETRY_CMAKE_ARGS
        -DPKG_CONFIG_USE_CMAKE_PREFIX_PATH=ON
    )
  endif()

  ExternalProject_Add(
    caelum
    DEPENDS ogre
	# TODO temporarily use alternative sources which build without Boost
    #GIT_REPOSITORY https://github.com/RigsOfRods/ogre-caelum.git
	GIT_REPOSITORY https://github.com/tritonas00/ogre-caelum.git
	GIT_TAG boost-cleanups
    UPDATE_COMMAND ""
    CMAKE_ARGS
      -DPKG_CONFIG_USE_CMAKE_PREFIX_PATH=ON
      -DCMAKE_PREFIX_PATH=${DEPENDENCIES_OUTPUT_DIR}
      -DCMAKE_INSTALL_PREFIX=${DEPENDENCIES_OUTPUT_DIR}
	  ${PAGEDGEOMETRY_CMAKE_ARGS}
      -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
      -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
    )
endif()



# # ------------------------------------------------------------------------------------------------#
# #  SocketW
# # ------------------------------------------------------------------------------------------------#

if( BUILD_SOCKETW )

  set( SOCKETW_SOURCE_DIR ${CMAKE_BINARY_DIR}/Source/socketw )

  ExternalProject_Add(
    socketw
    GIT_REPOSITORY https://github.com/RigsOfRods/socketw.git
    UPDATE_COMMAND ""
    PATCH_COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_SOURCE_DIR}/patches/sw_config.h ${SOCKETW_SOURCE_DIR}/src/sw_config.h
    CMAKE_ARGS
      -DCMAKE_INSTALL_PREFIX=${DEPENDENCIES_OUTPUT_DIR}
      -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
      -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
  )

endif()



# ------------------------------------------------------------------------------------------------#
#  Angelscript
# ------------------------------------------------------------------------------------------------#

if( BUILD_ANGELSCRIPT )

  set( ANGELSCRIPT_BUILD_DIR ${CMAKE_BINARY_DIR}/Build/angelscript )
  set( ANGELSCRIPT_SOURCE_DIR ${CMAKE_BINARY_DIR}/Source/angelscript )

  ExternalProject_Add(
	angelscript-download
	URL http://angelcode.com/angelscript/sdk/files/angelscript_2.22.1.zip
    SOURCE_DIR ${ANGELSCRIPT_SOURCE_DIR}
	CONFIGURE_COMMAND ""
	BUILD_COMMAND ""
	INSTALL_COMMAND ""
  )

  ExternalProject_Add(
	angelscript
	DEPENDS angelscript-download
	DOWNLOAD_COMMAND ""
    SOURCE_DIR ${ANGELSCRIPT_SOURCE_DIR}/angelscript/projects/cmake
	BUILD_IN_SOURCE 1
    CMAKE_ARGS
      -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
      -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
    INSTALL_COMMAND ${CMAKE_COMMAND} -E copy_directory ${ANGELSCRIPT_SOURCE_DIR}/angelscript/include ${DEPENDENCIES_INCLUDE_DIR}
	COMMAND	${CMAKE_COMMAND} -E copy_directory ${ANGELSCRIPT_SOURCE_DIR}/angelscript/lib ${DEPENDENCIES_LIB_DIR}
  )

endif()



# ------------------------------------------------------------------------------------------------#
#  Mofilereader
# ------------------------------------------------------------------------------------------------#

if( WIN32 AND BUILD_MOFILEREADER )

  set( MOFILEREADER_SOURCE_DIR ${CMAKE_BINARY_DIR}/Source/mofilereader )

  ExternalProject_Add(
	mofilereader-download
	URL https://bitbucket.org/scorcher24/mofilereader/get/e86fcb882723.zip
    SOURCE_DIR ${MOFILEREADER_SOURCE_DIR}
	CONFIGURE_COMMAND ""
	BUILD_COMMAND ""
	INSTALL_COMMAND ""
  )

  ExternalProject_Add(
	mofilereader
	DEPENDS mofilereader-download
	DOWNLOAD_COMMAND ""
    SOURCE_DIR ${MOFILEREADER_SOURCE_DIR}/build
	BUILD_IN_SOURCE 1
    CMAKE_ARGS
      -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
      -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
    INSTALL_COMMAND ${CMAKE_COMMAND} -E copy_directory ${MOFILEREADER_SOURCE_DIR}/include ${DEPENDENCIES_INCLUDE_DIR}
	COMMAND	${CMAKE_COMMAND} -E copy_directory ${MOFILEREADER_SOURCE_DIR}/lib ${DEPENDENCIES_LIB_DIR}
  )

endif()		  



# ------------------------------------------------------------------------------------------------#
#  WxWidgets
# ------------------------------------------------------------------------------------------------#
# Instead of actually building WxWidgets, simply download the precompiled binaries for
# Visual Studio 2015.
# For Linux WxWidgets should be installed using the distros package management.

if( WIN32 AND BUILD_WXWIDGETS )

  set( WXWIDGETS_SOURCE_DIR ${CMAKE_BINARY_DIR}/Source/wxwidgets )
  
  ExternalProject_Add(
	wxwidgets-header
	URL https://github.com/wxWidgets/wxWidgets/releases/download/v3.1.0/wxWidgets-3.1.0-headers.7z
    SOURCE_DIR ${WXWIDGETS_SOURCE_DIR}/headers
	CONFIGURE_COMMAND ""
	BUILD_COMMAND ""
	INSTALL_COMMAND ${CMAKE_COMMAND} -E copy_directory ${WXWIDGETS_SOURCE_DIR}/headers ${DEPENDENCIES_INCLUDE_DIR}
  )

  ExternalProject_Add(
	wxwidgets-dev
	URL https://github.com/wxWidgets/wxWidgets/releases/download/v3.1.0/wxMSW-3.1.0_vc140_Dev.7z
    SOURCE_DIR ${WXWIDGETS_SOURCE_DIR}/dev
	CONFIGURE_COMMAND ""
	BUILD_COMMAND ""
	INSTALL_COMMAND ${CMAKE_COMMAND} -E copy_directory ${WXWIDGETS_SOURCE_DIR}/dev/vc140_dll ${DEPENDENCIES_LIB_DIR}/vc_dll
  )

  ExternalProject_Add(
	wxwidgets-dll
	URL https://github.com/wxWidgets/wxWidgets/releases/download/v3.1.0/wxMSW-3.1.0_vc140_ReleaseDLL.7z
    SOURCE_DIR ${WXWIDGETS_SOURCE_DIR}/dll
	CONFIGURE_COMMAND ""
	BUILD_COMMAND ""
	INSTALL_COMMAND ${CMAKE_COMMAND} -E copy_directory ${WXWIDGETS_SOURCE_DIR}/dll/vc140_dll ${DEPENDENCIES_BIN_DIR}/vc_dll
  )
  
endif()		  
