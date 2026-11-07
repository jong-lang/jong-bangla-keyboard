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
| Native package lifecycle | [Container commands and coverage](PACKAGING.md#recipes-and-verification) | Yes; separate Arch, Debian testing and Fedora 44 runtime images |
| Documentation links | `python3 tools/check-docs.py` | Yes |
| Tool regression tests | `python3 -m unittest discover -s tools/tests -v` | Yes; real cargo-deny cases run in the policy job |
| Synthetic benchmark smoke | `python3 tools/measure-baseline.py smoke --output target/perf-smoke` | Yes; protocol/workload checks only, no timing thresholds; [full local baseline](PERFORMANCE.md) |
| Source privacy tripwires | `python3 tools/check-privacy.py` | Yes, also included in the full build and exported-source run |
| Rust dependency licenses, bans, and sources | `cargo deny --workspace --all-features --locked check bans licenses sources` | Yes, separate policy job |
| RustSec vulnerabilities and advisory warnings | `cargo audit --file Cargo.lock --deny warnings` | Yes, separate policy job with current advisory data |
| Native ASan/UBSan and allocator LSan | `python3 tools/check-memory.py target/memory-sanitizers` | Yes, separate Clang build; see recipes below |
| Release Rust/native Memcheck | `python3 tools/check-memory.py --mode valgrind target/memory-release` | Yes, separate unsanitized build |
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

Run both recipes for ownership/native boundary changes and before a release.
The separate memory CI job runs both, retains synthetic stdout/stderr and
Memcheck XML as artifacts, and records toolchain versions. The ordinary build's
CTest run remains unsanitized. No desktop acceptance or performance benchmark
is needed for changes to memory tooling alone.

### Prerequisites and coverage

Use x86-64 Linux, the ordinary build prerequisites, Clang with its matching
compiler-rt, LLVM tools (`llvm-nm`, `llvm-symbolizer`), and Valgrind. Install
`clang compiler-rt llvm valgrind debuginfod` alongside the build packages on
Arch. The verified local combination is Rust 1.99.1, Clang/compiler-rt 23.1.4,
Fcitx5 5.1.23, and Valgrind 3.25.1. CI records rolling Arch package versions;
other compiler/OS combinations are not established by this recipe. Neither
Cargo manifest's minimum Rust requirement changes. No nightly or
`RUSTC_BOOTSTRAP` is used.

Use fresh, separate Ninja build directories and ordinary Cargo release settings.
Unset custom `RUSTFLAGS`, `CARGO_ENCODED_RUSTFLAGS`, `CXXFLAGS`, linker overrides,
and preloads before reproducing these commands. Do not combine Valgrind with
sanitizers. The checker verifies the CMake build marker and uses `llvm-nm` to
check ASan/UBSan references in the addon, both workload objects, and Rust archive.
Unexpected or missing instrumentation fails, rather than changing coverage claims.
These symbol checks establish references, not exhaustive instruction coverage.

| Component | Native sanitizer build | Release Memcheck |
| --- | --- | --- |
| C++ addon, FFI workload, Fcitx5 harness | ASan and UBSan `undefined` group instrumented | Executed machine code checked dynamically |
| Native fault controls | ASan/UBSan instrumented and required to fail | Not built/run; release uses the Rust-session leak control |
| Rust core, FFI, Rust standard library | Ordinary stable release archive, no ASan/UBSan instrumentation | Executed machine code checked dynamically |
| System Fcitx5, C/C++ libraries | Not rebuilt/instrumented | Executed machine code checked dynamically |
| Rust heap allocations through the system allocator | LSan observes lost allocations; verified with a leaked Rust session | Memcheck observes lost allocations; same control |

Native ASan does not check arbitrary Rust loads/stores, and native UBSan is not
a Rust undefined-behavior checker. The `undefined` group does not include every
Clang check (for example `vptr`). Full Rust ASan instrumentation would require a
separate verified nightly/runtime/standard-library recipe; none is claimed here.
LSan uses allocator interception and conservative reachability, so a positive
leak control does not establish full Rust instrumentation or general leak freedom.
Memcheck also has limits for stack/global bounds, custom allocators, optimized
code, and unexecuted paths. It is not a Rust aliasing/provenance checker.

### Native ASan, UBSan and allocator LSan

```sh
cmake -S adapters/fcitx5 -B target/memory-sanitizers -G Ninja \
  -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DJONG_ENABLE_SANITIZERS=ON
cmake --build target/memory-sanitizers
python3 tools/check-memory.py target/memory-sanitizers
```

The option supplies `-fsanitize=address,undefined`, debug information and frame
pointers to native compilation, and sanitizer flags to native linking. The
instrumented executable supplies ASan runtime symbols to the loaded addon;
only this build omits the module's `--no-undefined` link constraint. Run these
binaries through the checker; do not install them into the desktop.

Before clean workloads, the checker requires three independent positive controls:
a native heap overread, native signed overflow, and an intentionally lost Rust
session with live buffers. Each must produce its specific diagnostic and exit 23.
Only then must `jong-ffi-memory` and `jong-fcitx5-harness` exit zero with no
ASan/LSan/UBSan diagnostic. Detector environment options are overridden to enable
leak detection and stop on errors, with a common exit code of 23. Controls are
not ordinary CTest cases, and are never passed to the clean workloads implicitly.

The FFI workload covers creation, Unicode insertion, editing, commit, all reset
and cancellation actions, destruction with pending composition, null handles,
invalid arguments and C++ RAII cleanup after an injected exception. The real
addon harness exercises isolated synthetic input contexts and lifecycle events.
It does not force every addon allocation or UI callback to fail. Rust panic
cleanup is checked separately below and by the ordinary Rust test suite.

### Unsanitized release Memcheck and exceptional cleanup

```sh
cmake -S adapters/fcitx5 -B target/memory-release -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DJONG_ENABLE_SANITIZERS=OFF \
  -DCMAKE_CXX_FLAGS_RELEASE='-O2 -g -DNDEBUG'
cmake --build target/memory-release
python3 tools/check-memory.py --mode valgrind target/memory-release
```

Memcheck first must detect the lost Rust session with a definitely-lost report
and exit 23. The clean lifecycle and addon workloads must then exit zero with
no memory errors or definite, indirect, or possible leaks. Still-reachable
blocks are recorded and permitted, not described as leaks or zero retention.
No project suppressions are applied to the native workloads. The helper uses
`--command-line-only=yes` to ignore user/local `.valgrindrc` files and
`VALGRIND_OPTS`, so inherited options or suppressions cannot disable checks.
It also uses `--leak-check=full`,
`--show-leak-kinds=all`, `--errors-for-leak-kinds=definite,indirect,possible`,
`--track-origins=yes`, and `--error-exitcode=23`, and validates completed XML
reports. Missing, malformed, incomplete, or stale reports cannot pass.

The helper also builds the existing private Rust panic tests with
`cargo test --offline --locked --release -p jong-bangla-fcitx5-ffi --lib --no-run
--message-format=json`, using a separate `rust-panic-tests` target directory
inside the build. It runs `panic_tests::panic_policy_child --exact --ignored
--nocapture --test-threads=1` directly under Memcheck. `JONG_TEST_PANIC_MODE=0`
must reclaim an ordinary heap panic payload and recover the session cleanly.
Mode 1 must detect the deliberately retained replacement payload when the
original payload's destructor panics. This is an expected positive control,
not a clean-workload exemption or a production fault-injection interface.

Both Rust-only probes apply [a narrow libtest suppression](../tools/valgrind-rust-tests.supp)
for an observed possible leak in the Rust test runner's main-thread context.
It matches the allocator, standard-library thread/context, and libtest receive
stack frames. It suppresses only that possible-leak stack, never definite leaks
or Jong allocation paths. Suppression counts are printed and retained in XML.
This is a limit of the Rust probe evidence, not a claim that all runtime
allocations are freed. A changed toolchain may require renewed investigation.

The existing ordinary Rust `panic_policy_subprocesses` test also verifies
unrecoverable double-panic and panicking-hook aborts. Those abort probes are not
clean leak workloads. Exceptional retention remains as documented in
[jong.h](../adapters/fcitx5/jong.h) and
[the architecture](ARCHITECTURE.md#ffi-boundary); these checks do not promise
recovery from OOM/abort, invalid pointers, or every exceptional cleanup path.

### Failures, logs and optional profiling

The helper exits nonzero with `FAIL:` for missing tools/binaries, wrong build
mode, timeouts (300 seconds per process), failed controls, unexpected workload
reports or detector startup failures. Each completed subprocess's synthetic
stdout/stderr and each Memcheck XML report are retained under the selected
build's `memory-logs-sanitizers` or `memory-logs-valgrind` directory. Python
regressions inject missing detectors, incorrect exits/diagnostics, timeouts,
wrong build modes and invalid reports. A real Valgrind regression requires a
mismatched allocation/free to fail even with `.valgrindrc` disabling that check.
Run them with `python3 -m unittest discover -s tools/tests -p test_memory.py -v`.
The real-detector case skips locally without Valgrind or `c++`; the memory CI
job installs both and runs this suite.

LSan requires process inspection. A ptrace-restricted sandbox, debugger or
unsupported host can make its control fail; use a suitable test runner without
changing host ptrace settings. Valgrind may require matching glibc loader debug
symbols (for example `libc6-dbg` on Debian). On Arch, install `debuginfod` and use
`DEBUGINFOD_URLS=https://debuginfod.archlinux.org` for the Memcheck command;
on CachyOS use the distro's matching server. This tool-only lookup needs network
access, or pre-cached debug symbols. CI enables the Arch lookup explicitly.
A detector that cannot start is unavailable evidence, never a passing check.

Heaptrack is optional for allocation-growth investigations on the same
unsanitized release build. With heaptrack installed, a verified synthetic recipe is:

```sh
heaptrack --record-only -o /tmp/jong-synthetic-allocations \
  target/memory-release/jong-ffi-memory
heaptrack_print /tmp/jong-synthetic-allocations.zst > /tmp/jong-synthetic-allocations.txt
```

Heaptrack 1.5.0 writes the `.zst` file shown above; use the printed output filename
if your distribution chooses another compression format. Review allocation
stacks and retained capacity for growth investigations; profiler leak labels
are not a substitute for ASan/LSan or Memcheck acceptance. Profile only these
synthetic harnesses, never a real input-method daemon or application containing
typed text. Keep benchmark numbers in [PERFORMANCE.md](PERFORMANCE.md).

References: [ASan](https://clang.llvm.org/docs/AddressSanitizer.html),
[LSan](https://clang.llvm.org/docs/LeakSanitizer.html),
[UBSan](https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html),
[Rust sanitizer limitations](https://doc.rust-lang.org/unstable-book/compiler-flags/sanitizer.html),
[Memcheck](https://valgrind.org/docs/manual/mc-manual.html),
[Valgrind debuginfod](https://valgrind.org/docs/manual/manual-core.html#manual-core.debuginfod),
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

### Package desktop acceptance

The maintainer runs this checklist in disposable x86-64 KDE Plasma Wayland VMs
for Debian testing and Fedora 44, plus the CachyOS reference desktop or an Arch
VM. Use a fresh snapshot and repositories supplying Fcitx5 5.1.23 or newer.
Record the ISO URL/checksum or VM image identity, distro update date, kernel,
Plasma, Fcitx5, package version/hash, application/toolkit versions and backend.
Container identities and results are recorded separately by the package runner.

1. Install the matching PR artifact with the command in
   [PACKAGING.md](PACKAGING.md#install-upgrade-activate-and-remove). Install
   `fcitx5-configtool` on Arch/Fedora or `fcitx5-config-qt` on Debian, plus
   Kate, KWrite and Firefox from that distro. Check that the package manager
   resolves dependencies without copying libraries or modifying system paths.
2. Log out/in. Select Fcitx5 in KDE's Virtual Keyboard settings and add Jong
   Bangla in Fcitx5 Configuration. Expect one Jong entry, and successful
   activation without a missing-addon error. Record the exact setup changes;
   agents never perform these changes on the maintainer's desktop.
3. Run the typing scenarios above in Kate, KWrite and Firefox on Wayland,
   including focus changes, password fields, input-method switching and
   synthetic `kh12T`. Record exact actual output and any duplicated commits.
   Repeat the existing Python GTK and Qt acceptance environments if available;
   report unavailable applications explicitly. XWayland needs a separate run.
4. Install the supplied revision-2 test package over revision 1, restart the
   Fcitx5 session and repeat activation and `kh12T`. Expect the newer package
   revision, one registration and unchanged behavior. This tests a package
   revision upgrade, not migration from an earlier public engine release.
5. Switch to another input method, remove Jong with the documented command,
   then log out/in. Expect Jong's library and registrations removed, other
   input methods working, and existing user configuration retained. Restore
   the VM snapshot when finished.

Report each environment and step's actual result on the implementation PR.
Until returned, mark desktop results pending and retain the platform matrix's
existing support limits. Release publication requires this maintainer evidence.
