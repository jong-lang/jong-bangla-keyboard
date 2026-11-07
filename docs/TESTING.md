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
| Release-tool regression tests | `python3 -m unittest discover -s tools/tests -v` | Yes |
| External phonetic reference | `node tools/check-reference.mjs /path/to/avro-lib.js` | Not currently run in CI |

The full script also checks formatting and Clippy with warnings denied, builds
release libraries and API documentation, and runs a conversion smoke check.
It requires Rust, CMake, Ninja, a C++ compiler, Fcitx5 development files, and
Python. Compiler requirements live in the manifests and CMake. Offline Cargo
commands require dependencies to be available locally.

The ordinary CTest lifecycle test is not a sanitizer run. Synthetic tests do
not establish acceptance in a real desktop or application.

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
reset behavior. Coverage audit and additions are planned in
[#26](https://github.com/shaadahmmed/jong-bangla-keyboard/issues/26).
A finite passing corpus does not establish parity for every possible input.

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
