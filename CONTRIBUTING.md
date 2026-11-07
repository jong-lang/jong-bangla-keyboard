# Contributing

Start with [AGENTS.md](AGENTS.md). It is the entry point for commands, repository
layout, conventions, and instructions on which document to read for a task.

## Choose the mode

Check the current branch and working tree before editing. Preserve unrelated work.
Check GitHub authentication and inspect open issues and pull requests before
starting a task. Report access failures; do not assume the tracker is empty.

- **Problem report:** On `main`, when the maintainer describes a problem without
  asking for implementation, create a GitHub issue with `gh issue create` using
  the bug template. Include reproduction steps, expected behavior, and actual
  behavior. Mark missing details as unknown. Do not edit code. Stop after filing.
- **Task:** Find the issue or create one first. Update `main`, then create
  `type/issue-number-short-description`. Allowed types are `feat`, `fix`,
  `refactor`, `perf`, `docs`, `ci`, `test`, and `chore`.
- **Review:** Verify `gh auth status`. Reconstruct state from `gh pr view`,
  `gh pr diff`, and PR comments. Review the complete current revision without
  relying on earlier chats. Record the reviewed commit and limits of the review.
- **Fix:** Verify authentication and reconstruct the same PR state. Work on the
  PR branch, address each finding, reply to its comment with the correction and
  validation, and push. Obtain a separate review of the updated revision.

## Complete a task

Explain the purpose and expected result before editing. Keep each task coherent.
Use Conventional Commits: `type: description` or `type(scope): description`.

Implement the change and relevant regression tests. Select checks by impact:

| Change | Required validation |
| --- | --- |
| Documentation only | Local links, line budgets, and consistency with agreed behavior and verified code |
| Rust code | Formatting, Clippy with warnings denied, unit and integration tests |
| Performance or per-keystroke behavior | Relevant code checks and comparison against the committed performance baseline |
| Memory ownership or native boundary | Relevant code checks, memory checks, and appropriate boundary sanitizers |
| Platform behavior or packaging | Relevant automated checks and a maintainer-run desktop or installation test |

Use the exact commands in AGENTS.md and the task-specific testing guide. Report
actual commands and outcomes in a short table. Identify skipped or unavailable
checks and their reasons. Do not report old results as newly run checks.
Benchmark comparisons run locally on the reference machine. CI smoke benchmarks
cannot establish performance parity. The performance baseline still requires
implementation in [#28](https://github.com/shaadahmmed/jong-bangla-keyboard/issues/28).
Use the implemented [memory recipes](docs/TESTING.md#memory-checks) for native
sanitizers and separate release Memcheck; do not describe them as full Rust
sanitizer instrumentation.

When manual testing is needed, give the maintainer the exact desktop, VM, or
container setup, steps, and expected result. The maintainer runs these tests.
Record the returned result and any remaining limits before opening the PR.
Never change the maintainer's input-method settings as a development side effect.

Complete the relevant documentation and checks, then commit, push, and open a PR
using the PR template. Link its issue and include the head commit, validation,
manual results when applicable, and a handoff for a separate review chat.
Routine commit, push, and PR creation do not require another approval.

## Review and merge

Review happens in a separate chat. Passing CI and implementation-session
self-review do not replace it. Put findings on the PR with a precise location,
severity, evidence, impact, and recommended correction. Label optional suggestions.
Assess correctness, architecture, regressions, and tests, plus ownership, unsafe
boundaries, performance, security, privacy, and compatibility where relevant.
Record findings, review limits, and an explicit recommendation for the reviewed
commit. Track bugs in issues without duplicating their reports across documents.

After fixes, rerun affected checks and review the updated diff. Before merging,
require a separate review recommending the latest revision, passing required
checks, resolved findings and conversations, and no merge conflicts. Report any
blocked gate on the PR and leave it open. Never bypass protections.

Wait for the maintainer's explicit merge instruction even when all gates pass.
Then squash merge, verify the merge and post-merge CI, delete only the completed
task's remote and local branches, and update local `main`. If verification fails,
preserve the branches and unrelated work, and track the failure in an issue.

## Engineering standards

- Keep functions and modules small and cohesive, with explicit control flow and
  no dead code. Put needed refactors in their own `refactor/` branch and PR.
- Add dependencies or abstractions only for a concrete need stated in the PR.
  Dependencies must satisfy the permissive license allowlist in `deny.toml`
  and pass cargo-deny and cargo-audit. See [SECURITY.md](SECURITY.md#enforcement)
  for scope, license obligations, and the exception process.
- Keep the core free of platform dependencies, I/O, and global state. Treat it
  as a deterministic state machine: input event in, engine actions out.
- Keep adapters thin: translate native events and engine actions. Put no
  phonetic logic in adapters. Fix Bangla output bugs in the core.
- Handle or return errors. Use `Result` for recoverable failures and actionable
  messages without typed text. Do not use `unwrap`, `expect`, or panics on the
  input path, or `unwrap` and `expect` on fallible production paths. Tests may
  use assertions and `unwrap`. Outside the input path, document the invariant
  behind any intentional panic.
- Forbid unsafe code in the core. Confine necessary unsafe code to the FFI
  layer and explain every unsafe block with a `// SAFETY:` comment. Document
  ownership, lifetimes, encoding, error behavior, and panic containment. Prevent
  Rust unwinding across the native boundary.
- Keep the per-keystroke path allocation-light. Changes to that path require
  a benchmark against the baseline; report unavailable evidence explicitly.
- Use idiomatic Rust names and consistent native naming. Document public API
  behavior, errors, and relevant invariants. Exported C functions must document
  pointer validity and ownership. Use comments to explain decisions.
- Use each crate's `Cargo.toml` `rust-version` as its minimum Rust requirement.
  Keep workspace requirements consistent. Raising the minimum requires an
  explicit justification and CI verification. Do not duplicate it in prose.

Standards apply to new work and review. They do not certify the existing code.
Review enforces rules that do not have an automated check.

| Enforcement | State |
| --- | --- |
| Formatting and Clippy with warnings denied | Implemented in `tools/check-build.sh`, called by CI |
| No unsafe code in the core | Implemented by its Cargo lint configuration |
| Dependency licenses, networking/telemetry crate bans, and dependency sources | Implemented by `deny.toml` and cargo-deny in the CI policy job |
| Known dependency vulnerabilities | Implemented by cargo-audit with warnings denied in the CI policy job |
| Known source networking, logging, persistence, and core boundary violations | Implemented by `tools/check-privacy.py`; [coverage and limits](SECURITY.md#enforcement) require complementary review |
| No explicit panics or fallible unwraps in the FFI input path | Implemented by validated action decoding and exhaustive dispatch, with action/scalar regressions; [#25](https://github.com/shaadahmmed/jong-bangla-keyboard/issues/25). Panic containment remains defensive; review enforces this policy |
| Compatibility coverage audit and useful property tests | Implemented: [finite corpus, selected-rule inventory, and limits](docs/TESTING.md#reference-coverage-audit); external reference checks run manually |
| Reproducible Rust/native memory-check recipes | Implemented: [native ASan/UBSan, allocator LSan, release Memcheck and exceptional-retention controls](docs/TESTING.md#memory-checks) in CI; Rust instructions are not sanitizer-instrumented |
| Committed performance baseline and CI smoke benchmark | Planned: [#28](https://github.com/shaadahmmed/jong-bangla-keyboard/issues/28) |

## Release policy and checklist

Finish and release Fcitx5 before IBus, then Windows TSF. The first Fcitx5 release
targets x86-64. Native packages come first; Flatpak is a later prototype.
Keep macOS out of scope unless a viable free path is established.

Use semantic versions, staying in `0.x` until stable. Prepare a release through
an issue branch and reviewed PR. Keep commits and squash titles consistent with
[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/), and keep
changelog entries focused on user-visible changes rather than a raw commit log,
following [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

Current tag automation validates versions, runs CI, and prepares a source archive
and `SHA256SUMS` in a draft GitHub Release. It does not deliver binary archives
or native packages. The maintainer publishes drafts explicitly.

Planned delivery:

| Work | Issue |
| --- | --- |
| Conventional Commits changelog generation and complete artifact drafts | [#29](https://github.com/shaadahmmed/jong-bangla-keyboard/issues/29) |
| Binary archive, .deb, .rpm, maintained AUR recipe, and clean-image checks | [#30](https://github.com/shaadahmmed/jong-bangla-keyboard/issues/30) |
| Flatpak Fcitx5 add-on prototype after the native release | [#31](https://github.com/shaadahmmed/jong-bangla-keyboard/issues/31) |

For each release:

1. Update both Cargo manifests, their lockfile entries, addon version metadata,
   and dated changelog notes together. Retain `## Unreleased`. The current
   validator requires nonempty `Highlights`, `Fixes`, `Breaking changes`,
   `Installation and upgrade`, `Tested environments`, and `Known issues` sections.
   Run `python3 tools/check-release.py --base origin/main` before the PR.
2. Pass the applicable automated checks and obtain the maintainer's desktop
   acceptance from [TESTING.md](docs/TESTING.md#maintainer-run-desktop-acceptance).
   Verify every package by installing and removing it in a clean Arch,
   Debian or Ubuntu, and Fedora container or VM, as applicable to its format.
   Record image identities and results on the PR. Container checks do not
   establish interactive desktop support.
3. Complete separate review and obtain explicit merge authorization. After
   merging and verifying CI, obtain the maintainer's release instruction before
   creating or pushing a `vX.Y.Z` tag. Do not overwrite tags or existing releases.
4. Inspect the resulting draft, notes, artifacts, and every checksum. Leave an
   incomplete draft unpublished. The maintainer performs publication.

When TSF lands, add a Windows installer and Windows acceptance checks. Initially
the installer is unsigned; document the SmartScreen warning. Revisit IBus
Flatpak feasibility in its adapter stage. Do not promise untested artifacts.

The Flatpak route needs a separate extension for the Flatpak Fcitx5 daemon;
upstream still requires native host input modules. Its parent sandbox grants
network permission. Preserve the no-network-call policy and review inherited
permissions before shipping. Findings and primary sources are recorded in #31.
