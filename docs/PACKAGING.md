# Native Fcitx5 packages

The first release targets x86-64 Linux with Fcitx5 5.1.23 or newer. Packages
are built separately against each distribution's libraries and paths. The
Arch binary payload is specific to its recorded build environment. Do not
copy it into Debian or Fedora. Older framework versions are not supported.
Desktop coverage remains in [FEATURES.md](FEATURES.md#platform-matrix).

## Install, upgrade, activate and remove

No release has been published yet. After the maintainer publishes a release,
download the matching package and `SHA256SUMS` from that release. Verify the
download against its entry with `sha256sum --check --ignore-missing SHA256SUMS`.
Checksums detect corruption; obtain the manifest from the trusted release too.

| Target | Install or upgrade a downloaded package | Remove |
| --- | --- | --- |
| Arch x86-64 | `sudo pacman -U ./jong-bangla-*.pkg.tar.zst` | `sudo pacman -R jong-bangla` |
| Debian testing x86-64 | `sudo apt install ./jong-bangla_*_amd64.deb` | `sudo apt purge jong-bangla` |
| Fedora 44 x86-64 | `sudo dnf install ./jong-bangla-*.x86_64.rpm` | `sudo dnf remove jong-bangla` |

Use a single explicitly selected file for installation; avoid keeping multiple
versions matched by a wildcard. Package managers resolve framework, C++ and
libc dependencies. Debian/Ubuntu installations need repositories providing
the declared dependencies; no compatibility with older stable/LTS releases
is implied by the `.deb` format. No package enables a daemon, changes a user's
profile, or sets input-module environment variables.

After installation or upgrade, log out and back in, or explicitly restart your
Fcitx5 session. Install your distribution's Fcitx5 configuration tool. On KDE
Plasma Wayland, select Fcitx5 in System Settings > Virtual Keyboard and add
Jong Bangla in Fcitx5 Configuration (disable the current-language filter if
needed). Follow the upstream [KDE Wayland setup](https://fcitx-im.org/wiki/Using_Fcitx_5_on_Wayland#KDE_Plasma).
Do not set GTK/Qt input-module variables globally for this setup. Other desktop
setups require their own upstream configuration and acceptance evidence.
Before removal, select another input method; restart the session afterwards.
User-created Fcitx5 configuration is retained by removal.

The binary `.tar.gz` contains the Arch `usr/` payload, MIT license, attribution,
this guide, and `payload-info.json`. Prefer the package manager for installation
and upgrades. For an isolated staging inspection, extract it into a temporary
directory with `tar -xzf FILE.tar.gz -C DIRECTORY`; inspect its metadata and
`usr/` files without copying them into the host. It is not a package-manager
installer. The source archive contains the full build and testing guides.
The payload and every package also carry the actual Rust toolchain's
standard-library notices and license texts beside the project license.

## Recipes and verification

The release workflow builds the source and Arch payload twice, then runs three
independent package jobs using official digest-pinned Arch, Debian testing,
and Fedora 44 images. Distribution repositories supply signed packages; their
versions may change. Each `package-check-FORMAT.json` records image identity,
source hash, compilers, build and runtime package versions, and actual results.
These records accompany release packages and checksums. Package builds are
not claimed byte reproducible across distributions or repository updates.

To repeat a check with Docker, use the release source archive and epoch from
`build-info.json`. This creates disposable containers and new output directories;
it does not install packages or configure Fcitx5 on the host:

```sh
python3 tools/check-packages.py deb --source /path/to/jong-bangla-VERSION.tar.gz \
  --epoch SOURCE_DATE_EPOCH --output target/packages-deb
python3 tools/check-packages.py rpm --source /path/to/jong-bangla-VERSION.tar.gz \
  --epoch SOURCE_DATE_EPOCH --output target/packages-rpm
python3 tools/check-packages.py arch --source /path/to/jong-bangla-VERSION.tar.gz \
  --epoch SOURCE_DATE_EPOCH --output target/packages-arch
```

The Debian build image installs the manifest-required Rust toolchain through
Debian's rustup package because testing's distro compiler is older. Fedora and
Arch use their distro compilers. Debian uses debhelper and generated shlib
dependencies; RPM uses automatic ELF requirements. All formats also require
Fcitx5 explicitly. Paths come from the installed framework's CMake configuration:
Debian multiarch `lib/x86_64-linux-gnu`, Fedora `lib64`, Arch `lib`.

Checks install revision 1 into a fresh runtime image, verify package ownership,
registration, licenses/instructions and `ldd -r`, then run the isolated native
synthetic harness against installed paths. Revision 2 uses the same code with
a higher package release number to test upgrade transactions. It is a test
control, not a published release or evidence of migration from an older engine.
The missing-library control must fail; removal must delete package files while
preserving an unrelated addon and synthetic user profile. No display or host
session is used. Full logs are retained in CI artifacts. Interactive acceptance
uses [the desktop checklist](TESTING.md#package-desktop-acceptance).

## Maintaining the Arch/AUR recipe

`packaging/arch/PKGBUILD` and `.SRCINFO` pin an immutable reviewed source commit
and its archive checksum. They are maintained here; an AUR submission is a
separate maintainer action. Release artifacts also include an AUR recipe archive
generated from `PKGBUILD.in`, pinned to that release's source URL and SHA-256.
It builds offline after source download and does not fetch Cargo dependencies.

When updating the committed recipe, set its version, source root, immutable
commit URL and verified archive hash together using the template. Download and
verify that exact source, run `makepkg --verifysource`, `makepkg --cleanbuild`,
then `makepkg --printsrcinfo > .SRCINFO` as an ordinary user in an Arch build
environment. Compare the generated `.SRCINFO` and run the lifecycle check.
Never use `SKIP`, a moving branch, or an unverified checksum. On release
preparation, regenerate the release recipe from the new source artifact; do
not mutate an already published package. Bump `pkgrel` for packaging-only fixes.
