# Development guide

Run all commands from the repository root. For contribution scope and review
expectations, read [CONTRIBUTING.md](../CONTRIBUTING.md). Obtain a Git checkout
for contributor checks; an extracted source archive is sufficient for the Rust
and Linux-adapter build/test blocks. For installation, use the separate
[installation guide](installation.md) and [IBus experiment guide](ibus.md).
Experimental Fcitx5 and IBus adapters are implemented; other platform and
package work follows the [roadmap](roadmap.md).

## Documentation and release tooling

For documentation and release-tooling changes, use Python **3.11 or newer** and
run:

```sh
python3 tools/check-docs.py
python3 -m unittest discover -s tools/tests -v
git diff --check
```

The documentation checker validates repository Markdown links/anchors, fences
and shell example syntax. It does not fetch external links or execute examples.
It uses `git ls-files`, so it and the Git diff checks require a checkout; they
cannot run on an extracted source archive. The adapter resource measurement tool
also uses Git for provenance. CI separately builds and tests an exported source
archive with the same Rust/Linux-adapter checks as the checkout, including staged
installation. This does not make Git-based contributor/provenance checks
available in an archive. The unit tests exercise release metadata,
note-validation and release-preparation gates.
Run `actionlint` when changing `.github/workflows/`; installing ShellCheck also
enables its shell diagnostics. CI installs both tools in its build container.

The local `git diff --check` command checks uncommitted edits. CI fetches history
and checks committed changes: PRs against their base commit, pushes to `main`
across the full pushed range, and release tags against the tagged commit's first
parent (or an empty tree for a root commit).
The same job runs `python3 tools/check-release.py --base BASE_REVISION` against
that base (the root commit uses itself). An unchanged initial unreleased version
may omit dated notes, but all version fields must agree. A version change or
release heading in either revision requires complete dated notes for the current
version. Existing release notes remain checked on later ordinary PRs.

To run the CI build/test block locally, use `bash tools/check-build.sh` from the
source root. It runs the Rust checks below and Release Fcitx5/IBus builds, CTest and
staged-installation checks, without changing the desktop or installing system files.
To check the committed source export independently of checkout build artifacts:

```sh
source_check_dir="$(mktemp -d)"
git archive --format=tar --prefix=jong-bangla/ HEAD | gzip -n > "$source_check_dir/source.tar.gz"
tar -xzf "$source_check_dir/source.tar.gz" -C "$source_check_dir"
(cd "$source_check_dir/jong-bangla" && bash tools/check-build.sh)
rm -rf "$source_check_dir"
```

This checks `HEAD`, so commit intended changes first. CI uses a temporary directory
outside the checkout, verifies there is no enclosing Git worktree, and cleans it
on exit. Export trusts only the exact CI workspace for that Git command, covering
container/checkout ownership differences without changing global Git settings.
The archive has the same layout and compression as the release asset;
the version-specific release prefix is substituted only when drafting a release.

## Build and check the Rust workspace

Use Rust/Cargo **1.99.1 or newer**, with rustfmt and Clippy. This initial baseline
is the toolchain actually validated, not evidence that older Rust cannot work.
The library uses the Rust 2024 edition and has no external dependencies.

From the repository root:

```sh
cargo fmt --all -- --check
cargo clippy --offline --locked --workspace --all-targets -- -D warnings
cargo test --offline --locked --workspace
cargo build --offline --locked --workspace --release
cargo doc --offline --locked --workspace --no-deps
cargo run --offline --locked --example convert -- 'kh12T'
```

The conversion example prints `খ১২ট`. See the [typing guide](typing.md) for
more examples and composition controls. API docs are generated in `target/doc/`.

## Build and check the Fcitx5 experiment

This builds an experimental addon and runs synthetic input through the installed
Fcitx5 dispatcher. It does not install the addon, connect a desktop frontend, or
change input-method settings. Limited user-reported desktop smoke observations
are recorded in the [validation record](fcitx5-validation.md#fcitx5-local-feasibility-result);
the full frontend matrix is still unverified.

In addition to Rust, use Fcitx5 Core/Utils development headers **5.1.23 or newer**,
a C++20 compiler, CMake **3.25 or newer**, and Ninja. These are build requirements;
only the versions in the [environment record](fcitx5-validation.md#fcitx5-local-feasibility-result)
have been validated. Cargo remains offline and adds no registry dependencies.

```sh
cmake -S adapters/fcitx5 -B target/fcitx5 -G Ninja -DCMAKE_BUILD_TYPE=Debug
cmake --build target/fcitx5
ctest --test-dir target/fcitx5 --output-on-failure
```

The build produces `target/fcitx5/libjong-bangla.so` and
`target/fcitx5/jong-fcitx5-harness`. The harness loads that actual shared addon,
allows only it and a test passthrough engine, and uses temporary XDG configuration,
cache and runtime directories. Build-local metadata contains the absolute library
path and is unsuitable for installation. Separate install rules generate metadata
without a build path; see [experimental installation](installation.md#install-the-experimental-addon)
for the explicit install/removal procedure and
[layout decisions](fcitx5-validation.md#experimental-local-installation-plan).
Only synthetic strings are recorded by the harness; the addon has no input logger.

Ten suites check editing, boundaries/shortcuts, releases/modifiers/repeats, resolved
text, invisible buffers, switching/focus/reset, context isolation, fallback preedit
and explicit preedit clicks. They verify UTF-8 cursor offsets and ordered
preedit/commit/application-key effects, including framework-owned shortcuts and
both focus-out commit owners. A simulated frontend commit is not evidence that a
real toolkit honors that path. Actual AltGr/compose completion, document relocation,
Wayland/XWayland delivery and desktop UI still need systematic smoke tests.
Use the [remaining desktop checklist](fcitx5-validation.md#remaining-desktop-smoke-checklist)
to report those observations and application runtime details.
The user has manually confirmed that the updated Escape behavior works. For
repeat tests, `ki` then Escape should keep কি, and the next `i` should start a
fresh ই. Follow the explicit install/restart procedure for a new desktop build;
an already loaded process keeps its old implementation. The desktop checklist
uses installed applications and does not require the historical private helper.
The precise
[boundary contract and limits](fcitx5-validation.md#fcitx5-local-feasibility-result) are recorded
alongside the product specification.

For C++ formatting (validated with clang-format 23.1.4):

```sh
clang-format --dry-run --Werror adapters/fcitx5/addon.cpp adapters/ffi/jong.h \
  adapters/fcitx5/tests/harness.cpp adapters/fcitx5/tests/memory.cpp \
  adapters/fcitx5/tests/resources.cpp
```

Run this for C++ changes; current CI does not enforce C++ formatting. Adding that
job is a planned tooling change. For adapter changes, also run CTest and the
staged installation check in the [installation guide](installation.md).

The Rust workspace checks above include the C-ABI crate through `--workspace`. To repeat
the C++ AddressSanitizer/UndefinedBehaviorSanitizer check as well:

```sh
cmake -S adapters/fcitx5 -B target/fcitx5-sanitized -G Ninja -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_CXX_FLAGS='-fsanitize=address,undefined -fno-omit-frame-pointer' \
  -DCMAKE_SHARED_LINKER_FLAGS='-fsanitize=address,undefined' \
  -DCMAKE_EXE_LINKER_FLAGS='-fsanitize=address,undefined'
cmake --build target/fcitx5-sanitized
ASAN_OPTIONS=detect_leaks=0 ctest --test-dir target/fcitx5-sanitized --output-on-failure
```

These sanitizers instrument the C++ addon and harness, not the Rust static library
or the system Fcitx5 libraries. The command above disables leak detection because
LeakSanitizer fails under a ptrace execution sandbox; it is not a leak check.
Rust boundary tests separately check invalid scalar arguments, UTF-8 spans and
recovery after a caught panic. On Linux, workspace tests also run five isolated
failure scenarios: ordinary heap-payload cleanup, a panicking payload destructor,
double panics during operation/cleanup, and a panicking runtime hook. Expected
aborts stay in child processes with core dumps disabled. The ignored child helper
is invoked by the parent test; it needs no separate manual run.

The boundary attempts to release a caught payload once. If its destructor panics,
the replacement payload is deliberately retained, and the session is cleared.
Double panics and panicking hooks still abort; this policy is not a guarantee of
leak freedom or recovery from arbitrary destructor code. See the
[failure-policy evidence](adapter-contract.md#c-abi-caught-panic-policy-review).

For a leak check, use the same sanitized build in an ordinary terminal outside
ptrace/debugger tracing, with Python 3 available:

```sh
python3 tools/check-memory.py target/fcitx5-sanitized target/ibus-sanitized
```

This first requires LeakSanitizer to detect an intentionally lost Rust session,
then runs 20,000 C-ABI lifecycle cycles and the ten dispatcher suites with
ASan/UBSan/leak detection enabled. It fails if the detector is unavailable, if
the build lacks leak detection, or if a normal workload reports an error. The
normal lifecycle test is also included in CTest. The optional second build
argument runs the production IBus service suite with the same diagnostics;
configure it using the [IBus sanitizer commands](ibus.md#build-and-synthetic-checks). No suppression file is used.
Rust heap allocations are observed through the system allocator, as verified by
the deliberate leak; this does not instrument Rust memory accesses. These
synthetic tests do not exercise every failure path or a live desktop daemon.
See the [results and panic-path limit](performance.md#local-resource-measurement-and-leak-check).

## Library structure

[`src/lib.rs`](../src/lib.rs) exposes `jong_bangla_core::transliterate` and the
`Composition`, `CompositionKey`, and `KeyEffect` types.
[`src/composition.rs`](../src/composition.rs) owns the editable raw buffer and
converted preedit, plus platform-independent editing actions. It reuses the
transliterator without retaining committed text. Regression sequences are in
[`tests/composition.rs`](../tests/composition.rs).

The transliterator lives in private modules under `src/transliteration/`:

- [`mod.rs`](../src/transliteration/mod.rs): the scanner, per-call context, and
  explicit matching priority across rule families.
- [`case.rs`](../src/transliteration/case.rs): selective ASCII aliases before rule matching;
  Unicode and the remaining case distinctions are preserved.
- [`rules.rs`](../src/transliteration/rules.rs): independently authored mapping
  tables, retaining their verified order and provenance comments.
- [`vowels.rs`](../src/transliteration/vowels.rs): fixed vowel-sign escapes and
  ordinary contextual vowels; the scanner preserves ng/nasal-r priority and
  handles ordinary `rri` plus `aZ`/`oZ`.
- [`symbols.rs`](../src/transliteration/symbols.rs): ordered punctuation, symbol escapes,
  and empty-output backticks; all reset raw phonetic context.
- [`reph.rs`](../src/transliteration/reph.rs): leading-`rr` attachment, raw preceding-r
  guard, and terminal `rrr` exception.
- [`following_r.rs`](../src/transliteration/following_r.rs): shared following-`r`
  attachment and exceptions based on raw keys.

The shared private Rust boundary and C header are under
[`adapters/ffi`](../adapters/ffi/Cargo.toml). The experimental IBus service uses
C11/GLib under [`adapters/ibus`](../adapters/ibus/CMakeLists.txt); build and test
commands and actual validation scope are in the [IBus guide](ibus.md). Format
its C/C++ sources with:

```sh
clang-format --dry-run --Werror adapters/ibus/*.c adapters/ibus/*.h adapters/ibus/tests/*.cpp
```

The experimental Fcitx5 addon is under
[`adapters/fcitx5`](../adapters/fcitx5/CMakeLists.txt), with shared Rust C-ABI
usage and C++ framework code. The core still forbids unsafe code and has no
platform dependencies. See [the architecture plan](v1.md#proposed-architecture).

Source comments keep the API contract and reasons for non-obvious matching
choices close to the code. Detailed rule behavior belongs in
[the behavior notes](v1.md#transliteration-api); exhaustive examples live
in tests and fixtures. Crate documentation keeps three transliteration examples;
the `Composition` type includes an executable word-deletion example.
