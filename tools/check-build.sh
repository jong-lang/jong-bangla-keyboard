#!/usr/bin/env bash
# Run from a checkout or exported source root. No installation or desktop changes.
set -euo pipefail

cargo fmt --all -- --check
cargo clippy --offline --locked --workspace --all-targets -- -D warnings
cargo test --offline --locked --workspace
cargo build --offline --locked --workspace --release
cargo doc --offline --locked --workspace --no-deps
test "$(cargo run --offline --locked --quiet --example convert -- 'kh12T')" = 'খ১২ট'

cmake -S adapters/fcitx5 -B target/ci-fcitx5 -G Ninja \
    -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr \
    -DFCITX_INSTALL_USE_FCITX_SYS_PATHS=ON
cmake --build target/ci-fcitx5
ctest --test-dir target/ci-fcitx5 --output-on-failure
python3 tools/check-install.py target/ci-fcitx5
