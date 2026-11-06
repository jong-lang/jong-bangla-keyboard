# Platform and release roadmap

## Confirmed scope

On 2026-11-05, the maintainer expanded the release plan and chose staged releases.
The delivery targets are Linux with Fcitx5 and IBus; Flatpak, Debian `.deb`, RPM
`.rpm` and pacman `.pkg.tar.zst` packages with maintained AUR recipes; Windows
using Text Services Framework (TSF); and macOS on Apple silicon and Intel.
These are planned deliverables. Only the Rust core, composition controller and
experimental Fcitx5 adapter exist today. No package or additional platform is
available or supported merely because it appears here.

The stage order below is an engineering plan based on the existing implementation.
It keeps each adapter and distribution route independently reviewable. Stages
can overlap when the shared behavior is stable; later targets do not block an
earlier scoped release. Versions and dates remain manually selected. The
[v1 behavior contract](v1.md#confirmed-requirements) applies to the initial
delivery; this roadmap supersedes its former Fcitx5-only platform scope.

| Target | Current evidence | Release boundary |
| --- | --- | --- |
| Fcitx5 on Linux | Experimental adapter, synthetic dispatcher and staged source installation; limited desktop observations | First scoped release; support claims require the acceptance gate below |
| IBus on Linux | Planned | Separate adapter and real desktop acceptance |
| pacman and AUR | Planned | Native package plus maintained `PKGBUILD` and `.SRCINFO` |
| Debian and RPM | Planned | Packages built and installed on explicitly named distribution releases |
| Flatpak | Planned; deployment model needs a feasibility experiment | Working engine delivery and sandboxed-client input, independently validated |
| Windows TSF | Planned | Native text service, installer and application acceptance |
| macOS arm64 and x86_64 | Planned | Native input method and tested delivery on both architectures |

## Architecture boundaries

Keep deterministic transliteration and editable composition in the shared Rust
crates. Each platform adapter owns key-event translation, focus/context lifetime,
preedit rendering, commits and native registration. Packaging installs those
adapters; it must not contain a second transliteration implementation. Typing
stays local and does not require a network service.

The Fcitx5 experiment already uses a small C++ adapter and a private Rust C ABI.
Keep that working boundary. For IBus, TSF and macOS, select bindings and any native
glue during their feasibility steps, based on API coverage, maintenance and
ownership requirements. Do not impose the Fcitx5 C ABI or C++ implementation on
every platform, or build a generic adapter framework before actual reuse exists.

Share semantic acceptance sequences across adapters, while testing native event
translation separately. Specify cursor/range units at each boundary rather than
reusing Fcitx5 byte offsets blindly. Native editing shortcuts, focus-out commit
ownership and restricted-field behavior need platform-specific mappings; in
particular, macOS shortcut conventions need an explicit mapping before coding.
Any difference from the confirmed composition behavior requires a documented
decision. Unsafe boundaries must specify encoding, ownership, lifetimes,
reentrancy, errors and panic containment.

## Delivery stages

### 1. Establish the Fcitx5 release baseline

Validate the real installed addon on CachyOS/KDE Plasma Wayland, using the
[desktop checklist](fcitx5-validation.md#remaining-desktop-smoke-checklist). Record the exact
commit, Fcitx5, toolkit, application and actual input route for each result.
Basic installed-route checks have [user-reported passes](fcitx5-validation.md#installed-route-basic-smoke-result)
in KWrite 26.08.2 and Firefox 159.0.1 on Wayland; the remaining lifecycle checks
and missing candidate/runtime details still need evidence.
Choose the initial support matrix from those results. A source alpha may ship
with explicitly unvalidated routes; a supported route must pass the acceptance
gate. Keep platform bugs and release-blocking decisions in
[GitHub Issues](https://github.com/shaadahmmed/jong-bangla-keyboard/issues).

### 2. Add IBus

Build the smallest IBus engine around the existing Rust controller. Establish
preedit/commit ownership, key forwarding and per-context isolation before adding
installation metadata. Test an installed engine in a named GNOME/IBus Wayland
environment with GTK, Qt and browser clients, plus XWayland wherever claimed. Fcitx5 and
IBus are alternative session integrations; packages must not silently switch the
user's active framework or enable competing daemons.

### 3. Deliver Linux packages

Use the same reviewed source tag for native packages and Flatpak builds. Prefer
separate Fcitx5 and IBus package payloads so users install their chosen adapter.
Exact package names and any shared runtime package depend on actual artifacts.
Keep distro-specific build recipes outside engine code.

| Channel | Required work before availability |
| --- | --- |
| pacman / AUR | Build `.pkg.tar.zst` packages in a clean Arch environment. Maintain versioned-source `PKGBUILD` and generated `.SRCINFO`, checksums, dependencies and package revisions. Document upstream-to-package prerelease version mapping. AUR carries build recipes; prebuilt pacman artifacts are a separate release asset. |
| Debian | Maintain Debian packaging metadata and build dependencies; build/test `.deb` packages on selected Debian-family releases. Validate upgrade/removal and package lint results. Do not claim all Debian derivatives from one build. |
| RPM | Maintain a spec and source-package recipe; build/test `.rpm` packages on selected RPM distributions and releases. Validate dependencies, upgrade/removal and package lint results. One RPM build does not establish every RPM distribution's support. |
| Flatpak | First prove how the engine is delivered and discovered, then test native and sandboxed clients for the declared route. Choose an appropriate framework extension or another documented deployment after the experiment. Flathub submission, IDs and runtime branches remain implementation decisions. |

Flatpak is a confirmed distribution target, with an unresolved deployment design.
A normal sandboxed application cannot be assumed to install a host input-method
addon. Flatpak extensions need an extension point supplied by a runtime or app;
host-engine input in sandboxed client apps is a separate validation path.
This is an engineering inference from the official
[sandbox rules](https://docs.flatpak.org/en/latest/sandbox-permissions.html),
[extension model](https://docs.flatpak.org/en/latest/extension.html), and
[Fcitx container integration guide](https://fcitx-im.org/wiki/Using_Fcitx_with_container).
The Flatpak experiment must demonstrate actual typing, not only a successful
manifest build. Native packages can ship while that experiment continues.

Test fresh installation, activation, source/manual-install conflicts, upgrade,
removal and recovery through each package manager. Let package managers own
installed files; preserve user configuration and other input methods. Record
runtime dependencies and license notices, checksums and artifact provenance.
Decide repository hosting, package signing and update ownership before offering
an automatic update channel. A maintained AUR recipe is required; admission to
official distro repositories or Flathub is a separate submission process.

### 4. Deliver Windows TSF

Implement a native TSF text service around the Rust core. The feasibility step
must settle COM/thread ownership, edit sessions, composition ranges, UTF-16
conversion, registration and teardown. Choose supported Windows versions and
processor/application architectures explicitly, including any 32-bit client
coverage; the scope currently does not select them. Deliver an installer with
tested upgrade/removal, signing/provenance policy and native language switching.
Test actual TSF clients and browsers before declaring support. Do not replace
native integration with global keystroke injection.

### 5. Deliver macOS on Apple silicon and Intel

Investigate InputMethodKit as the native adapter, retaining the Rust engine and
controller. Deliver native `arm64` and `x86_64` code, preferably in a universal
bundle if the experiment validates it. Select minimum macOS versions separately
for each architecture based on SDK availability and real tests. Establish input
source registration, marked-text lifecycle, range conversion, signing,
notarization and install/update/removal before public delivery.

Both architectures are required for this stage. Cross-compilation or running an
Intel slice through Rosetta alone does not establish native Intel-machine
acceptance. Record actual Apple-silicon and Intel test environments and apps.
Distribution format and native glue language remain feasibility decisions.

## Acceptance gate for each release scope

Every release PR must identify the exact adapters, artifacts, OS versions,
architectures and application/input routes included. Use the
[release template](../.github/RELEASE_TEMPLATE.md); unimplemented targets remain
planned and absent from that release's availability claims.

- Pass shared Rust checks and pinned reference comparisons for phonetic changes.
  Record Unicode policy differences separately from parity evidence.
- Pass each included adapter's event/ownership tests, including editable raw
  Backspace, whole-buffer deletion, boundaries, Escape, modifiers, repeats,
  releases, focus, reset, switching, restricted fields and context isolation.
- Run the desktop checklist for each declared route against the exact installed
  candidate. On Linux, include a GTK app, a Qt app and a browser for each claimed
  framework/session route; record Electron and XWayland independently if claimed.
  Windows and macOS need native text controls and a browser, plus other claimed
  application families. Record pass/fail/unavailable for every relevant case.
- Build each artifact from the approved source; test fresh install, activation,
  upgrade and removal through its intended delivery channel. Source archives must
  build and run relevant checks without Git metadata. Select and test minimum
  build tools separately from the latest-toolchain CI job.
- Record resource measurements for the candidate and choose reviewed latency and
  memory regression thresholds before declaring beta support. Existing batch
  timings are a baseline, not a per-keystroke or desktop responsiveness budget.
- Resolve release-blocking Issues or record an explicit maintainer deferral there
  with the affected release scope. Docs and release notes link to Issues; they
  do not duplicate bug reports. Missing implementation or validation must remain
  visible even when bug details live only in the tracker.

An alpha may state unmet gates in its tested-scope notes. Beta requires these
gates for its declared scope; an RC additionally has no open blocking Issues for
that scope. A stable release promises only its validated matrix. Completion of
one stage does not assert support for every roadmap target.

## Implementation follow-ups from the documentation review

Release-preparation PR CI now checks versions and dated notes before tag creation.
CI also builds and tests an exported source archive with Rust/Fcitx5 and staged
installation checks. Git-based documentation and provenance checks still require
a checkout; see the [development guide](development.md#documentation-and-release-tooling).

The following work remains planned:

- Add C++ formatting enforcement in CI; the development guide covers all current
  C++ files for local checks.
- Preserve any future desktop-test helpers in the repository with reproducible
  launch instructions. The current checklist uses normally installed apps and
  does not depend on the older untracked private-session helper.

Ordinary protected PR merging and required hosted checks were verified on
2026-11-05. Keep these gates in place for future stages; see the
[release guide](releases.md#github-repository-settings) for dated evidence.

## Platform and packaging references

Official sources consulted for this plan on 2026-11-05:

- [IBus engine API](https://ibus.github.io/docs/ibus-1.5/IBusEngine.html).
- [Microsoft TSF](https://learn.microsoft.com/en-us/windows/win32/tsf/text-services-framework).
- [Apple InputMethodKit](https://developer.apple.com/documentation/inputmethodkit)
  and [universal macOS binaries](https://developer.apple.com/documentation/apple-silicon/building-a-universal-macos-binary).
- [Arch PKGBUILD manual](https://man.archlinux.org/man/PKGBUILD.5.en),
  [Guide for Debian Maintainers](https://www.debian.org/doc/manuals/debmake-doc/),
  and [RPM Packaging Guide](https://rpm-packaging-guide.github.io/).
