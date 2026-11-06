cmake_minimum_required(VERSION 3.25)
project(jong_bangla_fcitx5 LANGUAGES CXX)

find_package(Fcitx5Core 5.1.23 REQUIRED)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

get_filename_component(JONG_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../.." ABSOLUTE)
include("${JONG_ROOT}/adapters/ffi/build.cmake")

add_library(jong-bangla MODULE addon.cpp)
target_compile_options(jong-bangla PRIVATE -Wall -Wextra -Wpedantic -Werror)
target_link_libraries(jong-bangla PRIVATE jong_ffi Fcitx5::Core Threads::Threads ${CMAKE_DL_LIBS} m)
target_link_options(jong-bangla PRIVATE -Wl,--no-undefined -Wl,--exclude-libs,ALL)
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
# The stage checker reads resolved paths rather than assuming a distro layout.
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/install-layout.txt"
    "${FCITX_INSTALL_ADDONDIR}\n${FCITX_INSTALL_PKGDATADIR}\n")

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
