# Development progress

This is the current handoff for developers and future coding sessions. Replace
these summaries after each completed step; aim for 50–100 lines before
[Completed steps](#completed-steps). That section preserves older history and
need not grow. Use Git for detailed changes, [v1.md](v1.md) for behavior and the
[roadmap](roadmap.md) for delivery gates. Bug reports and investigation belong in
[GitHub Issues](https://github.com/shaadahmmed/jong-bangla-keyboard/issues).
Dates use the project's Asia/Dhaka timezone.

## Current position

- **Implemented:** independent Rust transliteration/composition, shared private
  Rust C ABI, experimental C++ Fcitx5 addon and C11/GLib IBus service. The
  [IBus record](ibus.md) owns boundary decisions, commands and validation limits.
- **IBus evidence:** the production executable passes private D-Bus factory/key/
  lifecycle tests and staged source-install/removal checks. No IBus daemon or
  real GNOME/client route was tested; no beta/stable support is declared.
- **Shared boundary:** `adapters/ffi` now serves both native adapters. No
  transliteration/composition semantics or Rust dependencies changed. Native
  cursor units remain separate: Fcitx5 UTF-8 bytes, IBus Unicode characters.
- **Fcitx5 baseline:** the previously verified Release build of
  `72378338e59f399e05ef6a1f0ad688e106440735` matches the installed addon and
  registrations. This step did not replace it or recheck loaded-process identity.
  [Desktop evidence](fcitx5-validation.md#installed-route-basic-smoke-result)
  remains scoped user-reported KWrite/Firefox/Kate results on CachyOS/Plasma
  Wayland. Fcitx5 beta/stable acceptance remains outstanding.
- **Workflow handoff corrected:** [PR #18](https://github.com/shaadahmmed/jong-bangla-keyboard/pull/18)
  was merged as `2f444b0`; its review/merge is no longer the pending next step.
  Every new PR still needs a separate reviewer chat for its latest revision;
  implementation self-review and CI cannot authorize merge.
- **Environment:** CachyOS x86_64, GCC 16.2.1, Rust/Cargo 1.99.1, GLib 2.90.1,
  CMake 4.4.5; temporary extracted Arch `libibus` 1.5.34-2 development files
  report pkg-config version 1.5.34-rc2. No system package, input-method setting,
  installed addon or desktop daemon was changed.
- **Other delivery:** Linux packages/AUR, Windows TSF and macOS remain planned
  in the [roadmap](roadmap.md). Publication stays manual. No new performance or
  full-reference-parity claim is made; earlier 522,933 parity and 60 Unicode
  policy rows remain prior evidence, not checks rerun in this step.

## Latest completed step

- **2026-11-06 — Implement the experimental IBus service and repair the handoff.**
  Added the native engine/factory, executable and generated registration, using
  the existing Rust controller through a shared, renamed private C-ABI crate.
  IBus/frontend owns focus/switch preedit commits; engine callbacks discard raw
  state without committing twice. Focus IDs, reset/destruction, restrictions,
  original-key forwarding and character cursor offsets have synthetic coverage.
- **Tests and delivery tooling:** production-executable protocol tests use a
  private D-Bus bus with temporary XDG directories and no display. The staged
  checker validates exactly two files and IBus XML parsing, runs the staged
  executable, rejects a missing executable and preserves unrelated files.
  CI now checks both adapters in checkout and exported-source builds; the
  existing required job name `Rust and Fcitx5` stays unchanged.
- **Actual checks:** `bash tools/check-build.sh` passed Rust format, Clippy,
  workspace tests, Release build, API docs and conversion smoke; Fcitx5 CTest
  (two tests, ten dispatcher suites) and staged installation; IBus CTest and
  staged installation. Final native edits received affected IBus checks again.
  A clean `git archive --format=tar HEAD` export outside the checkout passed
  the same `bash tools/check-build.sh` block without Git metadata.
  Temporary dependency paths were supplied through `PKG_CONFIG_PATH` and
  `LD_LIBRARY_PATH`; the [IBus guide](ibus.md#build-and-synthetic-checks) explains
  custom-prefix validation.
- **Native memory checks:** configured/built the documented sanitizer builds;
  `python3 tools/check-memory.py target/fcitx5-sanitized target/ibus-sanitized`
  passed: intentional Rust leak detected, 20,000 normal C-ABI lifecycle cycles,
  ten Fcitx5 suites and the production IBus suite with ASan/UBSan/LSan enabled,
  without normal-workload reports. System libraries/Rust accesses are not fully
  instrumented; exceptional panic-payload retention remains documented.
- **Documentation/tooling checks:** `python3 tools/check-docs.py`,
  `python3 -m unittest discover -s tools/tests -v` (16 tests),
  `python3 tools/check-release.py --base origin/main`, `actionlint`,
  `shellcheck tools/check-build.sh`, native `clang-format --dry-run --Werror`
  and `git diff --check` passed. No release version was changed.
- **Tracker/delivery:** no open Issues or PRs at task start. Work uses fresh
  `feat/ibus-adapter` from synchronized main. Separate-session review and merge
  of this implementation remain pending; do not treat self-review as that gate.
- **Limits:** no GNOME/IBus installed acceptance, completed Compose-table support,
  verified AltGr/frontend routing, generic mouse-relocation notification or
  desktop latency result. These limits are detailed in the IBus record rather
  than implied support claims. Historical progress entries are unchanged.

## Next small implementation step

1. Review the IBus implementation PR in a separate chat using the
   [review protocol](../CONTRIBUTING.md#separate-session-review). Cover the full
   shared-boundary move, native memory/lifecycle behavior, protocol tests,
   registration, source export and CI changes. Post the exact reviewed head,
   findings, limits and explicit merge recommendation on the PR.
2. Fix findings and renew review/checks after a push. Merge only when the latest
   revision has the separate recommendation and all gates pass; verify post-merge
   CI before task-branch cleanup and synchronization.
3. Validate installed IBus in a named GNOME/IBus Wayland environment using the
   [desktop acceptance checklist](ibus.md#next-desktop-acceptance), preserving the
   current Fcitx5 session. Investigate real focus/switch ownership, GTK/Qt/browser
   routes, restrictions, AltGr/Compose and mouse/selection behavior. Track any
   reproduced bugs and release decisions in GitHub Issues.

**Done when:** this implementation has separate-session review and verified
PR delivery. IBus desktop acceptance and Fcitx5 beta/stable acceptance remain
separate, outstanding gates; binary packaging follows the roadmap.

## Completed steps

### 2026-10-29 — Related ShN and Shm conjunct batch

**Result:** exact `ShN` → ষ্ণ (U+09B7 U+09CD U+09A3) and `Shm` → ষ্ম
(U+09B7 U+09CD U+09AE) now match before basic `Sh`. Independent checks
confirmed their vowel context and following-`r` behavior; two small branches
reuse the existing helper with final raw `N` and `m`. Single `r` attaches
without U+200D (`ShNry` → `ষ্ণ্র্য`); `rri`/`rry`/`rrZ` retain priority.

The batch resolves `kkShN` → `ক্কষ্ণ` and `kkShm` → `ক্কষ্ম`. Consuming
`N` before the following `g` also resolves the selected `ShNg…` gaps:
`ShNgx` → `ষ্ণগক্স`, `ShNgk` → `ষ্ণগক`, `ShNgkh` → `ষ্ণগখ`, and
`ShNgkx`/`ShNgkkh`/`ShNgkSh` → `ষ্ণগক্ষ`. Earlier `kShN`/`kShm` and
`NgkSh` retain priority. Consuming `m` keeps a following nasal separate
(`Shmng` → `ষ্মং`, `Shmn` → `ষ্মন`). Resolved partial-output assertions were
replaced by reference fixtures; remaining gaps retain explicit assertions.
No third-party source, tables, fixtures, or dependencies were imported; the
existing external parser and license in `/tmp` were reused.

**Checks and outcomes:**

- Independently authored and reference-checked **465 `ShN`** and **468 `Shm`**
  cases before changing Rust: Unicode, vowels/aliases and transitions,
  preceding contexts, one through eight following `r` keys, nasal overlaps,
  earlier/adjacent matches, repetition, all digits, boundaries, copied Unicode,
  raw spelling, and words (`biShNu` → `বিষ্ণু`, `uShma` → `উষ্মা`).
- `node tools/check-reference.mjs /tmp/jong-avro-v1.1.4-rsz8kb89/avro-lib.js`
  — all **12,933** authored cases matched the SHA-256-checked pinned parser;
  nine remaining-gap probes printed exact reference output. Node **v24.21.0**.
- `cargo fmt --all -- --check` — passed.
- `cargo clippy --offline --all-targets -- -D warnings` — passed.
- `cargo test --offline` — passed: **55 integration tests** and **1 doctest**,
  including fixtures, control boundaries, separate calls, long mixed input,
  unchanged supported forms, and explicit remaining-gap assertions.
- `cargo build --offline --release` — passed.
- `cargo run --offline --example convert -- 'biShNu uShNo uShma ShNr Shmrri kkShN kkShm ShNgx'`
  — printed `বিষ্ণু উষ্ণ উষ্মা ষ্ণ্র ষ্মৃ ক্কষ্ণ ক্কষ্ম ষ্ণগক্স`.
- Documentation links/anchors, fixture registration/totals and exact code points,
  55 new documented examples/gaps against Rust and the reference, and
  `git diff --check` — passed.
- Toolchain: Rust/Cargo **1.99.1**. No performance or platform test was run.

**Limitations:** basic consonant-plus-`r` forms (`kr`/`khr`/`Shr`/`gr`/`mr`),
`mm`/`mn`, earlier `nk`/`lk`/`sk`/`Shk`, lowercase `shn`/`shm` and `Sm`,
uppercase aliases (including `ShNG`), reph, and punctuation/escapes remain
incomplete. Current probes cover `ShNG`, `ShNgr`, `Shmgr`, `Shmmm`, `ShNmng`,
`NgkShmr`, `ShM`, `rrShN`, and `` Shm`a ``. Composition and Fcitx5 remain
later work; full Avro compatibility is not established.

**Next action:** independently check the following-`r` batch after basic
`k`/`kh`/`Sh`, including longer `r` runs, vowel/ya context, and priority against
existing conjuncts. Investigate `kkkhr`, `kkShr`, and `Ngkkr` without adding
other consonants or platform work.

### 2026-10-29 — Exact kk conjunct and k-conjunct priority

**Result:** exact `kk` now produces ক্ক (U+0995 U+09CD U+0995), with supported
vowel context and the existing following-`r` helper using final raw `k`.
Single `r` attaches without U+200D (`kkr` → `ক্ক্র`, `kkry` → `ক্ক্র্য`);
`rri`/`rry`/`rrZ` keep priority. Longer `kkh`/`kkhN`/`kkhm` and earlier
`Ng` forms still win (`Ngkk` → `ঙ্কক`, `Ngkkh` → `ঙ্ক্ষ`).

Consuming both keys fixes earlier partial outputs for `kkkh` → `ক্কখ`,
`kkSh` → `ক্কষ`, `kkx` → `ক্কক্স`, and selected longer `N`/`m` forms.
Repeated and adjacent forms now match (`kkkk` → `ক্কক্ক`, `kkhkk` → `ক্ষক্ক`).
`kkShN`/`kkShm` instead expose separate `ShN`/`Shm` gaps, giving current
`ক্কষণ`/`ক্কষম` versus reference `ক্কষ্ণ`/`ক্কষ্ম`. The old partial-output
assertions were replaced by supported fixtures or updated explicit gap assertions.
Initial test runs exposed obsolete assertions; the final full suite passes.
Uppercase controls that the reference normalizes remain gap assertions rather
than supported fixtures. No third-party source, tables, fixtures, or dependencies
were imported; the existing external parser and license were reused in `/tmp`.

**Checks and outcomes:**

- Authored 501 `kk` fixtures and verified them against the SHA-256-checked
  pinned parser before changing Rust. They cover exact Unicode, vowels/aliases
  and transitions, preceding contexts, one through eight following `r` keys,
  overlaps with existing forms, one through twelve `k` keys, repetition,
  digits, boundaries, copied Unicode, raw spelling, and words such as
  `Dhakka` → `ঢাক্কা` and `dhakka` → `ধাক্কা`.
- `node tools/check-reference.mjs /tmp/jong-avro-v1.1.4-rsz8kb89/avro-lib.js`
  — all **12,000** authored cases matched; nine remaining-gap probes printed
  exact reference output. Runtime: Node **v24.21.0**.
- `cargo fmt --all -- --check` — passed.
- `cargo clippy --offline --all-targets -- -D warnings` — passed.
- `cargo test --offline` — passed: **52 integration tests** and **1 doctest**,
  including all fixtures, control boundaries, separate calls, long mixed input,
  unchanged supported forms, and explicit remaining-gap assertions.
- `cargo build --offline --release` — passed.
- `cargo run --offline --example convert -- 'kk kka kkr kkrri kkkh kkSh kkx Dhakka'`
  — printed `ক্ক ক্কা ক্ক্র ক্কৃ ক্কখ ক্কষ ক্কক্স ঢাক্কা`.
- Documentation links/anchors, fixture registration and totals, exact Unicode,
  new documented examples/gaps, and `git diff --check` — passed.
- Toolchain: Rust/Cargo **1.99.1**. No performance or platform test was run.

**Limitations:** basic `k`/`kh`/`Sh` following-`r` forms, earlier
`nk`/`lk`/`sk`/`Shk`, `ShN`/`Shm`, basic `mr`/`mm`/`mn`, uppercase aliases,
reph, and punctuation/escapes remain incomplete. The new probes record
`kkShN`, `kkShm`, `kkkhr`, `kkShr`, `Ngkkr`, `nkk`, `kkH`, `rrkk`, and
`` kk`a ``. Composition and Fcitx5 remain later work; full compatibility is
not established.

**Next action:** independently check the related `ShN`/`Shm` batch, its
vowels/following-`r` context, and priority over the exposed `kkShN`/`kkShm`
gaps while preserving existing exact `kShN`/`kShm` behavior.

### 2026-10-29 — Related kkhm, kShm and kxm conjunct batch

**Result:** exact `kkhm`/`kShm`/`kxm` now produce ক্ষ্ম
(U+0995 U+09CD U+09B7 U+09CD U+09AE) before shorter `kkh`/`kSh`/`kx`.
Independent checks confirmed shared vowel context and following-`r` behavior,
so the three forms share one branch and the existing helper with final raw `m`.
Single `r` attaches without U+200D (`kxmry` → `ক্ষ্ম্র্য`); two `r` keys and
`rri`/`rry`/`rrZ` retain their checked priority. Earlier
`Ngkkh`/`NgkSh`/`Ngkx` still win (`NgkShm` → `ঙ্ক্ষম`). Consuming `m`
prevents it joining a following nasal (`kShmn` → `ক্ষ্মন`, `kShmng` → `ক্ষ্মং`).
Basic `mr`/`mm`/`mn` behavior stays outside this step.

Added 1,196 independently authored fixtures: 399 `kkhm`, 399 `kShm`, and
398 `kxm`, each with expected UTF-8 and exact code points. They cover supported
vowels/aliases and transitions, preceding contexts, earlier/adjacent matches,
nasal overlaps, one through eight following `r` keys, repetition, raw spelling,
all digits, boundaries, copied Unicode, and words such as `lokkhmI` → `লক্ষ্মী`
and `sUkShmo` → `সূক্ষ্ম`. Rust regressions cover control characters,
separate calls, long mixed input, and remaining partial outputs. README and
behavior notes describe the new slice and its limits. No upstream source,
rule tables, fixtures, dependencies, normalization, persistent state,
performance measurements, or platform code added.

**Checks:**

- All 1,196 final expectations matched the external pinned parser after SHA-256
  verification before implementation. Draft reference checks corrected basic
  `mN`/`mNg`/`mNG` assumptions and identified uppercase aliases and other
  unsupported behavior, kept separate from supported fixtures.
- The new Rust fixture test failed on `kkhm` before implementation, confirming
  the missing virama (joining character) before ম. A subsequent full run caught
  an out-of-scope basic `mn` fixture and an obsolete `kkhm` gap assertion;
  the `mn` fixture was removed with partial-output coverage retained, and the
  obsolete assertion was replaced by the new reference fixtures.
- `node tools/check-reference.mjs` passed all **11,499** cases with Node
  v24.21.0 and printed nine remaining-gap probes.
- `cargo fmt --all -- --check`, `cargo clippy --offline --all-targets -- -D warnings`,
  `cargo test --offline` (**50 integration tests and 1 doc test**), and
  `cargo build --offline --release` passed with Rust/Cargo 1.99.1.
- Terminal examples passed: `kh12T` → `খ১২ট`;
  `kkhm kShma kxmr kxmrri kShmng NgkShm kShM` →
  `ক্ষ্ম ক্ষ্মা ক্ষ্ম্র ক্ষ্মৃ ক্ষ্মং ঙ্ক্ষম ক্ষM`; and
  `lokkhmI lokShmI lokxmI sUkShmo` → `লক্ষ্মী লক্ষ্মী লক্ষ্মী সূক্ষ্ম`.
- `git diff --check` and all **345** local documentation links/anchors passed.
  All 44 fixture files agree between Rust, the reference checker, and disk,
  with unique inputs per file, matching exact code points, and matching totals.

**Limitations:** earlier `kk`/`nk`/`lk`/`sk`/`Shk` matches consume the initial
`k` before the selected form in the reference. All five prefixes were checked
for each spelling; the engine still produces partial outputs. Basic `mr`/`mm`/`mn`
and adjacent unimplemented conjuncts remain gaps (`NgkShmr` produces `ঙ্ক্ষমর`
versus reference `ঙ্ক্ষম্র`). Uppercase aliases, reph, punctuation/escapes,
composition, and Fcitx5 remain incomplete. Full Avro compatibility and desktop
support are not established.

**Next:** independently check exact `kk` → ক্ক, its vowel/following-`r`
context, and priority over existing k-conjuncts. This follows the earlier-prefix
conflicts exposed by the completed batches; it remains planned work.

### 2026-10-29 — Related kkhN, kShN and kxN conjunct batch

**Result:** exact `kkhN`/`kShN`/`kxN` now produce ক্ষ্ণ
(U+0995 U+09CD U+09B7 U+09CD U+09A3) before shorter `kkh`/`kSh`/`kx`.
Each spelling was checked independently before sharing one branch and the
existing following-`r` helper with final raw `N`. Single `r` attaches without
U+200D (`kxNry` → `ক্ষ্ণ্র্য`); two `r` keys and `rri`/`rry`/`rrZ` keep
their checked priority. Basic `Nr` behavior is unchanged. Earlier
`Ngkkh`/`NgkSh`/`Ngkx` still win (`NgkShN` → `ঙ্ক্ষণ`). Consuming `N`
resolves `kkhNgkkh`/`kShNgkSh` → `ক্ষ্ণগক্ষ` and six former `kxNg…` gaps.

Added 1,231 independently authored fixtures: 410 `kkhN`, 411 `kShN`, and
410 `kxN`, each with expected UTF-8 and exact code points. They cover supported
vowels/aliases and transitions, preceding contexts, earlier/neighboring match
priority, following `g` and nasal overlaps, one through eight following `r`
keys, repetition, digits, boundaries, copied Unicode, raw spelling, and words.
Rust regressions also cover control characters, separate calls, long mixed
input, and remaining partial outputs. Updated README examples and behavior
notes. No upstream source/rules/fixtures, dependencies, normalization,
persistent state, performance measurements, or platform code added.

**Checks:**

- Before implementation, the original 1,222 expectations matched the external pinned
  parser after SHA-256 verification. A new Rust fixture test then failed on
  `kkhN` as expected, confirming the missing virama before ণ.
- Nine additional `g`-overlap cases were authored and reference-checked afterward.
- After implementation, `node tools/check-reference.mjs` passed all **10,303**
  cases with Node v24.21.0 and printed seven remaining-gap probes.
- `cargo fmt --all -- --check`, `cargo clippy --offline --all-targets -- -D warnings`,
  `cargo test --offline` (**46 integration tests and 1 doc test**), and
  `cargo build --offline --release` passed with Rust/Cargo 1.99.1.
- Terminal examples passed: `kh12T` → `খ১২ট`, and
  `kkhN kShNa kxNr kxNrri kShNgkSh NgkShN kShNG` →
  `ক্ষ্ণ ক্ষ্ণা ক্ষ্ণ্র ক্ষ্ণৃ ক্ষ্ণগক্ষ ঙ্ক্ষণ ক্ষ্ণG`.
- `git diff --check` passed. All 334 local documentation links/anchors passed;
  the 41 fixture files agree between Rust and the reference checker, with
  unique inputs per file and matching exact code points/counts.

**Limitations:** `kkhNG`/`kShNG`/`kxNG` produce partial `ক্ষ্ণG` versus
reference `ক্ষ্ণগ`; standalone uppercase `G` remains outside this batch, as
specified by its scope. Earlier `kk`/`nk`/`lk`/`sk`/`Shk` conflicts, adjacent
unimplemented conjuncts, `kkhm`/`kShm`/`kxm`, reph, uppercase aliases,
punctuation/escapes, composition, and Fcitx5 remain incomplete. Full Avro
compatibility and desktop support are not established.

**Next:** independently check exact `kkhm`/`kShm`/`kxm` → ক্ষ্ম and their
vowels, following-`r` behavior, and overlaps as one related batch.

### 2026-10-29 — Use related conjunct batches for rule coverage

- The user chose small batches of related conjuncts instead of a separate
  increment for every spelling. Updated `AGENTS.md`, `README.md`, and
  `docs/v1.md` to make this the default workflow, with scope defined before
  editing and checks, documentation, and a commit for each completed batch.
- Each spelling still needs independent reference checks for exact Unicode,
  vowel/context behavior, following-`r` behavior, and match priority. Shared
  output alone does not justify shared implementation. Split batches when
  behavioral differences make review difficult; no fixed batch size is required.
- Replaced the single-`kkhN` handoff with the planned
  `kkhN`/`kShN`/`kxN` → ক্ষ্ণ batch, including shorter matches and conflicts
  caused by consuming `N` before a following nasal sequence. Historical
  implementation entries retain the plans recorded at their dates.
- Checks: UTF-8, local Markdown links/anchors across all four edited documents,
  final newlines, trailing whitespace, manual consistency review, and
  `git diff --check` passed. No engine, fixture, dependency, or platform changes;
  Cargo and reference comparisons were not rerun for this documentation step.
  The pre-existing untracked `.vscode/` is untouched.
- Limitations: the planned batch remains unimplemented; the documented 9,072
  reference-checked cases and compatibility limitations are unchanged.
- Next: independently author and reference-check cases for each of
  `kkhN`/`kShN`/`kxN`, then implement and validate that batch.

### 2026-10-29 — Exact standalone kSh conjunct

- Added exact `kSh` → ক্ষ (U+0995 U+09CD U+09B7) before basic `k`,
  sharing `kkh`'s branch after independently checking its behavior. Earlier
  exact `NgkSh` and all existing conjuncts retain priority. The 40 basic
  consonant sequences producing 35 letters remain unchanged.
- Reused vowel context and the existing following-`r` helper with final raw `h`:
  single `r` attaches without U+200D (`kShr` → ক্ষ্র, `kShry` → ক্ষ্র্য),
  preserving two-`r` consumption and `rri`/`rry`/`rrZ` exceptions.
  `NGkSh` → ঞক্ষ and `ngkSh` → ংক্ষ now match; `ksh` → কশ stays distinct.
- Authored 332 [fixtures](../tests/fixtures/conjunct-ksh.tsv), checked
  against the SHA-256-verified pinned parser before implementation. These
  independently authored cases extend our MIT fixture patterns without importing
  upstream code, rules, or fixtures. They cover vowels/aliases and transitions,
  preceding contexts including `NG`/`ng`, one through eight following `r` keys,
  attachment/joiner exceptions, repetition, raw-spelling/case controls,
  all digits, boundaries, copied Unicode, and words. All 9,072 reference cases
  pass under Node.js v24.21.0.
- The focused Rust test failed on `kSh` before implementation and passed
  afterward. Extended control-character, separate-call, and long-buffer checks;
  removed the three resolved gap expectations. Recorded partial outputs for
  earlier `kk`/`nk`/`lk`/`sk`/`Shk`, longer `kShN`/`kShm`, aliases, reph,
  and escapes; refreshed seven reference gap probes.
- Updated [README.md](../README.md) and [v1.md](compatibility/exact-conjuncts.md#exact-ksh-conjunct)
  with Unicode sequences, priority, examples, counts, limitations, and next work.
  Marked earlier gap descriptions as historical. No dependencies, normalization,
  persistent state, performance measurement, or platform code added.
- Checks: `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, `cargo test --offline`
  (42 regression tests and one documentation example), and
  `cargo build --offline --release` passed. `node --check` and all 9,072
  pinned-reference comparisons passed. Reused Rust/Cargo 1.99.1 and Node.js
  v24.21.0; no tools installed or upgraded. The cached reference parser and
  license remain outside the repository.
- Example: `cargo run --offline --example convert -- 'kSh kSha kShr kShrri'`
  printed `ক্ষ ক্ষা ক্ষ্র ক্ষৃ`; the README's `kh12T` example still printed
  `খ১২ট`. All 46 documented conversions and gap examples in the new v1 section
  passed direct CLI and pinned-reference checks.
- Documentation/fixture checks: UTF-8, local Markdown links/anchors, final
  newlines, trailing whitespace, all fixture code points, 332 distinct new
  inputs, both runner registrations, and `git diff --check` passed.
  The pre-existing untracked `.vscode/` is untouched.
- Limitations: longer `kkhN`/`kShN`/`kkhm`/`kShm`, earlier-prefix conflicts,
  other conjuncts, reph, uppercase aliases, punctuation/escapes, composition,
  and Fcitx5 integration remain incomplete. No broader compatibility,
  performance, or platform validation claimed.
- Next planned increment: check exact `kkhN` → ক্ষ্ণ and its supported
  vowel/context interactions independently against the pinned reference.

### 2026-10-29 — Exact standalone kkh conjunct

- Added exact `kkh` → ক্ষ (U+0995 U+09CD U+09B7) before basic `k`/`kh`,
  preserving earlier exact `Ngkkh` and all existing conjuncts. The 40 basic
  consonant sequences producing 35 letters remain unchanged.
- Reused the existing following-`r` helper with final raw `h`: single `r`
  attaches without U+200D (`kkhr` → ক্ষ্র, `kkhry` → ক্ষ্র্য), with the same
  two-`r` behavior and `rri`/`rry`/`rrZ` exceptions as `Ngkh`.
  Case-distinct `NGkkh` → ঞক্ষ and `ngkkh` → ংক্ষ now also match.
- Independently authored 330 [fixtures](../tests/fixtures/conjunct-kkh.tsv)
  and checked them against the SHA-256-verified pinned parser before implementation.
  They cover vowels/aliases and transitions, selected preceding contexts,
  one through eight following `r` keys, attachment/joiner exceptions,
  repetition, raw-spelling controls, digits, boundaries, copied Unicode, and
  words. All 8,740 reference cases pass under Node.js v24.21.0.
- The focused Rust regression failed on `kkh` before implementation and passed
  afterward. Extended control-character, separate-call, and long-buffer checks;
  replaced resolved gap regressions with supported fixtures. Recorded explicit
  partial outputs for earlier `kk`/`nk`/`lk`/`sk`/`Shk` matches, longer
  `kkhN`/`kkhm`, aliases, reph, and escapes; refreshed seven reference gap probes.
- Updated [README.md](../README.md) and [v1.md](compatibility/exact-conjuncts.md#exact-kkh-conjunct)
  with Unicode sequences, priority, examples, counts, limitations, and next work.
  Earlier gap descriptions are historical. No upstream source, rule tables,
  fixtures, dependencies, normalization, persistent state, or platform code added.
- Checks: `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, `cargo test --offline`
  (41 regression tests and one documentation example), and
  `cargo build --offline --release` passed. `node --check` and all 8,740
  pinned-reference comparisons passed. Reused Rust/Cargo 1.99.1 and Node.js
  v24.21.0; no tools installed or upgraded. The cached reference parser and
  license remain outside the repository.
- Example: `cargo run --offline --example convert -- 'kkh kkha kkhr kkhrri'`
  printed `ক্ষ ক্ষা ক্ষ্র ক্ষৃ`. All 46 documented conversions and gap examples
  in the new v1 section passed direct CLI and pinned-reference checks.
- Documentation/fixture checks: UTF-8, local Markdown links/anchors,
  final newlines, trailing whitespace, all fixture code points, 330 distinct
  new inputs, both runner registrations, and `git diff --check` passed.
  The pre-existing untracked `.vscode/` is untouched.
- Limitations: standalone `kSh`, earlier-prefix conflicts, longer `kkhN`/`kkhm`,
  other conjuncts, reph, uppercase aliases, punctuation/escapes, composition,
  and Fcitx5 integration remain incomplete. No broader compatibility,
  performance, or platform validation claimed.
- Next: check exact standalone `kSh` → ক্ষ and its supported vowel/context
  interactions as a separate reference-checked increment.

### 2026-10-29 — Focused project reading instructions

- Replaced the blanket read-all-documents rule in [AGENTS.md](../AGENTS.md)
  with focused reading: current handoff first, relevant README/requirements
  sections and affected code/tests as needed, history for investigations only.
- Required reuse of unchanged context, targeted recovery after compaction, and
  concise successful check output. Existing validation requirements still apply.
- Checks: UTF-8, final newlines, trailing whitespace, and 120 local links/anchors
  passed across both changed documents; `git diff --check` passed. Reviewed
  consistency with existing requirements and validation rules. No engine or
  reference comparison checks apply to this documentation-only change.
- Limitations: missing context and changed files may still require rereading.
  This step changes instructions only; the reference checker's output is unchanged.
- Next: check standalone `kkh` against the pinned reference as described above.

### 2026-10-28 — Exact NgkSh conjunct

- Added exact `NgkSh` → ঙ্ক্ষ (U+0999 U+09CD U+0995 U+09CD U+09B7),
  matching before shorter `Ngk`, basic `Ng`, and single `N`. The 40 basic
  consonant sequences producing 35 letters remain unchanged.
- Shared `Ngkkh`'s conversion branch after reference checks confirmed the
  same vowel context and following-`r` behavior. Single `r` attaches without
  U+200D (`NgkShr` → `ঙ্ক্ষ্র`, `NgkShry` → `ঙ্ক্ষ্র্য`). Two-`r`
  consumption and `rri`/`rry`/`rrZ` exceptions remain in priority
  (`NgkShrri` → `ঙ্ক্ষৃ`, `NgkShrry` → `ঙ্ক্ষরর‍্য`). No new helper
  rule added. Case-distinct `Ngksh` → `ঙ্কশ` is reference-checked.
- Authored 468 [fixtures](../tests/fixtures/conjunct-ngksh.tsv), checked
  against the SHA-256-verified pinned parser before implementation. They
  cover supported vowels/aliases and transitions, selected preceding contexts,
  adjacency, one through eight following `r` keys, priority/joiner exceptions,
  contrasts with `Ngkkh`/`Ngkx`, repetition, case/raw-spelling controls,
  all digits, boundaries, copied Unicode, and words. All 8,410 reference
  cases match under Node.js v24.21.0.
- The focused Rust regression failed on `NgkSh` before implementation and
  passed afterward. Extended control-character, separate-call, and long-buffer
  regressions; removed the resolved `NgkSh` gap expectation. Added explicit
  partial outputs for earlier-prefix conflicts, aliases, reph, escapes,
  standalone `kSh`, and `NGkSh`/`ngkSh` (which still need `kSh` conversion).
  Refreshed seven reference gap probes.
- Updated [README.md](../README.md) and
  [v1.md](compatibility/exact-conjuncts.md#exact-ngksh-conjunct) with exact Unicode, matching priority,
  examples, counts, limitations, and next work. Marked earlier `NgkSh` gaps
  as historical. No upstream source, rules, fixtures, dependencies,
  normalization, persistent state, or platform code added.
- Checks: after applying rustfmt, `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, `cargo test --offline`
  (40 regression tests and one documentation example), and
  `cargo build --offline --release` passed. `node --check` passed, and the
  reference comparison passed all 8,410 cases.
- Example: `cargo run --offline --example convert -- 'NgkSh NgkSha NgkShr NgkShrri'`
  printed `ঙ্ক্ষ ঙ্ক্ষা ঙ্ক্ষ্র ঙ্ক্ষৃ`. All 46 conversions and gap examples
  in the new v1 section passed direct CLI and pinned-reference checks.
  Rechecked and reused Rust/Cargo 1.99.1 and Node.js v24.21.0; no tools
  installed or upgraded. The cached reference parser and license remain
  outside the repository.
- Documentation/fixture checks: UTF-8, 295 local Markdown links/anchors,
  final newlines, trailing whitespace, all fixture code points, gap-table
  reference code points, 468 distinct new inputs, both runner registrations,
  and `git diff --check` passed. The pre-existing untracked `.vscode/` is untouched.
- Limitations: standalone `kkh`/`kSh`, earlier-prefix conflicts, other
  conjuncts, reph, uppercase aliases, punctuation/escapes, composition, and
  platform integration remain incomplete. No broader compatibility,
  performance, or platform validation claimed.
- Next: check exact standalone `kkh` → ক্ষ and its supported vowel/context
  interactions as a separate reference-checked increment.

### 2026-10-28 — Exact Ngkkh conjunct

- Added exact `Ngkkh` → ঙ্ক্ষ (U+0999 U+09CD U+0995 U+09CD U+09B7),
  matching before shorter `Ngk`, basic `Ng`, and single `N`. The 40 basic
  consonant sequences producing 35 letters remain unchanged.
- Reused `Ngkh`'s following-`r` behavior through the existing helper:
  single `r` attaches without U+200D (`Ngkkhr` → `ঙ্ক্ষ্র`,
  `Ngkkhry` → `ঙ্ক্ষ্র্য`), unlike `Ngkx`'s separate single `r`.
  Two-`r` consumption and `rri`/`rry`/`rrZ` exceptions remain in priority
  (`Ngkkhrri` → `ঙ্ক্ষৃ`, `Ngkkhrry` → `ঙ্ক্ষরর‍্য`). No new helper
  rule added; standalone `kkh` and basic `kh` behavior are unchanged.
- Authored 458 [fixtures](../tests/fixtures/conjunct-ngkkh.tsv), checked
  against the SHA-256-verified pinned parser before implementation. They
  cover supported vowels/aliases and transitions, selected preceding contexts,
  adjacency, one through eight following `r` keys, priority/joiner exceptions,
  explicit contrasts with `Ngkx`, repetition, raw-spelling controls, all digits,
  boundaries, copied Unicode, and words. All 7,942 reference cases match
  under Node.js v24.21.0.
- The focused Rust regression failed on `Ngkkh` before implementation and
  passed afterward. Extended control-character, separate-call, and long-buffer
  regressions; removed the resolved `Ngkkh` gap expectation. Added explicit
  partial outputs for earlier-prefix conflicts, aliases, reph, escapes, and
  `NGkkh`/`ngkkh` (which still need standalone `kkh` conversion).
  Refreshed seven reference gap probes.
- Updated [README.md](../README.md) and
  [v1.md](compatibility/exact-conjuncts.md#exact-ngkkh-conjunct) with exact Unicode, matching priority,
  examples, counts, limitations, and next work. Marked earlier `Ngkkh` gaps
  as historical. No upstream source, rules, fixtures, dependencies,
  normalization, persistent state, or platform code added.
- Checks: after applying rustfmt, `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, `cargo test --offline`
  (39 regression tests and one documentation example), and
  `cargo build --offline --release` passed. `node --check` passed, and the
  reference comparison passed all 7,942 cases.
- Example: `cargo run --offline --example convert -- 'Ngkkh Ngkkha Ngkkhr Ngkkhrri'`
  printed `ঙ্ক্ষ ঙ্ক্ষা ঙ্ক্ষ্র ঙ্ক্ষৃ`. All 45 conversions and gap examples
  in the new v1 section passed direct CLI and pinned-reference checks.
  Rechecked and reused Rust/Cargo 1.99.1 and Node.js v24.21.0; no tools
  installed or upgraded. The cached reference parser and license remain
  outside the repository.
- Documentation/fixture checks: UTF-8, 287 local Markdown links/anchors,
  final newlines, trailing whitespace, all fixture code points, gap-table
  reference code points, 458 distinct new inputs, both runner registrations,
  and `git diff --check` passed. The pre-existing untracked `.vscode/` is untouched.
- Limitations: `NgkSh`, earlier-prefix conflicts, standalone `kkh`, other
  conjuncts, reph, uppercase aliases, punctuation/escapes, composition, and
  platform integration remain incomplete. No broader compatibility,
  performance, or platform validation claimed.
- Next: check exact `NgkSh` → ঙ্ক্ষ and its supported vowel/context
  interactions as a separate reference-checked increment.

### 2026-10-28 — Exact Ngkx conjunct

- Added exact `Ngkx` → ঙ্ক্ষ (U+0999 U+09CD U+0995 U+09CD U+09B7),
  matching before shorter `Ngk`, basic `Ng`, and single `N`. The 40 basic
  consonant sequences producing 35 letters remain unchanged.
- Reused `Ngx`/`kx` following-`r` behavior through the existing helper:
  two `r` keys attach before matching resumes (`Ngkxrr` → `ঙ্ক্ষ্রর`),
  preserving `rri`/`rry`/`rrZ` priority (`Ngkxrri` → `ঙ্ক্ষৃ`,
  `Ngkxrry` → `ঙ্ক্ষরর‍্য`). A single `r` stays separate and retains
  U+200D before `y`/`Z` (`Ngkxry` → `ঙ্ক্ষর‍্য`), differing from
  `Ngk`/`Ngkh` single-`r` attachment. No new helper rule added.
- Authored 432 [fixtures](../tests/fixtures/conjunct-ngkx.tsv), checked
  against the SHA-256-verified pinned parser before implementation. They
  cover supported vowels/aliases and transitions, selected preceding contexts,
  adjacency, one through eight following `r` keys, priority/joiner exceptions,
  repetition, raw-spelling controls, all digits, boundaries, copied Unicode,
  and words. All 7,484 reference cases match under Node.js v24.21.0.
- The focused Rust regression failed on `Ngkx` before implementation and
  passed afterward. Extended control-character, separate-call, and long-buffer
  regressions; removed the resolved `Ngkx` gap expectation. Added explicit
  partial outputs for earlier-prefix conflicts, aliases, reph, and escapes,
  and refreshed seven reference gap probes.
- Updated [README.md](../README.md) and
  [v1.md](compatibility/exact-conjuncts.md#exact-ngkx-conjunct) with exact Unicode, matching priority,
  examples, counts, limitations, and next work. Marked the earlier `Ngkx`
  gap as historical. Probes confirmed related `Ngkkh`/`NgkSh` spellings
  remain separate: their single following `r` attaches, unlike `Ngkx`.
  No upstream source, rules, fixtures, dependencies, normalization, persistent
  state, or platform code added.
- Checks: after applying rustfmt, `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, `cargo test --offline`
  (38 regression tests and one documentation example), and
  `cargo build --offline --release` passed. `node --check` passed, and the
  reference comparison passed all 7,484 cases.
- Example: `cargo run --offline --example convert -- 'Ngkx Ngkxa Ngkxrri Ngkxrr'`
  printed `ঙ্ক্ষ ঙ্ক্ষা ঙ্ক্ষৃ ঙ্ক্ষ্রর`. All 44 conversions and gap examples
  in the new v1 section passed direct CLI and pinned-reference checks.
  Rechecked and reused Rust/Cargo 1.99.1 and Node.js v24.21.0; no tools
  installed or upgraded. The cached reference parser and license remain
  outside the repository.
- Documentation/fixture checks: UTF-8, 279 local Markdown links/anchors,
  final newlines, trailing whitespace, all fixture code points, 432 distinct
  new inputs, both runner registrations, and `git diff --check` passed.
  The pre-existing untracked `.vscode/` is untouched.
- Limitations: `Ngkkh`/`NgkSh`, earlier-prefix conflicts, other conjuncts,
  reph, uppercase aliases, punctuation/escapes, composition, and platform
  integration remain incomplete. No broader compatibility, performance, or
  platform validation claimed.
- Next: check exact `Ngkkh` → ঙ্ক্ষ and its supported vowel/context
  interactions, including its differing single-`r` attachment, as a separate
  reference-checked increment.

### 2026-10-28 — Exact Ngkh conjunct

- Added exact `Ngkh` → ঙ্খ (U+0999 U+09CD U+0996), matching before
  shorter `Ngk`, basic `Ng`, and single `N`. The 40 basic consonant
  sequences producing 35 letters remain unchanged.
- Reused the following-`r` helper for matched `Ngkh`: single `r` attaches
  without U+200D (`Ngkhr` → `ঙ্খ্র`, `Ngkhry` → `ঙ্খ্র্য`). Two-`r`
  consumption and `rri`/`rry`/`rrZ` exceptions remain in priority
  (`Ngkhrri` → `ঙ্খৃ`, `Ngkhrry` → `ঙ্খরর‍্য`). Basic `h`/`kh`
  following-`r` behavior is unchanged and explicitly covered as incomplete.
- Authored 454 [fixtures](../tests/fixtures/conjunct-ngkh.tsv), checked
  against the SHA-256-verified pinned parser before implementation. They
  cover supported vowels/aliases and transitions, selected preceding contexts,
  adjacency, one through eight following `r` keys, priority/joiner exceptions,
  repetition, raw-spelling controls, all digits, boundaries, copied Unicode,
  and words. Corrected the initial mixed-case control's input spelling before
  implementation. All 7,052 reference cases match under Node.js v24.21.0.
- The focused Rust regression failed on `Ngkh` before implementation and
  passed afterward. Extended control-character, separate-call, and long-buffer
  regressions; removed the resolved `Ngkh` gap expectation. Added explicit
  partial outputs for earlier-prefix conflicts, aliases, reph, and escapes,
  and refreshed seven reference gap probes.
- Updated [README.md](../README.md) and
  [v1.md](compatibility/exact-conjuncts.md#exact-ngkh-conjunct) with exact Unicode, matching priority,
  examples, counts, limitations, and next work. Marked the earlier `Ngkh`
  gap as historical. No upstream source, rules, fixtures, dependencies,
  normalization, persistent state, or platform code added.
- Checks: `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, `cargo test --offline`
  (37 regression tests and one documentation example), and
  `cargo build --offline --release` passed. `node --check` passed, and the
  reference comparison passed all 7,052 cases.
- Example: `cargo run --offline --example convert -- 'Ngkh Ngkha Ngkhr Ngkhrri'`
  printed `ঙ্খ ঙ্খা ঙ্খ্র ঙ্খৃ`. All 43 conversions and gap examples in
  the new v1 section passed direct CLI and pinned-reference checks. Rechecked
  and reused Rust/Cargo 1.99.1 and Node.js v24.21.0; no tools installed or
  upgraded. The cached reference parser and license remain outside the repository.
- Documentation/fixture checks: UTF-8, 271 local Markdown links/anchors,
  final newlines, trailing whitespace, all fixture code points, 454 distinct
  new inputs, both runner registrations, and `git diff --check` passed.
  The pre-existing untracked `.vscode/` is untouched.
- Limitations: `Ngkx`/`Ngkkh`/`NgkSh`, earlier-prefix conflicts, other conjuncts,
  reph, uppercase aliases, punctuation/escapes, composition, and platform
  integration remain incomplete. No broader compatibility, performance, or
  platform validation claimed.
- Next: check exact `Ngkx` → ঙ্ক্ষ and its supported vowel/context interactions
  as a separate reference-checked increment.

### 2026-10-28 — Exact Ngk conjunct

- Added exact `Ngk` → ঙ্ক (U+0999 U+09CD U+0995), matching before basic
  `Ng` and single `N`. The 40 basic consonant sequences producing 35 letters
  remain unchanged; `Ngk` is an added conjunct sequence with consonant context.
- Extended the existing following-`r` helper for matched `Ngk`: single `r`
  attaches as ্র, including before `y`/`Z` without U+200D (`Ngkry` → `ঙ্ক্র্য`).
  Two-`r` consumption and `rri`/`rry`/`rrZ` exceptions remain in priority
  (`Ngkrri` → `ঙ্কৃ`, `Ngkrry` → `ঙ্করর‍্য`). Basic `k` is unchanged.
- Authored 433 [fixtures](../tests/fixtures/conjunct-ngk.tsv), all checked
  against the SHA-256-verified pinned parser before implementation. They cover
  supported vowels/aliases and transitions, selected preceding contexts,
  adjacency, one through eight following `r` keys, single-`r` attachment,
  priority/joiner exceptions, repetition, raw-spelling controls, all digits,
  boundaries, copied Unicode, and words. All 6,598 reference cases match
  under Node.js v24.21.0.
- Reference probes confirmed separate longer `Ngkh`/`Ngkx`/`Ngkkh`/`NgkSh`
  rules and the five earlier-prefix conflicts already identified for `Ngx`.
  Kept them outside supported fixtures and added explicit partial-output
  regressions, along with reph, alias, and escape gaps. Documented the changed
  partial `Ngkh` output (ঙখ → ঙ্কহ) caused by matching supported `Ngk` first.
  Refreshed seven reference gap probes; no wider compatibility claimed.
- The focused Rust regression failed on `Ngk` before implementation. All
  tests passed afterward, including extended control-character, separate-call,
  and long-buffer regressions. Removed the resolved `Ngk` gap expectation.
- Updated [README.md](../README.md) and
  [v1.md](compatibility/exact-conjuncts.md#exact-ngk-conjunct) with exact Unicode, matching priority,
  examples, counts, limitations, and next work. Marked earlier `Ngk` gap
  descriptions as historical. No upstream source, rules, fixtures, dependencies,
  normalization, persistent state, or platform code added.
- Checks: after applying rustfmt, `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, `cargo test --offline`
  (36 regression tests and one documentation example), and
  `cargo build --offline --release` passed. `node --check` passed.
- Example: `cargo run --offline --example convert -- 'Ngk Ngka Ngkr Ngkrri'`
  printed `ঙ্ক ঙ্কা ঙ্ক্র ঙ্কৃ`. All 41 conversions and gap examples in the
  new v1 section passed direct CLI and pinned-reference checks. Rechecked and
  reused Rust/Cargo 1.99.1 and Node.js v24.21.0; no tools installed or upgraded.
  The cached reference parser and license remain outside the repository.
- Documentation/fixture checks: UTF-8, local Markdown links/anchors, final
  newlines, trailing whitespace, all fixture code points, 433 distinct new
  inputs, both runner registrations, and `git diff --check` passed. The
  pre-existing untracked `.vscode/` is untouched.
- Limitations: longer `Ngkh`/`Ngkx`/`Ngkkh`/`NgkSh`, earlier-prefix conflicts,
  other conjuncts, reph, uppercase aliases, punctuation/escapes, composition,
  and platform integration remain incomplete. No performance or platform
  validation claimed.
- Next: check exact `Ngkh` → ঙ্খ and its supported vowel/context interactions
  as a separate reference-checked increment.

### 2026-10-28 — Exact Ngx conjunct

- Added exact `Ngx` → ঙ্ষ (U+0999 U+09CD U+09B7), matching before basic
  `Ng` and single `N`. It establishes consonant context without a joiner and
  shares `x`/`kx` following-`r` priority through the existing helper:
  `Ngxrri` → `ঙ্ষৃ`, `Ngxrr` → `ঙ্ষ্রর`, `Ngxrry` → `ঙ্ষরর‍্য`.
  The 40 basic consonant sequences producing 35 letters remain unchanged;
  `Ngx` is an added conjunct sequence.
- Authored 322 [fixtures](../tests/fixtures/conjunct-ngx.tsv). The initial
  reference comparison exposed five preceding contexts with earlier longer
  matches (`gNgx`, `NNgx`, `hNgx`, `ShNgx`, `kxNgx`). Removed those from
  the supported fixture set and documented their exact partial/reference
  outputs as separate conjunct gaps. Verified their earlier prefixes against
  the pinned parser. The final set passed reference comparison before
  implementation; all 6,165 reference cases now match under Node.js v24.21.0.
- Fixtures cover supported vowels/aliases and transitions, selected preceding
  contexts, adjacency, one through eight following `r` keys, `rri`/`rry`/`rrZ`
  exceptions, repetition, raw-spelling controls, all digits, boundaries,
  and copied Unicode. Reused the SHA-256-verified external parser and its
  license in a temporary directory; no upstream source, rules, fixtures,
  dependencies, or platform code imported.
- The focused Rust regression failed on `Ngx` before implementation. All
  tests passed afterward, including extended control-character, separate-call,
  and long-buffer regressions. Removed the resolved `Ngx` gap expectation;
  added explicit partial outputs for the five precedence gaps, `NgX`, `NgxA`,
  `rrNgx`, and escapes. Refreshed seven reference gap probes.
- Updated [README.md](../README.md) and
  [v1.md](compatibility/exact-conjuncts.md#exact-ngx-conjunct) with exact Unicode, matching order,
  examples, counts, limitations, and next work. Marked earlier `Ngx` gap
  descriptions as historical and refreshed fixture comments.
- Checks: after applying rustfmt, `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, `cargo test --offline`
  (35 regression tests and one documentation example), and
  `cargo build --offline --release` passed. `node --check` passed.
- Example: `cargo run --offline --example convert -- 'Ngx Ngxa Ngxrri Ngxrr'`
  printed `ঙ্ষ ঙ্ষা ঙ্ষৃ ঙ্ষ্রর`. All 38 documented conversions and gap
  examples in the new v1 section passed direct CLI and pinned-reference checks.
  Rechecked and reused Rust/Cargo 1.99.1 and Node.js v24.21.0; no tools upgraded.
- Documentation/fixture checks: UTF-8, local Markdown links/anchors, final
  newlines, trailing whitespace, all fixture code points, 322 distinct new
  inputs, both runner registrations, and `git diff --check` passed. The
  pre-existing untracked `.vscode/` is untouched.
- Limitations: earlier longer matches in the five contexts above, `Ngk`/`kkx`,
  other conjuncts, reph, uppercase aliases, punctuation/escapes, composition,
  and platform integration remain incomplete. No broader compatibility,
  performance, or platform validation claimed.
- Next: check exact `Ngk` → ঙ্ক and its supported vowel/context interactions
  as a separate reference-checked increment.

### 2026-10-28 — Following r after lowercase x and exact kx

- Added selected following-`r` forms after lowercase `x` and exact `kx`,
  reusing the existing helper. Two `r` keys add ্রর before the rest is
  matched: `xrrri` → `এক্স্রররি`, `kxrr` → `ক্ষ্রর`.
  Preserved `rri` and `rry`/`rrZ` priority (`xrri` → `এক্সৃ`,
  `xrry` → `এক্সরর‍্য`). Single `xr`/`kxr` stays separate and retains
  U+200D before `y`/`Z`. The basic inventory and `kx` conjunct are unchanged.
- Authored 755 [fixtures](../tests/fixtures/x-following-r.tsv), checked against
  the SHA-256-verified pinned parser before implementation. They cover one
  through eight `r` keys, vowel/alias overlaps and transitions, joiner
  exceptions, preceding contexts, repetition, all digits, boundaries, and
  copied Unicode. All 5,843 reference cases match under Node.js v24.21.0.
  Reused the external parser and license in a temporary directory; no upstream
  source, rules, fixtures, dependencies, or platform code imported.
- The focused Rust regression failed on `xrr` before implementation. After
  implementation all tests passed, including extended control-character,
  separate-call, and long-buffer regressions. Removed resolved `xrr`/`kxrr`
  gap expectations, retained `Ngx`/`kkx`/`rrx`, added `rrkx` as an explicit
  partial-output regression, and refreshed seven reference gap probes.
- Updated [README.md](../README.md) and
  [v1.md](compatibility/foundations.md#following-r-after-lowercase-x-and-exact-kx) with exact Unicode,
  matching priority, examples, counts, remaining gaps, and next work. Marked
  earlier following-`r` gap descriptions as historical.
- Checks: after applying rustfmt, `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, `cargo test --offline`
  (34 regression tests and one documentation example), and
  `cargo build --offline --release` passed. `node --check` passed.
- Example: `cargo run --offline --example convert -- 'xr xrr xrri xrrri kxrr'`
  printed `এক্সর এক্স্রর এক্সৃ এক্স্রররি ক্ষ্রর`; 21 conversions documented
  in the new v1 section also passed direct CLI checks. Rechecked and reused
  Rust/Cargo 1.99.1 and Node.js v24.21.0; no tools installed or upgraded.
- Documentation/fixture checks: UTF-8, local Markdown links/anchors, final
  newlines, trailing whitespace, fixture code points, 755 distinct new inputs,
  both runner registrations, and `git diff --check` passed. The pre-existing
  untracked `.vscode/` remains untouched.
- Limitations: `Ngx`/`kkx`, reph (including `rrx`/`rrkx`), uppercase aliases,
  other conjuncts, punctuation/escapes, composition, and platform integration
  remain incomplete. No broader compatibility, performance, or platform
  validation claimed.
- Next: check exact `Ngx` → ঙ্ষ and its supported vowel/context interactions
  as a separate reference-checked increment.

### 2026-10-28 — Contextual lowercase x and exact kx

- Added exact lowercase `x`: এক্স (U+098F U+0995 U+09CD U+09B8) at the
  start/after a copied character or digit, and ক্স (U+0995 U+09CD U+09B8)
  after supported converted input (`ax` → `আক্স`, `qx` → `কক্স`). Added
  exact `kx` → ক্ষ (U+0995 U+09CD U+09B7), matching before single `k`.
  The 40 basic consonant sequences producing 35 letters are unchanged;
  `kx` is an added conjunct sequence, included as an explicit planned gap.
- Both forms establish consonant context without a joiner: supported vowel
  signs/aliases and transitions apply (`xia` → `এক্সিয়া`, `kxrri` → `ক্ষৃ`).
  Preserved raw spelling (`khx` → `খক্স`, distinct from `kx` → `ক্ষ`),
  repetitions, `y`/`Y`/`Z` distinctions, and longer `aZ`/`oZ` priority.
  No normalization, spelling correction, persistent state, dependencies, or
  platform code added.
- Authored 392 [fixtures](../tests/fixtures/consonant-x.tsv), checked against
  the SHA-256-verified pinned parser before implementation. They cover all
  basic consonants before `x` except the separate `Ngx`/`rrx` gaps, supported
  contexts, all vowels/aliases before and after the selected forms, transitions,
  repetition, raw-spelling/case controls, digits, boundaries, copied Unicode,
  and words. All 5,088 reference cases match under Node.js v24.21.0.
  No upstream source, rules, or fixtures imported.
- The focused Rust regression failed on `x` before implementation and passed
  afterward. Extended control-character boundaries, separate-call, and long-buffer
  regressions; the full run passed. Kept `Ngx`/`kkx`, following-`r` attachments,
  reph, aliases, and escapes as explicit partial-output regressions and refreshed
  seven reference gap probes.
- Updated [README.md](../README.md) and
  [v1.md](compatibility/foundations.md#contextual-lowercase-x-and-exact-kx) with exact Unicode,
  context, examples, case count, limitations, and next work. Marked prior
  `x`/`kx` probes as historical and replaced obsolete unsupported-`x`
  descriptions in the README with the remaining uppercase-`Q` gap.
- Checks: `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, `cargo test --offline`
  (33 regression tests and one documentation example), and
  `cargo build --offline --release` passed. `node --check` passed.
- Example: `cargo run --offline --example convert -- 'x xa axa kx kxa'`
  printed `এক্স এক্সা আক্সা ক্ষ ক্ষা`; 14 new documented conversions also
  passed direct CLI checks. Rechecked and reused Rust/Cargo 1.99.1 and Node.js
  v24.21.0. No tools upgraded; the external parser stays outside the repository.
- Documentation/fixture checks: UTF-8, local Markdown links/anchors, final
  newlines, trailing whitespace, fixture counts/code points, distinct new inputs,
  both runner registrations, and `git diff --check` passed. The pre-existing
  untracked `.vscode/` is untouched.
- Limitations: `Ngx`/`kkx`, following-`r` attachment after `x`/`kx`, reph,
  remaining letter forms and aliases, other conjuncts, punctuation/escapes,
  composition, and platform integration remain incomplete. No broader
  compatibility, performance, or platform validation claimed.
- Next: check following-`r` priority after lowercase `x` and exact `kx` as a
  separate reference-checked increment.

### 2026-10-28 — Following r after lowercase w

- Added selected following-`r` forms after exact lowercase `w`, reusing the
  existing matching helper and renaming it `consume_following_r_prefix` for
  its broader scope. Two `r` keys add ্রর (U+09CD U+09B0 U+09B0) before
  the rest is matched: `wrrri` → `ও্রররি`, `wrrrri` → `ও্ররৃ`.
  The 40 basic consonant sequences producing 35 letters remain unchanged.
- Preserved existing `rri` and `rry`/`rrZ` priority (`wrri` → `ওৃ`,
  `wrry` → `ওরর‍্য`). Single `wr` stays separate; `wry` retains U+200D.
  The same rules apply after vowels/consonants (`awrr` → `আও্রর`,
  `kwrr` → `ক্ব্রর`) and in repetitions (`wrrwrr` → `ও্রর্ব্রর`).
  No normalization, spelling correction, persistent state, dependencies, or
  platform code added.
- Authored 385 [fixtures](../tests/fixtures/w-following-r.tsv), checked against
  the SHA-256-verified pinned parser before implementation. They cover runs of
  one through eight `r` keys, `rri`/`rry`/`rrZ` exceptions, vowels/aliases and
  transitions, differing preceding contexts, repetition, case distinctions,
  all digits, boundaries, and copied Unicode. All 4,696 reference cases match
  under Node.js v24.21.0. No upstream source, rules, or fixtures imported.
- The focused Rust regression failed on `wrr` before implementation and passed
  afterward. Extended control-character boundaries, separate-call, and long-buffer
  regressions; the full run passed. Removed the resolved `wrr`/`wrrri` gap
  expectations and refreshed seven probes around remaining `x`, aliases, reph,
  and escapes.
- Updated [README.md](../README.md) and
  [v1.md](compatibility/foundations.md#following-r-after-lowercase-w) with exact Unicode, matching
  priority, examples, case count, limitations, and next work. Marked the
  previous `wrr`/`wrrri` gap descriptions as historical.
- Checks: `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, `cargo test --offline`
  (32 regression tests and one documentation example), and
  `cargo build --offline --release` passed. `node --check` passed.
- Example: `cargo run --offline --example convert -- 'wr wrri wrrri wrry'`
  printed `ওর ওৃ ও্রররি ওরর‍্য`; 13 new documented conversions also passed
  direct CLI checks. Rechecked and reused Rust/Cargo 1.99.1 and Node.js v24.21.0.
  No tools upgraded; the external parser stays outside the repository.
- Documentation/fixture checks: UTF-8, local Markdown links/anchors, final
  newlines, trailing whitespace, fixture counts/code points, distinct new inputs,
  both runner registrations, and `git diff --check` passed. The pre-existing
  untracked `.vscode/` is untouched.
- Limitations: `rrw` and other reph/conjunct forms, remaining letters and
  aliases, punctuation/escapes, composition, and platform integration remain
  incomplete. No broader compatibility, performance, or platform validation claimed.
- Next: check lowercase `x` and its context-dependent forms as a separate
  reference-checked increment.

### 2026-10-28 — Contextual lowercase w

- Added exact lowercase `w`: ও (U+0993) independently/after vowels and ্ব
  (U+09CD U+09AC) after supported consonants. At the start or after a copied
  character/digit it adds য় (U+09DF) before a supported vowel key:
  `wa` → `ওয়া`, versus vowel-following `awa` → `আওা` and consonant-following
  `kwa` → `ক্বা`. Every form establishes consonant context without a joiner.
  The 40 basic consonant sequences producing 35 letters remain unchanged.
- Preserved following-vowel/alias matching, longer `aZ`/`oZ` priority, and
  repetition (`wrri` → `ওৃ`, `waZ` → `ওয়অ্যা`, `ww` → `ও্ব`, `wy` → `ও্য`).
  No normalization, spelling correction, input persistence, dependencies, or
  platform code added.
- Authored 311 [fixtures](../tests/fixtures/consonant-w.tsv), checked against
  the SHA-256-verified pinned parser before implementation. They cover every
  basic consonant before `w` except the separate `rrw` reph gap, additional
  context forms, every supported vowel/alias on either side, following-vowel
  transitions, repetition, `y`/`Y`/`Z` distinctions, all digits, boundaries,
  copied Unicode, and words. All 4,311 reference cases match under Node.js
  v24.21.0. No upstream source, rules, or fixtures imported.
- The focused Rust regression failed on `w` before implementation and passed
  afterward. Extended control-character boundaries, separate-call, and long-buffer
  regressions; the full run passed. Kept uppercase aliases, `wrr`/`wrrri`,
  `rrw`, and escapes as explicit partial-output regressions and refreshed seven
  reference gap probes.
- Updated [README.md](../README.md) and [v1.md](compatibility/foundations.md#contextual-lowercase-w)
  with exact Unicode, matching context, examples, case count, limitations, and
  next work. Marked the earlier `w` probe as historical and replaced obsolete
  README descriptions of unsupported `w` with still-unsupported `x`.
- Checks: `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, `cargo test --offline`
  (31 regression tests and one documentation example), and
  `cargo build --offline --release` passed. `node --check` passed.
- Example: `cargo run --offline --example convert -- 'w wa awa kw kwa'`
  printed `ও ওয়া আওা ক্ব ক্বা`; 21 new documented conversions also passed
  direct CLI checks. Rechecked and reused Rust/Cargo 1.99.1 and Node.js v24.21.0.
  No tools upgraded; the external parser stays outside the repository.
- Documentation/fixture checks: UTF-8, local Markdown links/anchors, final
  newlines, trailing whitespace, fixture counts/code points, distinct new inputs,
  both runner registrations, and `git diff --check` passed. The pre-existing
  untracked `.vscode/` is untouched.
- Limitations: following-`r` attachment after `w`, `rrw` reph, remaining letters
  and aliases, other conjuncts, punctuation/escapes, composition, and platform
  integration remain incomplete. No broader compatibility, performance, or
  platform validation claimed.
- Next: check following-`r` priority after lowercase `w` as a separate
  reference-checked increment.

### 2026-10-28 — Basic lowercase v consonant

- Added exact lowercase `v` → ভ (U+09AD) using the existing consonant matcher
  and vowel context (`vi` → `ভি`, `vU` → `ভূ`, `vrri` → `ভৃ`). The basic
  inventory is now 40 sequences producing 35 distinct letters. Existing `bh`
  retains its two-key match; `vh` → `ভহ`, `vv` → `ভভ`, and `vbh` → `ভভ`.
- Authored 136 [fixtures](../tests/fixtures/consonant-v.tsv), checked against
  the SHA-256-verified pinned parser before implementation. They cover all
  supported vowels/aliases on either side, following-vowel transitions,
  adjacency and `bh` controls, repetition, `y`/`Y`/`Z` distinctions, digits,
  boundaries, copied Unicode, and words. All 4,000 reference cases match under
  Node.js v24.21.0. No upstream source, rules, or fixtures imported.
- The focused Rust regression failed on `v` before implementation and passed
  afterward. Extended control-character boundaries, separate-call, and long-buffer
  regressions; the full run passed. Kept uppercase `V`, `vr`, uppercase-`H`
  adjacency, and escapes as explicit partial-output regressions and refreshed
  seven reference gap probes.
- Updated [README.md](../README.md) and
  [v1.md](compatibility/foundations.md#basic-lowercase-v-consonant) with exact Unicode, examples,
  inventory/case counts, remaining gaps, and next work. Marked the earlier `v`
  gap probe as historical. No dependencies, normalization, spelling correction,
  persistent state, or platform code added.
- Checks: `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, `cargo test --offline`
  (30 regression tests and one documentation example), and
  `cargo build --offline --release` passed. `node --check` passed.
- Example: `cargo run --offline --example convert -- 'v vi vU valO vUmi'`
  printed `ভ ভি ভূ ভালো ভূমি`. Rechecked and reused Rust/Cargo 1.99.1 and
  Node.js v24.21.0. No tools upgraded; the external parser stays outside the
  repository. The pre-existing untracked `.vscode/` is untouched.
- Documentation/fixture checks: UTF-8, local Markdown links/anchors, final
  newlines, trailing whitespace, fixture counts/code points, distinct new inputs,
  both runner registrations, documented conversions, and `git diff --check` passed.
- Limitations: uppercase `V`, `vr` and other conjunct/reph forms, remaining
  letters and aliases, punctuation/escapes, composition, and platform integration
  remain incomplete. No broader compatibility, performance, or platform
  validation claimed.
- Next: check lowercase `w` and its context-dependent forms as a separate
  reference-checked increment.

### 2026-10-28 — Basic lowercase q consonant

- Added exact lowercase `q` → ক (U+0995) using the existing consonant matcher
  and vowel context (`qa` → `কা`, `qOI` → `কৈ`, `qrri` → `কৃ`). The basic
  inventory is now 39 sequences producing 35 distinct letters. Raw matching
  stays independent of `k`: `qh` → `কহ`, `qq` → `কক`, and `qkh` → `কখ`.
- Authored 132 [fixtures](../tests/fixtures/consonant-q.tsv), checked against
  the SHA-256-verified pinned parser before implementation. They cover all
  supported vowels/aliases on either side, following-vowel transitions,
  adjacency, repetition, `y`/`Y`/`Z` distinctions, digits, boundaries,
  copied Unicode, and words. All 3,864 reference cases match under Node.js
  v24.21.0. No upstream source, rules, or fixtures imported.
- The focused Rust regression failed on `q` before implementation and passed
  afterward. Extended control-character boundaries, separate-call, and long-buffer
  regressions; the full run passed. Updated the old unmatched-`qX` controls
  because `q` now converts. Kept uppercase `Q`, `qr`, and escapes as explicit
  partial-output regressions and refreshed seven reference gap probes.
- Updated [README.md](../README.md) and
  [v1.md](compatibility/foundations.md#basic-lowercase-q-consonant) with exact Unicode, examples,
  inventory/case counts, remaining gaps, and next work. Marked earlier `q`
  gap descriptions as historical. No dependencies or platform code added.
- Checks: `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, `cargo test --offline`
  (29 regression tests and one documentation example), and
  `cargo build --offline --release` passed. `node --check` passed.
- Example: `cargo run --offline --example convert -- 'q qa qi qOI qotha'`
  printed `ক কা কি কৈ কথা`. Rechecked and reused Rust/Cargo 1.99.1 and
  Node.js v24.21.0. No tools upgraded; the external parser stays outside the
  repository. The pre-existing untracked `.vscode/` is untouched.
- Documentation/fixture checks: UTF-8, local Markdown links/anchors, final
  newlines, trailing whitespace, fixture counts/code points, distinct new inputs,
  both runner registrations, documented conversions, and `git diff --check` passed.
- Limitations: uppercase `Q`, `qr` and other conjunct/reph forms, remaining
  letters and aliases, punctuation/escapes, composition, and platform integration
  remain incomplete. No broader compatibility, performance, or platform
  validation claimed.
- Next: check and add basic lowercase `v` → ভ and its vowel context as a
  separate reference-checked increment.

### 2026-10-28 — Following r after uppercase Y

- Added selected following-`r` forms after exact uppercase `Y`, extending the
  existing raw-key matching helper. Single `Yr` adds ্র (`Yr` → `য়্র`),
  including before `y`/`Z` without U+200D (`Yry`/`YrZ` → `য়্র্য`).
  Generated য় stays U+09DF; copied decomposed য় stays U+09AF U+09BC.
  The basic inventory remains 38 sequences producing 35 letters.
- Longer runs share the two-`r` consumption rule from `y`/`Z`, with `rri`
  and `rry`/`rrZ` retaining priority: `Yrrri` → `য়্রররি`,
  `Yrrrri` → `য়্ররৃ`, `Yrri` → `য়ৃ`, and `Yrry` → `য়রর‍্য`.
  Lowercase `y` and uppercase `Z` keep their distinct single-`r` behavior.
  No output normalization, spelling correction, or persistent state added.
- Authored 286 [fixtures](../tests/fixtures/uppercase-y-following-r.tsv),
  checked against the SHA-256-verified pinned parser before implementation.
  They cover one through eight `r` keys, vowel overlaps/aliases and transitions,
  joiner exceptions, preceding contexts, repeated forms, all digits, boundaries,
  copied Unicode, and case controls. All 3,732 reference cases match under
  Node.js v24.21.0. No upstream source, rules, or fixtures imported.
- The focused Rust regression failed on `Yr` before implementation and passed
  afterward. Extended control-character, separate-call, and long-buffer
  regressions; the full test run passed. Removed resolved `Yr`/`Yrr`/`Yry`
  gap expectations and refreshed seven probes around remaining lowercase `q`,
  alias, reph, and escape limitations.
- Updated [README.md](../README.md) and
  [v1.md](compatibility/foundations.md#following-r-after-uppercase-y) with exact Unicode, matching
  priority, examples, counts, remaining gaps, and next work. Marked earlier
  `Y` gap descriptions as historical and refreshed fixture comments.
- Checks: `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, `cargo test --offline`
  (28 regression tests and one documentation example), and
  `cargo build --offline --release` passed. `node --check` passed.
- Example: `cargo run --offline --example convert -- 'Yr Yrri Yry Yrry'` printed
  `য়্র য়ৃ য়্র্য য়রর‍্য`. Rechecked and reused Rust/Cargo 1.99.1 and
  Node.js v24.21.0. No tools upgraded or dependencies added; the external parser
  stays outside the repository. The pre-existing untracked `.vscode/` is untouched.
- Documentation/fixture checks: UTF-8, local Markdown links/anchors, final
  newlines, trailing whitespace, fixture counts/code points, distinct new inputs,
  both runner registrations, documented conversions, and `git diff --check` passed.
- Limitations: remaining letters and aliases, other conjunct/reph forms
  (including `rrY`), punctuation/escapes, composition, and platform integration
  remain incomplete. No broader compatibility, performance, or platform
  validation claimed.
- Next: check and add basic lowercase `q` and its vowel context as a separate
  reference-checked increment.

### 2026-10-28 — Following r after lowercase y and uppercase Z

- Added selected following-`r` matches after lowercase `y` and uppercase `Z`,
  including the final `Z` in `aZ`/`oZ`. Two `r` keys normally add ্রর and
  are consumed before the rest is matched (`yrrri` → `ইয়্রররি`,
  `yrrrri` → `ইয়্ররৃ`). Existing `rri` and `rry`/`rrZ` keep priority
  (`yrri` → `ইয়ৃ`, `yrry` → `ইয়রর‍্য`). Basic inventory remains 38 sequences
  producing 35 letters.
- Preserved single `yr`/`Zr`. Only uppercase `Z` before `ry`/`rZ` adds ্র
  without U+200D (`Zry` → `্য্র্য`); lowercase `yry` retains the joiner
  (`ইয়র‍্য`). Context remains local to one conversion call; copied Unicode
  is preserved without normalization. Uppercase `Y` conjuncts remain separate.
- Authored 418 [fixtures](../tests/fixtures/ya-following-r.tsv), checked against
  the SHA-256-verified pinned parser before implementation. They cover one to
  eight `r` keys, vowel overlaps/aliases, joiner exceptions, preceding contexts,
  `aZ`/`oZ`, repetition, digits, boundaries, copied Unicode, and uppercase `Y`
  controls. All 3,446 reference cases match under Node.js v24.21.0. No upstream
  source, rules, or fixtures imported.
- The focused Rust regression failed on `yrr` before implementation and passed
  afterward. Extended control-character boundaries, separate-call, and long-buffer
  regressions. Corrected a missing র in the new long-buffer expectation after
  the first full run; the final full run passed. Removed resolved gap expectations
  and refreshed seven reference probes around remaining uppercase `Y`, alias,
  reph, and escape limitations.
- Updated [README.md](../README.md) and
  [v1.md](compatibility/foundations.md#following-r-after-lowercase-y-and-uppercase-z) with exact Unicode,
  matching priority, examples, counts, remaining gaps, and next work. Marked
  earlier gap tables as historical and refreshed fixture comments.
- Checks: after applying rustfmt, `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, `cargo test --offline`
  (27 regression tests and one documentation example), and
  `cargo build --offline --release` passed. `node --check` passed.
- Example: `cargo run --offline --example convert -- 'yrr yrri yry Zry'` printed
  `ইয়্রর ইয়ৃ ইয়র‍্য ্য্র্য`. Rechecked and reused Rust/Cargo 1.99.1 and
  Node.js v24.21.0. No tools upgraded or dependencies added; the external parser
  stays outside the repository. The pre-existing untracked `.vscode/` is untouched.
- Documentation/fixture checks: UTF-8, local Markdown links/anchors, final
  newlines, trailing whitespace, fixture counts/code points, distinct new inputs,
  both runner registrations, documented conversions, and `git diff --check` passed.
- Limitations: uppercase `Y` following-`r` forms, other conjunct/reph forms,
  remaining letters and aliases, punctuation/escapes, composition, and platform
  integration remain incomplete. No broader compatibility, performance, or
  platform validation claimed.
- Next: resolve following-`r` matching after uppercase `Y` as a separate
  reference-checked increment, preserving `Yrri` and `Yrry`/`YrrZ` controls.

### 2026-10-28 — Uppercase Z with aZ and oZ forms

- Added exact uppercase `Z` → ্য (U+09CD U+09AF), including standalone output,
  following vowel signs, repeated `Z`/lowercase `y`, and ordinary adjacency.
  Basic `r`/`rr` shares the existing U+200D flag with lowercase `y`
  (`rZ` → `র‍্য`); nasal-plus-`r` prefixes and copied র omit that joiner.
  The 38 basic consonant sequences (35 letters) remain unchanged.
- Reference probes established longer `aZ` → অ্যা and `oZ` → অ্য matches before
  ordinary vowel handling, even after a consonant (`kaZ` → `কঅ্যা`). Both establish
  consonant context, preserving exact sequences such as `aZa` → `অ্যাা`.
  Existing `oo`/`ng`-vowel priority remains intact (`ooZ` → `উ্য`,
  `ngaZ` → `ঙ্গা্য`, `ngooZ` → `ঙ্গঅ্য`). No spelling correction or normalization.
- Authored 398 [fixtures](../tests/fixtures/consonant-z-uppercase.tsv), checked
  against the SHA-256-verified pinned parser before implementation. They cover
  every supported consonant, vowels/aliases on either side, longer-match priority,
  ng-vowel overlaps, repetition, joiners, digits, boundaries, copied Unicode,
  and case distinctions. All 3,028 reference cases match under Node.js v24.21.0.
  No upstream code, rules, or fixtures imported.
- The focused Rust regression first failed on `kZ`, then passed after the
  implementation. Extended Unicode-boundary, control-character, separate-call,
  and long-buffer checks. Removed resolved `Z`/`kZ`/`zZ`/`yZ`/`YZ` gap expectations;
  added explicit longer `Zrr`/`Zry`, `AZ`, and escape limitations. Updated old
  fixture comments, README, and [v1.md](compatibility/foundations.md#uppercase-z-with-az-and-oz-forms).
- Checks: after applying rustfmt, `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, `cargo test --offline`
  (26 regression tests and one documentation example), and
  `cargo build --offline --release` passed. `node --check` passed.
- Example: `cargo run --offline --example convert -- 'kZa aZ oZ baZ'` printed
  `ক্যা অ্যা অ্য বঅ্যা`. Rechecked and reused Rust/Cargo 1.99.1 and
  Node.js v24.21.0. No tools upgraded or dependencies added; the external parser
  stays outside the repository. The pre-existing untracked `.vscode/` is untouched.
- Documentation/fixture checks: UTF-8, local Markdown links/anchors, final
  newlines, trailing whitespace, fixture counts/code points, distinct new inputs,
  both runner registrations, and `git diff --check` passed.
- Limitations: longer `yrr`/`Zrr`/`Zry`, other conjunct/reph forms, remaining
  letters and aliases (including `AZ`), punctuation/escapes, composition, and
  platform integration remain incomplete. No broader compatibility, performance,
  or platform validation claimed.
- Next: resolve following-`r` matching after lowercase `y` and uppercase `Z`
  as a separate reference-checked increment.

### 2026-10-28 — Contextual lowercase y

- Added exact lowercase `y`: independent ইয় (U+0987 U+09DF), য় (U+09DF)
  after a supported vowel, and ্য (U+09CD U+09AF) after a supported consonant.
  Every form establishes consonant context for following vowel signs; repeated
  `y` adds another ্য. Uppercase `Y` stays distinct (`kY` → `কয়`, `ky` → `ক্য`).
  The 38 basic consonant sequences (35 letters) are unchanged.
- Basic `r`/`rr` now retains a flag for U+200D before following lowercase `y`:
  `ry` → `র‍্য`. Reference-checked `Ngr`/`NGr`/`ngr` prefixes omit that joiner
  (`Ngry` → `ঙর্য`); a subsequent basic `r` restores it (`Ngrry` → `ঙরর‍্য`).
  Context stays local to one conversion call. No output normalization added.
- Authored 338 [fixtures](../tests/fixtures/consonant-y-lowercase.tsv), checked
  against the SHA-256-verified pinned parser before implementation. They cover
  every supported consonant, vowels/aliases before and after `y`, following-vowel
  transitions, repeated keys, joiner distinctions, digits, boundaries, copied
  Unicode, case controls, and words. All 2,630 reference cases match under
  Node.js v24.21.0. No upstream source, rules, or fixtures imported.
- The focused Rust regression first failed on `ky`, then passed after the
  implementation. Extended boundary, separate-call, and long-buffer checks.
  The first full run exposed a missing separator in the new repeated test input;
  corrected that test boundary, then all tests passed. Replaced resolved `y`/`Yy`
  gap expectations with longer `yrr`, `yZ`, and escape cases; refreshed seven
  reference gap probes.
- Updated [README.md](../README.md) and
  [v1.md](compatibility/foundations.md#contextual-lowercase-y) with Unicode, examples, counts, and remaining
  gaps. No dependencies, composition, platform code, or tool upgrades added.
- Checks: `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, `cargo test --offline`
  (25 regression tests and one documentation example), and
  `cargo build --offline --release` passed. `node --check` passed.
- Example: `cargo run --offline --example convert -- 'y ay ky kiya'` printed
  `ইয় আয় ক্য কিয়া`. Rechecked and reused Rust/Cargo 1.99.1 and Node.js v24.21.0.
  The external reference stays outside the repository; the pre-existing untracked
  `.vscode/` directory is untouched.
- Documentation/fixture checks: UTF-8, local Markdown links/anchors, final
  newlines, trailing whitespace, fixture counts/code points, distinct new inputs,
  both runner registrations, and `git diff --check` passed.
- Limitations: longer `yrr`, other conjunct/reph forms, remaining letters,
  uppercase `Z`, aliases, punctuation/escapes, composition, and platform integration
  remain incomplete. No full compatibility, performance, or platform validation
  claimed.
- Next: add uppercase `Z` → ্য in a separate increment after reference checks.

### 2026-10-28 — Basic uppercase Y consonant

- Added exact uppercase `Y` → য় (U+09DF), with consonant context for supported
  vowels/aliases, including `Yi` → `য়ি` and `Yrri` → `য়ৃ`. The basic inventory
  is now 38 consonant sequences producing 35 distinct letters. Lowercase `y`
  remains a separate, incomplete context-dependent form.
- Authored 142 [fixtures](../tests/fixtures/consonant-y-uppercase.tsv), checked
  against the SHA-256-verified pinned parser before implementation. They cover
  every supported vowel/alias on either side, following-vowel transitions,
  ordinary adjacency, repeated `Y`, digits, boundaries, copied Unicode, and words.
  All 2,292 reference cases match under Node.js v24.21.0; seven gap probes report
  lowercase `y`, conjunct/reph, `Z`, and escape limitations. No upstream source,
  rules, or fixtures imported.
- Generated য় is U+09DF. A fixture preserves copied decomposed য় as U+09AF
  U+09BC before generated U+09DF U+09BF; no normalization added. Verified
  ordinary `kY` → `কয়`, `Yk` → `য়ক`, and `YY` → `য়য়` without automatic conjuncts.
- The focused Rust regression failed on `Y` before implementation, then passed
  after adding the mapping. Extended Unicode-boundary, separate-call, and
  long-buffer checks. Updated the old unmatched-`qXYZ` check because its `Y`
  now converts, while `q`, `X`, and `Z` remain literal.
- Updated [README.md](../README.md) and
  [v1.md](compatibility/foundations.md#basic-uppercase-y-consonant) with Unicode, counts, examples, and
  exact remaining gaps. No dependencies, composition, or platform code added.
- Checks: `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, `cargo test --offline`
  (24 regression tests and one documentation example), and
  `cargo build --offline --release` passed. `node --check` passed.
- Example: `cargo run --offline --example convert -- 'zaY hoY hoYe maYa'`
  printed `যায় হয় হয়ে মায়া`. Rechecked and reused Rust/Cargo 1.99.1 and
  Node.js v24.21.0; no tools installed or upgraded. The external reference remains
  outside the repository; the pre-existing untracked `.vscode/` directory is untouched.
- Documentation/fixture checks: UTF-8 decoding, 161 local Markdown links/anchors
  across four documents, final newlines, trailing whitespace, fixture counts,
  exact code points, both runner registrations, distinct new inputs, and
  `git diff --check` passed.
- Limitations: lowercase `y`, remaining letters, conjunct/reph forms, aliases,
  punctuation/escapes, composition, and platform integration remain incomplete.
  No full compatibility, performance, or platform validation claimed.
- Next: add lowercase `y` context rules in a separate increment. Preliminary
  probes confirm `y` → `ইয়`, `ay` → `আয়`, `ky` → `ক্য`, and `kiya` → `কিয়া`;
  full vowel/context fixtures still need independent checks.

### 2026-10-28 — Following rri after Ng/NG/ng

- Fixed matching order with three independently authored prefixes:
  `Ngr` → `ঙর`, `NGr` → `ঞর`, and `ngr` → `ংর`. Each consumes the first `r`
  with its nasal form before matching the remainder. This fixes `Ngrri` → `ঙররি`,
  `NGrri` → `ঞররি`, and `ngrri` → `ংররি`, plus longer runs such as
  `Ngrrri` → `ঙরৃ` and `Ngrrrri` → `ঙররররি`. The basic inventory remains 37
  consonant sequences (34 letters), with these three additional matching forms.
- Probed other multi-key consonants before selecting the exception: `khrri`,
  `phrri`, and `Rhrri` still require `খৃ`, `ফৃ`, and `ঢ়ৃ`. Their existing matching
  is preserved. Digits, copied Unicode, and intervening vowels separate the
  matches; nothing is retained between conversion calls.
- Authored 274 [fixtures](../tests/fixtures/nasal-rri.tsv), verified against the
  SHA-256-checked pinned parser before implementation. They cover all three
  prefixes, one through ten `r` keys before `i` and subsequent `a`/`o`, shorter
  runs without `i`, vowels/aliases, repetition, case distinctions, boundaries,
  digits, copied Unicode, and other-consonant controls. All 2,150 reference cases
  match under Node.js v24.21.0. No upstream source, rules, or fixtures imported.
- The focused Rust regression failed on `Ngrri` before the fix, reproducing the
  known `ঙৃ` output; it and all existing tests pass after the fix. Extended
  long-buffer and separate-call checks, removed resolved gap expectations, and
  refreshed seven reference gap probes. Updated [README.md](../README.md),
  [v1.md](compatibility/foundations.md#following-rri-after-ng-ng-and-ng), and older fixture comments so
  they no longer describe these three cases as unsupported.
- Checks: `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, `cargo test --offline`
  (23 regression tests and one documentation example), and
  `cargo build --offline --release` passed. `node --check` passed.
- Example: `cargo run --offline --example convert -- 'Ngrri NGrrri ngrrrri'`
  printed `ঙররি ঞরৃ ংররররি`. Rechecked and reused Rust/Cargo 1.99.1 and
  Node.js v24.21.0; no tools installed or upgraded. The external reference remains
  outside the repository; the pre-existing untracked `.vscode/` directory is untouched.
- Documentation/fixture checks: UTF-8 decoding, 154 local Markdown links/anchors
  across four documents, final newlines, trailing whitespace, fixture counts,
  exact code points, both runner registrations, distinct new inputs, and
  `git diff --check` passed.
- Limitations: remaining letters, other conjunct/reph forms, aliases,
  punctuation/escapes, composition, and platform integration remain incomplete.
  No full compatibility, performance, or platform validation claimed; no
  dependencies or platform code added.
- Next: add basic uppercase `Y` → য় in a separate increment. Preliminary probes
  confirm U+09DF, `Yi` → `য়ি`, `Yrri` → `য়ৃ`, and ordinary adjacency `kY` → `কয়`;
  lowercase `y` remains distinct. Full vowel/context fixtures still need checking.

### 2026-10-28 — Lowercase ng sign and vowel forms

- Added exact lowercase `ng` → ং (U+0982) before single `n`, distinct from
  `Ng` → ঙ and `NG` → ঞ. Added the reference's selected ng-vowel forms producing
  ঙ্গ (U+0999 U+09CD U+0997) with the corresponding vowel sign. This is a sign
  and specific longer forms; the 37 consonant sequences (34 letters) are unchanged.
- Reference probes established that `nga` → `ঙ্গা`, rather than attaching a sign
  to ং. The longer forms consume their vowel keys before ordinary aliases:
  `ngee` → `ঙ্গেএ`, `ngoo` → `ঙ্গঅ`. Matching `OI`/`OU` before `O` and retaining
  the last raw vowel key preserves `ngOI` → `ঙ্গৈ` and `ngia` → `ঙ্গিয়া`.
  Longer `ngh`/`nng`, following `rri`, case variants, and escapes remain gaps.
- Authored 110 [fixtures](../tests/fixtures/sign-ng.tsv), checked against the
  SHA-256-verified pinned external parser before Rust implementation. They cover
  vowel prefixes/suffixes, repeated vowel keys and transitions, adjacent consonants,
  repeated signs, case distinctions, digits, boundaries, copied Unicode, and
  words. All 1,876 reference cases match under Node.js v24.21.0; seven gap probes
  report remaining behavior. No upstream source, rules, or fixtures imported.
- Extended Unicode-boundary, separate-call, and long-buffer checks. Removed the
  old unsupported-`ng` expectation and recorded partial outputs for the new gap
  probes. Updated [README.md](../README.md) and
  [v1.md](compatibility/foundations.md#lowercase-ng-sign-and-vowel-forms) with exact Unicode, examples,
  matching priority, counts, and limits. No dependencies or platform code added.
- Checks: `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, `cargo test --offline`
  (22 regression tests and one documentation example), and
  `cargo build --offline --release` passed. `node --check` passed.
- Example: `cargo run --offline --example convert -- 'bangla rong nga ngi'`
  printed `বাংলা রং ঙ্গা ঙ্গি`. Rechecked and reused Rust/Cargo 1.99.1 and
  Node.js v24.21.0; no tools installed or upgraded. The external reference remains
  outside the repository; the pre-existing untracked `.vscode/` directory is untouched.
- Documentation/fixture checks: UTF-8 decoding, 145 local Markdown links/anchors
  across four documents, final newlines, trailing whitespace, all fixture counts
  and code points, both runner registrations, distinct new inputs, and
  `git diff --check` passed.
- Limitations: following-`rri` context after `Ng`/`NG`/`ng`, other longer
  consonant/conjunct/reph forms, aliases, punctuation/escapes, composition, and
  platform integration remain incomplete. No full compatibility, performance,
  or platform validation claimed.
- Next: resolve following-`rri` context after `Ng`/`NG`/`ng` as a separate
  increment after independently checking longer runs and boundaries.

### 2026-10-28 — Basic Ng/NG consonants

- Added exact `Ng` → ঙ (U+0999) and `NG` → ঞ (U+099E). Both match before single
  `N` → ণ and establish consonant context for vowel signs. The core now implements
  37 consonant input sequences producing 34 distinct letters.
- Finished the prepared [fixtures](../tests/fixtures/consonants-ng-nj.tsv) and
  reference-checker edits. The first reference run rejected `Ngrri` → `ঙৃ`;
  a full mismatch probe also rejected `NGrri` → `ঞৃ`. Actual reference outputs
  are `ঙররি` and `ঞররি`. Excluded those two expectations from compatibility
  fixtures and recorded both as context gaps with current partial engine outputs.
- All 88 final new cases were checked against the SHA-256-verified pinned parser
  before Rust implementation. They cover supported vowels/aliases (except the
  following-`rri` exception), case distinctions, priority over `N`, repeated and
  neighboring input, digits, boundaries, copied Unicode, and words. All 1,766
  cases match the external reference under Node.js v24.21.0; seven gap probes
  record remaining behavior. No upstream source, rules, or fixtures imported.
- Extended Unicode-boundary, separate-call, and long-buffer regression checks.
  Documented partial outputs for lowercase `ng`, `Ngk`, `NGc`, `NGch`, escapes,
  and following `rri`. Updated [README.md](../README.md) and
  [v1.md](compatibility/foundations.md#basic-ng-and-ng-consonants) with Unicode, examples, counts, and
  limitations. No dependencies, composition, or platform code added.
- Checks: `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, `cargo test --offline`
  (21 regression tests and one documentation example), and
  `cargo build --offline --release` passed. `node --check` passed.
- Example: `cargo run --offline --example convert -- 'Ng NG aNgul raNga'` printed
  `ঙ ঞ আঙুল রাঙা`. Rechecked and reused Rust/Cargo 1.99.1 and Node.js v24.21.0;
  no tools installed or upgraded. The cached external reference remains outside
  the repository. The pre-existing untracked `.vscode/` directory is untouched.
- Documentation/fixture checks: UTF-8 decoding, 138 local Markdown links/anchors
  across four documents, final newlines, trailing whitespace, fixture counts,
  code points, registration in both runners, and `git diff --check` passed.
- Limitations: following-`rri` context, lowercase `ng`, remaining consonants,
  conjunct/reph forms, aliases, punctuation/escapes, composition, and platform
  integration remain incomplete. No full compatibility, performance, or platform
  validation claimed.
- Next: add lowercase `ng` → ং as a separate increment after independently
  checking surrounding context against the pinned reference.

### 2026-10-28 — Basic lowercase z consonant

- Added exact lowercase `z` → য (U+09AF), establishing consonant context for
  supported vowels. It remains distinct from `j` → জ and the still-unimplemented
  uppercase `Z`. The core now implements 35 consonant input sequences producing
  32 distinct letters.
- Authored 51 [fixtures](../tests/fixtures/consonant-z.tsv), verified against the
  pinned parser before Rust implementation. They cover every supported vowel/alias
  on either side, following-vowel transitions, repeated and neighboring input,
  boundaries, digits, copied Unicode, and words. All 1,678 cases match the
  SHA-256-verified external parser under Node.js v24.21.0. No upstream source,
  rules, or fixtures imported.
- Verified ordinary adjacency (`kz` → `কয`, `zk` → `যক`, `zz` → `যয`) and raw
  vowel case (`zini` → `যিনি`, `zIni` → `যীনি`), without spelling correction.
  Extended Unicode-boundary, separate-call, and long-buffer checks. Recorded
  partial outputs for uppercase `Z`, related conjuncts, `zr`, and escapes.
- Updated [README.md](../README.md) and [v1.md](compatibility/foundations.md#basic-lowercase-z-consonant)
  with Unicode, counts, examples, and remaining gaps. No dependencies,
  composition, or platform code added.
- Checks: `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, `cargo test --offline`
  (20 regression tests and one documentation example), and
  `cargo build --offline --release` passed. The reference comparison passed all
  1,678 cases and reported five remaining gap probes.
- Example: `cargo run --offline --example convert -- 'zai zabe zodi zokhon'`
  printed `যাই যাবে যদি যখন`; 20 direct CLI checks passed for vowels, words,
  adjacency, Unicode boundaries, and documented gaps. Reused inspected Rust/Cargo
  1.99.1 and Node.js v24.21.0; no tools installed or upgraded. The cached external
  reference remained outside the repository.
- Documentation/tool checks: `node --check`, UTF-8 decoding, 131 local Markdown
  links/anchors across four documents, final newlines, trailing whitespace,
  fixture counts, and `git diff --check` passed. The pre-existing untracked
  `.vscode/` directory was left untouched.
- Limitations: uppercase `Z` and related conjuncts, `zr`, remaining consonants,
  conjunct/reph forms, aliases, punctuation/escapes, composition, and platform
  integration remain incomplete. No full compatibility, performance, or platform
  validation claimed.
- Next: add basic `Ng`/`NG` → ঙ/ঞ as a separate increment. Preliminary standalone
  reference probes confirm U+0999/U+099E and distinguish lowercase `ng` → ং
  (U+0982), which remains outside the next basic consonant group. Vowel/context
  cases still need independent fixtures and reference checks before implementation.

### 2026-10-28 — Basic uppercase R/Rh consonants

- Added exact `R` → ড় (U+09DC) and `Rh` → ঢ় (U+09DD). The existing longest-match
  rule consumes `Rh` before `R`; both establish consonant context for supported
  vowels. The core now implements 34 consonant input sequences producing
  31 distinct letters.
- Authored 94 [fixtures](../tests/fixtures/consonants-r-retroflex.tsv), verified
  against the pinned parser before Rust implementation. They cover every
  supported vowel/alias on either side, following-vowel transitions, interactions
  with lowercase `r`/`rri`, extra `h`, boundaries, digits, copied Unicode, and words.
  All 1,627 cases match the SHA-256-verified external parser under Node.js v24.21.0.
  No upstream source, rules, or fixtures imported.
- Confirmed `Rrri` → `ড়ৃ` and `RrriR` → `ড়ৃড়` without changing `rri` priority.
  Generated ড়/ঢ় remain single U+09DC/U+09DD code points. Two fixtures preserve
  copied decomposed ড়/ঢ় (base letter plus U+09BC) alongside newly generated
  single-code-point letters; no normalization was added.
- Extended Unicode-boundary, separate-call, and long-buffer checks. Updated
  the remaining `Rri` partial output to `ড়রি`; its reference conjunct `ড়্রি`
  remains unimplemented. Updated [README.md](../README.md) and
  [v1.md](compatibility/foundations.md#basic-uppercase-r-and-rh-consonants) with counts, Unicode, examples,
  and current limitations. No dependencies, composition, or platform code added.
- Checks: `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, `cargo test --offline`
  (19 regression tests and one documentation example), and
  `cargo build --offline --release` passed. The reference comparison passed all
  1,627 cases and reported five remaining gap probes.
- Example: `cargo run --offline --example convert -- 'baRi gaRi gaRh drriRh'`
  printed `বাড়ি গাড়ি গাঢ় দৃঢ়`; 20 direct CLI checks passed for new letters,
  vowels, longer sequences, Unicode encodings, boundaries, and documented gaps.
  Reused inspected Rust/Cargo 1.99.1 and Node.js v24.21.0; no tools installed or
  upgraded. The cached external reference remained outside the repository.
- Documentation/tool checks: `node --check`, UTF-8 decoding, 124 local Markdown
  links/anchors across four documents, final newlines, trailing whitespace,
  fixture counts, and `git diff --check` passed. The pre-existing untracked
  `.vscode/` directory was left untouched.
- Limitations: `Rri`, `Rr`, `Rhr`, `RH`, remaining consonants, conjunct/reph forms,
  other aliases, punctuation/escapes, composition, and platform integration remain
  incomplete. No full compatibility, performance, or platform validation claimed.
- Next: add lowercase `z` → য as a separate increment. Preliminary reference
  probes distinguish `z` → য (U+09AF) from `Z` → ্য (U+09CD U+09AF); uppercase
  `Z` stays outside the basic-letter scope. Vowel/context cases still need
  independent fixtures and reference checks before implementation.

### 2026-10-28 — Confirmed s/sh/S/Sh consonants

- Implemented the user's confirmed mapping: `s` → স (U+09B8), `sh`/`S` → শ
  (U+09B6), and `Sh` → ষ (U+09B7). The existing longest-match rule consumes `sh`
  before `s` and `Sh` before `S`. All four establish consonant context for
  supported vowels. There are now 32 consonant input sequences producing
  29 distinct letters.
- Authored 174 [fixtures](../tests/fixtures/consonants-s-sh.tsv), checked against
  the pinned parser before Rust implementation. They cover all supported
  vowels/aliases on either side, following-vowel transitions, case distinctions,
  overlapping sequences, digits, boundaries, copied Unicode, and words.
  All 1,533 cases match the SHA-256-verified external parser under Node.js v24.21.0.
  No upstream source, rules, or fixtures imported.
- Kept raw spelling deterministic: `shishu`/`SiSu` → `শিশু`, while `sisu` → `সিসু`.
  Verified overlapping `ssh` → `সশ`, adjacent `shSh`/`Shsh`, and extra `h` after
  `sh`/`Sh`. Extended Unicode-boundary, separate-call, and long-buffer checks.
  Added explicit partial outputs for conjuncts, uppercase-`H` aliases, and escapes.
- Updated [README.md](../README.md) and
  [v1.md](compatibility/foundations.md#confirmed-s-sh-s-and-sh-mapping) with implemented status, Unicode,
  counts, examples, and remaining gaps. No dependencies, composition, or
  platform code added.
- Checks: `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, `cargo test --offline`
  (18 regression tests and one documentation example), and
  `cargo build --offline --release` passed. The reference comparison passed all
  1,533 cases and reported five remaining gap probes.
- Examples: `cargo run --offline --example convert -- 's sh S Sh'` printed
  `স শ শ ষ`; the same command with `'sokal shishu SiSu bhaSha'` printed
  `সকাল শিশু শিশু ভাষা`. Twenty-one direct CLI checks passed for mappings,
  vowels, longer sequences, boundaries, words, and documented partial outputs.
  Reused inspected Rust/Cargo 1.99.1 and Node.js v24.21.0; no tools installed or
  upgraded. The cached external reference remained outside the repository.
- Documentation/tool checks: `node --check`, UTF-8 decoding, 117 local Markdown
  links/anchors across four documents, final newlines, trailing whitespace,
  fixture counts, and `git diff --check` passed. The pre-existing untracked
  `.vscode/` directory was left untouched.
- Limitations: `sk`, `st`, `ShT`, uppercase-`H` aliases, other remaining consonants,
  conjunct/reph forms, punctuation/escapes, composition, and platform integration
  remain incomplete. No full compatibility, performance, or platform validation
  claimed.
- Next: add basic `R`/`Rh` for ড়/ঢ় as a separate increment. Preliminary standalone
  probes match the pinned reference (U+09DC/U+09DD); vowel/context cases still
  need independent fixtures and reference checks before implementation.

### 2026-10-28 — Correct next consonant mapping

- Recorded the user's confirmed mapping: `s` → স (U+09B8), `sh`/`S` → শ
  (U+09B6), and `Sh` → ষ (U+09B7). This supersedes the earlier incorrect
  three-form next-task description; `S` does not produce ষ.
- Checked all four standalone forms against the SHA-256-verified external
  jsAvroPhonetic v1.1.4 parser with Node.js v24.21.0. All match; no deliberate
  reference deviation is needed. No upstream source, rules, or fixtures imported.
- Updated [v1.md](compatibility/foundations.md#confirmed-s-sh-s-and-sh-mapping), README, and the next-step
  plan. This is a documentation correction; engine code and fixture counts
  remain unchanged. No Cargo checks apply to this increment.
- Checks: UTF-8 decoding, local Markdown links/anchors, final newlines, trailing
  whitespace, and `git diff --check` passed. The pre-existing untracked `.vscode/`
  directory was left untouched.
- Limitations: the four forms remain unimplemented. Vowel combinations and
  neighboring input have not yet been reference-checked for this group.
- Next: implement the corrected four-form group with authored regression cases,
  preserving case distinctions and longest-sequence matching.

### 2026-10-28 — Basic l/h consonants

- Added lowercase `l` → ল (U+09B2) and standalone `h` → হ (U+09B9). Both
  establish consonant context for supported vowels. The core now implements
  28 consonant input sequences producing 26 distinct letters.
- Authored 110 [fixtures](../tests/fixtures/consonants-l-h.tsv), verified against
  the pinned parser before Rust implementation. They cover all supported
  vowels/aliases on either side, following-vowel transitions, digits, boundaries,
  copied Unicode, and words. All 1,359 cases match the SHA-256-verified external
  parser under Node.js v24.21.0. No upstream source, rules, or fixtures imported.
- Checked all ten existing two-key consonants with an extra `h`/`ha`; longest
  matching still consumes `kh` as খ, followed by standalone হ in `khh` → `খহ`.
  Moved now-supported `phh`/`chh`/`dhh`/`Dhh` cases into reference fixtures and
  updated partial uppercase/escape outputs to reflect converted `h`. Escapes
  remain unsupported: a backtick still appears in `` d`h `` → `` দ`হ ``.
- Extended Unicode boundary, separate-call, and long-buffer regressions. Updated
  [README.md](../README.md) and [v1.md](compatibility/foundations.md#basic-l-and-h-consonants) with exact
  Unicode, examples, current counts, and remaining gaps, including affected
  earlier gap tables. No dependencies, composition, or platform code added.
- Checks: `cargo fmt --all -- --check` passed after applying rustfmt;
  `cargo clippy --offline --all-targets -- -D warnings`, `cargo test --offline`
  (17 regression tests and one documentation example), and
  `cargo build --offline --release` passed. The reference comparison passed all
  1,359 cases and reported five remaining gap probes.
- Example: `cargo run --offline --example convert -- 'lal holud bhalO'` printed
  `লাল হলুদ ভালো`; 20 direct CLI checks passed for new letters, vowels,
  two-key matching, boundaries, words, and documented partial outputs. Reused
  inspected Rust/Cargo 1.99.1 and Node.js v24.21.0; no tools installed or upgraded.
  The cached external reference remained outside the repository.
- Documentation/tool checks: `node --check`, UTF-8 decoding, 108 local Markdown
  links/anchors across four documents, final newlines, trailing whitespace,
  fixture counts, and `git diff --check` passed. The pre-existing untracked
  `.vscode/` directory was left untouched.
- Limitations: `ll`/`hl` and other conjuncts, uppercase `L`/`H` and other aliases,
  remaining consonants, conjunct/reph forms, punctuation/escapes, composition,
  and platform integration remain incomplete. No full compatibility,
  performance, or platform validation claimed.
- Next: add basic `s`/`sh`/`S` for স/শ/ষ as a separate consonant increment after
  reference checks for case distinctions and longest-sequence matching.

### 2026-10-28 — Basic d/dh/D/Dh consonants

- Added exact `d` → দ (U+09A6), `dh` → ধ (U+09A7), `D` → ড (U+09A1), and
  `Dh` → ঢ (U+09A2). The existing longest-match rule consumes `dh`/`Dh` before
  their single-key prefixes. All four establish consonant context for supported
  vowels. There are now 26 consonant input sequences producing 24 letters.
- Authored 164 [fixtures](../tests/fixtures/consonants-d-dh.tsv) covering each
  pattern, all supported vowels/aliases before and after it, following-vowel
  transitions, case distinctions, digits, boundaries, copied Unicode, and words.
  The initial reference check caught a word example requiring uppercase `O`:
  corrected `dokan` to `dOkan` for `দোকান`. Reference comparison then passed before
  Rust implementation. The first Rust run caught two word examples using the
  unsupported uppercase `A`; changed `dhAn`/`DAn` to `dhan`/`Dan` and reran both
  checks. All 1,249 final cases match the SHA-256-verified external pinned parser
  under Node.js v24.21.0. No upstream source, rules, or fixtures imported.
- Extended long-buffer and separate-call regressions and documented temporary
  limits for conjuncts, uppercase-`H` aliases, standalone `h`, and escapes.
  Updated [README.md](../README.md) and
  [v1.md](compatibility/foundations.md#basic-d-dh-d-and-dh-consonants) with Unicode, examples, current
  counts, and gaps. No dependencies, composition, or platform code added.
- Checks after correcting the examples: `cargo test --offline` passed (16
  regression tests and one documentation example);
  `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, and
  `cargo build --offline --release` passed. The reference comparison passed all
  1,249 cases and reported five remaining gap probes.
- Example: `cargo run --offline --example convert -- 'din dhan Dan Dhaka'`
  printed `দিন ধান ডান ঢাকা`; 20 direct CLI checks passed for new patterns,
  case distinctions, vowel signs, boundaries, words, and documented gaps.
  Reused inspected Rust/Cargo 1.99.1 and Node.js v24.21.0; no tools installed
  or upgraded. The cached external reference remained outside the repository.
- Documentation/tool checks: `node --check`, UTF-8 decoding, 101 local Markdown
  links/anchors across four documents, final newlines, trailing whitespace, and
  `git diff --check` passed. The pre-existing untracked `.vscode/` directory was
  left untouched.
- Limitations: `ddh`, `DDh`, `dr`, `dH`/`DH`, standalone `h`, remaining consonants,
  conjunct/reph forms, uppercase vowel aliases, punctuation/escapes, composition,
  and platform integration remain incomplete. No full compatibility,
  performance, or platform validation claimed.
- Next: add basic `l`/`h` for ল/হ as a separate consonant increment after checking
  reference behavior and interactions with existing two-key consonants.

### 2026-10-28 — Basic c/ch/j/jh consonants

- Added lowercase `c` → চ (U+099A), `ch` → ছ (U+099B), `j` → জ (U+099C), and
  `jh` → ঝ (U+099D). The existing longest-match rule handles `ch` and `jh` before
  single keys. All four establish consonant context for supported vowel signs.
  There are now 22 consonant input sequences producing 20 distinct letters.
- Authored 148 [fixtures](../tests/fixtures/consonants-c-ch-j-jh.tsv), checked
  against the pinned parser before Rust changes. Cases cover each pattern alone,
  all supported vowels/aliases before and after it, digits, boundaries, copied
  Unicode, and words. All 1,085 reference cases match with the SHA-256-verified
  external parser under Node.js v24.21.0. No upstream source, rules, or fixtures
  imported.
- Extended long-buffer and separate-call checks and recorded temporary limits
  for conjuncts, uppercase variants, standalone `h`, and escapes. Reference `Jh`
  produces জহ, distinct from `jh` → ঝ; no blanket case normalization added.
  Updated [README.md](../README.md) and
  [v1.md](compatibility/foundations.md#basic-c-ch-j-and-jh-consonants) with exact Unicode, current counts,
  examples, and remaining gaps. No dependencies or platform code added.
- Checks: `cargo test --offline` passed (15 regression tests and one documentation
  example); `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, and
  `cargo build --offline --release` passed. The reference comparison passed all
  1,085 cases and reported five remaining gap probes.
- Example: `cargo run --offline --example convert -- 'cabi chabi jani jhuri'`
  printed `চাবি ছাবি জানি ঝুরি`; 20 additional CLI checks passed for the new
  patterns, vowel signs, boundaries, words, and documented partial outputs.
  Reused inspected Rust/Cargo 1.99.1 and Node.js v24.21.0; no tools were installed
  or upgraded.
- Documentation/tool checks: `node --check`, UTF-8 decoding, 94 local Markdown
  links/anchors across four files, final newlines, trailing whitespace, and
  `git diff --check` passed. The pre-existing untracked `.vscode/` directory was
  left untouched.
- Limitations: `cc`, `cch`, `jjh`, `cr`, uppercase variants, standalone `h`,
  remaining consonants, conjunct/reph forms, punctuation/escapes, composition,
  and platform integration remain incomplete. No full compatibility or
  performance/platform validation claimed.
- Next: add basic `d`/`dh`/`D`/`Dh` for দ/ধ/ড/ঢ as a separate consonant increment.

### 2026-10-28 — Basic p/ph/f consonants

- Added lowercase `p` → প (U+09AA), and `ph`/`f` → ফ (U+09AB). The existing
  longest-match rule consumes `ph` before `p`; both spellings of ফ establish
  identical consonant context (`phi` and `fi` → `ফি`). There are now 18 consonant
  input sequences producing 16 distinct letters.
- Authored 115 [fixtures](../tests/fixtures/consonants-p-ph-f.tsv), checked against
  the pinned parser before Rust changes. Cases cover the three patterns with all
  supported vowels/aliases before and after them, digits, boundaries, copied
  Unicode, and words. All 937 reference cases match with the SHA-256-verified
  external parser under Node.js v24.21.0. No upstream source, rules, or fixtures
  imported.
- Extended long-buffer and separate-call checks and recorded temporary limits
  for uppercase aliases, conjuncts, overlapping `pph`, and interrupted/escaped
  input. Updated [README.md](../README.md) and
  [v1.md](compatibility/foundations.md#basic-p-ph-and-f-consonants) with exact Unicode, current counts,
  examples, and remaining gaps. No dependencies or platform code added.
- Checks: `cargo test --offline` passed (14 regression tests and one documentation
  example); `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, and
  `cargo build --offline --release` passed. The reference comparison passed all
  937 cases and reported five remaining gap probes.
- Example: `cargo run --offline --example convert -- 'pani phOn fOn'` printed
  `পানি ফোন ফোন`; 19 additional documented conversions passed direct CLI checks.
  Reused inspected Rust/Cargo 1.99.1 and Node.js v24.21.0; no tools were installed
  or upgraded.
- Documentation/tool checks: `node --check`, UTF-8 decoding, local Markdown links
  and heading anchors, final newlines, trailing whitespace, and `git diff --check`
  passed. The pre-existing untracked `.vscode/` directory was left untouched.
- Limitations: `pr`, `pp`, `pph`, uppercase `P`/`F` and other aliases, standalone
  `h`, remaining consonants, conjunct/reph forms, punctuation/escapes, composition,
  and platform integration remain incomplete. No full compatibility or
  performance/platform validation claimed.
- Next: add basic `c`/`ch`/`j`/`jh` for চ/ছ/জ/ঝ as a separate consonant increment.

### 2026-10-28 — Basic r/rr consonants

- Added `r` → র (U+09B0) and basic `rr` → রর (U+09B0 U+09B0). The longest
  consonant match selects `rr` before `r`; the existing three-key `rri` still
  takes precedence over either. There are now 15 consonant input sequences
  producing 14 distinct letters.
- Resolved the prior lowercase-run gaps: `rrri` → `রররি`, `rrrri` → `ররৃ`.
  `rrI` → `ররী` stays distinct from `rri` → `ঋ`. Added 115 independently authored
  [fixtures](../tests/fixtures/consonants-r.tsv), verified against the pinned
  parser before Rust changes. Cases cover vowels/aliases, overlapping/repeated
  runs, basic `r` before supported consonants, boundaries, Unicode, and words.
- All 822 reference cases match with the SHA-256-verified external parser under
  Node.js v24.21.0. Updated temporary-limit tests and documented remaining conjunct,
  reph, and uppercase-`R` gaps in [v1.md](compatibility/foundations.md#basic-r-and-rr-consonants).
  Extended long-buffer and separate-call checks; updated [README.md](../README.md).
  No upstream source, rules, fixtures, dependencies, or platform code imported.
- Checks: `cargo test --offline` passed (13 regression tests and one documentation
  example); `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, and
  `cargo build --offline --release` passed. The reference comparison passed all
  822 cases and reported five remaining gap probes.
- Example: `cargo run --offline --example convert -- 'ram rani rrri rrrri'` printed
  `রাম রানি রররি ররৃ`; 22 additional documented conversions passed direct CLI checks.
  Reused inspected Rust/Cargo 1.99.1 and Node.js v24.21.0; no tools were installed
  or upgraded.
- Documentation/tool checks: `node --check`, UTF-8 decoding, local Markdown links
  and heading anchors, final newlines, trailing whitespace, and `git diff --check`
  passed. The pre-existing untracked `.vscode/` directory was left untouched.
- Limitations: `kr`, `rrk`, bare `rrr`, and other contextual/conjunct/reph forms
  still differ from the reference. Uppercase `R`, other remaining consonants,
  uppercase aliases, punctuation/escapes, composition, and platform integration
  remain incomplete. No full compatibility or performance/platform validation
  claimed.
- Next: add basic `p`/`ph`/`f` for প/ফ as a separate consonant increment.

### 2026-10-28 — rri vowel group

- Added exact lowercase `rri` before individual consonants: independent ঋ
  (U+098B), or dependent ৃ (U+09C3) after a supported consonant. Retained final
  raw `i` context (`rria` → `ঋয়া`, `rrio` → `ঋও`). The principal forms for all
  11 basic vowels now exist, with broader context/alias compatibility still partial.
- Authored 84 [fixtures](../tests/fixtures/vowels-rri.tsv), verified against the
  pinned parser before Rust changes. They cover all 13 supported consonants,
  surrounding vowels/aliases, repetition, transitions, digits, boundaries, Unicode,
  and words. All 707 reference cases match with the SHA-256-verified external
  parser under Node.js v24.21.0. No upstream source, rules, or fixtures imported.
- Extra reference probes exposed longer-`r`-run behavior tied to the still-missing
  `r`/`rr` consonant matching. Documented current outputs (`rrri` → `rঋ`,
  `rrrri` → `rrঋ`) as gaps for the next increment rather than introducing a
  temporary vowel-boundary restriction. Added regressions that make these
  temporary limits, case variants, and literal backticks explicit.
- Extended boundary, separate-call, and long-buffer tests to `rri`. Updated
  [README.md](../README.md) and [v1.md](compatibility/foundations.md#seventh-vowel-group) for the implemented
  forms, exact Unicode, count, examples, and remaining gaps. No dependencies,
  composition controls, or platform code added.
- Checks: `cargo test --offline` passed (12 regression tests and one documentation
  example); `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, and
  `cargo build --offline --release` passed. The reference comparison passed all
  707 cases and reported five remaining gap probes.
- Example: `cargo run --offline --example convert -- 'rri krri krriti rriN'` printed
  `ঋ কৃ কৃতি ঋণ`; 14 additional documented conversions passed direct CLI checks.
  Reused inspected Rust/Cargo 1.99.1 and Node.js v24.21.0; no tools or dependencies
  were installed or upgraded.
- Documentation/tool checks: `node --check`, UTF-8 decoding, local Markdown links
  and heading anchors, final newlines, trailing whitespace, and `git diff --check`
  passed. The pre-existing untracked `.vscode/` directory was left untouched.
- Limitations: standalone `r`/`rr`, their case variants, other remaining consonants,
  uppercase `A`/`E`, contextual/conjunct rules, punctuation/escapes, composition,
  and platform integration remain incomplete. No full compatibility, performance,
  or platform validation claimed.
- Next: implement basic `r`/`rr` and resolve the overlapping lowercase runs.

### 2026-10-28 — OI/OU two-key vowel group

- Added exact uppercase `OI`/`OU` before single `O`: independent ঐ/ঔ
  (U+0990/U+0994), or dependent ৈ/ৌ (U+09C8/U+09CC) after a supported consonant.
  Case variants remain distinct (`OI` → `ঐ`, `Oi` → `ওই`). Retained the final raw
  key (`I`/`U`) in conversion context for following vowels, including `OIa` →
  `ঐয়া` and `OIo` → `ঐও`.
- Authored 150 [fixtures](../tests/fixtures/vowels-oi-ou.tsv) and verified expected
  output/code points against the pinned parser before Rust implementation. They
  cover both pairs after all 13 consonants, neighboring vowels/aliases, longer
  transitions, case variants, digits, boundaries, copied Unicode, and words.
  All 623 reference cases match using the SHA-256-verified external parser under
  Node.js v24.21.0. No upstream source, rules, or fixtures imported.
- Extended boundary, separate-call, long-buffer, and literal-backtick regressions
  to both pairs; removed their obsolete temporary-limit expectations. Updated
  [README.md](../README.md) and [v1.md](compatibility/foundations.md#sixth-vowel-group) with current
  behavior, exact Unicode, count, examples, and remaining gaps.
- Checks: `cargo test --offline` passed (11 regression tests and one documentation
  example); `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, and
  `cargo build --offline --release` passed. The reference comparison passed all
  623 cases and reported five remaining gap probes.
- Example: `cargo run --offline --example convert -- 'OI kOI OU kOU nOUka'` printed
  `ঐ কৈ ঔ কৌ নৌকা`; 19 additional documented conversions passed direct CLI checks.
  Reused inspected Rust/Cargo 1.99.1 and Node.js v24.21.0; no tools or dependencies
  were installed or upgraded.
- Documentation/tool checks: `node --check`, UTF-8 decoding, local Markdown links
  and heading anchors, final newlines, trailing whitespace, and `git diff --check`
  passed. The pre-existing untracked `.vscode/` directory was left untouched.
- Limitations: `rri`, uppercase `A`/`E`, remaining consonants, other phonetic
  sequences, conjuncts, punctuation/escapes, composition, and platform integration
  remain incomplete. No full compatibility, performance, or platform validation
  claimed.
- Next: add `rri` for the remaining basic vowel ঋ and its sign ৃ.

### 2026-10-28 — Contextual o/O and oo vowel group

- Added lowercase `o`: independent অ (U+0985), no added character immediately
  after a supported consonant, and ও (U+0993) after other supported raw vowel
  keys. Added uppercase `O`: independent ও or dependent ো (U+09CB). Added greedy
  `oo` as short `u`: independent উ or dependent ু (U+09C1).
- Context now keeps the raw vowel key, including `a` and the ends of repeated-key
  aliases: `ao` → `আও`, `eeo` → `ঈও`, `ooo` → `উঅ`. Even when `o` adds no character,
  it establishes vowel context (`koO` → `কও`, `koa` → `কয়া`). Context remains
  conversion-local; copied characters and digits reset it.
- Authored 156 [fixtures](../tests/fixtures/vowels-o.tsv), checked against the
  pinned parser before Rust implementation. They cover all 13 consonants with
  all three forms, neighboring vowels/aliases, longer runs, boundaries, Unicode,
  and words. All 473 reference cases match with the SHA-256-verified external
  parser under Node.js v24.21.0. No upstream source, rules, or fixtures imported.
- Extended boundary, separate-call, long-buffer, and literal-backtick regressions.
  Replaced the temporary `kemon` gap expectation with its reference-checked result
  `কেমন`. Kept the two-key vowels `OI`/`OU` explicitly incomplete for the next step.
- Updated [README.md](../README.md) and [v1.md](compatibility/foundations.md#fifth-vowel-group) with exact
  Unicode, raw-context behavior, examples, current count, and remaining gaps.
  No dependencies, composition controls, or platform code added.
- Checks: `cargo test --offline` passed (ten regression tests and one documentation
  example); `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, and
  `cargo build --offline --release` passed. The reference comparison passed all
  473 cases and reported five remaining gap probes.
- Example: `cargo run --offline --example convert -- 'tumi kemon tOmake'` printed
  `তুমি কেমন তোমাকে`; 18 additional documented conversions passed direct CLI checks.
  Reused inspected Rust/Cargo 1.99.1 and Node.js v24.21.0; no tools were installed
  or upgraded.
- Documentation/tool checks: `node --check`, UTF-8 decoding, local Markdown links
  and heading anchors, final newlines, trailing whitespace, and `git diff --check`
  passed. The pre-existing untracked `.vscode/` directory was left untouched.
- Limitations: `OI`/`OU`, uppercase `A`/`E`, other phonetic sequences, unsupported
  consonants, conjuncts, punctuation/escapes, composition, and platform integration
  remain incomplete. No full compatibility, performance, or platform validation
  claimed.
- Next: add the `OI`/`OU` two-key vowels after checking their reference behavior.

### 2026-10-28 — Contextual e and ee vowel group

- Added lowercase `e`: independent এ (U+098F), dependent ে (U+09C7) after a
  supported consonant. Added greedy `ee` matching as an alias for `I`: independent
  ঈ and dependent ী. An `a` after either form produces য়া with U+09DF, so
  `kea` → `কেয়া`, `keea` → `কীয়া`. Longer runs include `eee` → `ঈএ`.
- Authored 92 [fixtures](../tests/fixtures/vowels-e.tsv) for both sequences after
  all 13 supported consonants, neighboring vowels, longer runs, digits,
  boundaries, Unicode, and words. The initial reference check passed; Rust's
  first test run exposed an example outside this slice (`kemon` needs `o`).
  Replaced that example with `ami ke`, kept `o` explicitly unsupported, and
  rechecked the final set against the reference. All 317 cases match under
  Node.js v24.21.0, using the SHA-256-verified external parser.
- Extended boundary, separate-call, long-buffer, and literal-backtick regressions
  to `e`/`ee`. The two-key match advances only after an ASCII `ee` prefix, keeping
  UTF-8 boundaries intact. Existing consonant and vowel cases continue to pass.
- Updated [README.md](../README.md) and [v1.md](compatibility/foundations.md#fourth-vowel-group) with
  behavior, exact Unicode, examples, current fixture count, and remaining gaps.
  No dependencies, upstream source/rules/fixtures, or platform code imported.
- Checks after correcting the example: `cargo test --offline` passed (nine
  regression tests and one documentation example);
  `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, and
  `cargo build --offline --release` passed. The reference comparison passed all
  317 cases and reported five remaining gap probes.
- Example: `cargo run --offline --example convert -- 'ami ke kee'` printed
  `আমি কে কী`; 15 additional documented conversions passed direct CLI checks.
  Reused inspected Rust/Cargo 1.99.1 and Node.js v24.21.0; no tools were installed
  or upgraded.
- Documentation/tool checks: `node --check`, UTF-8 decoding, local Markdown links
  and heading anchors, final newlines, trailing whitespace, and `git diff --check`
  passed. The pre-existing untracked `.vscode/` directory was left untouched.
- Limitations: uppercase `A`/`E`, other vowels, unsupported consonants, conjuncts,
  phonetic punctuation/escapes, composition, and platform integration remain
  incomplete. No full compatibility, performance, or platform validation claimed.
- Next: add the `o`/`O` vowel group after checking the reference's context rules.

### 2026-10-28 — Uppercase I vowel group

- Added uppercase `I`: independent ঈ (U+0988), and dependent ী (U+09C0) after a
  supported consonant. Kept `i`/`I` distinct (`ki` → `কি`, `kI` → `কী`) and
  extended the existing following-`a` behavior (`kIa` → `কীয়া`, using U+09DF).
- Authored 52 [new fixtures](../tests/fixtures/vowels-i-long.tsv), covering `I`
  with all 13 supported consonants, vowel pairs and longer transitions, digits,
  boundaries, Unicode, and words. Expected output and code points were verified
  against the pinned parser before Rust implementation.
- Added the fixtures to both Rust and reference runners; all 225 cases match the
  SHA-256-verified external reference under Node.js v24.21.0. Extended boundary,
  separate-call, long-buffer, and literal-backtick regressions to `I`. Removed
  the obsolete temporary-limit expectation that uppercase `I` remains Latin.
- Updated [README.md](../README.md) and [v1.md](compatibility/foundations.md#third-vowel-group) for current
  behavior, exact Unicode, examples, count, and remaining gaps. No dependencies
  or upstream source, rules, or fixtures were imported.
- Checks: `cargo test --offline` passed (eight regression tests and one
  documentation example); `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, and
  `cargo build --offline --release` passed. The reference comparison passed all
  225 cases and reported five remaining gap probes.
- Example: `cargo run --offline --example convert -- 'ki kI nIti'` printed
  `কি কী নীতি`; nine additional documented conversions passed direct CLI checks.
  Reused inspected Rust/Cargo 1.99.1 and Node.js v24.21.0; no tools were installed
  or upgraded.
- Documentation/tool checks: `node --check`, UTF-8 decoding, local Markdown links
  and heading anchors, final newlines, trailing whitespace, and `git diff --check`
  passed. The pre-existing untracked `.vscode/` directory was left untouched.
- Limitations: uppercase `A`, remaining vowels, unsupported consonants, conjuncts,
  phonetic punctuation/escapes, composition, and platform integration remain
  incomplete. No full compatibility, performance, or platform validation claimed.
- Next: add the `e` vowel group after checking its context rules against the
  pinned reference.

### 2026-10-28 — Case-sensitive u/U vowel group

- Added `u`/`U`: independent উ/ঊ (U+0989/U+098A), and dependent ু/ূ
  (U+09C1/U+09C2) after supported consonants. Extended the existing `i` context so
  `a` after either new vowel also produces য়া: `kua` → `কুয়া`, `kUa` → `কূয়া`.
  Preserved case-sensitive spelling (`bhumi` → `ভুমি`, `bhUmi` → `ভূমি`).
- Authored 80 [new fixtures](../tests/fixtures/vowels-u.tsv), including both vowels
  after all 13 supported consonants, vowel pairs, transitions with `a`/`i`,
  repetition, digits, boundaries, Unicode, and words. Expected output/code points
  were checked against the pinned parser before implementing Rust changes.
- Extended the Rust and reference fixture runners: all 173 cases match the
  SHA-256-verified external jsAvroPhonetic parser under Node.js v24.21.0. No
  upstream code, rules, fixtures, runtime dependencies, or platform code imported.
- Extended boundary and per-call reset regressions to the new vowels. Updated
  temporary-limit tests now that `u` is supported, including literal backticks;
  the long-buffer correctness test now includes both `u`/`U` and a following `a`.
- Updated [README.md](../README.md) usage/status and
  [v1.md](compatibility/foundations.md#second-vowel-group) for the new behavior, exact Unicode, current
  fixture count, and remaining gaps. Previous slice descriptions remain historical.
- Checks: `cargo test --offline` passed (seven regression tests and one
  documentation example); `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, and
  `cargo build --offline --release` passed. The reference comparison passed all
  173 cases and reported five remaining gap probes.
- Example: `cargo run --offline --example convert -- 'tumi bhUmi kua'` printed
  `তুমি ভূমি কুয়া`; 11 additional documented conversions passed direct CLI checks.
  Reused inspected Rust/Cargo 1.99.1 and Node.js v24.21.0; no tools were installed
  or upgraded.
- Documentation/tool checks: `node --check`, UTF-8 decoding, local Markdown links
  and heading anchors, final newlines, trailing whitespace, and `git diff --check`
  passed. The pre-existing untracked `.vscode/` directory was left untouched.
- Limitations: uppercase `A`/`I`, other vowels, unsupported consonants, conjuncts,
  phonetic punctuation/escapes, composition, and platform integration remain
  incomplete. No full compatibility, performance, or platform validation claimed.
- Next: add uppercase `I` with its own reference cases and case-sensitive checks.

### 2026-10-28 — First contextual vowel group

- Added lowercase `a` and `i`: independent আ/ই, dependent া/ি after a supported
  consonant, and য়া after `i` (`kia` → `কিয়া`). Context uses matched input tokens
  during a single conversion; digits and unmatched characters reset it. Existing
  Bangla and other copied Unicode do not establish consonant context.
- Authored 66 new [vowel fixtures](../tests/fixtures/vowels.tsv) with exact Unicode
  sequences, and checked them against the pinned parser before implementing the
  Rust rules. The updated reference checker runs these plus the initial 27 cases:
  all 93 pass, using the SHA-256-verified external parser with Node.js v24.21.0.
  No upstream code, rules, or fixtures were added to the repository.
- Added regressions for vowel adjacency, all 13 supported consonants with both
  vowels, boundaries, mixed Unicode, and separate conversion calls. Updated
  earlier temporary-limit tests where `a` is now supported. Fixture readers now
  reject files with no cases, avoiding an empty fixture passing silently.
- Updated [README.md](../README.md) examples and [v1.md](compatibility/foundations.md#first-vowel-group)
  behavior/limits. Kept the original conversion-slice description as history,
  explicitly marking `a` and `ka` gaps as resolved by this increment.
- Checks: `cargo test --offline` passed (six regression tests and one documentation
  example); `cargo fmt --all -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`, and
  `cargo build --offline --release` passed. `node --check` passed; the reference
  comparison passed all 93 cases and reported five remaining gap probes.
- Example: `cargo run --offline --example convert -- 'ami khani kia'` printed
  `আমি খানি কিয়া`; six additional documented conversions passed direct CLI checks.
  Rust/Cargo 1.99.1 and Node.js v24.21.0 were inspected and reused; no dependencies
  or tools were installed.
- Documentation checks: UTF-8, local links/heading anchors, final newlines,
  trailing whitespace, and `git diff --check` passed. The pre-existing untracked
  `.vscode/` directory was left outside this step.
- Limitations: uppercase `A`/`I`, other vowels, unsupported-consonant context,
  conjuncts, punctuation conversion, and escapes remain incomplete. The precise
  reference sequence for inserted `য়` is U+09DF; no normalization is performed.
  Composition, platform support, and performance remain unvalidated.
- Next: implement `u`/`U` as the next small vowel group after reference checks.

### 2026-10-28 — First Rust conversion slice

- Added the `jong-bangla-core` library, Rust 2024 edition, with Rust/Cargo 1.99.1
  as the initially validated baseline. No external dependencies; unsafe code is
  forbidden. Added a terminal example and ignored Cargo's generated `target/`.
- Implemented all ten Bangla digits and 13 independently authored consonant
  sequences: `k`, `kh`, `g`, `gh`, `t`, `th`, `T`, `Th`, `n`, `N`, `b`, `bh`, `m`.
  Matching selects the longest supported sequence at each position. Unmatched
  characters pass through at valid UTF-8 boundaries; no input is retained/logged.
- Added 27 authored fixtures with explicit Unicode code points. All matched
  `OmicronLab.Avro.Phonetic.parse(input)` from the pinned reference, executed with
  Node.js v24.21.0. The parser and its license were downloaded into a temporary
  directory outside the repository; no upstream source/table/fixture was added
  to the project. The comparison tool verifies the parser's SHA-256 first.
- Documented reproducible build, example, and reference-comparison commands in
  [README.md](../README.md); recorded supported sequences and five observed gaps
  in [v1.md](compatibility/foundations.md#first-conversion-slice).
- Checks: `cargo fmt --all -- --check` passed after applying rustfmt;
  `cargo clippy --offline --all-targets -- -D warnings` passed;
  `cargo test --offline` passed (four regression tests and one documentation
  example); `cargo build --offline --release` passed. Regression coverage includes
  the 27 fixtures, empty input, mixed Unicode/combining marks, literal unsupported
  characters, temporary coverage limits, and a repeated long input buffer.
- Example checks: `cargo run --offline --example convert -- 'kh12T'` printed
  `খ১২ট`; three further direct example invocations matched expected output.
  Missing/extra arguments returned usage and exit status 2. `node --check` passed;
  the reference comparison passed all 27 cases and rejected a mismatched source
  file before evaluation. Five reference gap probes were recorded in v1.md.
- Documentation checks: UTF-8, local links/heading anchors, final newlines,
  trailing whitespace, and `git diff --check` passed. Rust 1.99.1 was rechecked
  against the official latest stable announcement; no tool installation occurred.
- Limitations: vowels, conjuncts, broader case handling, phonetic punctuation and
  escapes remain absent. Passing these examples does not establish arbitrary-word
  compatibility. The long-buffer test checks correctness, not performance.
  No composition/controller/platform tests or resource measurements have run.
- Next: implement the small vowel group described above, keeping this increment
  separate from composition and platform integration.

### 2026-10-28 — Phonetic reference and development tools

- Selected jsAvroPhonetic v1.1.4, commit
  `d3790172ebff92d43f0294bc51fed1fca7c80039`, as the deterministic conversion
  reference. Documented its scope, MPL-1.1 provenance, and comparison requirements
  in [v1.md](compatibility.md#phonetic-behavior-reference). No upstream source or data imported.
- Recorded the user's preference for the latest stable tools where practical in
  [AGENTS.md](../AGENTS.md). Continue explaining each small step before edits.
- Added the user's commit-per-step workflow: after checks and the progress update,
  commit each completed increment with a descriptive message and only its changes.
- Tools inspected: distro-provided `rustc 1.99.1`, `cargo 1.99.1`,
  `rustfmt 1.10.0`, and `clippy 0.1.99`. The official Rust
  [latest release announcement](https://blog.rust-lang.org/2026/10/15/Rust-1.99.1/)
  confirms 1.99.1 as current stable on the inspection date. `rustup` is absent;
  no tools were installed or upgraded. A minimum Rust version is not yet set.
- Reference checks: official OmicronLab project link, upstream Git tag identifiers,
  and pinned README/package metadata verified. Direct sandbox network access
  failed DNS resolution; approved read-only network commands verified the tag
  and metadata. Reference conversion has not been executed.
- Git checks: repository root and latest commit verified; working tree was clean
  before this documentation increment. Corrected the current status above.
- Documentation checks: local Markdown links and heading anchors, UTF-8 decoding,
  final newlines, and trailing whitespace passed across all four Markdown files;
  `git diff --check` passed. Reviewed the diff for requirement/status consistency.
- Limitations: no Rust library, executable conversion tests, compatibility result,
  performance result, or platform validation yet.
- Next: build the dependency-free Rust conversion slice, list supported sequences,
  compare authored fixtures with the reference, and document actual Cargo checks.

### 2026-10-28 — Initial project agreement

- Added [README.md](../README.md), [AGENTS.md](../AGENTS.md),
  [v1.md](v1.md), and the [MIT license](../LICENSE).
- Recorded a from-scratch Rust engine, Linux/Fcitx5 first, CachyOS + KDE Plasma
  on Wayland, editable phonetic composition, and Bangla digits by default.
- Confirmed two choices: converted Bangla first and the original Latin input
  second. Autocorrection remains separate future functionality.
- Clarified that Avro compatibility describes behavior; it does not mean copying
  an existing engine. No engine source has been added.
- Checks: local Markdown targets, UTF-8 decoding, final newlines, trailing
  whitespace, and presence of key confirmed requirements passed.
- Limitations: no executable code or platform tests; compatibility reference,
  detailed controls, and Rust/Fcitx5 interoperability remain unresolved.

### 2026-10-28 — Progress tracking

- Added this log and linked it from the README and contributor guide.
- Required future contributors to record completed changes, actual verification,
  limitations, and the next task after each small step.
- Defined the first implementation increment without starting application code.
- Checks: local Markdown targets, UTF-8 decoding, final newlines, and trailing
  whitespace passed across all project documentation.
- Limitations: documentation tracking only; Git history remains unavailable in
  the current workspace. No Rust or platform checks apply yet.
