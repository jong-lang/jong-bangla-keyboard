# Jong Bangla

A Bangla phonetic keyboard with an independently implemented Rust engine and
Avro-compatible behavior as its target. Original project code is MIT licensed.

## Current status

Working on CachyOS KDE Plasma Wayland through Fcitx5. The maintainer considers
that desktop implementation complete; release preparation remains. Other
Linux distributions are untested. Exhaustive Avro parity is unverified.

Release order: Fcitx5, then IBus, then Windows TSF. The first release targets
x86-64. Native packages come first; Flatpak is a later prototype. macOS is out
of scope unless a viable free path is established.

## Build and install

No published packages are available yet. Build from source with Rust, a C++
compiler, CMake, Ninja, Fcitx5 development files, and Python installed. Install
Fcitx5 Configuration for desktop setup. Compiler requirements are declared in
[Cargo.toml](Cargo.toml) and [CMakeLists.txt](adapters/fcitx5/CMakeLists.txt).
Offline Cargo builds require dependencies to be available locally.

```sh
cmake -S adapters/fcitx5 -B target/fcitx5 -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr \
  -DFCITX_INSTALL_USE_FCITX_SYS_PATHS=ON
cmake --build target/fcitx5
```

To install the built addon system-wide, run explicitly:

```sh
sudo cmake --install target/fcitx5
```

Restart the Fcitx5 session to load the addon. In KDE System Settings, select
Fcitx5 as the Virtual Keyboard, then add Jong Bangla in Fcitx5 Configuration.
Follow [Fcitx's KDE Wayland setup](https://fcitx-im.org/wiki/Using_Fcitx_5_on_Wayland#KDE_Plasma).
Do not set GTK or Qt input-module variables globally for this setup.

## Test

Run full Rust, native adapter, and staged installation checks without changing
the desktop configuration:

```sh
bash tools/check-build.sh
```

## Guides

- [AGENTS.md](AGENTS.md): agent entry point, commands, and document routing.
- [Features and support](docs/FEATURES.md), [architecture](docs/ARCHITECTURE.md).
- [Testing and manual acceptance](docs/TESTING.md), [performance evidence](docs/PERFORMANCE.md).
- [Contributing and releases](CONTRIBUTING.md), [changelog](CHANGELOG.md).
- [Security and private reports](SECURITY.md), [code of conduct](CODE_OF_CONDUCT.md).
- [MIT license](LICENSE), [third-party notices](THIRD_PARTY_NOTICES).
