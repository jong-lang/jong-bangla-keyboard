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
| Fedora 45 x86-64 | `sudo dnf install ./jong-bangla-*.x86_64.rpm` | `sudo dnf remove jong-bangla` |

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

After native activation on the reference desktop, the optional
[KWrite/Firefox input-path proof](TESTING.md#kwritefirefox-input-path-proof)
can check committed synthetic text. It is not full package or desktop acceptance.

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
and Fedora 45 images. Distribution repositories supply signed packages; their
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

## Flatpak extension prototype

[#31](https://github.com/shaadahmmed/jong-bangla-keyboard/issues/31) evaluates
two routes: native Fcitx5/Jong serving Flatpak applications, and Jong loaded by
Flatpak Fcitx5. The second route is a local x86-64 prototype, not a shipping
package or Flathub submission. Desktop acceptance and the route decision remain
pending. Native Jong is not installed into the Flatpak daemon by this recipe.

The parent inspected on 2026-11-08 is `org.fcitx.Fcitx5/x86_64/stable`, commit
`41eaac428e5bf7dd55a09ddfa203f208a2bdb8ec79ddcf7f27972806d36ec227`, with
Fcitx5 5.1.23 and KDE runtime/SDK 6.11. Its extension branch is `stable`, distinct
from the SDK's `6.11` branch. The recipe uses `org.fcitx.Fcitx5.Addon.Jong` and
prefix `/app/addons/Jong`. It explicitly disables Fcitx system installation
paths: the library belongs in `lib/fcitx5`, and registrations in `share/fcitx5`,
relative to this prefix. The parent supplies development headers/libraries;
Jong does not bundle a second framework. The existing CMake build needs no change.

The SDK's Rust extension on its matching `25.08` branch currently reports
1.98.1, below the manifests' minimum. A checksum-pinned official Rust 1.99.1
archive supplies build tools only. Cleanup removes the toolchain; the final
extension retains the actual statically linked standard-library notices.
Cargo runs offline and locked, with no registry dependencies in the current
workspace. SDK/parent branches can move: record their exact installed commits
for every run and rebuild/retest after an update. This recipe is not a claim
of compatibility with every future stable parent or SDK.

Primary sources used for this independently written recipe:

- [Parent manifest](https://github.com/flathub/org.fcitx.Fcitx5/blob/2b9c2c89bb7888cca1cfa04d3fab7af949f8e762/org.fcitx.Fcitx5.yaml)
  and [launcher](https://github.com/flathub/org.fcitx.Fcitx5/blob/2b9c2c89bb7888cca1cfa04d3fab7af949f8e762/fcitx5.sh).
- [Existing engine extension](https://github.com/flathub/org.fcitx.Fcitx5.Addon.Mozc/blob/497a51e2c8128a496db543992dfcdbbd6e9e1cc7/org.fcitx.Fcitx5.Addon.Mozc.yaml)
  demonstrates the parent/SDK relationship; no engine source is copied.
- [Flatpak extension matching](https://docs.flatpak.org/en/latest/extension.html)
  and [Fcitx installation prerequisites](https://fcitx-im.org/wiki/Install_Fcitx_5).

### Build and export without desktop activation

Use an x86-64 Linux build environment supporting unprivileged Flatpak sandboxes,
with Flatpak, flatpak-builder 1.4.12 or newer, Git and Python 3.12 or newer.
Use a clean committed checkout. The preparation tool rejects outstanding work,
exports only `git archive HEAD`, and records the commit/archive hash. Ignored
build outputs and `.git` never enter the source. The output must not exist.
Build inputs are local and unsigned; verify transferred bundle hashes using a
trusted copy of the manifest. Never install an unknown bundle.

The following dependency installation is for a disposable build VM. It does not
activate a daemon. Agents use isolated XDG data/config/cache directories under
`target/` when doing local investigations, rather than the desktop installation.

```sh
flatpak remote-add --user --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak install --user --no-related flathub org.fcitx.Fcitx5//stable org.kde.Sdk//6.11
flatpak info --user --show-commit org.fcitx.Fcitx5
flatpak info --show-commit org.kde.Sdk//6.11
flatpak info --user --show-metadata org.fcitx.Fcitx5
python3 tools/prepare-flatpak.py --output target/flatpak-input
flatpak-builder --user --keep-build-dirs --state-dir=target/flatpak-state \
  --repo=target/flatpak-repo target/flatpak-build \
  target/flatpak-input/org.fcitx.Fcitx5.Addon.Jong.json
flatpak build-bundle --runtime target/flatpak-repo target/Jong-r1.flatpak \
  org.fcitx.Fcitx5.Addon.Jong stable
sha256sum target/Jong-r1.flatpak
```

Save build stdout/stderr. The build runs formatting, Clippy, workspace tests,
the privacy scan, native CTest, and staged loading/removal with a missing-library
control. It also loads the final installed extension paths in the synthetic
harness. No host bus, display, real input or daemon is used by that harness.
Inspect `target/flatpak-build/files`: expect the three Jong runtime files,
licenses, guides, source identity and compiler/framework versions, with no
`toolchain` directory. This is build/staged evidence, not desktop acceptance.

To prepare a same-code upgrade control, export a new commit with a different
subject; the runtime files are unchanged. Record both OSTree commits and bundle
hashes. This does not test migration between engine versions.

```sh
flatpak build-export --runtime --subject='Jong same-code upgrade control' \
  target/flatpak-repo target/flatpak-build stable
flatpak build-bundle --runtime target/flatpak-repo target/Jong-r2.flatpak \
  org.fcitx.Fcitx5.Addon.Jong stable
sha256sum target/Jong-r1.flatpak target/Jong-r2.flatpak
(cd target && sha256sum Jong-r1.flatpak Jong-r2.flatpak > Jong-SHA256SUMS)
```

Run the [maintainer comparison](TESTING.md#flatpak-prototype-comparison) before
choosing a route. Keep the first bundle before exporting the second. Neither
command installs an extension or changes input settings. No Flatpak artifact
is added to the native release workflow.

### Permission assessment

The parent runs engines in its own process. Its inspected metadata grants
network and IPC sharing, X11/Wayland/session-bus access, DRI, writable Fcitx/IBus
configuration and IBus cache, writable `kxkbrc`, and read access to font/KDE
configuration. The extension adds no permissions but inherits that process's
access. It is not independently network-isolated. Host GTK/Qt input modules
are still native prerequisites where the chosen application protocol needs them.
KDE Wayland protocol integration must be tested, not inferred from permissions.

Jong's [privacy contract](../SECURITY.md) still prohibits runtime network calls,
telemetry, typed-text logging and unrelated persistence. Build downloads are
separate from typing. Review manifests, scripts and dataflow as well as running
the existing finite privacy/dependency checks; offline typing alone is not proof
of no network calls. Broader parent permissions and future parent changes need
an explicit assessment before any shipping decision.
