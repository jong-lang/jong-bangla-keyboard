# Shared private Rust ABI, linked independently into each native adapter.
find_package(Threads REQUIRED)
find_program(CARGO_EXECUTABLE cargo REQUIRED)
file(GLOB_RECURSE RUST_SOURCES CONFIGURE_DEPENDS
    "${JONG_ROOT}/src/*.rs" "${JONG_ROOT}/adapters/ffi/src/*.rs")
set(RUST_LIBRARY "${CMAKE_CURRENT_BINARY_DIR}/rust/release/libjong_bangla_ffi.a")
add_custom_command(OUTPUT "${RUST_LIBRARY}"
    COMMAND "${CARGO_EXECUTABLE}" build --offline --locked --release
        --manifest-path "${JONG_ROOT}/Cargo.toml" -p jong-bangla-ffi
        --target-dir "${CMAKE_CURRENT_BINARY_DIR}/rust"
    DEPENDS ${RUST_SOURCES} "${JONG_ROOT}/Cargo.toml" "${JONG_ROOT}/Cargo.lock"
        "${JONG_ROOT}/adapters/ffi/Cargo.toml"
    WORKING_DIRECTORY "${JONG_ROOT}"
    COMMENT "Building the shared Rust composition boundary" VERBATIM)
add_custom_target(jong_rust DEPENDS "${RUST_LIBRARY}")
add_library(jong_ffi STATIC IMPORTED)
set_target_properties(jong_ffi PROPERTIES IMPORTED_LOCATION "${RUST_LIBRARY}")
add_dependencies(jong_ffi jong_rust)
