# Developer and agent guide

## Project

Jong Bangla (`jong-bangla-board`) is a Bangla phonetic desktop input method,
implemented from scratch with a reusable Rust engine. The staged release scope
includes Linux Fcitx5 and IBus, Flatpak/deb/rpm/pacman packages and maintained AUR
recipes, Windows TSF, and macOS on Apple silicon and Intel. Fcitx5 on CachyOS +
KDE Plasma Wayland is the first implementation/test environment. Follow
[the roadmap](docs/roadmap.md); planned targets are not delivered support.
Project code is MIT licensed.

`docs/v1.md` distinguishes confirmed requirements from proposals and open decisions.
Do not turn a proposal into a requirement without explaining the decision.
User instructions take precedence over this guide; update the docs when they change.

## Read project context efficiently

- Follow applicable `AGENTS.md` instructions; reuse instructions already supplied
  in the conversation instead of reading the same file again.
- At the start of a session, read only the
  [Current position](docs/progress.md#current-position),
  [Latest completed step](docs/progress.md#latest-completed-step), and
  [Next small implementation step](docs/progress.md#next-small-implementation-step)
  sections of the progress log for the current handoff.
- Use [README.md](README.md) for orientation and links to the focused guides.
  Read relevant sections of [docs/development.md](docs/development.md) for check
  commands, [CONTRIBUTING.md](CONTRIBUTING.md) for contribution expectations, and
  [docs/v1.md](docs/v1.md) for requirements and decisions needed by the task.
  Use [docs/roadmap.md](docs/roadmap.md) for platform/package stages and acceptance
  gates when the task affects release scope or delivery.
  Use [docs/adapter-contract.md](docs/adapter-contract.md) for native event and
  ownership rules, and [docs/compatibility.md](docs/compatibility.md) for reference
  provenance and Unicode policy. Read only the relevant rule-family sections in
  `docs/compatibility/` when investigating historical phonetic decisions; those
  records are not current requirements or routine handoff reading.
  Do not read these documents in full by default.
- Read historical progress entries only when investigating an earlier decision
  or regression, or when the current handoff lacks necessary context.
- Read affected code, related tests/fixtures, and check tooling as needed. Use
  targeted searches and line ranges instead of printing entire large files.
- Do not reread unchanged material already available in the conversation. After
  context compaction, recover only the sections needed to continue; reread when
  a file changes or necessary context is missing.
- Keep successful check output to a summary; inspect and show failure details
  when needed. Run all required checks without printing every passing fixture.
- Keep the current handoff accurate so routine work does not require reading
  the full history. These reading rules do not reduce validation requirements.

## Collaborate in coherent steps

- Before starting a new task, inspect open GitHub Issues and pull requests.
  Finish existing work and prioritize actionable bugs before unrelated work.
  Never close a valid issue just to clear the queue. Keep blocked issues open
  with an explanation; explain blocked work or unclear priorities before
  proceeding. If the tracker cannot be checked, report that limitation rather
  than assuming there are no open issues.
- Explain the purpose and expected result of the next coherent step before editing.
- Complete one coherent, reviewable increment at a time. Avoid combining engine
  changes, platform integration, packaging, and unrelated cleanup in one change.
- For phonetic rule coverage, prefer the largest coherent batch of related
  conjuncts or spellings that can be independently reference-checked, validated,
  and reviewed together. Start by looking for 3–6 related spellings and expand
  when the behavior remains manageable; this is a planning guide, not a cap.
  Do not split straightforward related work merely to keep batches small.
- Define each batch's scope before editing. Check each spelling's exact Unicode,
  vowel/context behavior, following-`r` behavior, and overlapping matches against
  the pinned reference independently; shared output alone does not establish
  shared behavior. Include interactions between the selected spellings and
  existing rules. Split only when behavioral differences, unresolved reference
  results, or review complexity prevent a reliable coherent change.
- Share fixture/check tooling where useful while preserving independent expected
  outputs and evidence for every spelling. Use targeted reference checks during
  investigation, then one full required validation run, documentation/handoff
  update, and review summary for the completed batch. Deliver the batch through
  the branch/PR workflow below. Repeat full checks when later edits or failures
  require them; do not repeat the full cycle for every spelling.
- Walk the user through the result in plain language: what changed, why it matters,
  how it was checked, and what comes next. Explain unfamiliar terms when introduced.
- Update the three handoff sections in `docs/progress.md` after each coherent
  step; replace their summaries rather than extending a cumulative narrative.
  Aim for 50–100 lines before the historical `Completed steps` section. Keep
  current state concise and point to coverage docs instead of listing every rule.
- In `Latest completed step`, record the date, result, actual check commands and
  outcomes, remaining limitations, and next action. Summarize successful checks;
  include failure details when they affect the handoff. Identify any older check
  results as prior evidence, not checks rerun in the current step.
- Preserve existing historical entries without routinely appending new ones.
  Use Git for detailed change history, `docs/v1.md` for requirements and behavioral
  decisions, and tests/fixtures for exact compatibility evidence. Reference a
  relevant existing commit when useful; do not try to embed a commit's own hash.
- Keep planned, in-progress, and completed work distinct. Never claim a check or
  milestone is complete without evidence.
- Track bugs, reproduction details, workarounds and release-blocking or deferral
  decisions in GitHub Issues. Link to issues from docs where needed; do not keep
  duplicate bug narratives in requirements, usage guides or the progress log.
  Keep implementation and validation limits documented accurately.
- Create a fresh branch from updated `main` for each coherent task, including
  documentation and maintenance. Do not reuse a completed task's branch or push
  task changes directly to `main`. Preserve unrelated work.
- Complete the task, relevant documentation and checks, then commit, push and
  create a PR to `main` without routine confirmation requests. Use descriptive
  commit/PR messages and include only the task's work. This workflow was approved
  on 2026-11-05 and supersedes the previous per-commit confirmation requirement.
- Review the complete PR for correctness, architecture, regressions and test
  coverage. Assess memory ownership/leaks, unsafe boundaries, performance,
  security and compatibility where relevant. State whether the review is
  self-review or independent review; do not imply self-review is independent
  approval. Match validation to the changed behavior and document its limits.
- Post findings on the PR with precise locations, severity, evidence, impact and
  recommended corrections. Distinguish optional suggestions from defects. Fix
  findings, repeat affected checks and review the updated diff. Track bugs in
  GitHub Issues and link them from the PR without duplicating reports in docs.
- Merge only when the latest revision has passed all required checks, all review
  findings and conversations are resolved, and there are no merge conflicts.
  Never bypass protections to finish a task. If any gate is blocked, explain it
  on the PR and keep the work open; lack of findings is not a defect-free guarantee.
- Link fixing PRs to their issues. Close issues only when resolved or with a
  justified closure reason. Verify the merge and post-merge CI, then delete only
  the completed task's remote and local branches and synchronize local `main`.
  Preserve branches and unrelated work if verification fails; track the failure
  in GitHub Issues and fix it on a new branch.
- Keep release versions manual and prepare them through a release pull request.
  Follow [the release guide](docs/releases.md); automation prepares drafts, while
  publication remains an explicit maintainer action.
- Continue within the requested scope without adding routine approval gates.
  Ask concise questions when an unresolved choice materially changes behavior.
- Keep documentation-only tasks to documentation. Do not scaffold an application
  or add dependencies just to make a documentation change look complete.
- Do not delegate to other agents unless the user explicitly requests it.

## Product behavior

- Aim for Avro-compatible phonetic behavior, using an independently implemented
  engine. Choose and document the compatibility reference before claiming parity.
- Keep the active word in preedit: text remains editable before it is committed
  to the application. Backspace removes a raw phonetic keystroke and recomputes it.
- Ctrl+Backspace clears the whole active raw buffer without committing; with no
  active buffer, let the application handle word deletion.
- Space and Enter commit active Bangla, then forward the same key to the application.
  Keep punctuation and phonetic escapes editable until an explicit boundary.
- For v1, show converted Bangla in editable preedit without a Bangla/Latin choice
  list or raw Latin selection. Revisit choices after the first release if needed.
- Convert digits to Bangla by default; digit keys enter text.
- Keep future autocorrection separate from deterministic transliteration. Do not
  silently change spelling, add dictionaries, or implement prediction for v1.
- Prioritize responsive typing and low resource use; verify performance claims.

## Architecture boundaries

- Keep transliteration independent of Fcitx5, display servers, desktop APIs, and UI.
- Keep composition state and edit/commit actions independent of platform adapters
  so Fcitx5, IBus, Windows TSF and macOS can share behavior.
- Keep framework-specific key events, preedit updates, and commits in the adapter.
  Reuse Fcitx5 UI facilities where suitable.
- Rust is the implementation language for engine and composition logic. The
  experimental Fcitx5 adapter uses a small C++ bridge and Rust C ABI. Other native
  bindings/glue are chosen during each platform's feasibility step; C++ is not a
  cross-platform requirement. Do not move transliteration rules into bridges.
- Add concrete extension points when needed. Implement IBus, TSF and macOS in
  their roadmap stages. Do not build a dynamic plugin system or generalize an
  adapter framework before concrete reuse exists.
- Keep unsafe code at a documented interoperability boundary when unavoidable.
  Specify ownership, lifetimes, encoding, error handling, and panic containment.

## Correctness and validation

- Store source and fixtures as UTF-8. Handle Rust strings at valid character
  boundaries; deleting a raw keystroke must not delete a byte from Bangla output.
- Add meaningful regression cases for phonetic rules and composition behavior:
  contextual vowels, conjuncts, case-sensitive sequences, punctuation/escape
  sequences, digits, Backspace, Ctrl+Backspace, boundary forwarding, commit,
  cancel, and reset.
- Track expected Unicode sequences and the source of compatibility fixtures.
  Visually similar output alone does not establish compatibility.
- Keep platform smoke tests separate from engine tests. Record actual distro,
  Plasma, Fcitx5, toolkit/application versions, and whether the app uses Wayland
  or XWayland. Do not describe an untested environment as supported.
- Once Rust code exists, use the repository's documented format, lint, and test
  commands. Until then, do not claim Cargo checks ran or invent setup commands.
- Run checks appropriate to the changed behavior and report checks that could
  not run. Documentation-only edits need link and consistency checks, not tests.
- Do not log or persist the user's typed text by default.

## Dependencies and documentation

- Prefer the latest stable development tools where practical. Verify current
  releases against official sources and record the versions actually used.
- Prefer small, justified dependencies. Keep per-keystroke processing local;
  typing must not depend on network access or a separate service.
- Write original project code under MIT. Check provenance and license obligations
  before introducing third-party source, rule tables, fixtures, or assets.
- Keep the README focused on the project introduction, status, quick start and
  links. Put detailed commands in the focused `docs/` guides; record notable
  user-facing changes under `Unreleased` in `CHANGELOG.md`.
- Record behavioral decisions in `docs/v1.md`; update usage/build instructions
  alongside code. Explain tradeoffs without creating unnecessary documents.
- Never overwrite unrelated work or change system input-method settings as a
  side effect of development. Document installation separately from source edits.
