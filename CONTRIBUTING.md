# Contributing to Jong Bangla

Jong Bangla is an experimental Bangla phonetic input method. Start with the
[README](README.md), the [current handoff](docs/progress.md#current-position),
and the relevant [requirements and behavior decisions](docs/v1.md).
[AGENTS.md](AGENTS.md) describes the detailed development workflow.

## Report a bug or suggest a change

Use [GitHub Issues](https://github.com/shaadahmmed/jong-bangla-keyboard/issues).
Search existing reports before opening an issue. Bug reproduction, investigation,
workarounds and resolution/deferral decisions belong in the issue, rather than
README, requirements or progress-log bug narratives. Docs may link to an issue
and must still state the implementation and validation scope accurately.

For conversion bugs, provide a minimal synthetic phonetic input, expected and
actual Bangla output, and Unicode code points when visually similar text differs.
State the reference and revision used for the expected behavior. For desktop
bugs, include reproduction steps, OS/distro, desktop, input framework and
application/toolkit versions, and the actual native or compatibility input route.
For Linux, distinguish Wayland from XWayland. Distinguish an
active editable word from text already committed to the application.

Use disposable sample text. Do not include passwords, private typed text or
unrelated application data in reports. Feature requests should explain the
desired typing behavior and whether they change a confirmed v1 decision.

## Prepare a change

Keep each change focused and independently reviewable. Follow the
[development guide](docs/development.md) for prerequisites and commands; run them
from the repository root. No network service is needed for ordinary Rust checks.

Before starting a new task, inspect open GitHub Issues and pull requests. Finish
existing work and prioritize actionable bugs before unrelated work. Keep blocked
issues open with an explanation; never close a valid issue just to clear the
queue. Explain blocked work or unclear priorities before proceeding. If the
tracker is unavailable, report that limitation instead of assuming it is empty.

Create a fresh branch from updated `main` for each coherent task and submit a
pull request to `main`; do not push task changes directly to `main` or reuse a
completed task's branch. Documentation and maintenance use the same process.
Preserve unrelated work.

- Keep transliteration and composition independent of Fcitx5 and desktop APIs.
- Add meaningful regression cases for behavior changes. For phonetic rules,
  verify exact Unicode, context and overlapping matches against the
  [pinned reference](docs/reference-checks.md).
- Keep fixtures independently authored and record their provenance. Do not copy
  upstream source or rule tables without a separate license review.
- Keep typed text local and avoid input logging.

## Validate and submit

For Rust changes, run the complete workspace check block in the development
guide, including API docs and the conversion smoke example. Run the Fcitx5
checks and staged installation check when changing the adapter; keep synthetic
harness results separate from actual desktop observations. Use reference and
resource checks when relevant to the behavior or claims being changed. Report
any check you could not run.

For documentation-only changes, check relative links, heading anchors, command
consistency and `git diff --check`; application tests are unnecessary.

Update usage instructions with code changes, behavioral decisions in
[docs/v1.md](docs/v1.md), and the three current handoff sections in
[docs/progress.md](docs/progress.md). Add notable user-facing changes under
`Unreleased` in [CHANGELOG.md](CHANGELOG.md); routine internal steps belong in Git
and the handoff. Keep the changelog distinct from detailed validation records.

The maintainer approved autonomous task delivery on 2026-11-05, replacing the
previous per-commit confirmation requirement. After completing the task, relevant
documentation and checks, an agent commits, pushes and creates a PR without
routine confirmation requests. Include only the task's work and use descriptive
messages. PRs explain the problem, resulting behavior, validation and material
limitations, and link related issues. Use `Fixes #123` only when the PR fully
resolves that issue. CI checks documentation/release tooling and the Rust/Fcitx5
build; hosted status checks do not replace desktop smoke observations.

## Review, merge and cleanup

Review the complete PR for correctness, architecture, regressions and test
coverage. Assess memory ownership/leaks, unsafe boundaries, performance,
security and compatibility when relevant. Documentation-only changes need link
and consistency checks, rather than runtime measurements. Identify self-review
explicitly; do not present it as independent approval. Independent review is
useful when available, but agents must not delegate without the user's request.

Post each finding on the PR with its file/line or affected setting, severity,
evidence or reproduction, impact and recommended correction. Distinguish
optional suggestions from defects. Fix findings, rerun affected checks and
review the updated diff. Keep bug reports and investigation in linked GitHub
Issues; PR comments describe the actionable review finding.

Merge only when the latest revision passes required checks, all review findings
and conversations are resolved, and there are no merge conflicts. A new push
requires review of the changes and checks for that revision. Never bypass branch
protections to finish a task. Explain any blocked gate on the PR and leave the
work open; a clean review does not guarantee the absence of defects.

Verify the merge and post-merge CI before deleting the completed task's remote
and local branches and synchronizing local `main`. Delete only that task's
branches, preserve unrelated work, and do not force-delete unmerged work. If
post-merge verification fails, keep the task branches, record the failure in an
Issue and fix it through a new branch/PR. Close issues only when resolved or
with a justified closure reason; a fixing PR can close them on merge.

Apply relevant PR labels: `enhancement`, `bug`, `breaking-change`, `documentation`
or `dependencies`. Use `skip-release-notes` only for changes with no release-note
value. Labels categorize generated notes; they do not select the release version.
Follow the [release guide](docs/releases.md) for manual versioning, release PRs,
draft review and publication. Project code is [MIT licensed](LICENSE); retain
applicable notices and document any third-party obligations.

Platform and packaging work follows the [staged roadmap](docs/roadmap.md).
Keep release scope and acceptance evidence separate from planned availability.
