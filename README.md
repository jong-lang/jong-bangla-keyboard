# Jong Bangla

A Bangla phonetic desktop input method with an independently implemented Rust
engine. Type phonetic Latin keys and edit the converted Bangla before committing
it to your application.

The working project name is `jong-bangla-board`; **Jong Bangla** is the proposed
display name. Delivery is staged: **Fcitx5 and IBus on Linux**, Linux packages
(Flatpak, `.deb`, `.rpm`, pacman and maintained AUR recipes), **Windows TSF**, and
**macOS on Apple silicon and Intel**. Fcitx5 on CachyOS + KDE Plasma Wayland is
the first implementation and test environment. See the [release roadmap](docs/roadmap.md)
for stage boundaries and acceptance gates.

## Project status

**Experimental and under development.** The Rust transliteration engine and
composition controller are implemented, and an experimental Fcitx5 addon builds
and passes isolated dispatcher and staged-installation checks. A fresh build of
revision `7237833` exactly matches the installed addon; see the
[verified baseline and initial scope](docs/fcitx5-validation.md#verified-source-baseline-and-initial-scope).
The initial scope is experimental source installation on CachyOS x86_64 with
KDE Plasma Wayland. KWrite, Firefox and Kate have scoped user-reported desktop
results; exact app versions, cases and missing evidence are in the
[validation record](docs/fcitx5-validation.md#installed-route-basic-smoke-result).
No beta or stable desktop support is declared.

The engine targets a [pinned jsAvroPhonetic reference](docs/compatibility.md#phonetic-behavior-reference).
Recorded evidence covers 522,933 parity cases plus separate Unicode policy cases;
this is bounded coverage, not a claim of full Avro compatibility. Unsupported
Unicode is preserved without lowercasing or normalization.

An [experimental IBus service](docs/ibus.md) now builds and passes private D-Bus
and staged-installation checks; installed GNOME/IBus desktop acceptance is pending.
Windows, macOS and binary packages remain planned. Broader application and
Wayland/XWayland routes remain unverified. Report
and track bugs in [GitHub Issues](https://github.com/shaadahmmed/jong-bangla-keyboard/issues).
See the [current handoff](docs/progress.md#current-position) for implementation
and validation status.

## Typing behavior

- Keep the active word editable as converted Bangla.
- Backspace removes a phonetic keystroke and recomputes the word.
- Ctrl+Backspace clears the active word; with no active word, the application handles it.
- Space and Enter commit Bangla and forward the same key to the application.
- Punctuation and phonetic escapes stay editable until a commit boundary.
- Digit keys produce Bangla digits by default.
- Typing runs locally, without dictionaries, prediction or automatic spelling changes.

See the [typing guide](docs/typing.md) for examples and other controls.

## Try the engine

Obtain a Git checkout or extract a source archive. With Rust/Cargo **1.99.1 or
newer**, run from that repository/source root:

```sh
cargo run --offline --example convert -- 'ami bangla'
```

Expected output: `আমি বাংলা`. This terminal example exercises conversion; the
desktop addon has separate prerequisites and installation steps.

To try the experimental desktop input method, follow the
[Fcitx5 installation guide](docs/installation.md). For building, testing and the
library layout, use the [development guide](docs/development.md).

## Documentation

| Document | Purpose |
| --- | --- |
| [Typing guide](docs/typing.md) | Common spellings and editing controls |
| [Installation](docs/installation.md) | Build, stage, install, activate, update and remove the addon |
| [IBus experiment](docs/ibus.md) | Build, ownership, staged installation and desktop acceptance limits |
| [Development](docs/development.md) | Toolchain, workspace checks, Fcitx5 harness and code layout |
| [Releases](docs/releases.md) | Pull requests, manual versions, release template and draft publication |
| [Roadmap](docs/roadmap.md) | Staged platform delivery, package channels and release acceptance gates |
| [Reference checks](docs/reference-checks.md) | Reproduce pinned compatibility comparisons and context audits |
| [Performance](docs/performance.md) | Reproduce core latency and adapter resource measurements |
| [Requirements and behavior](docs/v1.md) | Current product requirements, composition semantics and public API |
| [Adapter contract](docs/adapter-contract.md) | Native events, context lifecycle, C ABI and failure policy |
| [Fcitx5 validation](docs/fcitx5-validation.md) | Desktop checklist, environment and staged-install evidence |
| [Compatibility](docs/compatibility.md) | Reference provenance, Unicode policy and historical rule records |
| [Progress](docs/progress.md) | Current developer handoff and next implementation step |
| [Changelog](CHANGELOG.md) | Notable changes intended for users and contributors |

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) for bug reports, development checks and
pull request expectations. [AGENTS.md](AGENTS.md) contains the detailed developer
and coding-agent workflow. Contributions should keep transliteration independent
of desktop frameworks and preserve exact Unicode evidence for phonetic changes.

## License

Project code is licensed under [MIT](LICENSE). The compatibility reference stays
external and is not shipped with the library; its provenance is documented in the
[reference decision](docs/compatibility.md#phonetic-behavior-reference).
