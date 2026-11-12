cmake_minimum_required(VERSION 3.25)
project(jong_bangla_fcitx5 LANGUAGES CXX)

find_package(Fcitx5Core 5.1.23 REQUIRED)
find_package(Threads REQUIRED)
find_program(CARGO_EXECUTABLE cargo REQUIRED)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Native instrumentation only. Cargo below deliberately uses stable release
# settings; LSan can still observe Rust's system-allocator allocations.
option(JONG_ENABLE_SANITIZERS "Instrument native tests/addon with Clang ASan and UBSan" OFF)
if(JONG_ENABLE_SANITIZERS)
    if(NOT CMAKE_SYSTEM_NAME STREQUAL "Linux" OR
       NOT CMAKE_SYSTEM_PROCESSOR STREQUAL "x86_64" OR
       NOT CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
        message(FATAL_ERROR "Memory sanitizer recipe requires x86-64 Linux and Clang")
    endif()
    add_compile_options(-fsanitize=address,undefined -fno-omit-frame-pointer -g)
    add_link_options(-fsanitize=address,undefined)
endif()
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/memory-build.txt"
    "sanitizers=${JONG_ENABLE_SANITIZERS}\nbuild_type=${CMAKE_BUILD_TYPE}\nrust_instrumented=OFF\n")

get_filename_component(JONG_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../.." ABSOLUTE)
file(GLOB_RECURSE RUST_SOURCES CONFIGURE_DEPENDS
    "${JONG_ROOT}/src/*.rs" "${CMAKE_CURRENT_SOURCE_DIR}/ffi/src/*.rs")
set(RUST_LIBRARY "${CMAKE_CURRENT_BINARY_DIR}/rust/release/libjong_bangla_fcitx5_ffi.a")
add_custom_command(OUTPUT "${RUST_LIBRARY}"
    COMMAND "${CARGO_EXECUTABLE}" build --offline --locked --release
        --manifest-path "${JONG_ROOT}/Cargo.toml" -p jong-bangla-fcitx5-ffi
        --target-dir "${CMAKE_CURRENT_BINARY_DIR}/rust"
    DEPENDS ${RUST_SOURCES} "${JONG_ROOT}/Cargo.toml" "${JONG_ROOT}/Cargo.lock"
        "${CMAKE_CURRENT_SOURCE_DIR}/ffi/Cargo.toml"
    WORKING_DIRECTORY "${JONG_ROOT}"
    COMMENT "Building the local Rust composition boundary" VERBATIM)
add_custom_target(jong_rust DEPENDS "${RUST_LIBRARY}")
add_library(jong_ffi STATIC IMPORTED)
set_target_properties(jong_ffi PROPERTIES IMPORTED_LOCATION "${RUST_LIBRARY}")
add_dependencies(jong_ffi jong_rust)

add_library(jong-bangla MODULE addon.cpp)
target_compile_options(jong-bangla PRIVATE -Wall -Wextra -Wpedantic -Werror)
target_link_libraries(jong-bangla PRIVATE jong_ffi Fcitx5::Core Threads::Threads ${CMAKE_DL_LIBS} m)
target_link_options(jong-bangla PRIVATE -Wl,--exclude-libs,ALL)
if(NOT JONG_ENABLE_SANITIZERS)
    # Sanitized modules resolve ASan symbols from the instrumented executable.
    target_link_options(jong-bangla PRIVATE -Wl,--no-undefined)
endif()
set_target_properties(jong-bangla PROPERTIES CXX_VISIBILITY_PRESET hidden
    VISIBILITY_INLINES_HIDDEN YES)

# Keep build-local metadata separate from the relocatable installed registration.
set(HARNESS_DATA "${CMAKE_CURRENT_BINARY_DIR}/harness-data")
set(JONG_ADDON_LIBRARY "${CMAKE_CURRENT_BINARY_DIR}/libjong-bangla")
configure_file(jong-bangla.conf.in "${HARNESS_DATA}/fcitx5/addon/jong-bangla.conf" @ONLY)
configure_file(jong-bangla-inputmethod.conf
    "${HARNESS_DATA}/fcitx5/inputmethod/jong-bangla.conf" COPYONLY)
configure_file(tests/null-addon.conf
    "${HARNESS_DATA}/fcitx5/addon/jong-harness-null.conf" COPYONLY)
configure_file(tests/null-inputmethod.conf
    "${HARNESS_DATA}/fcitx5/inputmethod/keyboard-us.conf" COPYONLY)

# Installing files is an explicit user action; no daemon or profile is modified.
set(JONG_ADDON_LIBRARY "libjong-bangla")
configure_file(jong-bangla.conf.in "${CMAKE_CURRENT_BINARY_DIR}/install-data/jong-bangla.conf" @ONLY)
install(TARGETS jong-bangla LIBRARY DESTINATION "${FCITX_INSTALL_ADDONDIR}")
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/install-data/jong-bangla.conf"
    DESTINATION "${FCITX_INSTALL_PKGDATADIR}/addon")
install(FILES jong-bangla-inputmethod.conf
    DESTINATION "${FCITX_INSTALL_PKGDATADIR}/inputmethod" RENAME jong-bangla.conf)

# hicolor is the standard fallback theme; never install a private index.theme.
set(JONG_ICONDIR "${FCITX_INSTALL_DATADIR}/icons/hicolor")
install(FILES "${JONG_ROOT}/assets/app-icon/app-icon-light.svg"
    DESTINATION "${JONG_ICONDIR}/scalable/apps" RENAME jong-bangla.svg)
foreach(size 128 256 512)
    install(FILES "${JONG_ROOT}/assets/app-icon/app-icon-light-${size}px.png"
        DESTINATION "${JONG_ICONDIR}/${size}x${size}/apps" RENAME jong-bangla.png)
endforeach()
foreach(appearance light dark)
    install(FILES "${JONG_ROOT}/assets/tray-icon/icon-tray-linux-${appearance}.svg"
        DESTINATION "${JONG_ICONDIR}/scalable/status"
        RENAME "fcitx-jong-bangla-${appearance}.svg")
    install(FILES "${JONG_ROOT}/assets/tray-icon/icon-tray-linux-${appearance}-24px.png"
        DESTINATION "${JONG_ICONDIR}/24x24/status"
        RENAME "fcitx-jong-bangla-${appearance}.png")
endforeach()
# Retain the supplied artwork; derive KDE's palette-aware status variant.
# Consumers without palette support render the dark-ink fallback as supplied.
file(READ "${JONG_ROOT}/assets/tray-icon/icon-tray-linux-light.svg" JONG_SYMBOLIC)
string(REPLACE "<style>" "<style id=\"current-color-scheme\">" JONG_SYMBOLIC "${JONG_SYMBOLIC}")
string(REPLACE ".cls-1{fill:#24282b}" ".ColorScheme-Text{color:#24282b}" JONG_SYMBOLIC "${JONG_SYMBOLIC}")
string(REPLACE "class=\"cls-1\"" "class=\"ColorScheme-Text\" fill=\"currentColor\"" JONG_SYMBOLIC "${JONG_SYMBOLIC}")
file(CONFIGURE OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/install-data/jong-symbolic.svg"
    CONTENT "${JONG_SYMBOLIC}" @ONLY)
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
    "${JONG_ROOT}/assets/tray-icon/icon-tray-linux-light.svg")
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/install-data/jong-symbolic.svg"
    DESTINATION "${JONG_ICONDIR}/scalable/status")
# The stage checker reads resolved paths rather than assuming a distro layout.
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/install-layout.txt"
    "${FCITX_INSTALL_ADDONDIR}\n${FCITX_INSTALL_PKGDATADIR}\n${FCITX_INSTALL_DATADIR}\n")

enable_testing()
add_executable(jong-fcitx5-harness tests/harness.cpp)
target_compile_definitions(jong-fcitx5-harness PRIVATE JONG_HARNESS_DATA="${HARNESS_DATA}")
target_compile_options(jong-fcitx5-harness PRIVATE -Wall -Wextra -Wpedantic -Werror)
target_link_libraries(jong-fcitx5-harness PRIVATE Fcitx5::Core)
add_dependencies(jong-fcitx5-harness jong-bangla)
add_test(NAME fcitx5-synthetic COMMAND jong-fcitx5-harness)
set_tests_properties(fcitx5-synthetic PROPERTIES TIMEOUT 30)

# Links the same release Rust archive without Fcitx, isolating C-ABI ownership.
add_executable(jong-ffi-memory tests/memory.cpp)
target_compile_options(jong-ffi-memory PRIVATE -Wall -Wextra -Wpedantic -Werror)
target_link_libraries(jong-ffi-memory PRIVATE jong_ffi Threads::Threads ${CMAKE_DL_LIBS} m)
add_test(NAME ffi-memory-lifecycle COMMAND jong-ffi-memory)
set_tests_properties(ffi-memory-lifecycle PROPERTIES TIMEOUT 120)

# Never register intentional faults as ordinary passing CTest workloads.
if(JONG_ENABLE_SANITIZERS)
    add_executable(jong-memory-controls tests/memory_controls.cpp)
    target_compile_options(jong-memory-controls PRIVATE -Wall -Wextra -Wpedantic -Werror)
endif()

# Optional Linux/glibc resource probe. Run manually in Release, without sanitizers;
# timing/memory observations are not correctness tests or release thresholds.
option(JONG_BUILD_RESOURCE_PROBE "Build the optional Linux/glibc resource probe" OFF)
if(JONG_BUILD_RESOURCE_PROBE)
    if(NOT CMAKE_SYSTEM_NAME STREQUAL "Linux")
        message(FATAL_ERROR "The resource probe requires Linux/glibc")
    endif()
    add_executable(jong-fcitx5-resources tests/resources.cpp)
    target_compile_definitions(jong-fcitx5-resources PRIVATE
        JONG_HARNESS_DATA="${HARNESS_DATA}"
        JONG_RESOURCE_RELEASE=$<STREQUAL:$<CONFIG>,Release>)
    target_compile_options(jong-fcitx5-resources PRIVATE -Wall -Wextra -Wpedantic -Werror)
    target_link_libraries(jong-fcitx5-resources PRIVATE Fcitx5::Core)
    add_dependencies(jong-fcitx5-resources jong-bangla)
endif()
