if (WIN32)
    # Set paths to help find Ogre on Windows
    set(PAGEDGEOMETRY_CMAKE_ARGS
            -DOgre_INCLUDE_DIRS=${DEPENDENCIES_INCLUDE_DIR}/OGRE
            -DOgre_LIBRARY_DIRS=${DEPENDENCIES_LIB_DIR}
            )
elseif (UNIX)
    # Set pkgconfig path to find Ogre on Linux
    set(PAGEDGEOMETRY_CMAKE_ARGS
            -DPKG_CONFIG_USE_CMAKE_PREFIX_PATH=ON
            )
endif ()

ExternalProject_Add(
        pagedgeometry
        DEPENDS ogre
        GIT_REPOSITORY https://github.com/RigsOfRods/ogre-pagedgeometry.git
        CMAKE_ARGS
        -DPAGEDGEOMETRY_BUILD_SAMPLES=OFF
        -DCMAKE_PREFIX_PATH=${CMAKE_BINARY_DIR}/OgreDependencies/;${DEPENDENCIES_OUTPUT_DIR}
        -DCMAKE_INSTALL_PREFIX=${DEPENDENCIES_OUTPUT_DIR}
        ${PAGEDGEOMETRY_CMAKE_ARGS}
        -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
        -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
)