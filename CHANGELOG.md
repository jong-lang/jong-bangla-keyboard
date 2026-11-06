# Changelog

Notable changes to Jong Bangla are recorded here. Detailed development steps and
validation evidence live in Git history and the [progress handoff](docs/progress.md).

## Unreleased

This is the initial development baseline, not a published release. The Cargo
package version `0.1.0` does not establish a release date or desktop support claim.

### Added

- Independent, dependency-free Rust phonetic transliteration with contextual
  vowels, consonants, conjuncts, case-sensitive spellings, symbols, escapes,
  reph and Bangla digits.
- Platform-independent composition with editable Bangla, raw-key Backspace,
  Ctrl+Backspace clearing, commit, cancel and reset.
- Experimental Linux Fcitx5 addon with a Rust C ABI, C++ adapter, isolated
  dispatcher harness and staged installation/removal checks.
- Reference fixtures and comparison tooling for a pinned jsAvroPhonetic revision,
  with separate cases for deliberate Unicode preservation differences.
- Core latency, adapter resource and lifecycle/leak measurement tooling.
- Focused typing, installation, development, reference and performance guides,
  contribution instructions, and issue/pull request templates.
- A staged release roadmap covering Linux Fcitx5 and IBus, Flatpak/deb/rpm/pacman
  packages and maintained AUR recipes, Windows TSF, and macOS on Apple silicon
  and Intel. These additions describe planned delivery, not implemented support.
- GitHub CI for documentation/release tooling, Rust workspace and Fcitx5 staged
  installation checks; version-tag validation, reviewed release-note template,
  source archives with SHA-256 checksums, and automated draft releases.
- Release-preparation validation before PR merge, plus clean exported-source
  Rust/Fcitx5 builds, tests and staged-installation checks in CI.
- Weekly GitHub Actions dependency update PR configuration and a documented
  issue-first task workflow with fresh branches, automatic agent commits/PRs,
  relevant review, protected merging and verified branch cleanup. Release
  versions and publication remain manual.

### Behavior decisions

- Keep unsupported Unicode unchanged without lowercasing or normalization.
- Show converted Bangla without a Bangla/Latin choice list for v1.
- Escape commits active Bangla and consumes the press; Space and Enter commit
  before forwarding. Navigation and application shortcuts also commit first.
- Keep autocorrection and prediction outside the first release.
- Track bug reports, investigation and deferral decisions in GitHub Issues.

### Known limitations

- Compatibility checks cover a bounded set; full Avro parity is not established.
- Desktop evidence is limited to recorded environments. Actual installed-route
  typing and the broader frontend matrix still need confirmation.
- Additional adapters and binary packages remain unimplemented; release scope
  and acceptance gates are defined in the [roadmap](docs/roadmap.md).

Report and track bugs in
[GitHub Issues](https://github.com/shaadahmmed/jong-bangla-keyboard/issues).

See the [requirements](docs/v1.md) and [current handoff](docs/progress.md#current-position)
for exact decisions, environment evidence and next steps.
