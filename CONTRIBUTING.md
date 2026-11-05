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
Create a branch for every new feature or fix and submit a pull request to `main`;
do not push these changes directly to `main`. Documentation and maintenance work
should use the same branch and pull request process.

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

When an agent assists with a change, it must finish the checks and documentation,
present a detailed summary of changes, validation and limitations, and wait for
the user's explicit confirmation before committing. Task completion alone does
not authorize a commit. Use a descriptive message and include only the reviewed
work. Pull requests should explain the problem, resulting behavior, validation
and material limitations. CI checks documentation/release tooling and the Rust/
Fcitx5 build; hosted status checks do not replace desktop smoke observations.

Apply relevant PR labels: `enhancement`, `bug`, `breaking-change`, `documentation`
or `dependencies`. Use `skip-release-notes` only for changes with no release-note
value. Labels categorize generated notes; they do not select the release version.
Follow the [release guide](docs/releases.md) for manual versioning, release PRs,
draft review and publication. Project code is [MIT licensed](LICENSE); retain
applicable notices and document any third-party obligations.

Platform and packaging work follows the [staged roadmap](docs/roadmap.md).
Keep release scope and acceptance evidence separate from planned availability.
