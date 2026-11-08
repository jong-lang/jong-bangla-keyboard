#!/usr/bin/env bash
# Build/test only inside flatpak-builder. Never start a desktop daemon.
set -euo pipefail
test "${FLATPAK_DEST:?}" = /app/addons/Jong
test "$(uname -m)" = x86_64

cargo fmt --all -- --check
cargo clippy --offline --locked --workspace --all-targets -- -D warnings
cargo test --offline --locked --workspace
python3 tools/check-privacy.py

cmake -S adapters/fcitx5 -B _flatpak-build -G Ninja \
    -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$FLATPAK_DEST" \
    -DCMAKE_INSTALL_LIBDIR=lib -DFCITX_INSTALL_USE_FCITX_SYS_PATHS=OFF \
    -DCMAKE_PREFIX_PATH=/app
cmake --build _flatpak-build
ctest --test-dir _flatpak-build --output-on-failure
python3 tools/check-install.py _flatpak-build
cmake --install _flatpak-build
_flatpak-build/jong-fcitx5-harness --installed \
    "$FLATPAK_DEST/share/fcitx5" "$FLATPAK_DEST/lib/fcitx5"

install -Dm644 LICENSE "$FLATPAK_DEST/share/licenses/jong-bangla/LICENSE"
install -Dm644 THIRD_PARTY_NOTICES \
    "$FLATPAK_DEST/share/licenses/jong-bangla/THIRD_PARTY_NOTICES"
python3 tools/copy-rust-notices.py "$FLATPAK_DEST/share/licenses/jong-bangla/rust-stdlib"
install -Dm644 docs/PACKAGING.md "$FLATPAK_DEST/share/doc/jong-bangla/PACKAGING.md"
install -Dm644 docs/TESTING.md "$FLATPAK_DEST/share/doc/jong-bangla/TESTING.md"
install -Dm644 source-info.json "$FLATPAK_DEST/share/jong-bangla/source-info.json"
rustc -vV > "$FLATPAK_DEST/share/jong-bangla/rustc-version.txt"
c++ --version > "$FLATPAK_DEST/share/jong-bangla/cxx-version.txt"
pkg-config --modversion Fcitx5Core > "$FLATPAK_DEST/share/jong-bangla/fcitx5-version.txt"
