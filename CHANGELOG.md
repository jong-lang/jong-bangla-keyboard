# Changelog

Notable changes awaiting release are listed below. Released entries retain their
version and date. Release preparation follows [CONTRIBUTING.md](CONTRIBUTING.md#release-policy-and-checklist).

## Unreleased

### Highlights

- Remove the Flatpak packaging prototype and its build and comparison guides.
  Adapter delivery now proceeds from Fcitx5 to Windows TSF, then IBus. Native
  packages and the AUR recipe remain supported.

## 0.1.0 - 2026-11-08

### Highlights

- First native x86-64 Fcitx5 release preparation: local Bangla phonetic typing
  with editable preedit, contextual vowels, conjuncts, case-sensitive spellings,
  Bangla digits, punctuation and phonetic escapes.
- Backspace edits the active raw input; Ctrl+Backspace clears it. Space and
  Enter commit Bangla and pass the boundary to the application. Escape commits
  and is consumed while input is active, and otherwise passes through.
- Native Arch, Debian testing and Fedora 45 packages, source archives, an Arch
  binary payload, source-pinned AUR recipes, build provenance, package lifecycle
  records and SHA-256 checksums. Publication awaits the release gates below.
- Typing stays local, without network access, telemetry or typed-text logging.

### Fixes

- Initial release; no fixes relative to an earlier public release.

### Breaking changes

- Initial release; no earlier public release to upgrade from.

### Installation and upgrade

- Requires x86-64 Linux and Fcitx5 5.1.23 or newer. Follow the
  [native package guide](docs/PACKAGING.md#install-upgrade-activate-and-remove)
  to verify checksums, install the matching package, activate Jong Bangla,
  restart the session after upgrades, and remove it while retaining user config.
- Debian packages target testing/forky; older Debian and Ubuntu releases are
  unverified. Fedora packages target Fedora 45. The Arch binary payload is
  specific to its recorded environment, not a cross-distribution installer.
- Package revision upgrades use the same engine with a higher package release
  number; they do not establish migration from a previous public engine.
- The AUR recipe is provided as an artifact; AUR submission is a separate
  maintainer action. No package changes the user's input-method settings.

### Tested environments

- Recorded maintainer desktop passes cover CachyOS KDE Plasma Wayland on the
  Modern 15 A5M in Kate, KWrite and Firefox, plus earlier Python GTK and Qt test
  environments. They do not establish XWayland coverage.
- [Packaging PR #40](https://github.com/shaadahmmed/jong-bangla-keyboard/pull/40)
  records 2026-11-07 installation, typing, revision upgrade and removal passes
  on CachyOS, Debian testing/forky and Fedora 45 KDE Plasma Wayland using
  packages from source `63d08a633e8c98f293206126053675890ddc8e83`.
  The RPMs were built on Fedora 44 and tested on Fedora 45. Debian/Fedora
  reports are aggregate results with incomplete application/backend details.
- On 2026-11-08 the maintainer
  [reaffirmed the completed passes](https://github.com/shaadahmmed/jong-bangla-keyboard/pull/40#issuecomment-6711683895),
  but could not identify the RPM pair. This adds no new artifact-specific pass.
- Separate container checks establish synthetic loading and package lifecycle
  results, not interactive desktop support. See the
  [platform matrix](docs/FEATURES.md#platform-matrix) and
  [artifact acceptance handoff](docs/TESTING.md#release-artifact-acceptance).

### Known issues

- No user-visible bugs are currently known to the maintainer. Phonetic parity
  is established only for the finite [audited corpus](docs/TESTING.md#reference-coverage-audit);
  unsupported Unicode case preservation deliberately differs from the reference.
- Acceptance of the intended release artifacts remains open in
  [#41](https://github.com/shaadahmmed/jong-bangla-keyboard/issues/41), especially
  Fedora 45-built RPMs and subsequently rebuilt packages. Earlier desktop
  reports must not be attributed to new package hashes. Package-specific Python
  GTK/Qt results or availability, broader punctuation/escape/navigation cases,
  and missing environment details remain to be recorded.
- Other distributions/desktops, XWayland and ARM64 are unverified. IBus and
  Windows TSF are later adapters; macOS is out of scope. Flatpak follows the
  native release in [#31](https://github.com/shaadahmmed/jong-bangla-keyboard/issues/31).
- This entry prepares the release; it does not announce publication. Separate
  review, explicit merge and release instructions, successful CI, artifact
  acceptance and complete draft inspection remain required under the
  [release policy](CONTRIBUTING.md#release-policy-and-checklist).
