# Security and privacy

Jong Bangla sees keystrokes because it is an input method. Conversion is local:
no network access, no telemetry, no keystroke logging, and no persistence of
typed text beyond the in-memory composition and commit data needed for typing.
Applications receive committed text through the input framework.

Keep diagnostics free of typed text. Use synthetic input in tests, benchmarks,
and bug reports. Keep the core free of I/O; review native adapters for the same
privacy contract. See [architecture](docs/ARCHITECTURE.md) for ownership boundaries.

## Enforcement

Pull requests, pushes to `main`, and reusable CI runs execute a separate
dependency and privacy job. [Testing commands and setup](docs/TESTING.md#dependency-and-privacy-checks)
also work locally. No runtime dependency or service is added to typing.

- `cargo deny` checks every workspace member, all features, and all targets,
  including direct/transitive, development, build, and unpublished path crates.
  [deny.toml](deny.toml) permits MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC,
  Zlib, and Unicode-3.0 licenses. Other or missing licenses fail. These
  permissive dependency licenses require retaining their own notices and terms;
  approval does not relicense third-party code under MIT. There are no license
  exceptions. Propose any change or narrowly versioned exception in an issue
  with its license obligations and rationale for explicit maintainer decision.
- The same policy rejects listed networking runtimes, HTTP/DNS/socket/QUIC and
  WebSocket crates, and known telemetry crates, even through renamed or
  transitive dependencies. Unknown Git and non-crates.io registry sources fail.
- `cargo audit --file Cargo.lock --deny warnings` fetches current RustSec data
  and fails on known vulnerabilities and advisory warnings, including unmaintained
  or yanked crates. Fetch failures fail CI. There are no advisory ignores.
- `tools/check-privacy.py` scans Rust and C/C++ source/header files recursively
  under `src/` and `adapters/`, including Rust FFI and native bridge code. It
  rejects known networking APIs/headers, Rust I/O/process/environment modules,
  common logging, telemetry, file output, and process-launch APIs. In the core
  it also rejects static declarations, selected shared-state types, and known
  platform/FFI paths. The core's Cargo lint separately forbids unsafe code.

The source scan excludes `tests/` directories and the synthetic FFI
`adapters/fcitx5/ffi/src/panic_tests.rs` module. Other inline Rust tests remain
scanned. Tools, examples, benchmarks, external/native dependencies, generated
code outside those roots, and other source languages are outside its coverage.
CI tool installation and advisory/dependency downloads use the network during
development; the typing runtime must never do so.

This is a conservative text scan, not a compiler or dataflow analysis. It scans
comments and literals as well as a comment-stripped view; harmless occurrences
can fail. It has no inline suppression. Resolve false positives through review
of the rule or source change. Finite name lists miss new libraries, aliases,
macro-generated calls, indirect calls, dynamic loading, nested-comment tricks,
and arbitrary foreign APIs. It does not prove arbitrary code safe or determine
whether data reaching a sink is typed text. RustSec only covers known reported
issues in the locked Rust graph. Native/system libraries, CI tool dependencies,
and the separately supplied phonetic reference need their own review.

Review every new dependency, source exclusion, build script, native library, and
typing dataflow for network access, telemetry, diagnostics, and persistence.
Verify that only in-memory composition and framework commits retain typed text,
and that no core dependency introduces platform behavior, I/O, or global state.
The current std-based core keeps its existing boundary; adopting `no_std` could
restrict direct standard-library I/O but would require a separate refactor and
would not audit dependencies or foreign code. Static tripwires and unsafe-code
linting complement review without changing the runtime architecture.

## Report a vulnerability

Use [GitHub private vulnerability reporting](https://github.com/shaadahmmed/jong-bangla-keyboard/security/advisories/new).
Include the affected revision or release, environment, impact, and a minimal
synthetic reproduction. Keep vulnerability details out of public issues while
the report is being investigated. Discuss disclosure with the maintainer in
the private advisory.

Before the first release, fixes land on `main`. After releases begin, only the
latest published release receives security fixes. Older releases receive no
backports; upgrade to the latest release.

Reference licensing and attribution are recorded in
[THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES).
