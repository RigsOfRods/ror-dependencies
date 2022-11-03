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
        URL https://github.com/OGRECave/ogre-caelum/archive/4bd1b0581d55896d37922483981582661ca557de.tar.gz
        URL_MD5 e6378f99faf131624b364829de9d0b8a
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