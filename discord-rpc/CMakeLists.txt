# Reuse the graph's RapidJSON instead of upstream's unchecked configure download.
ror_add_dependency(discord-rpc
    DEPENDS RapidJSON
    URL unused URL_HASH SHA256=unused
    PATCH_COMMAND ${ROR_PATCH_COMMAND} ${CMAKE_CURRENT_SOURCE_DIR}/patches/rapidjson-prefix.patch
    CMAKE_ARGS
        -DBUILD_EXAMPLES=OFF
        -DENABLE_IO_THREAD=ON
        -DCLANG_FORMAT_CMD=CLANG_FORMAT_CMD-NOTFOUND)
