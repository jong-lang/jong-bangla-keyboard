# Agent instructions

Read only this file at chat start. Open another document only when the table
below applies. Treat maintainer answers as authoritative; verify specific code
claims with targeted reads. Report uncertainty instead of inventing evidence.

## Detect the mode

Check `git status --short --branch` and `gh auth status`. Inspect open issues and
PRs with `gh issue list --state open` and `gh pr list --state open`. Report access
failures. Preserve unrelated work. Do not delegate without an explicit request.

- On `main`, a problem description without an implementation request means
  report mode: use the bug template, run `gh issue create`, include reproduction,
  expected and actual behavior, mark unknown details, then stop. Do not edit code.
- For a requested task, find or create its issue, update `main`, then create
  `type/issue-number-short-description`. Use `feat`, `fix`, `refactor`, `perf`,
  `docs`, `ci`, `test`, or `chore`. Do not reuse a completed branch.
- For review or fixes, verify authentication and reconstruct state from
  `gh pr view`, `gh pr diff`, and PR comments. Do not rely on previous chats.
  Fix an existing PR on its branch; reply to every addressed finding.

## Repository map

| Path | Purpose |
| --- | --- |
| `src/transliteration/` | Phonetic conversion |
| `src/composition.rs` | Editable input state and engine actions |
| `adapters/fcitx5/` | C++ addon, Rust FFI, and native tests |
| `tests/` | Integration tests and Unicode TSV fixtures |
| `examples/`, `tools/` | Conversion, reference, measurement, and check tools |
| `.github/` | CI, release automation, and contribution templates |

## Commands

Run from the repository root. Read manifests and CMake for compiler requirements.

```sh
cargo fmt --all -- --check
cargo clippy --offline --locked --workspace --all-targets -- -D warnings
cargo test --offline --locked --workspace
bash tools/check-build.sh
python3 tools/check-docs.py
git diff --check
wc -l AGENTS.md README.md
```

The build script includes Rust checks, release builds, API docs, native tests,
and staged installation checks. It requires Fcitx5 development files, CMake,
Ninja, a C++ compiler, and Python. It does not install into the desktop.
For docs-only changes, check links, budgets, and consistency. Run benchmarks and
memory checks for relevant code changes, using the guides below. Report exact
commands, outcomes, and unavailable checks in a short table. Never claim an old
result as a new run. Planned checks need an issue link; do not claim they exist.

## Conventions and delivery

- Explain the purpose and expected result before editing. Keep work coherent.
- Keep modules cohesive and control flow explicit. Add no dead code. Put needed
  refactors in their own `refactor/` branch and PR. Justify dependencies and
  abstractions in the PR; require MIT-compatible dependency licenses.
- Keep the Rust core deterministic, with no platform dependencies, I/O, or global
  state. Keep adapters thin. Fix Bangla conversion bugs in the core.
- Handle input-path errors without `unwrap`, `expect`, or panics. Confine unsafe
  code to FFI and explain each block with `// SAFETY:`. Document API behavior,
  ownership, encoding, errors, lifetimes, and panic containment at native borders.
- Keep per-keystroke allocations low; benchmark changes against the baseline.
  Keep `Cargo.toml` minimum Rust requirements consistent; justify and test raises.
- Make typing local. Add no network access, telemetry, typed-text logging, or
  persistence beyond typing needs. Use synthetic text in diagnostics and tests.
- Preserve all older tests. Validate exact Unicode, not visual similarity.
- Give the maintainer exact setup, steps, and expected results for necessary
  manual tests. The maintainer runs them. Never change system input settings.
- Use Conventional Commits. Complete docs and checks, then commit, push, and open
  a PR from its template without routine confirmation. Link the issue.
- Leave the PR open for review in a separate chat. Require a review recommending
  the latest commit, passing required checks, resolved findings, and no conflicts.
  Then wait for the maintainer's explicit merge instruction. Never bypass gates.
- After authorization, squash merge, verify post-merge CI, delete only the task's
  local and remote branches, and update `main`. Preserve work if verification fails.
- Keep docs single-purpose. Link instead of copying. Put history in CHANGELOG.md
  and measured performance numbers only in docs/PERFORMANCE.md and raw artifacts.
  Keep AGENTS.md at most 120 lines and README.md at most 80. Keep CLAUDE.md to one
  link here. Propose any additional document before creating it. Use no em dashes.

## Read when needed

| When doing this | Read this |
| --- | --- |
| Install or build for use | [README.md](README.md) |
| Change typing behavior or platform scope | [docs/FEATURES.md](docs/FEATURES.md) |
| Change module boundaries, composition, or FFI | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| Add tests, change phonetic rules, or plan manual checks | [docs/TESTING.md](docs/TESTING.md) |
| Change performance or run benchmarks | [docs/PERFORMANCE.md](docs/PERFORMANCE.md) |
| Work on privacy, dependencies, or vulnerabilities | [SECURITY.md](SECURITY.md) |
| Use reference code, fixtures, or third-party material | [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES) |
| Plan a task, review/fix/merge a PR, or prepare a release | [CONTRIBUTING.md](CONTRIBUTING.md) |
| Record or inspect release changes | [CHANGELOG.md](CHANGELOG.md) |
| File an issue or open a PR | [Bug](.github/ISSUE_TEMPLATE/bug_report.md), [feature](.github/ISSUE_TEMPLATE/feature_request.md), or [PR template](.github/pull_request_template.md) |
| Handle community conduct | [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) |
