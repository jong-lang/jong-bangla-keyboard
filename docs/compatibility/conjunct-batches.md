# Related conjunct batches

Historical compatibility evidence, grouped by rule family. The outputs, counts
and unresolved gaps below describe each dated implementation stage. Use the
[current requirements](../v1.md), [compatibility policy](../compatibility.md)
and regression fixtures for current behavior. These records do not form a bug
tracker. Other rule families are indexed in
[Historical conversion increments](../compatibility.md#historical-conversion-increments).

## G and nasal conjunct batch

Added on 2026-10-29: expanded the planned `gg`/`gN`/`NN`/`hN` batch to ten
exact spellings, plus following `r` after basic `h`/`n`/`N`. Independent checks
against the SHA-256-verified pinned parser established each spelling's exact
Unicode, vowel/ya context, following `r`, and overlapping matches before engine
changes. The related `gn`/`ghn`/`hn` and earlier `dg`/`dgh`/`Rg` matches fit this
batch because they determine which keys remain after the selected matches.
The basic attachment additions resolve exposed consonants in those overlaps.
No upstream code, rule tables, fixtures, or dependencies were imported.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `gg` | জ্ঞ | U+099C U+09CD U+099E |
| `gN` | গ্ণ | U+0997 U+09CD U+09A3 |
| `NN` | ণ্ণ | U+09A3 U+09CD U+09A3 |
| `hN` | হ্ণ | U+09B9 U+09CD U+09A3 |
| `gn` | গ্ন | U+0997 U+09CD U+09A8 |
| `ghn` | ঘ্ন | U+0998 U+09CD U+09A8 |
| `hn` | হ্ন | U+09B9 U+09CD U+09A8 |
| `dg` | দ্গ | U+09A6 U+09CD U+0997 |
| `dgh` | দ্ঘ | U+09A6 U+09CD U+0998 |
| `Rg` | ড়্গ | U+09DC U+09CD U+0997 |
| `gNgg` | গ্ণজ্ঞ | U+0997 U+09CD U+09A3 U+099C U+09CD U+099E |
| `ShNggr` | ষ্ণজ্ঞ্র | U+09B7 U+09CD U+09A3 U+099C U+09CD U+099E U+09CD U+09B0 |
| `kShNgghr` | ক্ষ্ণজ্ঞহ্র | U+0995 U+09CD U+09B7 U+09CD U+09A3 U+099C U+09CD U+099E U+09B9 U+09CD U+09B0 |
| `dghnr` | দ্ঘন্র | U+09A6 U+09CD U+0998 U+09A8 U+09CD U+09B0 |
| `Rghr` | ড়্গহ্র | U+09DC U+09CD U+0997 U+09B9 U+09CD U+09B0 |
| `ghnrri` | ঘ্নৃ | U+0998 U+09CD U+09A8 U+09C3 |
| `NNrry` | ণ্ণরর‍্য | U+09A3 U+09CD U+09A3 U+09B0 U+09B0 U+200D U+09CD U+09AF |

All ten establish consonant context for supported vowels and aliases, including
`ee`/`oo`, `OI`/`OU`, `rri`, and ya forms without U+200D. Longer `aZ`/`oZ`
retain priority. Single `r` attaches as ্র; two `r` keys normally add ্রর.
The existing exceptions remain: `rri` supplies ৃ, and `rry`/`rrZ` leave রর
followed by U+200D and ya-phala. Each spelling was checked independently with
one through eight `r` keys, vowels, `y`/`Z`/`Y`, `w`, and `x`. Basic `h`/`n`/`N`
share those rules (`hr nr Nr` → হ্র ন্র ণ্র; `hrri` → হৃ).

The original exact-spelling table matches before basic consonants, with longer
`dgh` before `dg` and `ghn` before basic `gh`. Existing nasal/k/Sh conjuncts
retain priority. Keys consumed by a match cannot begin a later match:
`dgn` → দ্গন, `dggh` → দ্গঘ, `Nggn` → ঙ্গন, and `Ngghn` → ঙ্ঘন.
`ggh` produces জ্ঞহ, while `Nggh` produces ঙ্ঘ. Earlier `ShN`/`kkhN`/`kShN`/`kxN`
consume `N`, leaving a separate `gg`/`ggh`; their following-`r` forms now match,
including the exposed basic `h` in `kShNgghr`. The earlier documented partial
outputs for `gNgg`/`NNgg`/`hNgg` and the `gN`/`NN`/`hN` + `gx`/`gk`/`gkh`/
`gkx`/`gkkh`/`gkSh` overlaps are superseded by this batch's checked fixtures.
They have moved out of the unsupported-rule regressions.

The 7,883 new authored fixtures are separate per spelling, preserving independent
expected outputs and exact Unicode. They cover preceding vowels/consonants,
existing matches, all ordered pairs within the ten-spelling batch, longer and
shared-key overlaps, vowel transitions, following `r`, repetition, all digits,
raw boundaries, copied Unicode, controls, and words. The three basic attachment
files add independent vowel/ya/r-run and boundary evidence. See the fixture links
in the [reference overview](../compatibility.md#phonetic-behavior-reference).
Rust regressions also check NUL/newline/tab boundaries, separate calls, and long
mixed Unicode input. Copied Bangla does not create phonetic context: `জ্ঞr` → জ্ঞর.

Investigative checks found earlier matches that require separate rule work:

| Input | Engine at that step | Reference |
| --- | --- | --- |
| `nghnr` | ংহ্ন্র | ঙ্ঘন্র |
| `ddghr` | দদ্ঘ্র | দ্দঘ্র |
| `mnry` | মন্র্য | ম্ন্র্য |
| `shn` | শন | শ্ন |
| `Gg` | Gগ | জ্ঞ |
| `gNG` | গ্ণG | গ্ণগ |

Those were gap regressions at that step. The [nasal/h batch](#nasal-and-h-conjunct-batch)
now resolves `nghnr` and `mnry`. Its reference probes also replace the resolved
`Shmmm`/`ShNmng`/`NgkShmr` with still-unsupported spellings. The planned
`ngh`/`nn`/`Nn`/`mn`/`hm`/`hl` investigation is completed below;
`dd`, other conjuncts and following-`r` forms, aliases, reph, punctuation/escapes,
composition, and Fcitx5 remain later work. No performance or platform claim is
made by these checks.

At that earlier step, all 24,253 authored cases matched the pinned reference.
Formatting, Clippy, 78 integration tests, 1 doctest, release build, and smoke
checks passed then; these are prior results, superseded by the batch below.

## Nasal and h conjunct batch

Added on 2026-10-29: twelve exact spellings, plus following `r` after basic
`m`/`l`. The planned `ngh`/`nn`/`Nn`/`mn`/`hm`/`hl` investigation expanded
to `nm`/`Nm`/`mm`/`ml`/`Ngm` because their nasal/m/l endings and consumed-key
interactions fit one reviewable batch. It also includes `gm`: earlier `NN`,
`gN`, `hN`, `ShN`, and k-conjuncts can consume `N`, exposing the `gm` in `Ngm`.
Each spelling was independently checked against the SHA-256-verified pinned
reference before implementation, including Unicode, vowel/ya context,
following `r`, preceding matches, all ordered batch pairs, and shared-key overlaps.
No upstream source, rule tables, fixtures, dependencies, or case normalization
were imported.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `ngh` | ঙ্ঘ | U+0999 U+09CD U+0998 |
| `nn` | ন্ন | U+09A8 U+09CD U+09A8 |
| `Nn` | ণ্ন | U+09A3 U+09CD U+09A8 |
| `mn` | ম্ন | U+09AE U+09CD U+09A8 |
| `hm` | হ্ম | U+09B9 U+09CD U+09AE |
| `hl` | হ্ল | U+09B9 U+09CD U+09B2 |
| `nm` | ন্ম | U+09A8 U+09CD U+09AE |
| `Nm` | ণ্ম | U+09A3 U+09CD U+09AE |
| `mm` | ম্ম | U+09AE U+09CD U+09AE |
| `ml` | ম্ল | U+09AE U+09CD U+09B2 |
| `Ngm` | ঙ্ম | U+0999 U+09CD U+09AE |
| `gm` | গ্ম | U+0997 U+09CD U+09AE |
| `mr` | ম্র | U+09AE U+09CD U+09B0 |
| `lr` | ল্র | U+09B2 U+09CD U+09B0 |
| `nng` | ন্নগ | U+09A8 U+09CD U+09A8 U+0997 |
| `mng` | ম্নগ | U+09AE U+09CD U+09A8 U+0997 |
| `ShNgm` | ষ্ণগ্ম | U+09B7 U+09CD U+09A3 U+0997 U+09CD U+09AE |
| `NgkShmr` | ঙ্ক্ষম্র | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09AE U+09CD U+09B0 |
| `ShNmng` | ষ্ণম্নগ | U+09B7 U+09CD U+09A3 U+09AE U+09CD U+09A8 U+0997 |

All twelve establish consonant context for supported vowels and aliases,
including `ee`/`oo`, `OI`/`OU`, `rri`, and ya without U+200D. Longer `aZ`/`oZ`
retain priority. A single following `r` attaches as ্র, including after `hl`/`ml`;
two `r` keys normally add ্রর. `rri` supplies ৃ, while `rry`/`rrZ` leave রর
followed by U+200D and ya-phala. One through eight `r` keys were independently
checked for every spelling and basic `m`/`l`, with vowels, `y`/`Z`/`Y`, `w`, and `x`.
Basic `mr`/`lr` share these rules (`mrri` → মৃ, `lrry` → লরর‍্য).

`ngh` matches before the shorter `ng` sign and its vowel forms. Other existing
priorities remain: `Nggh` consumes its `h` before an `hm`/`hl` can begin, and
`kkhN` consumes `N` before a later `Nn`/`Nm`/`Ngm` can begin. Consumed keys
cannot start another match: `nng` → ন্নগ, `mng` → ম্নগ, `Ngmm` → ঙ্মম,
`gnn` → গ্নন, and `Nggm` → ঙ্গম. Exposed `gm` now matches in `ShNgm` → ষ্ণগ্ম
and `kShNgmr` → ক্ষ্ণগ্ম্র. The `m` left by `NgkSh` now attaches following `r`.
This resolves the earlier partial outputs for `ngh`, `nng`, `hl`, `nghnr`,
`mnry`, `Shmmm`, `ShNmng`, `NgkShmr`, `ShNmr`, and `Shmmr`, as well as
`kkhmmm`/`kShmmm`/`kxmmm` and their exposed basic `m` attachment cases.
Those assertions have moved from gap regressions into passing fixtures.

The 11,350 new independently authored fixture rows are separate per spelling:
843 `ngh`, 856 `nn`, 855 `Nn`, 861 `mn`, 864 `hm`, 855 `hl`, 865 `nm`,
856 `Nm`, 860 `mm`, 859 `ml`, 869 `Ngm`, 858 `gm`, and 527/522 basic `m`/`l`
attachment cases. They cover supported vowels and aliases, ya, repeated `r`
and exceptions, existing matches in both orders, all ordered batch pairs,
shared-key overlaps, all digits, repetition, boundaries, copied Unicode,
and selected words. Rust regressions additionally check NUL/newline/tab,
every internal split in the three-key spellings, separate calls, and long
mixed Unicode. Copied Bangla resets context (`হ্মr` → হ্মর).

Investigation kept earlier `dd`, `shn`/`shm`, `bhl`/`phl`/`shl`/`vl`, case aliases
such as `Gm`, reph, and backtick escapes outside this batch. For example,
`ddghr` then gave দদ্ঘ্র rather than দ্দঘ্র; the later
[d/dh batch](#d-and-dh-conjunct-batch) resolves it. `bhl` remains ভল rather than ভ্ল.
Nine gap probes remained separate from passing reference fixtures. The planned
`dd`/`ddh`/`dhn`/`dhm`/`dm`/`dbh`/`dv` investigation is completed below. Composition and Fcitx5 remain later work; these correctness
checks do not establish full compatibility, performance, or platform support.

At that step, all 35,603 authored cases matched the pinned reference. Formatting,
Clippy, 93 integration tests, 1 doctest, release build, and smoke checks passed
then; these are prior results, superseded by the batch below.

## D and dh conjunct batch

Added on 2026-10-29: eight exact spellings, plus following `r` after basic
`d`/`dh`/`D`/`Dh`/`b`/`bh`/`v`. The planned seven-spelling d/dh batch also
includes doubled retroflex `DD`, whose Unicode and overlaps were checked
independently. The basic attachments handle consonants exposed after consumed
matches, including `dddhr`, `ddbhr`, and `DDDhr`. Each spelling was checked
independently against the SHA-256-verified pinned reference before implementation.
No upstream source, rule tables, fixtures, dependencies, or case normalization
were imported.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `ddh` | দ্ধ | U+09A6 U+09CD U+09A7 |
| `dd` | দ্দ | U+09A6 U+09CD U+09A6 |
| `dhn` | ধ্ন | U+09A7 U+09CD U+09A8 |
| `dhm` | ধ্ম | U+09A7 U+09CD U+09AE |
| `dm` | দ্ম | U+09A6 U+09CD U+09AE |
| `dbh` | দ্ভ | U+09A6 U+09CD U+09AD |
| `dv` | দ্ভ | U+09A6 U+09CD U+09AD |
| `DD` | ড্ড | U+09A1 U+09CD U+09A1 |
| `dr` | দ্র | U+09A6 U+09CD U+09B0 |
| `dhr` | ধ্র | U+09A7 U+09CD U+09B0 |
| `Dr` | ড্র | U+09A1 U+09CD U+09B0 |
| `Dhr` | ঢ্র | U+09A2 U+09CD U+09B0 |
| `br` | ব্র | U+09AC U+09CD U+09B0 |
| `bhr` | ভ্র | U+09AD U+09CD U+09B0 |
| `vr` | ভ্র | U+09AD U+09CD U+09B0 |
| `ddghr` | দ্দঘ্র | U+09A6 U+09CD U+09A6 U+0998 U+09CD U+09B0 |
| `dddh` | দ্দধ | U+09A6 U+09CD U+09A6 U+09A7 |
| `DDh` | ড্ডহ | U+09A1 U+09CD U+09A1 U+09B9 |
| `ddbhr` | দ্দভ্র | U+09A6 U+09CD U+09A6 U+09AD U+09CD U+09B0 |

All eight establish consonant context for supported vowels and aliases,
including `ee`/`oo`, `OI`/`OU`, `rri`, and ya without U+200D. Longer `aZ`/`oZ`
retain priority. A single following `r` attaches as ্র; two `r` keys normally
add ্রর. `rri` supplies ৃ, while `rry`/`rrZ` leave রর followed by U+200D
and ya-phala. One through eight `r` keys were independently checked for each
spelling and all seven basic attachments, with vowels, `y`/`Z`/`Y`, `w`, and `x`.
`dbh` and `dv` share output but have separate context and overlap evidence.
Retroflex `DD` stays distinct from `dd`, `Dd`, and `dD`.

Longer `ddh` wins before `dd`; `dhn`/`dhm` win before basic `dh`, and `dbh`
consumes `bh` as part of its conjunct. Existing `dg`/`dgh`, nasal, k, and Sh
matches retain priority. Consumed keys cannot start a new match: `dddh` → দ্দধ,
`ddhn` → দ্ধন, `ddhm` → দ্ধম, `ddbh` → দ্দভ, and `DDh` → ড্ডহ.
The exposed basic letters now attach `r`: `ddghr` → দ্দঘ্র, `dddhr` → দ্দধ্র,
`ddbhr` → দ্দভ্র, and `DDDhr` → ড্ডঢ্র. Earlier partial assertions for `ddh`,
`DDh`, `dr`, `vr`, and `ddghr` moved from gap regressions into passing fixtures.

The 11,687 new independently authored rows have separate fixtures per spelling:
961 `ddh`, 956 `dd`, 955 each `dhn`/`dhm`/`dm`, 958 each `dbh`/`dv`, and 957 `DD`.
Basic attachment fixtures add 576 each `d`/`dh`/`D`, 575 `Dh`, 577 `b`, and
576 each `bh`/`v`. They cover vowels/aliases and transitions, ya, one through
eight `r` keys and exceptions, existing matches in both orders, all ordered
batch pairs, shared-key overlaps, adjacent basic consonants, all digits,
repetition, boundaries, copied Unicode, and words (`buddhi`, `podmo`,
`udbhob`/`udvob`, `aDDa`, `brrikkho`). Rust regressions additionally check
NUL/newline/tab, every internal split, separate calls, and long mixed Unicode.
Copied Bangla resets context (`দ্দr` → দ্দর).

At that step, earlier nasal/b-prefixed matches remained gaps: `ndd` gave নদ্দ
rather than ন্দদ, and `bdd` gave বদ্দ rather than ব্দদ. The later
[nasal dental and retroflex batch](#nasal-dental-and-retroflex-conjunct-batch)
resolves `ndd`; the [remaining conjunct batch](#remaining-exact-conjunct-batch)
resolves `bdd` by consuming `bd` before the later `dd` can match. Case aliases such as `ddH`/`dHn`/`dV`,
`shn`/`shm`, `bhl`/`phl`/`shl`/`vl`, reph, and escapes remain outside this batch.
Nine gap probes remained separate from passing fixtures; resolved `ddghr` was
then replaced by `ndd`. Composition and Fcitx5 remain later work; these
correctness checks do not establish full compatibility, performance, or
platform support.

All 47,290 authored cases matched the pinned reference. Formatting, Clippy,
109 integration tests, 1 doctest, release build, and default/batch smoke checks
passed in this step; actual commands and limitations are in the [handoff](../progress.md).

## Nasal dental and retroflex conjunct batch

Added on 2026-10-29: all eleven planned exact spellings, plus following `r`
after basic `t`/`th`/`T`/`Th`. Case distinguishes the two consonant families;
each spelling has its own expected Unicode and context evidence against the
SHA-256-verified pinned parser. The basic attachments handle letters exposed
after earlier matches consume their nasal (`nntr`, `kShNThr`). No upstream
source, rule tables, fixtures, dependencies, or case normalization were imported.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `ndh` | ন্ধ | U+09A8 U+09CD U+09A7 |
| `nd` | ন্দ | U+09A8 U+09CD U+09A6 |
| `nD` | ন্ড | U+09A8 U+09CD U+09A1 |
| `NDh` | ণ্ঢ | U+09A3 U+09CD U+09A2 |
| `ND` | ণ্ড | U+09A3 U+09CD U+09A1 |
| `nth` | ন্থ | U+09A8 U+09CD U+09A5 |
| `nt` | ন্ত | U+09A8 U+09CD U+09A4 |
| `nTh` | ন্ঠ | U+09A8 U+09CD U+09A0 |
| `nT` | ন্ট | U+09A8 U+09CD U+099F |
| `NTh` | ণ্ঠ | U+09A3 U+09CD U+09A0 |
| `NT` | ণ্ট | U+09A3 U+09CD U+099F |

All eleven establish consonant context for supported vowels and aliases,
including `ee`/`oo`, `OI`/`OU`, `rri`, and ya without U+200D. Longer `aZ`/`oZ`
retain priority. A single following `r` attaches as ্র; two `r` keys normally
add ্রর. `rri` supplies ৃ, while `rry`/`rrZ` leave রর followed by U+200D
and ya-phala. One through eight `r` keys were independently checked for each
spelling and all four basic attachments, with vowels, `y`/`Z`/`Y`, `w`, and `x`.
For example, `ndrri` → ন্দৃ and `ntrry` → ন্তরর‍্য.

Longer `ndh`/`NDh`/`nth`/`nTh`/`NTh` win before their shorter forms. Exact
`nDh` is different: `nD` consumes `D`, leaving হ (`nDh` → ন্ডহ), while
`NDh` → ণ্ঢ. `Nd`/`Ndh`/`Nt`/`Nth` remain separate letters, without a
conjunct. These distinctions are passing fixtures, not case aliases.
Consumed keys cannot start another match: `ndd` → ন্দদ, `nddh` → ন্দধ,
`ndhn` → ন্ধন, `ndhm` → ন্ধম, `NDD` → ণ্ডড, and `ntth` → ন্তথ.
Earlier nasal matches retain priority: `nndh` → ন্নধ, `Nndd` → ণ্নদ্দ,
`mnddh` → ম্নদ্ধ, `gndd` → গ্নদ্দ, and `dhnddh` → ধ্নদ্ধ.
Earlier `ShN`/`kkhN`/`kShN`/`kxN` likewise consume `N` before it can
start a new conjunct. Basic attachments give `nntr` → ন্নত্র,
`ShNThr` → ষ্ণঠ্র, and `kShNThr` → ক্ষ্ণঠ্র.

The 15,555 new independently authored fixture rows have separate files per
spelling: 1,155 `ndh`, 1,135 `nd`, 1,164 `nD`, 1,129 `NDh`, 1,122 `ND`,
1,155 `nth`, 1,139 `nt`, 1,154 `nTh`, 1,140 `nT`, 1,136 `NTh`, and 1,122 `NT`.
Basic attachment fixtures add 751 each for `t`/`th`/`T`/`Th`.
They cover vowels/aliases and transitions, ya, one through eight `r` keys
and exceptions, existing matches in both orders, every ordered batch pair,
shared-key overlaps, adjacent basic consonants, all digits, repetition,
every internal split, boundaries, copied Unicode, and words (`anondo`, `bondhu`,
`grontho`, `ghonTa`/`ghoNTa`, `konTho`/`koNTho`). Rust regressions additionally
check NUL/newline/tab, separate calls at every split, and long mixed Unicode;
473 authored control/split and long-input expectations also match the reference.
Copied Bangla resets context (`ন্দr` → ন্দর).

Resolved `ndd` moved from a partial-output assertion into passing fixtures;
the reference gap probe now uses unresolved `bdd`. Nine probes remain separate
from supported fixtures. At that step, earlier b-prefixed rules, t-family conjuncts,
`shn`/`shm`/`bhl`/`phl`/`shl`/`vl`, uppercase aliases, reph, and escapes
remained gaps. The following batch adds six t-family spellings, with independent
priority and context evidence.
Composition and Fcitx5 remain later work; no full-compatibility, performance,
or platform milestone is claimed.

All 62,845 authored fixture cases matched the pinned reference. Formatting,
Clippy, 125 integration tests, 1 doctest, release build, default/batch smoke
checks, and documentation consistency checks passed in this step; actual
commands and limitations are in the [handoff](../progress.md).

## T-family conjunct batch

Added on 2026-10-29: six exact spellings, independently checked against the
SHA-256-verified pinned parser before implementation. The related `TT`/`Tm`
forms fit the same context and attachment behavior as `tt`/`tth`/`tn`/`tm`.
No new basic attachment was needed: `t`/`th`/`T`/`Th`/`n`/`m`/`h` already
attach following `r`. No upstream source, tables, fixtures, dependencies, or
case normalization were imported.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `tth` | ত্থ | U+09A4 U+09CD U+09A5 |
| `tt` | ত্ত | U+09A4 U+09CD U+09A4 |
| `tn` | ত্ন | U+09A4 U+09CD U+09A8 |
| `tm` | ত্ম | U+09A4 U+09CD U+09AE |
| `TT` | ট্ট | U+099F U+09CD U+099F |
| `Tm` | ট্ম | U+099F U+09CD U+09AE |

Each establishes consonant context for supported vowel signs and aliases,
including `ee`/`oo`, `OI`/`OU`, and `rri`, and ya without U+200D. Longer
`aZ`/`oZ` keep priority. A following `r` attaches as ্র; two `r` keys normally
add ্রর. `rri` supplies ৃ, while `rry`/`rrZ` leave রর plus U+200D and ya.
One through eight `r` keys were independently checked for every spelling,
with vowels, `y`/`Z`/`Y`, `w`, and `x`. Examples: `ttrri` → ত্তৃ,
`tthrry` → ত্থরর‍্য, `tnr` → ত্ন্র, and `Tmry` → ট্ম্র্য.

Longer `tth` wins before `tt`; there is no exact `TTh` form. `TT` consumes
both capitals and leaves `h`: `TTh` → ট্টহ, `TThn` → ট্টহ্ন. Case-distinct
`thn`/`thm`/`Tn`/`Thn`/`Thm` stay separate (থন/থম/টন/ঠন/ঠম), as do
`tT`/`Tt`/`tTh`/`Tth` and `tb`/`tv`/`tbh`. These controls are passing fixtures.
Consumed keys cannot start another conjunct: `ttth` → ত্তথ, `ttn` → ত্তন,
`tng` → ত্নগ, `tngh` → ত্নঘ, `tmn` → ত্মন, `TTm` → ট্টম. Earlier nasal stops
retain priority (`ntt` → ন্তত, `ntth` → ন্তথ, `ntn` → ন্তন, `nTm` → ন্টম).
Earlier consuming matches can expose a complete new form (`kShNTmr` → ক্ষ্ণট্ম্র).

The 8,130 new independently authored fixture rows have separate files:
1,366 `tth`, 1,357 `tt`, 1,359 `tn`, 1,358 `tm`, 1,344 `TT`, and 1,346 `Tm`.
They check exact Unicode, vowels and transitions, ya, `r` runs and exceptions,
existing matches in both orders, every ordered batch pair, shared-key overlaps,
adjacent basic consonants within the supported scope, all digits, repetition,
every internal split, boundaries, copied Unicode, and words (`uttor`, `utthan`,
`rotno`, `zotno`, `atma`, `paTTa`). Rust regressions also check NUL/newline/tab,
separate calls at every split, and long mixed Unicode. All 242 authored control,
split, separate-call, long-input, and gap expectations also matched the reference.
Copied Bangla resets context (`ত্তr` → ত্তর).

At that step, independent preceding-context checks exposed earlier `kt`/`kT`/`lT` gaps:
`ktm`/`kTm`/`lTm` then gave কত্ম/কট্ম/লট্ম, against reference
ক্তম/ক্টম/ল্টম. These earlier matches consume the initial `t`/`T` before the
new t-family spelling could match; they were kept separate from passing fixtures.
Three new reference probes and explicit partial-output regressions tracked them.
Twelve gap probes remained separate at that step. The following k-family batch
resolves `ktm`/`kTm`; `lTm` remains separate. Other conjuncts, case aliases,
reph, escapes, composition, and Fcitx5 remain later work.

All 70,975 authored fixture cases matched the pinned reference. Formatting,
Clippy, 132 integration tests, 1 doctest, release build, default/batch smoke
checks, and documentation consistency checks passed in this step; commands
and limitations are in the [handoff](../progress.md). No full-compatibility,
performance, composition, or platform milestone is claimed.

## K-family conjunct batch

Added on 2026-10-29: three exact spellings, independently checked against the
SHA-256-verified pinned parser before implementation. Initial candidates `kn`
and `km` are separate consonants in the reference, so they remain controls
rather than new conjunct rules. No basic following-`r` extension is needed:
`t`/`T`/`l`/`n`/`m` already attach it. No upstream source, rule tables, fixtures,
dependencies, or case normalization were imported.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `kt` | ক্ত | U+0995 U+09CD U+09A4 |
| `kT` | ক্ট | U+0995 U+09CD U+099F |
| `kl` | ক্ল | U+0995 U+09CD U+09B2 |
| `kn` (control) | কন | U+0995 U+09A8 |
| `km` (control) | কম | U+0995 U+09AE |

Each selected conjunct establishes consonant context for supported vowel signs
and aliases (`ee`/`oo`, `OI`/`OU`, `rri`) and ya without U+200D. Longer `aZ`/`oZ`
keep priority. A following `r` attaches as ্র; two `r` keys normally add ্রর.
`rri` supplies ৃ, while `rry`/`rrZ` leave রর plus U+200D and ya. One through
eight `r` keys were independently checked for each spelling with vowels,
`y`/`Z`/`Y`, `w`, and `x`. Examples: `ktrri` → ক্তৃ, `kTrry` → ক্টরর‍্য,
`klry` → ক্ল্র্য. Copied Bangla resets context (`ক্তr` → ক্তর).

There is no exact `kth`/`kTh` match: `kt`/`kT` consume both keys, leaving `h`
(`kth` → ক্তহ, `kThn` → ক্টহ্ন). Consumed keys cannot start another conjunct:
`ktm` → ক্তম, `kTm` → ক্টম, `ktn` → ক্তন, `ktth` → ক্তথ, `kTT` → ক্টট,
`klm` → ক্লম. Earlier `Ngk`/`kk` still consume their `k` before a new form
can start (`Ngkt` → ঙ্কত, `kkl` → ক্কল). Earlier matches can expose a complete
new spelling (`kShNktr` → ক্ষ্ণক্ত্র). The former `ktm`/`kTm` gap assertions
and probes move into passing fixtures.

The 6,408 new independently authored fixture rows are separate per spelling:
[1,443 `kt`](../../tests/fixtures/conjunct-kt.tsv),
[1,442 `kT`](../../tests/fixtures/conjunct-k-t-retroflex.tsv), and
[1,440 `kl`](../../tests/fixtures/conjunct-kl.tsv), plus
[2,083 controls](../../tests/fixtures/k-family-controls.tsv). Each conjunct has
independent Unicode, vowel/ya/context, `r` runs/exceptions, existing matches in
both orders, every ordered batch pair, shared-key overlaps, adjacent supported
basics, all digits, repetition, split boundaries, copied Unicode, and words
(`rokto`, `shokti`, `dokTor`, `klanto`, `klab`). Controls cover `kn`/`km`,
`kN`/`khn`/`khm`/`khl`, and limited `kS`/`ksh` behavior. The latter controls
excluded following `r`: basic `S`/`sh` attachment was outside that batch.
Rust regressions add NUL/newline/tab, separate calls at the internal split,
and long mixed Unicode. All 124 authored boundary, separate-call, long-input,
and reference-gap expectations also matched the pinned reference.

At that step, preceding-context checks exposed earlier `nk`/`lk`/`sk`/`Shk` gaps:

| Input | Prior partial engine output | Reference output |
| --- | --- | --- |
| `nkt` | নক্ত | ঙ্কত |
| `lkt` | লক্ত | ল্কত |
| `skt` | সক্ত | স্কত |
| `Shkt` | ষক্ত | ষ্কত |
| `nktm` | নক্তম | ঙ্কত্ম |
| `lktm` | লক্তম | ল্কত্ম |
| `sktm` | সক্তম | স্কত্ম |
| `Shktm` | ষক্তম | ষ্কত্ম |

The earlier matches consume `k` before the selected spelling; the remaining
`t` can then start `tm`. These gaps were explicit partial-output regressions,
separate from compatibility fixtures. Four probes replaced the two resolved
ones; fourteen reference gap probes remained. The consuming k-family batch
below resolves these conflicts, `ks`/`skl`, and basic `S`/`sh` attachment.
`lT`, uppercase aliases (including `Kt`/`KT`/`kL`), other conjuncts, reph,
and escapes remain incomplete.

All 77,383 authored fixture cases matched the pinned reference. Formatting,
Clippy, 137 integration tests, 1 doctest, release build, default/batch smoke
checks, and documentation consistency checks passed in this step; actual
commands are in the [handoff](../progress.md). No full-compatibility, performance,
composition, or platform milestone is claimed.

## Consuming k-family batch

Added on 2026-10-29: eight independently checked conjunct spellings, expanded
from the initial six to include longer `nkh`/`skh`. Two longer spellings,
`lkh`/`ksh`, preserve separate consonants before `lk`/`ks` could add a hasanta
(the Bangla mark joining the consonants). Basic `s`/`sh`/`S` now attach following
`r`, including consonants exposed after these matches. The initial per-spelling
context/priority expectations matched the SHA-256-verified pinned parser before
implementation; final coverage also incorporates resolved older gap assertions.
No upstream source, rule tables, fixtures, dependencies, or case normalization
were imported.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `nkh` | ঙ্খ | U+0999 U+09CD U+0996 |
| `nk` | ঙ্ক | U+0999 U+09CD U+0995 |
| `lkh` | লখ | U+09B2 U+0996 |
| `lk` | ল্ক | U+09B2 U+09CD U+0995 |
| `skl` | স্ক্ল | U+09B8 U+09CD U+0995 U+09CD U+09B2 |
| `skh` | স্খ | U+09B8 U+09CD U+0996 |
| `sk` | স্ক | U+09B8 U+09CD U+0995 |
| `Shk` | ষ্ক | U+09B7 U+09CD U+0995 |
| `ksh` | কশ | U+0995 U+09B6 |
| `ks` | ক্স | U+0995 U+09CD U+09B8 |
| `s` | স | U+09B8 |
| `sh` | শ | U+09B6 |
| `S` | শ | U+09B6 |

Each establishes consonant context for supported vowel signs and aliases,
including `ee`/`oo`, `OI`/`OU`, and `rri`, and ya without U+200D. Longer
`aZ`/`oZ` retain priority. A following `r` attaches as ্র; two normally add ্রর.
`rri` supplies ৃ, while `rry`/`rrZ` leave রর plus U+200D and ya. One through
eight `r` keys were independently checked for each spelling with vowels,
`y`/`Z`/`Y`, `w`, and `x`. Examples: `nkrri` → ঙ্কৃ, `lkrry` → ল্করর‍্য,
`skrrZ` → স্করর‍্য, `Shkry` → ষ্ক্র্য, `sklrri` → স্ক্লৃ, `ksry` → ক্স্র্য.
Basic `sr`/`shr`/`Sr` produce স্র/শ্র/শ্র; `srri`/`shrri`/`Srri` give সৃ/শৃ/শৃ.
Copied Bangla resets context (`স্ক্লr` → স্ক্লর).

Longer `nkh`/`skh`/`skl` precede `nk`/`sk`; `lkh`/`ksh` precede `lk`/`ks`.
The last two exceptions consume all three keys, preserving `lkhm` → লখম and
`kshm` → কশম. Consumed keys cannot start another conjunct: `nktm` → ঙ্কত্ম,
`lktm` → ল্কত্ম, `sktm` → স্কত্ম, `Shktm` → ষ্কত্ম; `nkkh` → ঙ্কখ,
`lkkh` → ল্কখ, `skkh` → স্কখ, `Shkkh` → ষ্কখ. `skkl` → স্কক্ল, while
`sklk` → স্ক্লক and `sklkh` → স্ক্লখ. Earlier consuming matches retain
priority (`mnk` → ম্নক, `tnkh` → ত্নখ, `NgkShk` → ঙ্ক্ষক). Exposed basic
`s`/`sh` now attach `r` (`nksr` → ঙ্কস্র, `ksshr` → ক্সশ্র).
`Nk`/`Sk`/`shk` remain separate (ণক/শক/শক); case aliases are not generalized.

The 21,794 new authored fixture rows preserve independent evidence per spelling:
1,717 `nkh`, 1,737 `nk`, 1,668 `lkh`, 1,687 `lk`, 1,731 each `skl`/`skh`,
1,750 `sk`, 1,779 `Shk`, 1,745 `ksh`, and 1,730 `ks`; 1,177/1,191/1,191
basic `s`/`sh`/`S` attachment cases; and 960 case controls. See the individual
fixture links in the [reference overview](../compatibility.md#phonetic-behavior-reference).
Each selected spelling checks Unicode, vowels/ya, `r` runs/exceptions, existing
matches in both orders, every ordered batch pair, shared-key overlaps, adjacent
supported consonants, digits, repetition, every internal split, boundaries,
copied Unicode, and words (`onko`, `shonkho`, `alko`, `skhalon`, `sklera`,
`shuShko`, `baks`). Old `n/l/s/Sh` + `kkhN`/`kShN`/`kxN` and
`kkhm`/`kShm`/`kxm` gap assertions now have passing independent expectations.
Rust tests add NUL/newline/tab, separate calls at every split, and long mixed
Unicode. All 545 authored control/separate-call/long-input/reference-gap
expectations also matched the pinned parser. Lowercase `sh` fixtures use a
distinct filename; all earlier fixture files, including uppercase `Sh`, remain
unchanged.

Independent preceding-context checks exposed earlier consuming rules outside
this batch. At that step they were explicit partial-output regressions, not passing fixtures:

| Input | Prior partial engine output | Reference output |
| --- | --- | --- |
| `pnk` | পঙ্ক | প্নক |
| `snk` | সঙ্ক | স্নক |
| `shnk` | শঙ্ক | শ্নক |
| `blk` | বল্ক | ব্লক |
| `glk` | গল্ক | গ্লক |
| `llk` | লল্ক | ল্লক |
| `slk` | সল্ক | স্লক |
| `nsk` | নস্ক | ন্সক |
| `psk` | পস্ক | প্সক |

These earlier matches consume `n`/`l`/`s` before a selected form can start.
At that step, `pl`/`bhl`/`phl`/`shl`/`vl` interactions were also outside the
supported matrix. Eight probes replaced four resolved probes; eighteen gap
probes remained. The l-ending batch below resolves `blk`/`glk`/`llk`/`slk`
and adds the proposed l-ending forms. `pn`/`sn`/`shn`, `ns`/`ps`, `lT`,
other conjuncts, uppercase aliases, reph, escapes, composition, and platform
support remain incomplete.

All 99,177 authored fixture cases matched the pinned parser. Formatting, Clippy,
152 integration tests, 1 doctest, release build, default/batch smoke checks, and
documentation consistency checks passed. The first full test run exposed stale
gap assertions; those verified outputs moved into passing fixtures before the
successful full rerun. Actual commands and limitations are in the
[handoff](../progress.md). No broader compatibility or performance claim is made.

## L-ending conjunct batch

Added on 2026-10-29: eleven exact spellings, expanded from the initial nine
candidates to include independently checked `fl` and `Sl`. All establish
consonant context and share the existing l-ending following-`r` behavior.
Basic `p`/`ph`/`f` now attach following `r`, covering consonants exposed after
each selected form. Every spelling's Unicode, vowels/context, `r` exceptions,
and priorities were checked independently against the SHA-256-verified pinned
parser before implementation. No upstream source, tables, fixtures,
dependencies, or case normalization were imported.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `gl` | গ্ল | U+0997 U+09CD U+09B2 |
| `ll` | ল্ল | U+09B2 U+09CD U+09B2 |
| `bl` | ব্ল | U+09AC U+09CD U+09B2 |
| `pl` | প্ল | U+09AA U+09CD U+09B2 |
| `sl` | স্ল | U+09B8 U+09CD U+09B2 |
| `shl` | শ্ল | U+09B6 U+09CD U+09B2 |
| `bhl` | ভ্ল | U+09AD U+09CD U+09B2 |
| `phl` | ফ্ল | U+09AB U+09CD U+09B2 |
| `vl` | ভ্ল | U+09AD U+09CD U+09B2 |
| `fl` | ফ্ল | U+09AB U+09CD U+09B2 |
| `Sl` | শ্ল | U+09B6 U+09CD U+09B2 |
| `p` | প | U+09AA |
| `ph` | ফ | U+09AB |
| `f` | ফ | U+09AB |
| `Shl` | ষল | U+09B7 U+09B2 |

`Sl` is an exact spelling; `Shl` remains ষল. Each selected form takes supported
vowel signs and aliases (`ee`/`oo`, `OI`/`OU`, `rri`) and ya without U+200D.
Longer `aZ`/`oZ` keep priority. A following `r` adds ্র, and two normally add ্রর.
`rri` gives ৃ; `rry`/`rrZ` leave রর plus U+200D and ya. One through eight `r`
keys were independently checked with vowels, `y`/`Z`/`Y`, `w`, and `x` for
every spelling. Examples: `glr` → গ্ল্র, `blrri` → ব্লৃ, `llrry` → ল্লরর‍্য,
`shlry` → শ্ল্র্য. Basic `pr`/`phr`/`fr` give প্র/ফ্র/ফ্র, with the same
exceptions, including after every new conjunct (`glpr` → গ্লপ্র).
Copied Bangla resets context (`গ্লr` → গ্লর).

Consumed final `l` cannot begin `lk`/`lkh`/`ll`/`lT`: `blk` → ব্লক,
`glkh` → গ্লখ, `llk` → ল্লক, `slk` → স্লক, `gll` → গ্লল,
`blTm` → ব্লট্ম. Earlier matches keep priority: `ggl` → জ্ঞল, `Nggl` → ঙ্গল,
`ngl` → ংল, `dgl` → দ্গল, `Rgl` → ড়্গল, `dbhl`/`dvl` → দ্ভল,
`ksl` → ক্সল, `kshl` → কশল, `skll` → স্ক্লল. `dbhl` consumes `dbh` before `bhl` can start, leaving `l`; a future `bb`
match in `bbhl` would leave `hl` instead.
`mpl` stays মপ্ল, even though `mp` alone is ম্প in the reference. The subsequent
m-prefix batch below preserves this longer nonconjunct exception. The batch
resolves the old `blk`/`glk`/`llk`/`slk`, `bhl`/`phl`/`shl`/`vl`, `pr`,
and `ll` partial-output assertions by moving them into passing fixtures.

The 34,704 new authored rows preserve independent evidence per spelling:
1,903 `gl`, 1,904 each `ll`/`bhl`, 1,889 each `bl`/`fl`, 1,882 `pl`,
1,897 `sl`, 1,911 `shl`, 1,890 `phl`, 1,896 `vl`, 1,910 `Sl`,
3,863 each basic `p`/`ph`/`f` attachment, and 2,240 nonconjunct controls.
See the individual links in the [reference overview](../compatibility.md#phonetic-behavior-reference).
Coverage includes independent Unicode, vowels/ya/context, `r` runs/exceptions,
existing forms in both orders, every ordered batch pair, shared-key overlaps,
adjacent consonants, digits, repetition, every internal split, boundaries,
copied Unicode, and words (`glani`, `ullas`, `blok`, `plabon`, `sloth`,
`shlOk`, `phlash`, `flash`, `SlOk`). Controls cover `Shl`/`ghl`/`khl`/`thl`/
`dhl`/`ql`/`zl` without inventing conjuncts. Rust regressions add NUL/newline/tab,
separate calls at every split, and long mixed Unicode. All 510 additional
authored boundary/separate-call/long-input/gap expectations also matched the
pinned parser. Earlier fixture files remain unchanged.

Preceding-context checks exposed twenty-five conflicts outside this batch.
At that step these were partial-output regressions, separate from passing fixtures:

| Input | Prior partial engine output | Reference output |
| --- | --- | --- |
| `Shfl` | ষফ্ল | ষ্ফল |
| `Shphl` | ষফ্ল | ষ্ফল |
| `Shpl` | ষপ্ল | ষ্পল |
| `bbhl` | বভ্ল | ব্বহ্ল |
| `bbl` | বব্ল | ব্বল |
| `lbhl` | লভ্ল | ল্ভল |
| `lbl` | লব্ল | ল্বল |
| `lgl` | লগ্ল | ল্গল |
| `lphl` | লফ্ল | লফল |
| `lpl` | লপ্ল | ল্পল |
| `lvl` | লভ্ল | ল্ভল |
| `mbhl` | মভ্ল | ম্ভল |
| `mbl` | মব্ল | ম্বল |
| `mfl` | মফ্ল | ম্ফল |
| `mphl` | মফ্ল | ম্ফল |
| `mvl` | মভ্ল | ম্ভল |
| `nshl` | নশ্ল | নশল |
| `nsl` | নস্ল | ন্সল |
| `pphl` | পফ্ল | প্পহ্ল |
| `ppl` | পপ্ল | প্পল |
| `pshl` | পশ্ল | পশল |
| `psl` | পস্ল | প্সল |
| `sfl` | সফ্ল | স্ফল |
| `sphl` | সফ্ল | স্ফল |
| `spl` | সপ্ল | স্প্ল |

They involve earlier labial matches (`mb`/`mbh`/`mv`, `mph`/`mf`,
`lb`/`lbh`/`lv`/`lp`/`lph`/`lg`, `sp`/`sph`/`sf`/`spl`, `Shp`/`Shph`/`Shf`,
`bb`/`pp`) and the existing `ns`/`ps` conflicts, including longer `nsh`/`psh`.
Seven resolved probes were removed and twenty-five added; thirty-six reference
gap probes remained at that step. The m-prefix and m-ending batch below
resolves `mbl`/`mbhl`/`mvl`/`mphl`/`mfl` and preserves `mpl`. Other consuming
labial families, `pn`/`sn`/`shn`, `ns`/`ps`, `lT`, uppercase aliases, reph,
escapes, composition, and platform support remain incomplete.

All 133,881 authored fixture cases matched the pinned parser. Formatting,
Clippy, 169 integration tests, 1 doctest, release build, default/batch smoke
checks, and documentation checks passed. Actual commands and limits are in the
[handoff](../progress.md). No broader compatibility or performance claim is made.

## M-prefix and m-ending conjunct batch

Added on 2026-10-29: six m-prefix conjunct spellings and the longer `mpl`
exception, expanded with four related m-ending spellings `lm`/`sm`/`shm`/`Sm`.
The latter consume `m` before the new m-prefix forms can start, so including
them resolves a coherent set of preceding-context conflicts. Each spelling's
exact Unicode, vowels/context, following `r`, exceptions, and priorities were
independently checked against the SHA-256-verified pinned parser before
implementation. The existing context and following-`r` helper are reused;
no additional basic attachment, dependency, case normalization, or imported
upstream source, rule table, or fixture is needed.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `mbh` | ম্ভ | U+09AE U+09CD U+09AD |
| `mb` | ম্ব | U+09AE U+09CD U+09AC |
| `mv` | ম্ভ | U+09AE U+09CD U+09AD |
| `mph` | ম্ফ | U+09AE U+09CD U+09AB |
| `mpl` | মপ্ল | U+09AE U+09AA U+09CD U+09B2 |
| `mp` | ম্প | U+09AE U+09CD U+09AA |
| `mf` | ম্ফ | U+09AE U+09CD U+09AB |
| `lm` | ল্ম | U+09B2 U+09CD U+09AE |
| `sm` | স্ম | U+09B8 U+09CD U+09AE |
| `shm` | শ্ম | U+09B6 U+09CD U+09AE |
| `Sm` | শ্ম | U+09B6 U+09CD U+09AE |

Longer `mbh` precedes `mb`, and `mph`/`mpl` precede `mp`. `mpl` keeps `m`
separate from `pl`: মপ্ল, not ম্পল. It is an exact longer match, preserving
`mplk` → মপ্লক, `mpll` → মপ্লল, `mplTm` → মপ্লট্ম. `mphl`/`mfl` are
ম্ফল; their final `h`/`f` has already been consumed before `hl`/`fl` could form.
`mbl` → ম্বল, `mbhl`/`mvl` → ম্ভল likewise preserve consuming priority.

Each selected spelling establishes consonant context for supported vowel
signs and aliases (`ee`/`oo`, `OI`/`OU`, `rri`), and ya without U+200D.
Longer `aZ`/`oZ` keep priority. Single `r` attaches as ্র; two normally add ্রর.
`rri` gives ৃ; `rry`/`rrZ` leave রর plus U+200D and ya. One through eight `r`
keys were independently checked per spelling with vowels, `y`/`Z`/`Y`, `w`,
and `x`. Examples: `mbrri` → ম্বৃ, `mbhrry` → ম্ভরর‍্য, `mvrrZ` → ম্ভরর‍্য,
`mpry` → ম্প্র্য, `mphrri` → ম্ফৃ, `mfrry` → ম্ফরর‍্য, `mplrrZ` → মপ্লরর‍্য,
`lmrri` → ল্মৃ, `smrry` → স্মরর‍্য, `shmrrZ` → শ্মরর‍্য, `Smry` → শ্ম্র্য.
Copied Bangla resets context (`ম্বr` → ম্বর).

Earlier `lm`/`sm`/`shm`/`Sm` consume `m`: `lmp`/`smp`/`shmp`/`Smp`
produce ল্মপ/স্মপ/শ্মপ/শ্মপ; `lmpl`/`smpl`/`shmpl`/`Smpl` leave a separate
`pl`. Existing m-ending forms also win (`Ngmb` → ঙ্মব, `dmb` → দ্মব,
`Shmpl` → ষ্মপ্ল, `kkhmp` → ক্ষ্মপ); `sklm` → স্ক্লম and `kshm` → কশম
retain earlier `skl`/`ksh` priority. Consumed keys can expose a complete
new form (`mbbl` → ম্বব্ল, `mppl` → ম্পপ্ল, `hmbl` → হ্মব্ল). Case remains
exact: `sm` is স্ম, `shm`/`Sm` are শ্ম, and existing `Shm` remains ষ্ম.
`ms`/`msh`/`mS`/`mSh`/`mh` stay separate (মস/মশ/মশ/মষ/মহ).

The 23,459 new authored rows have independent expectations per spelling:
2,000 `mbh`; 1,985 each `mb`/`mp`/`shm`; 1,984 each `mv`/`mf`/`lm`/`Sm`;
1,999 each `mph`/`mpl`; 1,970 `sm`; and 1,600 nonconjunct controls. See the
individual links in the [reference overview](../compatibility.md#phonetic-behavior-reference).
They cover exact Unicode, vowels/ya/context, `r` runs/exceptions, existing forms
in both orders, all ordered batch pairs, shared-key overlaps, adjacent basics,
digits, repetition, every internal split, boundaries, copied Unicode, and words
(`kombol`, `lomba`, `gombhir`, `arambho`, `omvor`, `sompod`, `kompo`, `lompho`,
`domf`, `mplani`, `almari`, `smarok`, `shmoshan`, `Smoshan`). These preserve
reference spellings without dictionary correction. All earlier fixture files
remain unchanged. Seven resolved partial-output assertions moved into passing
fixtures. Rust regressions add NUL/newline/tab, separate calls at every internal
split, and long mixed Unicode. All 427 additional authored boundary,
separate-call, long-input, and gap expectations also matched the pinned parser.

At that step, four preceding-context conflicts remained outside the batch,
with partial-output regressions rather than passing compatibility fixtures.
The [ns/ps batch](#consuming-ns-and-ps-batch) below resolves all four:

| Input | Partial engine output | Reference output |
| --- | --- | --- |
| `nsm` | নস্ম | ন্সম |
| `psm` | পস্ম | প্সম |
| `nshm` | নশ্ম | নশম |
| `pshm` | পশ্ম | পশম |

Earlier `ns`/`ps` and longer `nsh`/`psh` consume keys in the reference. Five
resolved probes were removed and these four added; thirty-five gap probes
remain. Uppercase aliases are a separate incomplete behavior: authored
partial-output regressions cover `mB`/`mP`/`mV`/`mF`, `mbH`/`mpH`, `Mbh`/`Mph`,
`Lm`, and `sHm`, with independently checked reference outputs. They are not
passing fixtures or new aliases. At that step, other conjuncts (including
`mth`), l/s/Sh labial families, `bb`/`pp`, `lT`, `pn`/`sn`/`shn`, reph, escapes,
composition, and platform support remained incomplete. The proposed next batch
was `lg`/`lb`/`lbh`/`lv`/`lp`/`lph`, optionally `lT`. The consuming l-prefix
batch below resolves those l-prefix gaps.

All 157,340 authored fixture cases matched the pinned parser. Formatting,
Clippy, 183 integration tests, 1 doctest, release build, default/batch smoke
checks, and documentation checks passed. Actual commands and limits are in the
[handoff](../progress.md). No broader compatibility or performance claim is made.

## Consuming l-prefix batch

Added on 2026-10-29: the six planned l-prefix spellings, expanded with the
longer `lgh` exception and independently checked `lT`/`lD`/`ldh`. These share
consuming priority over later g/l/labial/d/t-family matches. Each spelling's
Unicode, vowels/context, following `r`, and overlaps was independently checked
against the SHA-256-verified pinned parser before implementation. The existing
context and following-`r` helper are reused. No upstream source, rule tables,
fixtures, dependencies, or case normalization were imported.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `lgh` | লঘ | U+09B2 U+0998 |
| `lg` | ল্গ | U+09B2 U+09CD U+0997 |
| `lbh` | ল্ভ | U+09B2 U+09CD U+09AD |
| `lb` | ল্ব | U+09B2 U+09CD U+09AC |
| `lv` | ল্ভ | U+09B2 U+09CD U+09AD |
| `lph` | লফ | U+09B2 U+09AB |
| `lp` | ল্প | U+09B2 U+09CD U+09AA |
| `lT` | ল্ট | U+09B2 U+09CD U+099F |
| `lD` | ল্ড | U+09B2 U+09CD U+09A1 |
| `ldh` | ল্ধ | U+09B2 U+09CD U+09A7 |

Longer `lgh` and `lph` keep separate consonants before `lg`/`lp` could join
them, but consume all three keys: `lghl` → লঘল, `lghn` → লঘন,
`lphl` → লফল. `lbh` precedes `lb`. The final key cannot start another
conjunct: `lgl` → ল্গল, `lgg` → ল্গগ, `lgn` → ল্গন, `lgN` → ল্গণ,
`lgm` → ল্গম; `lbl` → ল্বল, `lbhl`/`lvl` → ল্ভল; `lpl` → ল্পল,
`lTm` → ল্টম, `lTh` → ল্টহ, `lDD` → ল্ডড, `lDh` → ল্ডহ,
`ldhn` → ল্ধন. This resolves the seven former partial-output regressions
`lgl`/`lbl`/`lbhl`/`lvl`/`lpl`/`lphl`/`lTm`.

Each spelling establishes consonant context for supported vowel signs and
aliases (`ee`/`oo`, `OI`/`OU`, `rri`), and ya without U+200D. Longer
`aZ`/`oZ` keep priority. Single `r` attaches as ্র; two normally add ্রর.
`rri` gives ৃ; `rry`/`rrZ` leave রর plus U+200D and ya. One through eight
`r` keys were independently checked per spelling with vowels, `y`/`Z`/`Y`,
`w`, and `x`. Examples: `lgrri` → ল্গৃ, `lbrry` → ল্বরর‍্য,
`lbhry` → ল্ভ্র্য, `lvrrZ` → ল্ভরর‍্য, `lprri` → ল্পৃ,
`lphrrZ` → লফরর‍্য, `lghrri` → লঘৃ, `lTry` → ল্ট্র্য,
`lDrri` → ল্ডৃ, `ldhrry` → ল্ধরর‍্য. Copied Bangla resets context
(`ল্গr` → ল্গর); the raw spelling alone establishes attachment.

Earlier l-ending matches still consume `l`: `blg` → ব্লগ, `glg` → গ্লগ,
`llg` → ল্লগ, `mlg` → ম্লগ, `klg` → ক্লগ, `phlg` → ফ্লগ;
`sklgl` → স্ক্লগ্ল exposes a complete `gl` after `skl`. Every supported
l-ending form was checked with every new spelling at both adjacent and shared
keys. Existing Ng/k/Sh/nasal/d/t/m families retain priority, including `mpl`.
Nonconjunct controls remain distinct: `lf` → লফ, `lfl` → লফ্ল,
`lt`/`lth`/`ld` → লত/লথ/লদ. `lDh` is ল্ডহ because `lD` consumes `D`
before `Dh` could form; `ldh` instead matches exactly as ল্ধ.

The 22,602 new authored fixture rows retain independent evidence per spelling:
2,109 each `lgh`/`lbh`/`lph`/`ldh`; 2,094 each `lg`/`lb`/`lv`/`lD`;
2,095 each `lp`/`lT`; and 1,600 controls. Individual fixture links are in the
[reference overview](../compatibility.md#phonetic-behavior-reference). Cases cover exact Unicode,
vowels/ya/context, `r` runs/exceptions, existing forms in both orders, all ordered
batch pairs, shared-key overlaps, adjacent consonants, digits, repetition,
every internal split, boundaries, copied Unicode, and words (`golpo`, `olpo`,
`ulTa`, `albam`, `alpha`). These are exact reference conversions without
dictionary correction. All earlier fixture files
remain unchanged. Rust regressions add NUL/newline/tab, separate calls at every
internal split, and long mixed Unicode. All 389 additional authored boundary,
separate-call, long-input, and alias-gap expectations matched the pinned parser.

Seven resolved gap probes were removed, leaving twenty-eight. Uppercase aliases
remain incomplete: partial-output regressions cover `lG`/`lgH`/`lB`/`lbH`/
`lV`/`lP`/`lpH`/`LT`/`lDH`/`ldH`, with independent reference expectations.
Other s/Sh labial families, `bb`/`pp`, `pn`/`sn`/`shn`, `ns`/`ps`, `mth`,
reph, escapes, composition, and platform support remain incomplete. Next
investigate `sp`/`sph`/`sf`/`spl` and `Shp`/`Shph`/`Shf`, including longer
forms and consuming overlaps, before confirming that batch's scope.

All 179,942 authored fixture cases matched the pinned parser. Formatting,
Clippy, 197 integration tests, 1 doctest, release and documentation builds,
default/batch smoke checks, and documentation consistency checks passed.
Actual commands and limits are in the [handoff](../progress.md). No broader
compatibility or performance claim is made.

## S and Sh labial conjunct batch

Added on 2026-10-29: all seven planned exact spellings, with each spelling's
Unicode, vowel/context behavior, following `r`, and overlapping matches checked
independently against the SHA-256-verified pinned parser before implementation.
The existing context and following-`r` helper are reused. No upstream source,
rule tables, fixtures, dependencies, or case normalization were imported.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `sp` | স্প | U+09B8 U+09CD U+09AA |
| `sph` | স্ফ | U+09B8 U+09CD U+09AB |
| `sf` | স্ফ | U+09B8 U+09CD U+09AB |
| `spl` | স্প্ল | U+09B8 U+09CD U+09AA U+09CD U+09B2 |
| `Shp` | ষ্প | U+09B7 U+09CD U+09AA |
| `Shph` | ষ্ফ | U+09B7 U+09CD U+09AB |
| `Shf` | ষ্ফ | U+09B7 U+09CD U+09AB |

Longer `sph`/`spl` and `Shph` match before `sp`/`Shp`. Only `spl` joins
and consumes the final `l`. The other forms consume their final `p`/`h`/`f`
before a following l-ending rule can reuse it: `sphl`/`sfl` → স্ফল,
`Shpl` → ষ্পল, `Shphl`/`Shfl` → ষ্ফল. These longer inputs do not need
extra rules; their `l` remains available for a complete subsequent match.
Thus `spll` → স্প্লল, while `sphll`/`sfll` → স্ফল্ল,
`Shpll` → ষ্পল্ল, and `Shphll`/`Shfll` → ষ্ফল্ল.
Similarly `splm` → স্প্লম and `splg` → স্প্লগ, whereas
`sphlm` → স্ফল্ম and `Shplg` → ষ্পল্গ.

Every spelling establishes consonant context for supported vowel signs and
aliases (`ee`/`oo`, `OI`/`OU`, `rri`), and ya without U+200D. Longer
`aZ`/`oZ` keep priority. Single `r` attaches as ্র; two normally add ্রর.
`rri` gives ৃ; `rry`/`rrZ` leave রর plus U+200D and ya. One through eight
`r` keys were independently checked per spelling with vowels, `y`/`Z`/`Y`,
`w`, and `x`. Examples: `sprri` → স্পৃ, `sphrry` → স্ফরর‍্য,
`sfrrZ` → স্ফরর‍্য, `splry` → স্প্ল্র্য, `Shprri` → ষ্পৃ,
`Shphrry` → ষ্ফরর‍্য, `Shfry` → ষ্ফ্র্য. Copied Bangla resets
context (`স্পr` → স্পর); only matched raw keys establish attachment.

Earlier Ng/k/Sh/nasal/d/t/l/m-family matches keep their keys. In particular
`ks`/`kSh`/`NgkSh` consume shared s/Sh before a labial match could begin:
`ksp` → ক্সপ, `ksph`/`ksf` → ক্সফ, `kspl` → ক্সপ্ল,
`kShp` → ক্ষপ, `kShph`/`kShf` → ক্ষফ, `NgkShp` → ঙ্ক্ষপ.
Complete fresh matches still work after a consumed key (`sppl` → স্পপ্ল,
`spllg` → স্প্লল্গ). Case-sensitive controls `Sp`/`Sph`/`Sf` and
`shp`/`shph`/`shf` stay separate as শপ/শফ/শফ, with their own independent
context evidence. Equal output does not make the spellings interchangeable.

The 17,703 new authored fixture rows retain independent evidence per spelling:
2,175 each `sph`/`spl`, 2,163 `sp`, 2,160 `sf`, 2,204 `Shph`, 2,192 `Shp`,
2,189 `Shf`, and 2,445 controls. Individual links are in the
[reference overview](../compatibility.md#phonetic-behavior-reference). Cases cover exact Unicode,
vowels/ya/context, `r` runs/exceptions, existing forms in both orders, all ordered
batch pairs, shared-key overlaps, digits, every internal split, boundaries,
copied Unicode, repetition, and words (`sphulingo`, `sfUron`, `puShpo`,
`niShphol`, `niShfol`). These are exact reference conversions without dictionary
correction. All earlier fixture files remain unchanged. Rust regressions add
NUL/newline/tab, separate calls at every internal split, and long mixed Unicode.
All 315 additional authored boundary, separate-call, long-input, and gap
expectations matched the pinned parser.

The six former partial-output assertions and reference gap probes for
`spl`/`sphl`/`sfl`/`Shpl`/`Shphl`/`Shfl` moved into passing coverage,
leaving twenty-two probes. This resolves the earlier sections' s/Sh labial
limits. At that step, earlier `ns`/`ps` consumed s differently in the reference:
partial `nsp`/`psp` → নস্প/পস্প versus reference ন্সপ/প্সপ. Explicit
partial-output regressions retain these and `nsph`/`nsf`/`nspl`/`psph`/`psf`/
`pspl`, with independent reference expectations. These gaps are now resolved
by the [ns/ps batch](#consuming-ns-and-ps-batch). Uppercase aliases (`sP`,
`sF`, `sPh`, `spH`, `sPL`, `SHp`, `ShP`, `ShPh`, `ShpH`, `SHph`, `SHf`,
`ShF`), `bb`/`pp`, `pn`/`sn`/`shn`/`Sn`, other conjuncts, reph, escapes,
composition, and platform support remain incomplete. Next investigate
`bb`/`pp` and `pn`/`sn`/`shn`/`Sn`, including longer priorities and shared
keys, before confirming that batch's scope.

All 197,645 authored fixture cases matched the pinned parser. Formatting,
Clippy, 207 integration tests, 1 doctest, release and documentation builds,
and default/batch smoke checks passed. Actual commands and limits are in the
[handoff](../progress.md). No broader compatibility or performance claim is made.

## Repetition and n-ending conjunct batch

Added on 2026-10-29: the six planned exact spellings, with each spelling's
Unicode, vowel/context behavior, following `r`, and overlapping matches checked
independently against the SHA-256-verified pinned parser before implementation.
The existing consonant context and following-`r` helper are reused. No upstream
source, rule tables, fixtures, dependencies, or case normalization were imported.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `bb` | ব্ব | U+09AC U+09CD U+09AC |
| `pp` | প্প | U+09AA U+09CD U+09AA |
| `pn` | প্ন | U+09AA U+09CD U+09A8 |
| `sn` | স্ন | U+09B8 U+09CD U+09A8 |
| `shn` | শ্ন | U+09B6 U+09CD U+09A8 |
| `Sn` | শ্ন | U+09B6 U+09CD U+09A8 |

`bb`/`pp` consume both raw keys: their second `b`/`p` cannot start a later
`bh`/`ph`/`bl`/`pl` match. Thus `bbh`/`pph` → ব্বহ/প্পহ,
`bbl`/`ppl` → ব্বল/প্পল, and `bbhl`/`pphl` → ব্বহ্ল/প্পহ্ল.
No extra longer rules are needed. Following `h`/`l` stays available for fresh
matches: `bbhm` → ব্বহ্ম, `pphn` → প্পহ্ন, `bblg` → ব্বল্গ,
`pplm` → প্পল্ম. Repetition remains consuming: `bbb` → ব্বব and
`pppp` → প্পপ্প. A fresh complete match still works (`bbbh` → ব্বভ).

`pn`/`sn`/`shn`/`Sn` consume `n` before `nk`/`nkh`/`ngh`/`nn`/`nm` and
nasal dental/retroflex matches can reuse it. Consequently `pnk` → প্নক,
`snkh` → স্নখ, `shnn` → শ্নন, and `Snm` → শ্নম. Fresh later keys
can start those matches (`pnnk` → প্নঙ্ক, `snnkh` → স্নঙ্খ,
`shnngh` → শ্নঙ্ঘ, `Snnm` → শ্নন্ম). All four longer families were
checked independently; equal `shn`/`Sn` output does not imply normalization.
Controls `pN`/`sN`/`shN`/`SN`/`Shn` remain separate as পণ/সণ/শণ/শণ/ষন,
with their own context evidence. Existing `ShN` remains ষ্ণ.

Every selected spelling establishes consonant context for supported vowel
signs and aliases (`ee`/`oo`, `OI`/`OU`, `rri`), and ya without U+200D.
Longer `aZ`/`oZ` retain priority. Single `r` attaches as ্র; two normally add
্রর. `rri` supplies ৃ, while `rry`/`rrZ` leave রর plus U+200D and ya.
One through eight `r` keys were checked independently for every spelling with
vowels, `y`/`Z`/`Y`, `w`, and `x`. Examples: `bbrri` → ব্বৃ,
`pprry` → প্পরর‍্য, `pnrry` → প্নরর‍্য, `snrrZ` → স্নরর‍্য,
`shnry` → শ্ন্র্য, `Snry` → শ্ন্র্য. Copied Bangla resets context
(`প্নr` → প্নর); only matched raw keys establish attachment.

Earlier matches keep their consumed keys: `mbb` → ম্বব, `lbb` → ল্বব,
`spp` → স্পপ, `Shpp` → ষ্পপ, `mpn` → ম্পন, `lpn` → ল্পন,
`ppn` → প্পন, `spn` → স্পন, `Shpn` → ষ্পন, `ksn` → ক্সন,
and `kshn` → কশন. Longer complete tokens retain their priority
(`sphn` → স্ফন, `spln` → স্প্লন). Every existing Ng/k/Sh/nasal/d/t/l/m/s-labial
family and every ordered pair in this batch were independently checked in both
directions, including shared-key overlaps and fresh matches after consumed keys.

The 16,028 new authored fixture rows preserve independent evidence per spelling:
2,236 each `bb`/`pp`, 2,240 each `pn`/`Sn`, 2,227 `sn`, 2,241 `shn`,
and 2,608 controls. Individual links are in the
[reference overview](../compatibility.md#phonetic-behavior-reference). Cases cover exact Unicode,
vowels/ya/context, `r` runs/exceptions, longer forms, existing families in both
orders, all ordered batch pairs, shared keys, digits, every internal split,
boundaries, copied Unicode, repetition, and words (`abbas`, `dhappa`, `shopno`,
`snan`, `sneho`, `proshno`, `proSno`). These are exact reference conversions,
without dictionary spelling correction (`shopno` → শপ্ন). All earlier fixture
files remain unchanged. Rust regressions also cover NUL/newline/tab, separate
calls at every internal split, and long mixed Unicode. All 232 extra authored
boundary, separate-call, long-input, and gap expectations matched the parser.

Ten resolved partial-output assertions moved into passing coverage, including
`bbhl`/`bbl`/`pphl`/`ppl`, `pnk`/`snk`/`shnk`, `pp`/`pph`, and `shn`.
Seven resolved reference gap probes were removed; four new probes independently
tracked the then-remaining earlier `ns`/`ps` conflicts (`nsn`/`nshn`/`psn`/`pshn`),
leaving nineteen probes. Their partial engine output is নস্ন/নশ্ন/পস্ন/পশ্ন,
against reference ন্সন/নশন/প্সন/পশন. Uppercase aliases (`bB`, `Bb`, `BB`,
`bbH`, `pP`, `Pp`, `PP`, `ppH`, `Pn`, `sHn`, `SHn`), other conjuncts,
`mth`, reph, escapes, composition, platform integration, and performance
validation remain incomplete. This batch resolves the earlier sections'
`bb`/`pp` and `pn`/`sn`/`shn`/`Sn` limits. The next proposed batch was `ns`/`ps`
with longer `nsh`/`psh` exceptions; the section below resolves those gaps.

All 213,673 authored fixture rows matched the pinned parser. Formatting,
Clippy, 216 integration tests, 1 doctest, release and documentation builds,
and default/batch smoke checks passed. Actual commands and limits are in the
[handoff](../progress.md). No broader compatibility or performance claim is made.

## Consuming ns and ps batch

Added on 2026-10-29: all four planned exact spellings, independently checked
against the SHA-256-verified pinned parser before implementation. Longer forms
were investigated with h/n/k/l/m/labial overlaps; no further longer rules were
needed. The scanner reuses consonant context and the following-`r` helper.
No upstream source, rule tables, fixtures, dependencies, or normalization were
imported.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `ns` | ন্স | U+09A8 U+09CD U+09B8 |
| `nsh` | নশ | U+09A8 U+09B6 |
| `ps` | প্স | U+09AA U+09CD U+09B8 |
| `psh` | পশ | U+09AA U+09B6 |

Longer `nsh`/`psh` win over `ns`/`ps`, consume all three keys, and produce
separate consonants without a virama (U+09CD). Both shorter forms consume `s`
before s-family rules can reuse it: `nsk` → ন্সক, `psl` → প্সল,
`nsm` → ন্সম, `psp` → প্সপ, `nsn` → ন্সন. The longer exceptions also
consume `h`: `nshl` → নশল, `pshm` → পশম, `nshn` → নশন,
`pshN` → পশণ. Their `h` cannot start `hl`/`hm`/`hn`/`hN`.
Fresh following keys remain available (`nssn` → ন্সস্ন, `pssm` → প্সস্ম,
`nshhl` → নশহ্ল, `pshhm` → পশহ্ম). All four spellings have independent
longer-form and shared-key evidence; equal output from other spellings does
not imply normalization. Controls `nS`/`nSh`/`pS`/`pSh` remain নশ/নষ/পশ/পষ.

Each spelling establishes consonant context for supported vowel signs and
aliases (`ee`/`oo`, `OI`/`OU`, `rri`), and ya without U+200D. Longer `aZ`/`oZ`
keep their priority. Single `r` attaches as ্র; two normally add ্রর.
`rri` supplies ৃ, while `rry`/`rrZ` leave রর plus U+200D and ya. One through
eight `r` keys were checked independently per spelling with vowels, `y`/`Z`/`Y`,
`w`, and `x`. Examples: `nsrri` → ন্সৃ, `nshrri` → নশৃ,
`psrry` → প্সরর‍্য, `pshrrZ` → পশরর‍্য. Copied Bangla resets context
(`ন্সa` → ন্সআ); only matched raw keys establish attachment.

Earlier matches keep their keys: `nns` → ন্নস, `pnsh` → প্নশ,
`snsh` → স্নশ, `shnsh` → শ্নশ, `Sns` → শ্নস, `pps` → প্পস,
`sps` → স্পস, `Shps` → ষ্পস, `mps` → ম্পস, `lps` → ল্পস.
Every existing Ng/k/Sh/nasal/d/t/l/m/s-labial/repetition/n-ending family and all
ordered batch pairs were checked in both directions, including shared keys.

The 11,096 new authored fixture rows preserve independent evidence per spelling:
2,300 each `ns`/`nsh`/`ps`/`psh`, and 1,896 controls. Links are in the
[reference overview](../compatibility.md#phonetic-behavior-reference). Cases cover exact Unicode,
vowels/ya/context, `r` runs/exceptions, longer forms, existing families in both
orders, ordered pairs, shared keys, digits, every internal split, boundaries,
copied Unicode, repetition, and words (`mansik`, `lipsa`, `ipsito`). Outputs
follow the reference without dictionary spelling correction. Earlier fixture
files remain unchanged. Rust regressions add NUL/newline/tab, separate calls
at every internal split, explicit priorities, and long mixed Unicode. All 157
extra authored boundary, separate-call, and long-input expectations matched
the pinned parser.

Twenty-two resolved partial-output assertions moved into passing coverage.
Fourteen resolved reference gap probes were removed, leaving five. This batch
resolves the earlier sections' ns/ps and longer nsh/psh limits. Uppercase aliases,
other conjuncts (including `mth` and s/Sh dental/retroflex stop forms), reph,
escapes, composition, platform integration, and performance validation remained
incomplete at that step. The next proposed batch was `st`/`sth`/`sT`/`ShT`/
`ShTh`/`sht`/`St`; the section below resolves those stop forms.

All 224,769 authored fixture rows matched the pinned parser. Formatting,
Clippy, 222 integration tests, 1 doctest, release and documentation builds,
and default/batch smoke checks passed. Actual commands and limits are in the
[handoff](../progress.md). No broader compatibility or performance claim is made.

## S and Sh stop conjunct batch

Added on 2026-10-29: all seven proposed exact spellings, independently checked
against the SHA-256-verified pinned parser before implementation. Longer h forms
and t/T overlaps were investigated together. The scanner reuses consonant
context and the following-`r` helper. No upstream source, rule tables, fixtures,
dependencies, or normalization were imported.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `st` | স্ত | U+09B8 U+09CD U+09A4 |
| `sth` | স্থ | U+09B8 U+09CD U+09A5 |
| `sT` | স্ট | U+09B8 U+09CD U+099F |
| `ShT` | ষ্ট | U+09B7 U+09CD U+099F |
| `ShTh` | ষ্ঠ | U+09B7 U+09CD U+09A0 |
| `sht` | শ্ত | U+09B6 U+09CD U+09A4 |
| `St` | শ্ত | U+09B6 U+09CD U+09A4 |

Longer `sth`/`ShTh` win over `st`/`ShT` and consume `h`: `sthm` → স্থম,
`ShThm` → ষ্ঠম. By contrast, `sTh` → স্টহ, `shth` → শ্তহ, and `Sth` → শ্তহ
leave `h` available for a fresh rule (`sThm` → স্টহ্ম, `shthm` → শ্তহ্ম,
`Sthm` → শ্তহ্ম). No extra longer mapping is needed for these three forms.
Following fresh `h` stays available after every complete match (`sthhl` → স্থহ্ল,
`ShThhn` → ষ্ঠহ্ন). Equal output for `sht`/`St` does not imply case folding.
Controls `shT`/`ST` → শট, `shTh`/`STh` → শঠ, and `Shth` → ষথ remain
separate basic consonants, each with independent context and following-r checks.

Consumed `t`/`T` cannot begin a later t-family match: `stn` → স্তন,
`stm` → স্তম, `stt` → স্তত, `stth` → স্তথ, `sTm` → স্টম,
`ShTm` → ষ্টম, `ShTT` → ষ্টট, `ShTTh` → ষ্টঠ. Fresh later keys
can (`sttn` → স্তত্ন, `sttm` → স্তত্ম, `ShTTm` → ষ্টট্ম). All seven
spellings have independent consuming, longer-form, and shared-key evidence.

Each spelling establishes consonant context for supported vowel signs and
aliases (`ee`/`oo`, `OI`/`OU`, `rri`), and ya without U+200D. Longer `aZ`/`oZ`
keep their priority. Single `r` attaches as ্র; two normally add ্রর.
`rri` supplies ৃ, while `rry`/`rrZ` leave রর plus U+200D and ya. One through
eight `r` keys were checked independently per spelling with vowels, `y`/`Z`/`Y`,
`w`, and `x`. Examples: `strri` → স্তৃ, `sthrry` → স্থরর‍্য,
`sTrrZ` → স্টরর‍্য, `ShThry` → ষ্ঠ্র্য, `shtrri` → শ্তৃ,
`Strry` → শ্তরর‍্য. Copied Bangla resets context (`স্থa` → স্থআ);
only matched raw keys establish attachment.

Earlier matches keep their keys: `kst` → ক্সত, `ksth` → ক্সথ,
`ksht` → কশত, `nst` → ন্সত, `nsth` → ন্সথ, `nsht` → নশত,
`pst` → প্সত, `psth` → প্সথ, `psht` → পশত. In contrast, `kSt` → কশ্ত,
`nSt` → নশ্ত, `pSt` → পশ্ত: no earlier exact kS/nS/pS match consumes `S`.
Existing `kSh`/`NgkSh` also win (`kShT` → ক্ষট, `NgkShTh` → ঙ্ক্ষঠ).
Every existing Ng/k/Sh/nasal/d/t/l/m/s-labial/repetition/n-ending/ns-ps family
and all ordered batch pairs were checked in both directions, including shared keys.

The 20,090 new authored fixture rows preserve independent evidence per spelling:
2,377 each `sth`/`ShT`, 2,362 each `st`/`sT`, 2,391 `ShTh`, 2,376 `sht`,
2,361 `St`, and 3,484 controls. Links are in the
[reference overview](../compatibility.md#phonetic-behavior-reference). Cases cover exact Unicode,
vowels/ya/context, r runs/exceptions, longer forms, existing families in both
orders, ordered pairs, shared keys, digits, every internal split, boundaries,
copied Unicode, repetition, and words (`rasta`, `astha`, `sthir`, `sTeshon`,
`koShTo`, `niShTha`, `proshtho`, `proStho`). Outputs follow the reference
without dictionary spelling correction (`proshtho` → প্রশ্তহ). Earlier fixture
files remain unchanged. Rust regressions add NUL/newline/tab, separate calls
at every internal split, explicit priorities, and long mixed Unicode. All 287
extra authored boundary, separate-call, and long-input expectations matched
the pinned parser.

Two resolved partial-output assertions (`st`/`ShT`) moved into passing coverage;
the five existing reference gap probes remain. This batch resolves the earlier
sections' s/Sh stop limits. At that step, other conjuncts (including `mth` and b/p stop forms),
uppercase aliases, reph, escapes, composition, platform integration, and
performance validation remain incomplete. The next proposed batch investigates
`pt`/`pT`/`bd`/`bdh`/`bj`, including longer priorities and shared keys; its exact
scope had not been confirmed. The later [remaining conjunct batch](#remaining-exact-conjunct-batch)
implements those five candidates together with the other 20 identified spellings.

All 244,859 authored fixture rows matched the pinned parser. Formatting,
Clippy, 232 integration tests, 1 doctest, release and documentation builds,
and default/batch smoke checks passed. Actual commands and limits are in the
[handoff](../progress.md). No broader compatibility or performance claim is made.

## Remaining exact conjunct batch

Added on 2026-10-29 at the user's request: implement all 25 conjunct spellings
identified by the standalone gap audit in one coherent batch. Scope includes
the associated following-`r` behavior for basic `c`/`ch`/`j`/`jh`, needed to
exercise consumed and fresh c/j/h keys. Uppercase aliases, reph, punctuation,
escapes, composition, adapters, and packaging remain separate work.

Every spelling below was independently checked against the SHA-256-verified
pinned parser before implementation: exact Unicode, supported vowels and ya,
preceding context, following r runs and exceptions, longer matches, and overlaps.
Equal outputs for nasal or s/Sh spellings do not establish shared behavior.
The fixtures, mappings, and tests are independently authored under MIT; no
upstream source, rule tables, fixtures, dependencies, or normalization were imported.

| Input | Output | Exact Unicode | Fixture rows |
| --- | --- | --- | --- |
| `pt` | প্ত | U+09AA U+09CD U+09A4 | [3548](../../tests/fixtures/conjunct-completion-pt.tsv) |
| `pT` | প্ট | U+09AA U+09CD U+099F | [3548](../../tests/fixtures/conjunct-completion-p-retroflex-t.tsv) |
| `bdh` | ব্ধ | U+09AC U+09CD U+09A7 | [3561](../../tests/fixtures/conjunct-completion-bdh.tsv) |
| `bd` | ব্দ | U+09AC U+09CD U+09A6 | [3548](../../tests/fixtures/conjunct-completion-bd.tsv) |
| `bj` | ব্জ | U+09AC U+09CD U+099C | [3548](../../tests/fixtures/conjunct-completion-bj.tsv) |
| `cNG` | চ্ঞ | U+099A U+09CD U+099E | [3523](../../tests/fixtures/conjunct-completion-c-nya.tsv) |
| `cch` | চ্ছ | U+099A U+09CD U+099B | [3561](../../tests/fixtures/conjunct-completion-cch.tsv) |
| `cc` | চ্চ | U+099A U+09CD U+099A | [3540](../../tests/fixtures/conjunct-completion-cc.tsv) |
| `gdh` | গ্ধ | U+0997 U+09CD U+09A7 | [3561](../../tests/fixtures/conjunct-completion-gdh.tsv) |
| `jjh` | জ্ঝ | U+099C U+09CD U+099D | [3561](../../tests/fixtures/conjunct-completion-jjh.tsv) |
| `jNG` | জ্ঞ | U+099C U+09CD U+099E | [3528](../../tests/fixtures/conjunct-completion-j-nya.tsv) |
| `jj` | জ্জ | U+099C U+09CD U+099C | [3540](../../tests/fixtures/conjunct-completion-jj.tsv) |
| `mth` | ম্থ | U+09AE U+09CD U+09A5 | [3561](../../tests/fixtures/conjunct-completion-mth.tsv) |
| `NGch` | ঞ্ছ | U+099E U+09CD U+099B | [3505](../../tests/fixtures/conjunct-completion-nya-ch.tsv) |
| `NGjh` | ঞ্ঝ | U+099E U+09CD U+099D | [3505](../../tests/fixtures/conjunct-completion-nya-jh.tsv) |
| `NGc` | ঞ্চ | U+099E U+09CD U+099A | [3492](../../tests/fixtures/conjunct-completion-nya-c.tsv) |
| `NGj` | ঞ্জ | U+099E U+09CD U+099C | [3492](../../tests/fixtures/conjunct-completion-nya-j.tsv) |
| `nch` | ঞ্ছ | U+099E U+09CD U+099B | [3561](../../tests/fixtures/conjunct-completion-nch.tsv) |
| `njh` | ঞ্ঝ | U+099E U+09CD U+099D | [3561](../../tests/fixtures/conjunct-completion-njh.tsv) |
| `nj` | ঞ্জ | U+099E U+09CD U+099C | [3548](../../tests/fixtures/conjunct-completion-nj.tsv) |
| `nc` | ঞ্চ | U+099E U+09CD U+099A | [3548](../../tests/fixtures/conjunct-completion-nc.tsv) |
| `shch` | শ্ছ | U+09B6 U+09CD U+099B | [3574](../../tests/fixtures/conjunct-completion-sh-ch.tsv) |
| `Sch` | শ্ছ | U+09B6 U+09CD U+099B | [3561](../../tests/fixtures/conjunct-completion-s-uppercase-ch.tsv) |
| `shc` | শ্চ | U+09B6 U+09CD U+099A | [3561](../../tests/fixtures/conjunct-completion-sh-c.tsv) |
| `Sc` | শ্চ | U+09B6 U+09CD U+099A | [3548](../../tests/fixtures/conjunct-completion-s-uppercase-c.tsv) |

The remaining fixture files independently cover basic
[`c` following r](../../tests/fixtures/conjunct-completion-c-following-r.tsv),
[`ch` following r](../../tests/fixtures/conjunct-completion-ch-following-r.tsv),
[`j` following r](../../tests/fixtures/conjunct-completion-j-following-r.tsv),
[`jh` following r](../../tests/fixtures/conjunct-completion-jh-following-r.tsv), and
[longer forms, case controls, and words](../../tests/fixtures/conjunct-completion-controls.tsv).
Together the 30 files contain **108,815** new rows. All 244,859 earlier fixture
rows remain unchanged. Seven resolved partial-output assertions (`bdd`, `NGc`,
`NGch`, `cc`, `cch`, `jjh`, `cr`) moved into passing reference coverage.

Longer `bdh`/`cch`/`jjh`/`NGch`/`NGjh`/`nch`/`njh`/`shch`/`Sch`
consume h before their shorter matches. That h cannot start `hm`/`hl`/`hn`/`hN`:
`bdhm` → ব্ধম, `cchm` → চ্ছম, `NGchm` → ঞ্ছম, `shchm` → শ্ছম.
In contrast, no longer `pth`/`pTh`/`bjh` match consumes h:
`pthm` → প্তহ্ম, `pThm` → প্টহ্ম, `bjhm` → ব্জহ্ম.
Fresh later keys can form conjuncts (`bdhhn` → ব্ধহ্ন).
The new `bd` consumes d before a later `dd` (`bdd` → ব্দদ).
Similarly, `ccNG` → চ্চঞ and `jjNG` → জ্জঞ; a consumed c/j cannot
start the new `cNG`/`jNG` match. Fresh keys can (`cNGcNG` → চ্ঞচ্ঞ).

Existing families retain priority, including nasal, k, l, m, s/Sh stops,
labials, repetitions, n-ending forms and ns/ps exceptions. For example,
`pnch` → প্নছ while `pnnch` → প্নঞ্ছ; `ksch` → ক্সছ,
`kshch` → কশছ, `nshch` → নশছ. Fixtures check both orders and
all ordered pairs of the new spellings, plus shared keys with existing families.
`sc`/`sch` and `Shc`/`Shch` stay separate basic consonants;
`Nc`/`Nch`/`Nj`/`Njh` do not inherit lowercase-n conjunct behavior.

All 25 matches establish consonant context for vowel signs, vowel aliases,
and ya without U+200D. Single r attaches as ্র; two normally add ্রর.
`rri` supplies ৃ; `rry`/`rrZ` keep রর plus U+200D and ya. One through
eight r keys were independently checked per spelling with vowels and y/Z/Y/w/x.
Examples: `bjrri` → ব্জৃ, `cchrry` → চ্ছরর‍্য, `NGchry` → ঞ্ছ্র্য.
The final raw G of exact `cNG`/`jNG` allows attachment (`cNGr` → চ্ঞ্র),
without enabling standalone G. Basic `cr`/`chr`/`jr`/`jhr` → চ্র/ছ্র/জ্র/ঝ্র
also have separate context and overlap evidence.

Fixtures include digits, copied Unicode, separators, repetitions, every internal
split compatible with current aliases, and words such as `gupto`, `shobdo`,
`iccha`, `jNGan`, `ponjika`, and `nishcoy`. Rust regressions additionally
check NUL/newline/tab, every internal split (including exposed-G partial outputs),
separate calls, and long mixed Unicode. All **1,084** additional authored
supported boundary, split, separate-call, priority, and long-input expectations
matched the pinned parser. No spelling correction was added (`sapta` → সাপ্তা,
`labdho` → লাব্ধ).

Coverage limits remain explicit. Earlier matches can expose standalone uppercase
G (`ShNGch` currently gives ষ্ণGছ instead of ষ্ণগছ), as can splitting
`cNG` after N. These are alias gaps, with separate partial-output assertions;
they are excluded from supported reference fixtures. Existing following-r gaps
after `q`/`z`/`R`/`Rh`, reph, vowel-context edges, punctuation, and escapes
remained separate work at that step. The later
[following-r batch](case-symbols-reph.md#following-r-after-q-z-r-and-rh) resolves `cchqr` → চ্ছক্র.
Resolved `bdd` was replaced by uppercase `Gdh` in the five reference gap probes.

The standalone audit was rerun over 288 distinct reference pattern spellings
plus 14 additional uppercase letters (302 distinct inputs). All 25 selected
conjunct spellings now match. The remaining **52** standalone discrepancies
are the previously identified 27 uppercase/alternate spellings and 25
punctuation/symbol/escape spellings. This count excludes context interactions
and is not a full compatibility percentage or a guaranteed implementation count.
Next, investigate case handling before fixing an uppercase/alternate spelling
batch; do not infer blanket case folding from shared outputs.

All **353,674** authored fixture rows matched the pinned parser. Formatting,
Clippy, **265 integration tests**, 1 doctest, release and documentation builds,
and default/batch smoke checks passed. Actual commands and remaining limits
are in the [handoff](../progress.md). Composition, Fcitx5, platform support, and
performance milestones remain unimplemented or unverified.
