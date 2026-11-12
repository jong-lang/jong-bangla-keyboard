# Jong Bangla

<div align="center" style="padding: 24px 0;">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo/logo-tagline-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="assets/logo/logo-tagline-light.svg">
    <img src="assets/logo/logo-tagline-light.svg" alt="Jong Bangla Keyboard. A modern Bangla keyboard, built with Rust." width="540">
  </picture>
</div>

A Bangla phonetic keyboard with an independently implemented Rust engine and
Avro-compatible behavior as its target. Original project code is MIT licensed.

## Current status

Native Fcitx5 [v0.1.0 is available](https://github.com/shaadahmmed/jong-bangla-keyboard/releases/tag/v0.1.0).
Working on CachyOS KDE Plasma Wayland. Debian and
Fedora test reports and their limits are in the [platform matrix](docs/FEATURES.md#platform-matrix).
Exhaustive Avro parity is unverified.

Release order: Fcitx5, then Windows TSF, then IBus. The current release targets
x86-64 Linux. Flatpak packaging is out of scope for now. macOS is out
of scope unless a viable free path is established.

## Build and install

Download a native package and checksums from the release above; follow the
[package guide](docs/PACKAGING.md) for installation and activation. The AUR
recipe remains supported; AUR publication awaits maintainer account approval
in [#46](https://github.com/shaadahmmed/jong-bangla-keyboard/issues/46).

Alternatively, build from source with Rust, a C++
compiler, CMake, Ninja, Fcitx5 development files, `hicolor-icon-theme`, and Python. Install
Fcitx5 Configuration for desktop setup. Compiler requirements are declared in
[Cargo.toml](Cargo.toml) and [CMakeLists.txt](adapters/fcitx5/CMakeLists.txt).
Offline Cargo builds require dependencies to be available locally.

Version tags prepare drafts for maintainer publication with source, a reproducibility-checked
x86-64 Fcitx5 payload, Debian/Fedora/Arch packages, an AUR recipe, build and
clean-image verification records, and checksums. See
[package installation and activation](docs/PACKAGING.md). Container verification
does not establish interactive desktop support.
See the [release process](CONTRIBUTING.md#release-policy-and-checklist).

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
