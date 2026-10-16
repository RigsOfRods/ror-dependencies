# Native macOS source profile provenance

The profile is a compile foundation with OGRE 1.11.6.1 GL3+, STBI and ZIP.
Bites, Overlay, Paging, RTSS, MeshLOD and Terrain are included. Bites' optional
SDL integration is disabled: RoR owns native Cocoa window/event integration.
The pinned PagedGeometry source explicitly builds a static library; other runtime
libraries are shared. Only RTShaderLib/GLSL media is installed. Runtime window, input, UI/shader,
Retina and feature-rendering correctness still require their own validation.
No successful configure or compile establishes those runtime properties.

`macos-sources.json` records the source graph, its intentional differences from
RoR's Conan graph, source notices, and ordered patches. Archive SHA256s pin
bytes even for release-tag URLs. AngelScript 2.38.0 and fmt 12.2.0 are Apple
profile overrides; the default recipes retain their existing versions.

Patch provenance:

- `ogre/scriptlexer.patch`: existing dependency recipe patch, retained against
  the same legacy lexer. The Windows-only WiX patch remains in default recipes.
- `ogre/patches/macos/arm64-sdk.patch`: legacy OGRE 1.11.6 ARM detection and
  SDK-selection backport from the prior macOS port. Desktop Apple ARM falls
  through to the existing ARM detector; explicitly selected SDKs are preserved.
  Both changes are obsolete on current OGRE master. No renderer or event-pump
  changes are included.
- `caelum/patches/ogre-include.patch`: legacy compile-only correction to consume
  discovered OGRE include directories, independently of framework layout.
- `ois/patches/cocoa-modifiers.patch`: production callback backport from
  wgois/OIS PR #101, commit 23ca1f60ac6181e1bbc0a9528d5f93b47e6a3079,
  https://github.com/slavazhulanov/OIS/commit/23ca1f60ac6181e1bbc0a9528d5f93b47e6a3079.
  Applied to 1.6.0 without public ABI changes; standalone fixtures live in that
  contribution. Copyright/source notices are retained.
- `curl/patches/apple-pipe2-availability.patch`: use a declaration/availability
  probe for Apple pipe2, which SDK 27 exports as a weak symbol introduced in macOS
  27. Link-only detection incorrectly accepts it for an 11.0 deployment target;
  the corrected test chooses curl's existing pipe/fcntl fallback where needed.
  No availability warning is suppressed and the CURL subsystem stays enabled.
- `openssl/patches/darwin-install-name.patch`: quote the upstream Darwin
  install-name directory when generating linker flags so a prefix containing
  spaces remains one linker argument. `Configure` is invoked relatively to
  avoid absolute source paths becoming split make prerequisites. These are
  build integration fixes, with no crypto feature changes.
- `socketw/patches/openssl-interface.patch`: profile build integration makes
  OpenSSL required and exports SSL/Crypto as public dependencies, including
  package discovery. Headers, including generated sw_config.h, retain the
  `socketw/` installation directory.
- `discord-rpc/patches/rapidjson-prefix.patch`: replaces the unchecked configure
  download of RapidJSON 1.1.0 with this graph's pinned RapidJSON include path.

The installed source and notice inventory is not a binary redistribution
clearance. In particular Caelum's root MIT text coexists with LGPL source
notices; both are retained. zziplib's LGPL/MPL dual-license explanation is
retained without choosing terms for a future binary distributor. Corresponding
sources/build scripts, fonts and final asset notices remain a packaging gate.
