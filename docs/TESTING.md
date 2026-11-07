# Testing

Run commands from the repository root. Start with [AGENTS.md](../AGENTS.md) for
the check list. Use synthetic input, never real typing or credentials.

## Automated layers

| Layer | Command | Current CI coverage |
| --- | --- | --- |
| Full Rust and Fcitx5 checks | `bash tools/check-build.sh` | Yes, in an Arch container and from an exported source tree |
| Rust unit tests | `cargo test --offline --locked --workspace --lib` | Included in the full workspace test run |
| Core integration and fixtures | `cargo test --offline --locked -p jong-bangla-core --tests` | Included in the full workspace test run |
| Documentation examples | `cargo test --offline --locked --workspace --doc` | Included in the full workspace test run |
| Synthetic Fcitx5 and FFI lifecycle | `ctest --test-dir target/ci-fcitx5 --output-on-failure` | Yes, after the full script builds this directory |
| Staged installation | `python3 tools/check-install.py target/ci-fcitx5` | Yes; does not configure a desktop |
| Documentation links | `python3 tools/check-docs.py` | Yes |
| Tool regression tests | `python3 -m unittest discover -s tools/tests -v` | Yes; real cargo-deny cases run in the policy job |
| Source privacy tripwires | `python3 tools/check-privacy.py` | Yes, also included in the full build and exported-source run |
| Rust dependency licenses, bans, and sources | `cargo deny --workspace --all-features --locked check bans licenses sources` | Yes, separate policy job |
| RustSec vulnerabilities and advisory warnings | `cargo audit --file Cargo.lock --deny warnings` | Yes, separate policy job with current advisory data |
| External phonetic reference | `node tools/check-reference.mjs /path/to/avro-lib.js` | Not currently run in CI |

The full script also checks formatting and Clippy with warnings denied, builds
release libraries and API documentation, and runs a conversion smoke check.
It requires Rust, CMake, Ninja, a C++ compiler, Fcitx5 development files, and
Python. Compiler requirements live in the manifests and CMake. Offline Cargo
commands require dependencies to be available locally.

The ordinary CTest lifecycle test is not a sanitizer run. Synthetic tests do
not establish acceptance in a real desktop or application.

## Dependency and privacy checks

CI pins cargo-deny 0.20.2 and cargo-audit 0.22.2, verifies the official release
archive SHA-256 hashes before extracting binaries, and records both versions.
For local checks install these versions with Cargo into your development tool
directory, then make its `bin` directory available on `PATH`:

```sh
cargo install --locked --version 0.20.2 cargo-deny
cargo install --locked --version 0.22.2 cargo-audit
cargo deny --workspace --all-features --locked check bans licenses sources
cargo audit --file Cargo.lock --deny warnings
python3 tools/check-privacy.py
python3 -m unittest discover -s tools/tests -v
```

Tool installation, missing registry metadata/sources, and the current advisory
database require network access. The normal offline build does not install
these tools or fetch advisories. The source scan and its Python regression
tests need only Python; the dependency regression tests additionally require
Cargo and cargo-deny on `PATH`. They use temporary offline path crates without
building or downloading the real banned packages. Without cargo-deny, that
module reports skips locally and in the documentation job; the policy CI job
requires the tool and runs every dependency regression case.

The regressions accept a permissive private graph and reject renamed/direct,
transitive, dev, build, and target-specific banned dependencies, plus missing,
unapproved, dev, and build dependency licenses. Synthetic source cases reject
Rust and native networking calls/imports, logging, persistence, telemetry,
process launches, and core global/platform patterns. A CLI test confirms future
adapter discovery and diagnostics without source contents. All older Rust,
Unicode fixture, native, and release-tool tests remain part of their usual runs.

The [privacy policy](../SECURITY.md#enforcement) specifies exact scan scope,
exclusions, review duties, and limitations. The
[cargo-deny license](https://embarkstudios.github.io/cargo-deny/checks/licenses/cfg.html)
and [ban](https://embarkstudios.github.io/cargo-deny/checks/bans/cfg.html) documentation
describe the policy checks; [cargo-audit](https://github.com/rustsec/rustsec/tree/cargo-audit/v0.22.2/cargo-audit)
documents RustSec auditing. A passing text scan does not establish the privacy
of arbitrary code. No desktop acceptance, benchmark, or sanitizer run is needed
for policy tooling alone; changes to typing still require the applicable layers.

## Fixtures and compatibility

Keep the complete existing regression suite. Store independently authored
fixtures as UTF-8 TSV under [tests/fixtures/](../tests/fixtures/), with raw input,
expected Bangla, and exact Unicode code points. Visual similarity is insufficient.
Do not copy the reference implementation into production.

For phonetic changes, independently check each spelling, vowels and context,
following-r behavior, case, overlapping matches, and interactions with existing
rules. Use the pinned external source identified in the fixtures; the reference
helper rejects a different source hash and requires Node.js. License and provenance belong in
[THIRD_PARTY_NOTICES](../THIRD_PARTY_NOTICES).

Keep deliberate differences in `unicode-case-policy.tsv`, with separate engine
and reference expectations. Do not count them as parity cases or silently
replace expected output to make tests pass. Add regressions for corrected
behavior and property tests only for useful invariants, such as determinism and
reset behavior. All fixture files are discovered by the reference checker; it
also requires each parity fixture to be included by the Rust regression suite
and rejects conflicting expectations for repeated input.

### Reference coverage audit

The [#26](https://github.com/shaadahmmed/jong-bangla-keyboard/issues/26) audit
checked 522,973 parity rows (493,369 distinct inputs) across 304 TSV files,
including 40 new independently authored interaction cases. Repeated rows agree.
The separate policy fixture has 60 cases: 51 deliberate differences and nine
agreements. The engine preserves unsupported Unicode case; the reference
lowercases most UTF-16 code units. Neither normalization nor visual equivalence
substitutes for exact output comparisons.

[Reference coverage evidence](evidence/reference-coverage.json) inventories every
pinned pattern by zero-based index and records the actual selected default and
contextual rules. Its family grouping is descriptive, not an upstream taxonomy:

| Family | Selected / total patterns | Selected / total contextual rules |
| --- | --- | --- |
| Digraphs and conjuncts | 168 / 169 | 0 / 0 |
| Single consonants | 28 / 28 | 5 / 5 |
| Nasal-prefixed spellings | 30 / 30 | 0 / 0 |
| R and reph | 9 / 9 | 5 / 5 |
| Vowels | 15 / 16 | 17 / 28 |
| Escapes | 18 / 19 | 0 / 0 |
| Symbols | 8 / 8 | 0 / 0 |
| Digits | 10 / 10 | 0 / 0 |

Every reference spelling has a standalone fixture. Of 289 pattern entries,
286 are selected. The later duplicate `Sc` is shadowed by the earlier `Sc`;
`AZ` and `` A` `` normalize to lowercase forms before matching. Of 38 contextual
rules, 27 are selected. The other 11 are the second rules for `OI`, `OU`, `O`,
`rri`, `oo`, `i`, `I`, `u`, `U`, `ee`, and `e`: their punctuation prefix is
subsumed by the preceding non-consonant prefix with the same suffix conditions.
These are unreachable reference entries, not missing Jong behavior. The trace
runs in a separate VM and its output is checked against the untouched parser.

Reproduce with the external pinned source from
[THIRD_PARTY_NOTICES](../THIRD_PARTY_NOTICES), Node.js, and the workspace Rust
toolchain; these commands make no desktop changes:

```sh
node tools/check-reference.mjs /path/to/avro-lib.js /tmp/reference-coverage.json
node tools/audit-context.mjs /path/to/avro-lib.js /tmp/mixed-context-audit.json
cargo test --offline --locked --test properties
```

The [bounded differential audit](evidence/mixed-context-audit.json) compares
127,240 distinct inputs, including contexts and ASCII case variants for every
pinned spelling, overlaps, following-r forms, symbols, escapes, and Unicode
boundaries. It found zero unexpected differences and the three expected policy
probe differences. Generated probes use the external parser as an oracle;
they are distinct from independently authored expected-output fixtures. Reports
record source/tool hashes, runtime versions, and deterministic result hashes.

The property suite checks call-order independence, insertion/deletion against
whole-input conversion at every scalar prefix, finalization/reset history
removal, and independent composition sessions over 2,117 bounded fragment
combinations. Rust CI runs these properties and all older regression tests.
The external reference and differential checks remain manual, not CI gates.

This finite corpus establishes only these cases. Longer combinations, arbitrary
Unicode/case contexts, every possible rule interaction, and desktop behavior
remain unverified. Selected-rule coverage does not prove exhaustive parity.

## Memory checks

`python3 tools/check-memory.py SANITIZED_BUILD_DIRECTORY` requires a separately
sanitized native build. It first requires the detector to find an intentionally
leaked Rust session. An unavailable or broken detector fails the check.
Success does not prove all Rust code was instrumented or guarantee leak freedom.

Planned in [#27](https://github.com/shaadahmmed/jong-bangla-keyboard/issues/27):
verify reproducible ASan/LSan boundary checks and their Rust/native coverage,
plus appropriate UBSan checks. Use Valgrind Memcheck separately on an unsanitized
local release build for release/leak checks. Use heaptrack to investigate
allocation growth. Add exact recipes only after verifying them.

References: [ASan](https://clang.llvm.org/docs/AddressSanitizer.html),
[LSan](https://clang.llvm.org/docs/LeakSanitizer.html),
[Valgrind](https://valgrind.org/docs/manual/QuickStart.html),
[heaptrack](https://apps.kde.org/heaptrack/).

## Maintainer-run desktop acceptance

Use CachyOS KDE Plasma Wayland on the reference Modern 15 A5M. The maintainer
runs tests and any required installation or input-method setup. Agents provide
exact setup instructions for the build and never change system input settings.

Before a Fcitx5 release, test in Kate, Firefox, KWrite, and the Python GTK and Qt
test environments. For a task, run the affected scenarios.

| Steps | Expected result |
| --- | --- |
| Type `kh12T` | Editable preedit shows `খ১২ট` |
| Press Backspace, then Ctrl+Backspace | One raw character is removed, then the active buffer clears without committing |
| Use deletion keys with no active input | The application handles deletion normally |
| Type a word, then Space or Enter | Bangla commits once; the application handles the boundary once |
| Type punctuation, escapes, digits, and mixed case from a changed fixture | Exact expected output remains editable until a boundary |
| Press Escape with and without active input | Commit and consume while active; otherwise pass Escape through |
| Use application shortcuts and navigation during composition | Pending text finalizes correctly; application actions are not swallowed |
| Change focus, switch input methods, then revisit the field | No duplicate commit or composition shared across fields |
| Disable password input methods in Fcitx5 and type synthetic text in a password field | No Jong composition or stale preedit |

Record the commit, distro, desktop, Fcitx5, application/toolkit versions, Wayland
or XWayland backend, steps, and actual results on the PR or bug issue. Do not
infer XWayland or other distro coverage. Keep package tests separate from engine
tests. Report only checks actually run in this task.
