# OpenSSL's upstream build uses Perl Configure and make, not CMake.
find_package(Perl REQUIRED)
find_program(ROR_MAKE make REQUIRED)
if(NOT CMAKE_OSX_ARCHITECTURES STREQUAL "arm64")
    message(FATAL_ERROR "The OpenSSL profile currently supports a native arm64 build only")
endif()
string(TOUPPER "${CMAKE_BUILD_TYPE}" OPENSSL_CONFIG)
# CMake accepts SDK names; OpenSSL invokes the compiler directly and needs a path.
set(OPENSSL_SDK "${CMAKE_OSX_SYSROOT}")
if(NOT IS_ABSOLUTE "${OPENSSL_SDK}")
    execute_process(COMMAND xcrun --sdk "${OPENSSL_SDK}" --show-sdk-path
        OUTPUT_VARIABLE OPENSSL_SDK OUTPUT_STRIP_TRAILING_WHITESPACE COMMAND_ERROR_IS_FATAL ANY)
endif()
if(NOT IS_DIRECTORY "${OPENSSL_SDK}")
    message(FATAL_ERROR "OpenSSL SDK does not exist: ${OPENSSL_SDK}")
endif()
# CFLAGS is subsequently expanded by make and then its recipe shell. Preserve
# simple paths verbatim; quote other paths at those boundaries, not just env.
if(NOT OPENSSL_SDK MATCHES "^[A-Za-z0-9_./+-]+$")
    string(REPLACE "'" "'\\''" OPENSSL_SDK "${OPENSSL_SDK}")
    string(REPLACE "$" "$$" OPENSSL_SDK "${OPENSSL_SDK}")
    string(REPLACE "#" "\\#" OPENSSL_SDK "${OPENSSL_SDK}")
    set(OPENSSL_SDK "'${OPENSSL_SDK}'")
endif()
set(OPENSSL_PLATFORM_FLAGS "-arch arm64 -isysroot ${OPENSSL_SDK} -mmacosx-version-min=${CMAKE_OSX_DEPLOYMENT_TARGET}")
set(OPENSSL_CFLAGS "${CMAKE_C_FLAGS} ${CMAKE_C_FLAGS_${OPENSSL_CONFIG}} ${OPENSSL_PLATFORM_FLAGS}")
set(OPENSSL_LDFLAGS "${CMAKE_SHARED_LINKER_FLAGS}")
if(CMAKE_SHARED_LINKER_FLAGS_${OPENSSL_CONFIG})
    string(APPEND OPENSSL_LDFLAGS " ${CMAKE_SHARED_LINKER_FLAGS_${OPENSSL_CONFIG}}")
endif()
string(APPEND OPENSSL_LDFLAGS " -Wl,-headerpad_max_install_names")
ror_add_dependency(openssl
    URL unused URL_HASH SHA256=unused
    PATCH_COMMAND ${ROR_PATCH_COMMAND} ${CMAKE_CURRENT_SOURCE_DIR}/patches/darwin-install-name.patch
    CONFIGURE_COMMAND ${CMAKE_COMMAND} -E env
        "CC=${CMAKE_C_COMPILER}" "CFLAGS=${OPENSSL_CFLAGS}"
        "CXX=${CMAKE_CXX_COMPILER}" "CXXFLAGS=${CMAKE_CXX_FLAGS} ${CMAKE_CXX_FLAGS_${OPENSSL_CONFIG}} ${OPENSSL_PLATFORM_FLAGS}"
        "AS=${CMAKE_ASM_COMPILER}" "ASFLAGS=${CMAKE_ASM_FLAGS} ${CMAKE_ASM_FLAGS_${OPENSSL_CONFIG}} ${OPENSSL_PLATFORM_FLAGS}"
        "LDFLAGS=${OPENSSL_LDFLAGS}"
        ${PERL_EXECUTABLE} ./Configure darwin64-arm64-cc shared no-tests
            "--prefix=${DEPENDENCIES_OUTPUT_DIR}" --libdir=lib
    BUILD_COMMAND ${ROR_MAKE} -j3
    INSTALL_COMMAND ${ROR_MAKE} install_sw
    BUILD_IN_SOURCE TRUE)
