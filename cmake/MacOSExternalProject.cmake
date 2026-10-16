# ExternalProject configure runs during the later build, in a new process.
# Set these there rather than relying on the superbuild configure environment.
set(ENV{PKG_CONFIG_PATH} "${CMAKE_INSTALL_PREFIX}/lib/pkgconfig")
set(ENV{PKG_CONFIG_LIBDIR} "${CMAKE_INSTALL_PREFIX}/lib/pkgconfig")
unset(ENV{PKG_CONFIG_SYSROOT_DIR})
