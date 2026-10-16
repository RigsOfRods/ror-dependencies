# The default recipes remain unchanged unless this explicit profile is selected.
if(ROR_MACOS_GL3)
    if(NOT CMAKE_OSX_ARCHITECTURES OR NOT CMAKE_OSX_SYSROOT OR NOT CMAKE_OSX_DEPLOYMENT_TARGET)
        message(FATAL_ERROR "Set CMAKE_OSX_ARCHITECTURES, CMAKE_OSX_SYSROOT and CMAKE_OSX_DEPLOYMENT_TARGET explicitly")
    endif()
    if(NOT CMAKE_BUILD_TYPE OR CMAKE_CONFIGURATION_TYPES)
        message(FATAL_ERROR "Use a single-configuration generator and set CMAKE_BUILD_TYPE explicitly")
    endif()
    foreach(feature OGRE MYGUI OPENAL ANGELSCRIPT SOCKETW PAGEDGEOMETRY CAELUM RAPIDJSON FMT OIS CURL)
        if(NOT BUILD_${feature})
            message(FATAL_ERROR "The macOS GL3 profile requires BUILD_${feature}=ON")
        endif()
    endforeach()
    enable_language(ASM)
    file(READ "${CMAKE_SOURCE_DIR}/cmake/macos-sources.json" ROR_MACOS_SOURCES)
    # EP's LIST_SEPARATOR preserves multi-architecture and multi-prefix values.
    set(project_includes ${CMAKE_PROJECT_TOP_LEVEL_INCLUDES} "${CMAKE_SOURCE_DIR}/cmake/MacOSExternalProject.cmake")
    string(REPLACE ";" "|" project_includes "${project_includes}")
    set(ROR_MACOS_CMAKE_ARGS
        "-DCMAKE_INSTALL_PREFIX:PATH=${DEPENDENCIES_OUTPUT_DIR}"
        "-DCMAKE_PREFIX_PATH:STRING=${DEPENDENCIES_OUTPUT_DIR}"
        "-DCMAKE_IGNORE_PREFIX_PATH:STRING=/opt/homebrew|/usr/local"
        "-DCMAKE_PROJECT_TOP_LEVEL_INCLUDES:STRING=${project_includes}"
        -DCMAKE_FIND_USE_PACKAGE_REGISTRY:BOOL=OFF
        -DCMAKE_FIND_USE_SYSTEM_PACKAGE_REGISTRY:BOOL=OFF
        -DBUILD_SHARED_LIBS:BOOL=ON
        -DCMAKE_INSTALL_NAME_DIR:STRING=@rpath
        "-DCMAKE_SHARED_LINKER_FLAGS:STRING=${CMAKE_SHARED_LINKER_FLAGS} -Wl,-headerpad_max_install_names"
        "-DCMAKE_MODULE_LINKER_FLAGS:STRING=${CMAKE_MODULE_LINKER_FLAGS} -Wl,-headerpad_max_install_names"
        -DCMAKE_POLICY_VERSION_MINIMUM:STRING=3.5)
    foreach(var CMAKE_OSX_ARCHITECTURES CMAKE_OSX_SYSROOT CMAKE_OSX_DEPLOYMENT_TARGET
            CMAKE_BUILD_TYPE CMAKE_C_COMPILER CMAKE_CXX_COMPILER CMAKE_ASM_COMPILER
            CMAKE_C_FLAGS CMAKE_CXX_FLAGS CMAKE_ASM_FLAGS
            CMAKE_C_FLAGS_RELEASE CMAKE_CXX_FLAGS_RELEASE CMAKE_ASM_FLAGS_RELEASE
            CMAKE_C_FLAGS_DEBUG CMAKE_CXX_FLAGS_DEBUG CMAKE_ASM_FLAGS_DEBUG
            CMAKE_C_FLAGS_RELWITHDEBINFO CMAKE_CXX_FLAGS_RELWITHDEBINFO CMAKE_ASM_FLAGS_RELWITHDEBINFO
            CMAKE_C_FLAGS_MINSIZEREL CMAKE_CXX_FLAGS_MINSIZEREL CMAKE_ASM_FLAGS_MINSIZEREL
            CMAKE_EXE_LINKER_FLAGS
            CMAKE_SHARED_LINKER_FLAGS_RELEASE CMAKE_MODULE_LINKER_FLAGS_RELEASE CMAKE_EXE_LINKER_FLAGS_RELEASE
            CMAKE_SHARED_LINKER_FLAGS_DEBUG CMAKE_MODULE_LINKER_FLAGS_DEBUG CMAKE_EXE_LINKER_FLAGS_DEBUG
            CMAKE_SHARED_LINKER_FLAGS_RELWITHDEBINFO CMAKE_MODULE_LINKER_FLAGS_RELWITHDEBINFO CMAKE_EXE_LINKER_FLAGS_RELWITHDEBINFO
            CMAKE_SHARED_LINKER_FLAGS_MINSIZEREL CMAKE_MODULE_LINKER_FLAGS_MINSIZEREL CMAKE_EXE_LINKER_FLAGS_MINSIZEREL
            CMAKE_C_COMPILER_LAUNCHER CMAKE_CXX_COMPILER_LAUNCHER)
        if(DEFINED ${var})
            string(REPLACE ";" "|" value "${${var}}")
            list(APPEND ROR_MACOS_CMAKE_ARGS "-D${var}:STRING=${value}")
        endif()
    endforeach()
    set(ENV{PKG_CONFIG_PATH} "${DEPENDENCIES_OUTPUT_DIR}/lib/pkgconfig")
    set(ENV{PKG_CONFIG_LIBDIR} "${DEPENDENCIES_OUTPUT_DIR}/lib/pkgconfig")
    find_package(Git REQUIRED)
    set(ROR_PATCH_COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/apply_patches.py")
    add_custom_target(macos-downloads)
    add_custom_target(macos-patches)
endif()

function(ror_add_dependency name)
    if(NOT ROR_MACOS_GL3)
        ExternalProject_Add(${name} ${ARGN})
        return()
    endif()
    # Source archives and strong hashes come from the profile's reviewed inventory.
    # Keep all build choices in the individual existing recipes.
    string(JSON url GET "${ROR_MACOS_SOURCES}" components ${name} url)
    string(JSON hash GET "${ROR_MACOS_SOURCES}" components ${name} sha256)
    string(LENGTH "${hash}" hash_length)
    if(NOT hash_length EQUAL 64 OR NOT hash MATCHES "^[0-9a-f]+$")
        message(FATAL_ERROR "Missing SHA256 source pin for ${name}")
    endif()
    set(patch_files)
    string(JSON patch_count LENGTH "${ROR_MACOS_SOURCES}" components ${name} patches)
    if(patch_count GREATER 0)
        math(EXPR last_patch "${patch_count} - 1")
        foreach(index RANGE ${last_patch})
            string(JSON patch GET "${ROR_MACOS_SOURCES}" components ${name} patches ${index} path)
            string(JSON expected GET "${ROR_MACOS_SOURCES}" components ${name} patches ${index} sha256)
            list(APPEND patch_files "${CMAKE_SOURCE_DIR}/${patch}")
            file(SHA256 "${CMAKE_SOURCE_DIR}/${patch}" actual)
            if(NOT actual STREQUAL expected)
                message(FATAL_ERROR "Source patch hash changed: ${patch}")
            endif()
        endforeach()
    endif()
    set(args)
    set(skip FALSE)
    foreach(arg IN LISTS ARGN)
        if(skip)
            set(skip FALSE)
        elseif(arg STREQUAL "URL" OR arg STREQUAL "URL_HASH" OR arg STREQUAL "URL_MD5")
            set(skip TRUE)
        else()
            list(APPEND args "${arg}")
        endif()
    endforeach()
    if(NOT name STREQUAL "openssl")
        list(APPEND args BUILD_COMMAND ${CMAKE_COMMAND} --build <BINARY_DIR> --config ${CMAKE_BUILD_TYPE} --parallel 3)
    endif()
    ExternalProject_Add(${name} ${args}
        URL "${url}" URL_HASH "SHA256=${hash}"
        DOWNLOAD_DIR "${CMAKE_BINARY_DIR}/downloads/${name}"
        LIST_SEPARATOR |
        CMAKE_ARGS ${ROR_MACOS_CMAKE_ARGS}
        STEP_TARGETS download patch configure)
    if(patch_files)
        # File inputs belong on the patch command. StepDependencies also adds
        # target-level dependencies, which cannot name files when STEP_TARGETS
        # are enabled. This profile supports single-configuration generators.
        ExternalProject_Get_Property(${name} STAMP_DIR)
        add_custom_command(OUTPUT "${STAMP_DIR}/${name}-patch" APPEND DEPENDS ${patch_files})
    endif()
    add_dependencies(macos-downloads ${name}-download)
    add_dependencies(macos-patches ${name}-patch)
    set_property(GLOBAL APPEND PROPERTY ROR_MACOS_COMPONENTS ${name})
endfunction()

function(ror_macos_manifest)
    add_custom_target(macos-manifest ALL
        COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/macos_manifest.py"
            --inventory "${CMAKE_SOURCE_DIR}/cmake/macos-sources.json"
            --recipes "${CMAKE_SOURCE_DIR}" --sources "${CMAKE_BINARY_DIR}/Source"
            --prefix "${DEPENDENCIES_OUTPUT_DIR}"
        VERBATIM)
    get_property(components GLOBAL PROPERTY ROR_MACOS_COMPONENTS)
    add_dependencies(macos-manifest ${components})
    # Exact local compiler/SDK paths belong to private logs, not installed metadata.
    execute_process(COMMAND "${CMAKE_CXX_COMPILER}" --version OUTPUT_VARIABLE compiler)
    string(REGEX MATCH "^[^\n]*" compiler "${compiler}")
    execute_process(COMMAND xcrun --sdk "${CMAKE_OSX_SYSROOT}" --show-sdk-version OUTPUT_VARIABLE sdk OUTPUT_STRIP_TRAILING_WHITESPACE)
    file(WRITE "${DEPENDENCIES_OUTPUT_DIR}/share/ror-dependencies/build-receipt.txt"
        "CMake: ${CMAKE_VERSION}\nCompiler: ${compiler}\nSDK: ${sdk}\nArchitecture: ${CMAKE_OSX_ARCHITECTURES}\nDeployment target: ${CMAKE_OSX_DEPLOYMENT_TARGET}\nBuild type: ${CMAKE_BUILD_TYPE}\n")
endfunction()
