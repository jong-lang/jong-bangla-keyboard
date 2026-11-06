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
and passes isolated dispatcher tests. Limited desktop typing has been reported
in GTK3, Firefox, KWrite and Kate. Installation staging has been checked, and
basic installed-addon typing/editing checks have user-reported passes in KWrite
and Firefox on Wayland. Kate 26.08.3 follow-up reports cover modifiers, case,
held keys and cursor relocation. See the [results and remaining desktop checks](docs/fcitx5-validation.md#installed-route-basic-smoke-result).
Firefox 159.0.1 on Wayland also has a grouped user-reported pass for modifiers,
case, held keys, pointer motion, clicking and selection while composing.
Further reports cover KWrite 26.08.3/Qt 6.12.0 modifiers, case and repeats,
immediate key-release stopping in KWrite and Firefox, and grouped Compose/dead-key
success. Exact sequences and runtime/build identification limits are recorded in
the [follow-up](docs/fcitx5-validation.md#runtime-kwrite-and-key-release-follow-up).

The engine targets a [pinned jsAvroPhonetic reference](docs/compatibility.md#phonetic-behavior-reference).
Recorded evidence covers 522,933 parity cases plus separate Unicode policy cases;
this is bounded coverage, not a claim of full Avro compatibility. Unsupported
Unicode is preserved without lowercasing or normalization.

IBus, Windows, macOS and binary packages are planned, with no delivered support
yet. Broader application and Wayland/XWayland routes remain unverified. Report
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
