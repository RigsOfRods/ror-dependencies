# ror-dependencies
Dependencies that will be needed to compile the source.

## How to build on Windows

### Prerequisites

  * Install Windows Visual Studio 2017 Community Edition
  * Install [cmake](https://cmake.org/download/)
  * Install [git](https://git-scm.com/download)

Install with [Chocolatey](https://chocolatey.org/): ```choco install cmake git```

### Create Visual Studio solution file

  * Launch cmake-gui and point the source directory to the _ror-dependencies_ repository
  * Set the build directory to any folder where the resulting dependencies should be placed
  * Press _Configure_ and select `Visual Studio 15 2017` as generator (Notice: Win64 target not supported yet)
  * Press _Generate_ to create the solution file
  
### Build dependencies

  * Open the `ror-dependencies.sln` file inside the chosen build directory with Visual Studio
  * Select `Release` configuration (currently the only tested configuration)
  * Run Build->Build Solution (`Ctrl-Shift-B`)
  * This will populate the `Dependencies_Windows_Visual-Studio-15-2017` directory with the freshly built dependencies

## How to build on Linux

### Prerequisites

  * Install cmake, git
  
### Configure && build

    cmake <Path-to-ror-dependencies-repository>
	make
	
The resulting dependencies will be placed inside the `Dependencies_Linux` directory.
  

## Native macOS ARM64 GL3 source profile

The opt-in profile builds a separate pinned source prefix with the existing
ExternalProject recipes. CMake 3.24+, Python 3, Perl, make, Ninja and the Apple
command-line toolchain are required. The default Windows/Linux source versions
and renderer choices are retained. Do not reuse an installed or archived prefix.

```sh
sdk="$(xcrun --sdk macosx --show-sdk-path)"
cmake -S . -B build-macos -G Ninja \
  -DROR_MACOS_GL3=ON -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_OSX_ARCHITECTURES=arm64 -DCMAKE_OSX_SYSROOT="$sdk" \
  -DCMAKE_OSX_DEPLOYMENT_TARGET=11.0 \
  -DDEPENDENCIES_OUTPUT_DIR="$PWD/prefix-macos"
cmake --build build-macos --target macos-downloads --parallel 1
cmake --build build-macos --target macos-patches --parallel 1
cmake --build build-macos --parallel 1
```

Keep the outer build serial: each dependency builds with at most three jobs.
Keep at least 4 GiB free and stop the build before exhausting disk space. The
prefix is the only install destination; no system or Homebrew installation is
performed. Select a fresh build directory when changing source/patch versions.
A repeat patch step accepts an unchanged verified patched source tree and rejects
modified sources. Some upstream projects generate source headers during their
configuration; recreate their source/build tree before explicitly replaying patches.

The Apple profile requires every listed game dependency, including OpenSSL and
Discord RPC, and fails if any `BUILD_*` game feature is disabled. OGRE uses GL3+,
STBI and ZIP with Bites, Overlay, Paging, RTSS, MeshLOD and Terrain. Legacy GL,
Cg, FreeImage, optional SDL integration, samples and tools are explicitly off.
RoR owns native Cocoa window/event integration. FreeType uses the pinned zlib;
optional PNG/BZip2/Brotli/HarfBuzz support is not part of this graph. curl uses
the pinned OpenSSL/zlib, with optional SSH, PSL, Brotli, Zstd, GSSAPI, libidn2 and nghttp2 integrations
off. No game content is downloaded by this dependency build.

User C/C++/ASM flags and selected SDK/architecture/deployment target are forwarded
to every dependency. An SDK header-search workaround, when needed for a local
Apple toolchain, can be supplied explicitly as `CMAKE_CXX_FLAGS`; it is not baked
into the source profile. The OpenSSL recipe currently supports native arm64 only.
When configuring RoR, select `OPENAL_LIBRARY=<prefix>/lib/libopenal.dylib` and
`OPENAL_INCLUDE_DIR=<prefix>/include/AL` explicitly: CMake's FindOpenAL can otherwise
prefer Apple's SDK framework. Set `CMAKE_FIND_FRAMEWORK=LAST` for prefix discovery.
The legacy Caelum headers require C++11; initialize `Threads` before importing
AngelScript, as current RoR already does. PagedGeometry is static because its
pinned upstream CMake hardcodes that choice.
The documented 11.0 deployment setting is a compile target; a build on a newer
SDK does not establish runtime support on macOS 11.

See [profile provenance](cmake/macos-profile-notes.md) and the exact
[source inventory](cmake/macos-sources.json). The installed
`share/ror-dependencies/manifest.json`, `licenses/`, and `build-receipt.txt` retain
source pins, patch hashes, options and source notices beside the existing
`version.cmake` contract (30). Exact local toolchain paths belong in private logs.
The manifest records whether recipes were uncommitted at build time; rebuild its
metadata after committing to record the final recipe revision.

This is a compile foundation. Native window/event behavior, GL3 UI/RTSS shader
integration, feature rendering, Retina/input behavior, application packaging and
binary redistribution clearance remain separate gates. In particular the inventory
preserves mixed Caelum notices and zziplib's dual-license texts without asserting
that a future binary bundle is cleared for distribution.
