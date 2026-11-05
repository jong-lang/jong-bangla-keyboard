# Exact nasal, k and Sh conjuncts

Historical compatibility evidence, grouped by rule family. The outputs, counts
and unresolved gaps below describe each dated implementation stage. Use the
[current requirements](../v1.md), [compatibility policy](../compatibility.md)
and regression fixtures for current behavior. These records do not form a bug
tracker. Other rule families are indexed in
[Historical conversion increments](../compatibility.md#historical-conversion-increments).

## Exact Ngx conjunct

Added on 2026-10-28: exact `Ngx` produces ঙ্ষ (U+0999 U+09CD U+09B7),
matching before basic `Ng` and single `N`. This is an added conjunct sequence;
the inventory of 40 basic consonant sequences producing 35 letters is unchanged.
It establishes consonant context without a joiner and shares the existing
following-`r` priority of `x`/`kx`.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `Ngx` | ঙ্ষ | U+0999 U+09CD U+09B7 |
| `Ngxa` | ঙ্ষা | U+0999 U+09CD U+09B7 U+09BE |
| `Ngxi` | ঙ্ষি | U+0999 U+09CD U+09B7 U+09BF |
| `Ngxee` | ঙ্ষী | U+0999 U+09CD U+09B7 U+09C0 |
| `Ngxrri` | ঙ্ষৃ | U+0999 U+09CD U+09B7 U+09C3 |
| `Ngxr` | ঙ্ষর | U+0999 U+09CD U+09B7 U+09B0 |
| `Ngxrr` | ঙ্ষ্রর | U+0999 U+09CD U+09B7 U+09CD U+09B0 U+09B0 |
| `Ngxrrri` | ঙ্ষ্রররি | U+0999 U+09CD U+09B7 U+09CD U+09B0 U+09B0 U+09B0 U+09BF |
| `Ngxrrrri` | ঙ্ষ্ররৃ | U+0999 U+09CD U+09B7 U+09CD U+09B0 U+09B0 U+09C3 |
| `Ngxry` / `NgxrZ` | ঙ্ষর‍্য | U+0999 U+09CD U+09B7 U+09B0 U+200D U+09CD U+09AF |
| `Ngxrry` / `NgxrrZ` | ঙ্ষরর‍্য | U+0999 U+09CD U+09B7 U+09B0 U+09B0 U+200D U+09CD U+09AF |
| `Ngxy` / `NgxZ` | ঙ্ষ্য | U+0999 U+09CD U+09B7 U+09CD U+09AF |
| `NgxY` | ঙ্ষয় | U+0999 U+09CD U+09B7 U+09DF |

All supported vowel signs and aliases apply (`NgxOI` → `ঙ্ষৈ`,
`Ngxoo` → `ঙ্ষু`), with existing transitions (`Ngxia` → `ঙ্ষিয়া`).
Longer `aZ`/`oZ` keep priority at the following position (`NgxaZ` → `ঙ্ষঅ্যা`).
Two following `r` keys normally add ্রর before matching the rest. Existing
`rri` and `rry`/`rrZ` retain priority; single `r` stays separate and adds
U+200D before `y`/`Z`. Repetitions and adjacency follow raw matching:
`NgxNgx` → `ঙ্ষঙ্ষ`, `Ngxx` → `ঙ্ষক্স`, `Ngxkx` → `ঙ্ষক্ষ`.
Existing case distinctions remain: `NGx` → `ঞক্স`, `ngx` → `ংক্স`.
No normalization, spelling correction, or persistent state is added.

The 322 independently authored [fixtures](../../tests/fixtures/conjunct-ngx.tsv)
were checked against the SHA-256-verified pinned parser before implementation.
They cover supported vowels/aliases on either side, following transitions,
selected preceding consonants, adjacency, one through eight following `r`
keys, `rri`/`rry`/`rrZ` exceptions, repetition, raw-spelling controls, digits,
boundaries, and copied Unicode. All 6,165 reference cases match. Digits and
copied characters reset context (`Ngx1a` → `ঙ্ষ১আ`, `Ngx🙂a` → `ঙ্ষ🙂আ`)
and prevent matches across boundaries (`Ng🙂x` → `ঙ🙂এক্স`).
Copied decomposed য় stays U+09AF U+09BC. Separate calls share no state;
Rust regressions also cover control characters and long mixed input.
No performance result claimed.

The initial reference comparison identified five preceding contexts where an
earlier longer match consumes the `N` before `Ngx` can match. Those contexts
are excluded from the supported fixtures and kept as explicit partial-output
regressions, pending their own conjunct work:

| Input | Engine at that step | Reference |
| --- | --- | --- |
| `gNgx` | গঙ্ষ | গ্ণগক্স |
| `NNgx` | ণঙ্ষ | ণ্ণগক্স |
| `hNgx` | হঙ্ষ | হ্ণগক্স |
| `ShNgx` (resolved below) | ষঙ্ষ | ষ্ণগক্স |
| `kxNgx` (resolved below) | ক্ষঙ্ষ | ক্ষ্ণগক্স |

For example, the reference consumes `gN` first in `gNgx`; the trailing `gx`
then produces গক্স. Implementing exact `Ngx` alone cannot establish compatibility
for these inputs. Uppercase aliases, reph, and escapes also remain incomplete:

| Input | Engine at that step | Reference |
| --- | --- | --- |
| `NgX` | ঙX | ঙ্ষ (U+0999 U+09CD U+09B7) |
| `NgxA` | ঙ্ষA | ঙ্ষা (U+0999 U+09CD U+09B7 U+09BE) |
| `rrNgx` | ররঙ্ষ | র্ঙ্ষ (U+09B0 U+09CD U+0999 U+09CD U+09B7) |
| `` Ngx`a `` | `` ঙ্ষ`আ `` | ঙ্ষআ (U+0999 U+09CD U+09B7 U+0986) |
| `` Ngx`h `` | `` ঙ্ষ`হ `` | ঙ্ষহ (U+0999 U+09CD U+09B7 U+09B9) |

Gap probes at that step covered `Ngk`, `kkx`, `rrNgx`, `rrkx`, `NgX`, `` Ngx`a ``,
and `` Ngx`h ``. The [next increment](#exact-ngk-conjunct) adds exact `Ngk` → ঙ্ক
and its supported vowel/context interactions. Other conjuncts, reph, uppercase aliases,
punctuation/escapes, composition, and platform integration remain incomplete.
No dependencies or broader compatibility, performance, or platform claims added.

The [later N-conjunct batch](#exact-kkhn-kshn-and-kxn-conjuncts)
resolves `kxNgx`; the outputs above record this earlier step.

## Exact Ngk conjunct

Added on 2026-10-28: exact `Ngk` produces ঙ্ক (U+0999 U+09CD U+0995),
matching before basic `Ng` and single `N`. It is an added conjunct sequence;
the 40 basic consonant sequences producing 35 letters remain unchanged.
The matched form establishes consonant context without a joiner, with the
following-`r` priority already used for uppercase `Y`.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `Ngk` | ঙ্ক | U+0999 U+09CD U+0995 |
| `Ngka` | ঙ্কা | U+0999 U+09CD U+0995 U+09BE |
| `Ngki` | ঙ্কি | U+0999 U+09CD U+0995 U+09BF |
| `Ngkee` | ঙ্কী | U+0999 U+09CD U+0995 U+09C0 |
| `Ngkr` | ঙ্ক্র | U+0999 U+09CD U+0995 U+09CD U+09B0 |
| `Ngkrri` | ঙ্কৃ | U+0999 U+09CD U+0995 U+09C3 |
| `Ngkrr` | ঙ্ক্রর | U+0999 U+09CD U+0995 U+09CD U+09B0 U+09B0 |
| `Ngkrrri` | ঙ্ক্রররি | U+0999 U+09CD U+0995 U+09CD U+09B0 U+09B0 U+09B0 U+09BF |
| `Ngkrrrri` | ঙ্ক্ররৃ | U+0999 U+09CD U+0995 U+09CD U+09B0 U+09B0 U+09C3 |
| `Ngkry` / `NgkrZ` | ঙ্ক্র্য | U+0999 U+09CD U+0995 U+09CD U+09B0 U+09CD U+09AF |
| `Ngkrry` / `NgkrrZ` | ঙ্করর‍্য | U+0999 U+09CD U+0995 U+09B0 U+09B0 U+200D U+09CD U+09AF |
| `Ngky` / `NgkZ` | ঙ্ক্য | U+0999 U+09CD U+0995 U+09CD U+09AF |
| `NgkY` | ঙ্কয় | U+0999 U+09CD U+0995 U+09DF |

All supported vowel signs and aliases apply (`NgkOI` → `ঙ্কৈ`,
`Ngkoo` → `ঙ্কু`), with existing transitions (`Ngkia` → `ঙ্কিয়া`).
Longer `aZ`/`oZ` still match at the following position (`NgkaZ` → `ঙ্কঅ্যা`).
A single following `r` attaches as ্র without U+200D before `y`/`Z`;
this differs from `Ngxr` → `ঙ্ষর` and `Ngxry` → `ঙ্ষর‍্য`.
Two `r` keys normally add ্রর, consumed before matching the rest.
Existing `rri` and `rry`/`rrZ` keep priority: `Ngkrri` → `ঙ্কৃ`,
`Ngkrry` → `ঙ্করর‍্য`. The helper receives the `k` in matched `Ngk`;
basic `k` was unchanged at that step. The later
[basic following-`r` batch](#following-r-after-basic-k-kh-and-sh) adds `kr` → `ক্র`.
Repetition and case distinctions follow raw input (`NgkNgk` → `ঙ্কঙ্ক`,
`NGk` → `ঞক`, `ngk` → `ংক`). Examples include `oNgko` → `অঙ্ক`,
`aNgkur` → `আঙ্কুর`, and `shaNgka` → `শাঙ্কা`, without spelling correction.

The 433 independently authored [fixtures](../../tests/fixtures/conjunct-ngk.tsv)
were checked against the SHA-256-verified pinned parser before implementation.
They cover supported vowels/aliases and transitions, selected preceding
contexts, adjacency, one through eight following `r` keys, single-`r`
attachment, `rri`/`rry`/`rrZ` exceptions, repetition, raw-spelling controls,
digits, boundaries, copied Unicode, and words. All 6,598 reference cases match.
Digits and copied characters reset context (`Ngk1a` → `ঙ্ক১আ`,
`Ngk🙂a` → `ঙ্ক🙂আ`) and prevent matches across boundaries (`Ng🙂k` → `ঙ🙂ক`).
Copied decomposed য় stays U+09AF U+09BC; separate calls share no state.
Rust regressions also cover control characters and long mixed input.
No normalization, persistent state, dependencies, or performance claim added.

At this step, longer matches starting with `Ngk` remained separate. Matching
`Ngk` changed `Ngkh` from ঙখ to ঙ্কহ; the
[later exact `Ngkh` increment](#exact-ngkh-conjunct) resolves it to ঙ্খ.
The five earlier-prefix conflicts described for `Ngx` also apply to `Ngk`:
`gNgk`, `NNgk`, `hNgk`, `ShNgk`, and `kxNgk`. At that step, they were excluded
from supported fixtures and retained as explicit partial-output regressions.

| Input | Engine at that step | Reference |
| --- | --- | --- |
| `Ngkh` (resolved below) | ঙ্কহ | ঙ্খ (U+0999 U+09CD U+0996) |
| `Ngkx` (resolved below) | ঙ্কক্স | ঙ্ক্ষ (U+0999 U+09CD U+0995 U+09CD U+09B7) |
| `Ngkkh` (resolved below) | ঙ্কখ | ঙ্ক্ষ (U+0999 U+09CD U+0995 U+09CD U+09B7) |
| `NgkSh` (resolved below) | ঙ্কষ | ঙ্ক্ষ (U+0999 U+09CD U+0995 U+09CD U+09B7) |
| `gNgk` | গঙ্ক | গ্ণগক |
| `rrNgk` | ররঙ্ক | র্ঙ্ক (U+09B0 U+09CD U+0999 U+09CD U+0995) |
| `NgK` | ঙK | ঙ্ক (U+0999 U+09CD U+0995) |
| `NgkA` | ঙ্কA | ঙ্কা (U+0999 U+09CD U+0995 U+09BE) |
| `` Ngk`a `` | `` ঙ্ক`আ `` | ঙ্কআ (U+0999 U+09CD U+0995 U+0986) |
| `` Ngk`h `` | `` ঙ্ক`হ `` | ঙ্কহ (U+0999 U+09CD U+0995 U+09B9) |

Gap probes at that step covered `Ngkh`, `Ngkx`, `Ngkkh`, `NgkSh`, `rrNgk`, `NgK`,
and `` Ngk`a ``. The next increment below adds exact `Ngkh` → ঙ্খ and its
supported vowel/context interactions. Other longer matches, earlier-prefix
conflicts, reph, uppercase aliases, punctuation/escapes, composition, and
platform integration remain incomplete. No broader compatibility or platform
validation claimed.

The [later N-conjunct batch](#exact-kkhn-kshn-and-kxn-conjuncts)
resolves `kxNgk`; the outputs above record this earlier step.

## Exact Ngkh conjunct

Added on 2026-10-28: exact `Ngkh` produces ঙ্খ (U+0999 U+09CD U+0996),
matching before shorter `Ngk`, basic `Ng`, and single `N`. This is an added
conjunct sequence; the 40 basic consonant sequences producing 35 letters
remain unchanged. It establishes consonant context without a joiner and
shares `Ngk`'s following-`r` priority.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `Ngkh` | ঙ্খ | U+0999 U+09CD U+0996 |
| `Ngkha` | ঙ্খা | U+0999 U+09CD U+0996 U+09BE |
| `Ngkhi` | ঙ্খি | U+0999 U+09CD U+0996 U+09BF |
| `Ngkhee` | ঙ্খী | U+0999 U+09CD U+0996 U+09C0 |
| `Ngkhr` | ঙ্খ্র | U+0999 U+09CD U+0996 U+09CD U+09B0 |
| `Ngkhrri` | ঙ্খৃ | U+0999 U+09CD U+0996 U+09C3 |
| `Ngkhrr` | ঙ্খ্রর | U+0999 U+09CD U+0996 U+09CD U+09B0 U+09B0 |
| `Ngkhrrri` | ঙ্খ্রররি | U+0999 U+09CD U+0996 U+09CD U+09B0 U+09B0 U+09B0 U+09BF |
| `Ngkhrrrri` | ঙ্খ্ররৃ | U+0999 U+09CD U+0996 U+09CD U+09B0 U+09B0 U+09C3 |
| `Ngkhry` | ঙ্খ্র্য | U+0999 U+09CD U+0996 U+09CD U+09B0 U+09CD U+09AF |
| `Ngkhrry` | ঙ্খরর‍্য | U+0999 U+09CD U+0996 U+09B0 U+09B0 U+200D U+09CD U+09AF |
| `Ngkhy` | ঙ্খ্য | U+0999 U+09CD U+0996 U+09CD U+09AF |
| `NgkhY` | ঙ্খয় | U+0999 U+09CD U+0996 U+09DF |

All supported vowel signs and aliases apply (`NgkhOI` → `ঙ্খৈ`,
`Ngkhoo` → `ঙ্খু`), with existing transitions (`Ngkhia` → `ঙ্খিয়া`).
Longer `aZ`/`oZ` keep priority at the following position (`NgkhaZ` → `ঙ্খঅ্যা`).
A single following `r` attaches as ্র without U+200D before `y`/`Z`
(`NgkhrZ` → `ঙ্খ্র্য`). Two `r` keys normally add ্রর before matching
resumes, while `rri` and `rry`/`rrZ` retain priority (`NgkhrrZ` → `ঙ্খরর‍্য`).
The helper receives the `h` in matched `Ngkh`; basic `h` and `kh` were
unchanged at that step. The later
[basic following-`r` batch](#following-r-after-basic-k-kh-and-sh) adds `khr` → `খ্র`.

Raw matching preserves repetition and spelling distinctions:
`NgkhNgkh` → `ঙ্খঙ্খ`, `NgkhNgk` → `ঙ্খঙ্ক`, `Ngkhx` → `ঙ্খক্স`,
`NGkh` → `ঞখ`, and `ngkh` → `ংখ`. Examples include `shoNgkho` → `শঙ্খ`,
`shaNgkha` → `শাঙ্খা`, and `shoNgkher` → `শঙ্খের`, without spelling correction.

The 454 independently authored [fixtures](../../tests/fixtures/conjunct-ngkh.tsv)
were checked against the SHA-256-verified pinned parser before implementation.
They cover supported vowels/aliases and transitions, selected preceding
contexts, adjacency, one through eight following `r` keys, single-`r`
attachment, `rri`/`rry`/`rrZ` exceptions, repetition, raw-spelling controls,
all digits, boundaries, copied Unicode, and words. All 7,052 reference cases
match. Digits and copied characters reset context (`Ngkh1a` → `ঙ্খ১আ`,
`Ngkh🙂a` → `ঙ্খ🙂আ`) and prevent matches across boundaries
(`Ngk🙂h` → `ঙ্ক🙂হ`). Copied decomposed য় stays U+09AF U+09BC;
separate calls share no state. Rust regressions also cover control characters
and long mixed input. No normalization, dependencies, persistent state,
performance measurement, or platform validation added.

The five earlier-prefix conflicts described for `Ngx`/`Ngk` also apply here.
At that step, they were excluded from compatibility fixtures and retained as explicit
partial-output regressions; for example, `gN` consumes `N` before `Ngkh`
can match in the reference. Case aliases, reph, and escapes remain incomplete:

| Input | Engine at that step | Reference |
| --- | --- | --- |
| `hr` | হর | হ্র (U+09B9 U+09CD U+09B0) |
| `khr` | খর | খ্র (U+0996 U+09CD U+09B0) |
| `gNgkh` | গঙ্খ | গ্ণগখ |
| `NNgkh` | ণঙ্খ | ণ্ণগখ |
| `hNgkh` | হঙ্খ | হ্ণগখ |
| `ShNgkh` (resolved below) | ষঙ্খ | ষ্ণগখ |
| `kxNgkh` (resolved below) | ক্ষঙ্খ | ক্ষ্ণগখ |
| `rrNgkh` | ররঙ্খ | র্ঙ্খ (U+09B0 U+09CD U+0999 U+09CD U+0996) |
| `NgkH` | ঙ্কH | ঙ্খ (U+0999 U+09CD U+0996) |
| `NgKh` | ঙKহ | ঙ্খ (U+0999 U+09CD U+0996) |
| `NgkhA` | ঙ্খA | ঙ্খা (U+0999 U+09CD U+0996 U+09BE) |
| `` Ngkh`a `` | `` ঙ্খ`আ `` | ঙ্খআ (U+0999 U+09CD U+0996 U+0986) |
| `` Ngkh`h `` | `` ঙ্খ`হ `` | ঙ্খহ (U+0999 U+09CD U+0996 U+09B9) |

Gap probes at that step covered `Ngkx`, `Ngkkh`, `NgkSh`, `gNgkh`, `rrNgkh`,
`NgkH`, and `` Ngkh`a ``. The [next increment](#exact-ngkx-conjunct) adds
exact `Ngkx` → ঙ্ক্ষ and its supported vowel/context interactions. `Ngkkh`/`NgkSh`,
earlier-prefix conflicts, other conjuncts, reph, uppercase aliases,
punctuation/escapes, composition, and platform integration remain separate.
Passing these fixtures does not establish full Avro compatibility.

The [later N-conjunct batch](#exact-kkhn-kshn-and-kxn-conjuncts)
resolves `kxNgkh`; the outputs above record this earlier step.

## Exact Ngkx conjunct

Added on 2026-10-28: exact `Ngkx` produces ঙ্ক্ষ
(U+0999 U+09CD U+0995 U+09CD U+09B7), matching before shorter `Ngk`,
basic `Ng`, and single `N`. This is an added conjunct sequence; the 40 basic
consonant sequences producing 35 letters remain unchanged. It establishes
consonant context without a joiner and shares `Ngx`/`kx` following-`r` priority.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `Ngkx` | ঙ্ক্ষ | U+0999 U+09CD U+0995 U+09CD U+09B7 |
| `Ngkxa` | ঙ্ক্ষা | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09BE |
| `Ngkxi` | ঙ্ক্ষি | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09BF |
| `Ngkxee` | ঙ্ক্ষী | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09C0 |
| `Ngkxr` | ঙ্ক্ষর | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09B0 |
| `Ngkxrri` | ঙ্ক্ষৃ | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09C3 |
| `Ngkxrr` | ঙ্ক্ষ্রর | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09CD U+09B0 U+09B0 |
| `Ngkxrrri` | ঙ্ক্ষ্রররি | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09CD U+09B0 U+09B0 U+09B0 U+09BF |
| `Ngkxrrrri` | ঙ্ক্ষ্ররৃ | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09CD U+09B0 U+09B0 U+09C3 |
| `Ngkxry` | ঙ্ক্ষর‍্য | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09B0 U+200D U+09CD U+09AF |
| `Ngkxrry` | ঙ্ক্ষরর‍্য | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09B0 U+09B0 U+200D U+09CD U+09AF |
| `Ngkxy` | ঙ্ক্ষ্য | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09CD U+09AF |
| `NgkxY` | ঙ্ক্ষয় | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09DF |

All supported vowel signs and aliases apply (`NgkxOI` → `ঙ্ক্ষৈ`,
`Ngkxoo` → `ঙ্ক্ষু`), with existing transitions (`Ngkxia` → `ঙ্ক্ষিয়া`).
Longer `aZ`/`oZ` keep priority at the following position (`NgkxaZ` → `ঙ্ক্ষঅ্যা`).
Two following `r` keys normally add ্রর before matching resumes; `rri` and
`rry`/`rrZ` retain priority (`NgkxrrZ` → `ঙ্ক্ষরর‍্য`). Single `r` stays
separate and sets the basic-`r` U+200D joiner before `y`/`Z`
(`NgkxrZ` → `ঙ্ক্ষর‍্য`), unlike single-`r` attachment after `Ngk`/`Ngkh`.
The existing helper receives final raw `x`; no new following-`r` rule is added.

Raw matching preserves repetition and spelling distinctions:
`NgkxNgkx` → `ঙ্ক্ষঙ্ক্ষ`, `NgkxNgkh` → `ঙ্ক্ষঙ্খ`, `NgkxNgk` → `ঙ্ক্ষঙ্ক`,
`Ngkxx` → `ঙ্ক্ষক্স`, `NGkx` → `ঞক্ষ`, and `ngkx` → `ংক্ষ`.
Examples include `akaNgkxa` → `আকাঙ্ক্ষা` and `akaNgkxi` → `আকাঙ্ক্ষি`,
following the raw spelling without correction.

The 432 independently authored [fixtures](../../tests/fixtures/conjunct-ngkx.tsv)
were checked against the SHA-256-verified pinned parser before implementation.
They cover supported vowels/aliases and transitions, selected preceding
contexts, adjacency, one through eight following `r` keys, single-`r`
joiners, `rri`/`rry`/`rrZ` exceptions, repetition, raw-spelling controls,
all digits, boundaries, copied Unicode, and words. All 7,484 reference cases
match. Digits and copied characters reset context (`Ngkx1a` → `ঙ্ক্ষ১আ`,
`Ngkx🙂a` → `ঙ্ক্ষ🙂আ`) and prevent matches across boundaries
(`Ngk🙂x` → `ঙ্ক🙂এক্স`). Copied decomposed য় stays U+09AF U+09BC;
separate calls share no state. Rust regressions also cover control characters
and long mixed input. No normalization, dependencies, persistent state,
performance measurement, or platform validation added.

The five earlier-prefix conflicts described for `Ngx`/`Ngk`/`Ngkh` also apply
here. At that step, they were excluded from compatibility fixtures and retained as
explicit partial-output regressions; for example, `gN` consumes `N` before
`Ngkx` can match in the reference. Related spellings, case aliases, reph,
and escapes remain incomplete:

| Input | Engine at that step | Reference |
| --- | --- | --- |
| `Ngkkh` (resolved below) | ঙ্কখ | ঙ্ক্ষ (U+0999 U+09CD U+0995 U+09CD U+09B7) |
| `Ngkkhr` (resolved below) | ঙ্কখর | ঙ্ক্ষ্র (U+0999 U+09CD U+0995 U+09CD U+09B7 U+09CD U+09B0) |
| `NgkSh` (resolved below) | ঙ্কষ | ঙ্ক্ষ (U+0999 U+09CD U+0995 U+09CD U+09B7) |
| `gNgkx` | গঙ্ক্ষ | গ্ণগক্ষ |
| `NNgkx` | ণঙ্ক্ষ | ণ্ণগক্ষ |
| `hNgkx` | হঙ্ক্ষ | হ্ণগক্ষ |
| `ShNgkx` (resolved below) | ষঙ্ক্ষ | ষ্ণগক্ষ |
| `kxNgkx` (resolved below) | ক্ষঙ্ক্ষ | ক্ষ্ণগক্ষ |
| `rrNgkx` | ররঙ্ক্ষ | র্ঙ্ক্ষ (U+09B0 U+09CD U+0999 U+09CD U+0995 U+09CD U+09B7) |
| `NgkX` | ঙ্কX | ঙ্ক্ষ (U+0999 U+09CD U+0995 U+09CD U+09B7) |
| `NgKx` | ঙKএক্স | ঙ্ক্ষ (U+0999 U+09CD U+0995 U+09CD U+09B7) |
| `NgkxA` | ঙ্ক্ষA | ঙ্ক্ষা (U+0999 U+09CD U+0995 U+09CD U+09B7 U+09BE) |
| `` Ngkx`a `` | `` ঙ্ক্ষ`আ `` | ঙ্ক্ষআ (U+0999 U+09CD U+0995 U+09CD U+09B7 U+0986) |
| `` Ngkx`h `` | `` ঙ্ক্ষ`হ `` | ঙ্ক্ষহ (U+0999 U+09CD U+0995 U+09CD U+09B7 U+09B9) |

Gap probes at that step covered `Ngkkh`, `NgkSh`, `gNgkx`, `rrNgkx`, `NgkX`,
`NgkxA`, and `` Ngkx`a ``. The [next increment](#exact-ngkkh-conjunct) adds
exact `Ngkkh` → ঙ্ক্ষ and its supported vowel/context interactions, including
single-`r` attachment (`Ngkkhr` → `ঙ্ক্ষ্র`), unlike `Ngkxr` → `ঙ্ক্ষর`.
`NgkSh`, earlier-prefix conflicts, other conjuncts, reph, uppercase aliases, punctuation/escapes, composition,
and platform integration remain separate. Passing these fixtures does not
establish full Avro compatibility.

The [later N-conjunct batch](#exact-kkhn-kshn-and-kxn-conjuncts)
resolves `kxNgkx`; the outputs above record this earlier step.

## Exact Ngkkh conjunct

Added on 2026-10-28: exact `Ngkkh` produces ঙ্ক্ষ
(U+0999 U+09CD U+0995 U+09CD U+09B7), matching before shorter `Ngk`,
basic `Ng`, and single `N`. The 40 basic consonant sequences producing
35 letters remain unchanged. This added conjunct establishes consonant
context without a joiner and shares `Ngkh`'s following-`r` behavior.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `Ngkkh` | ঙ্ক্ষ | U+0999 U+09CD U+0995 U+09CD U+09B7 |
| `Ngkkha` | ঙ্ক্ষা | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09BE |
| `Ngkkhi` | ঙ্ক্ষি | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09BF |
| `Ngkkhee` | ঙ্ক্ষী | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09C0 |
| `Ngkkhr` | ঙ্ক্ষ্র | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09CD U+09B0 |
| `Ngkkhrri` | ঙ্ক্ষৃ | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09C3 |
| `Ngkkhrr` | ঙ্ক্ষ্রর | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09CD U+09B0 U+09B0 |
| `Ngkkhrrri` | ঙ্ক্ষ্রররি | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09CD U+09B0 U+09B0 U+09B0 U+09BF |
| `Ngkkhrrrri` | ঙ্ক্ষ্ররৃ | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09CD U+09B0 U+09B0 U+09C3 |
| `Ngkkhry` | ঙ্ক্ষ্র্য | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09CD U+09B0 U+09CD U+09AF |
| `Ngkkhrry` | ঙ্ক্ষরর‍্য | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09B0 U+09B0 U+200D U+09CD U+09AF |
| `Ngkkhy` | ঙ্ক্ষ্য | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09CD U+09AF |
| `NgkkhY` | ঙ্ক্ষয় | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09DF |

All supported vowel signs and aliases apply (`NgkkhOI` → `ঙ্ক্ষৈ`,
`Ngkkhoo` → `ঙ্ক্ষু`), with existing transitions (`Ngkkhia` → `ঙ্ক্ষিয়া`).
Longer `aZ`/`oZ` keep priority at the following position (`NgkkhaZ` → `ঙ্ক্ষঅ্যা`).
A single following `r` attaches as ্র without U+200D before `y`/`Z`
(`NgkkhrZ` → `ঙ্ক্ষ্র্য`), unlike `Ngkxry` → `ঙ্ক্ষর‍্য`.
Two `r` keys normally add ্রর before matching resumes; `rri` and
`rry`/`rrZ` retain priority (`NgkkhrrZ` → `ঙ্ক্ষরর‍্য`). The existing
helper receives final raw `h`; basic `kh` and standalone `kkh` are unchanged.

Raw matching preserves repetition and supported neighboring sequences:
`NgkkhNgkkh` → `ঙ্ক্ষঙ্ক্ষ`, `NgkkhNgkx` → `ঙ্ক্ষঙ্ক্ষ`,
`NgkkhNgkh` → `ঙ্ক্ষঙ্খ`, `NgkkhNgk` → `ঙ্ক্ষঙ্ক`, and `Ngkkhx` → `ঙ্ক্ষক্স`.
Examples include `akaNgkkha` → `আকাঙ্ক্ষা` and `akaNgkkhi` → `আকাঙ্ক্ষি`,
following the raw spelling without correction.

The 458 independently authored [fixtures](../../tests/fixtures/conjunct-ngkkh.tsv)
were checked against the SHA-256-verified pinned parser before implementation.
They cover supported vowels/aliases and transitions, selected preceding
contexts, adjacency, one through eight following `r` keys, single-`r`
attachment, `rri`/`rry`/`rrZ` exceptions, joiner contrasts with `Ngkx`,
repetition, raw-spelling controls, all digits, boundaries, copied Unicode,
and words. All 7,942 reference cases match. Digits and copied characters
reset context (`Ngkkh1a` → `ঙ্ক্ষ১আ`, `Ngkkh🙂a` → `ঙ্ক্ষ🙂আ`) and
prevent matches across boundaries (`Ngk🙂kh` → `ঙ্ক🙂খ`). Copied decomposed
য় stays U+09AF U+09BC; separate calls share no state. Rust regressions
also cover control characters and long mixed input. No normalization,
dependencies, persistent state, performance measurement, or platform validation added.

The five earlier-prefix conflicts described for the previous conjuncts also
apply here. At that step, they were excluded from compatibility fixtures and retained
as explicit partial-output regressions. At this step, standalone `kkh` → ক্ষ was
incomplete, so case-distinct `NGkkh`/`ngkkh` did not yet match the reference.
The [exact `kkh` increment](#exact-kkh-conjunct) below resolves these three gaps.
These are separate from exact `Ngkkh`. Other spellings, aliases, reph, and
escapes remain gaps:

| Input | Engine at that step | Reference |
| --- | --- | --- |
| `NgkSh` (resolved below) | ঙ্কষ | ঙ্ক্ষ (U+0999 U+09CD U+0995 U+09CD U+09B7) |
| `gNgkkh` | গঙ্ক্ষ | গ্ণগক্ষ |
| `NNgkkh` | ণঙ্ক্ষ | ণ্ণগক্ষ |
| `hNgkkh` | হঙ্ক্ষ | হ্ণগক্ষ |
| `ShNgkkh` (resolved below) | ষঙ্ক্ষ | ষ্ণগক্ষ |
| `kxNgkkh` (resolved below) | ক্ষঙ্ক্ষ | ক্ষ্ণগক্ষ |
| `rrNgkkh` | ররঙ্ক্ষ | র্ঙ্ক্ষ (U+09B0 U+09CD U+0999 U+09CD U+0995 U+09CD U+09B7) |
| `kkh` | কখ | ক্ষ (U+0995 U+09CD U+09B7) |
| `NGkkh` | ঞকখ | ঞক্ষ (U+099E U+0995 U+09CD U+09B7) |
| `ngkkh` | ংকখ | ংক্ষ (U+0982 U+0995 U+09CD U+09B7) |
| `NgKkh` | ঙKখ | ঙ্ক্ষ (U+0999 U+09CD U+0995 U+09CD U+09B7) |
| `NgkkH` | ঙ্ককH | ঙ্ক্ষ (U+0999 U+09CD U+0995 U+09CD U+09B7) |
| `NgkkhA` | ঙ্ক্ষA | ঙ্ক্ষা (U+0999 U+09CD U+0995 U+09CD U+09B7 U+09BE) |
| `` Ngkkh`a `` | `` ঙ্ক্ষ`আ `` | ঙ্ক্ষআ (U+0999 U+09CD U+0995 U+09CD U+09B7 U+0986) |
| `` Ngkkh`h `` | `` ঙ্ক্ষ`হ `` | ঙ্ক্ষহ (U+0999 U+09CD U+0995 U+09CD U+09B7 U+09B9) |

Gap probes at that step covered `NgkSh`, `gNgkkh`, `rrNgkkh`, `NGkkh`, `NgkkH`,
`NgkkhA`, and `` Ngkkh`a ``. The [next increment](#exact-ngksh-conjunct) adds
exact `NgkSh` → ঙ্ক্ষ and its supported vowel/context interactions. Other conjuncts,
earlier-prefix conflicts, standalone `kkh`, reph, uppercase aliases,
punctuation/escapes, composition, and platform integration remain separate.
Passing these fixtures does not establish full Avro compatibility.

The [later N-conjunct batch](#exact-kkhn-kshn-and-kxn-conjuncts)
resolves `kxNgkkh`; the outputs above record this earlier step.

## Exact NgkSh conjunct

Added on 2026-10-28: exact `NgkSh` produces ঙ্ক্ষ
(U+0999 U+09CD U+0995 U+09CD U+09B7), matching before shorter `Ngk`,
basic `Ng`, and single `N`. The 40 basic consonant sequences producing
35 letters remain unchanged. This added spelling shares `Ngkkh`'s branch,
consonant context without a joiner, and following-`r` behavior.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `NgkSh` | ঙ্ক্ষ | U+0999 U+09CD U+0995 U+09CD U+09B7 |
| `NgkSha` | ঙ্ক্ষা | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09BE |
| `NgkShi` | ঙ্ক্ষি | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09BF |
| `NgkShee` | ঙ্ক্ষী | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09C0 |
| `NgkShr` | ঙ্ক্ষ্র | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09CD U+09B0 |
| `NgkShrri` | ঙ্ক্ষৃ | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09C3 |
| `NgkShrr` | ঙ্ক্ষ্রর | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09CD U+09B0 U+09B0 |
| `NgkShrrri` | ঙ্ক্ষ্রররি | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09CD U+09B0 U+09B0 U+09B0 U+09BF |
| `NgkShrrrri` | ঙ্ক্ষ্ররৃ | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09CD U+09B0 U+09B0 U+09C3 |
| `NgkShry` | ঙ্ক্ষ্র্য | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09CD U+09B0 U+09CD U+09AF |
| `NgkShrry` | ঙ্ক্ষরর‍্য | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09B0 U+09B0 U+200D U+09CD U+09AF |
| `NgkShy` | ঙ্ক্ষ্য | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09CD U+09AF |
| `NgkShY` | ঙ্ক্ষয় | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09DF |

All supported vowel signs and aliases apply (`NgkShOI` → `ঙ্ক্ষৈ`,
`NgkShoo` → `ঙ্ক্ষু`), with existing transitions (`NgkShia` → `ঙ্ক্ষিয়া`).
Longer `aZ`/`oZ` keep priority at the following position (`NgkShaZ` → `ঙ্ক্ষঅ্যা`).
Single `r` attaches as ্র without U+200D before `y`/`Z`
(`NgkShrZ` → `ঙ্ক্ষ্র্য`), unlike `Ngkxry` → `ঙ্ক্ষর‍্য`.
Two `r` keys normally add ্রর before matching resumes; `rri` and
`rry`/`rrZ` retain priority (`NgkShrrZ` → `ঙ্ক্ষরর‍্য`). The existing
helper receives final raw `h`; no new following-`r` rule is added.

Raw matching preserves repetition and supported neighboring sequences:
`NgkShNgkSh` → `ঙ্ক্ষঙ্ক্ষ`, `NgkShNgkkh` → `ঙ্ক্ষঙ্ক্ষ`,
`NgkShNgkx` → `ঙ্ক্ষঙ্ক্ষ`, `NgkShNgkh` → `ঙ্ক্ষঙ্খ`, and `NgkShx` → `ঙ্ক্ষক্স`.
Case-sensitive `Ngksh` → `ঙ্কশ` stays distinct from `NgkSh` → `ঙ্ক্ষ`.
Examples include `akaNgkSha` → `আকাঙ্ক্ষা` and `akaNgkShi` → `আকাঙ্ক্ষি`,
following the raw spelling without correction or case normalization.

The 468 independently authored [fixtures](../../tests/fixtures/conjunct-ngksh.tsv)
were checked against the SHA-256-verified pinned parser before implementation.
They cover supported vowels/aliases and transitions, selected preceding
contexts, adjacency, one through eight following `r` keys, single-`r`
attachment, `rri`/`rry`/`rrZ` exceptions, contrasts with `Ngkkh`/`Ngkx`,
repetition, case/raw-spelling controls, all digits, boundaries, copied Unicode,
and words. All 8,410 reference cases match. Digits and copied characters
reset context (`NgkSh1a` → `ঙ্ক্ষ১আ`, `NgkSh🙂a` → `ঙ্ক্ষ🙂আ`) and
prevent matches across boundaries (`Ngk🙂Sh` → `ঙ্ক🙂ষ`). Copied decomposed
য় stays U+09AF U+09BC; separate calls share no state. Rust regressions
also cover control characters and long mixed input. No normalization,
dependencies, persistent state, performance measurement, or platform validation added.

The five earlier-prefix conflicts described for the previous conjuncts also
apply here. At that step, they were excluded from compatibility fixtures and retained
as explicit partial-output regressions. At this step, standalone `kSh` was incomplete,
so case-distinct `NGkSh`/`ngkSh` did not yet match the reference. The
[exact `kSh` increment](#exact-ksh-conjunct) below resolves these three gaps. Other
spellings, aliases, reph, and escapes remain gaps:

| Input | Engine at that step | Reference |
| --- | --- | --- |
| `kkh` (resolved below) | কখ | ক্ষ (U+0995 U+09CD U+09B7) |
| `kSh` | কষ | ক্ষ (U+0995 U+09CD U+09B7) |
| `gNgkSh` | গঙ্ক্ষ | গ্ণগক্ষ |
| `NNgkSh` | ণঙ্ক্ষ | ণ্ণগক্ষ |
| `hNgkSh` | হঙ্ক্ষ | হ্ণগক্ষ |
| `ShNgkSh` (resolved below) | ষঙ্ক্ষ | ষ্ণগক্ষ |
| `kxNgkSh` (resolved below) | ক্ষঙ্ক্ষ | ক্ষ্ণগক্ষ |
| `rrNgkSh` | ররঙ্ক্ষ | র্ঙ্ক্ষ (U+09B0 U+09CD U+0999 U+09CD U+0995 U+09CD U+09B7) |
| `NGkSh` | ঞকষ | ঞক্ষ (U+099E U+0995 U+09CD U+09B7) |
| `ngkSh` | ংকষ | ংক্ষ (U+0982 U+0995 U+09CD U+09B7) |
| `NgKSh` | ঙKষ | ঙ্ক্ষ (U+0999 U+09CD U+0995 U+09CD U+09B7) |
| `NgkSH` | ঙ্কশH | ঙ্ক্ষ (U+0999 U+09CD U+0995 U+09CD U+09B7) |
| `NgkShA` | ঙ্ক্ষA | ঙ্ক্ষা (U+0999 U+09CD U+0995 U+09CD U+09B7 U+09BE) |
| `` NgkSh`a `` | `` ঙ্ক্ষ`আ `` | ঙ্ক্ষআ (U+0999 U+09CD U+0995 U+09CD U+09B7 U+0986) |
| `` NgkSh`h `` | `` ঙ্ক্ষ`হ `` | ঙ্ক্ষহ (U+0999 U+09CD U+0995 U+09CD U+09B7 U+09B9) |

Gap probes at that step covered `kkh`, `kSh`, `gNgkSh`, `rrNgkSh`, `NGkSh`,
`NgkSH`, and `` NgkSh`a ``. The [next increment](#exact-kkh-conjunct) adds
exact standalone `kkh` → ক্ষ and its supported vowel/context interactions. `kSh`,
earlier-prefix conflicts, other conjuncts, reph, uppercase aliases,
punctuation/escapes, composition, and platform integration remain separate.
Passing these fixtures does not establish full Avro compatibility.

The [later N-conjunct batch](#exact-kkhn-kshn-and-kxn-conjuncts)
resolves `kxNgkSh`; the outputs above record this earlier step.

## Exact kkh conjunct

Added on 2026-10-29: exact `kkh` produces ক্ষ (U+0995 U+09CD U+09B7),
matching before basic `k`/`kh`. The 40 basic consonant sequences producing
35 letters remain unchanged. Earlier exact `Ngkkh` still wins; standalone
`kkh` also resolves `NGkkh` → `ঞক্ষ` and `ngkkh` → `ংক্ষ`.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `kkh` | ক্ষ | U+0995 U+09CD U+09B7 |
| `kkha` | ক্ষা | U+0995 U+09CD U+09B7 U+09BE |
| `kkhee` | ক্ষী | U+0995 U+09CD U+09B7 U+09C0 |
| `kkhr` | ক্ষ্র | U+0995 U+09CD U+09B7 U+09CD U+09B0 |
| `kkhrri` | ক্ষৃ | U+0995 U+09CD U+09B7 U+09C3 |
| `kkhrr` | ক্ষ্রর | U+0995 U+09CD U+09B7 U+09CD U+09B0 U+09B0 |
| `kkhry` | ক্ষ্র্য | U+0995 U+09CD U+09B7 U+09CD U+09B0 U+09CD U+09AF |
| `kkhrry` | ক্ষরর‍্য | U+0995 U+09CD U+09B7 U+09B0 U+09B0 U+200D U+09CD U+09AF |
| `NGkkh` | ঞক্ষ | U+099E U+0995 U+09CD U+09B7 |
| `ngkkh` | ংক্ষ | U+0982 U+0995 U+09CD U+09B7 |

Supported vowel signs and aliases apply (`kkhOI` → `ক্ষৈ`, `kkhoo` → `ক্ষু`),
with existing transitions (`kkhia` → `ক্ষিয়া`, `kkhooo` → `ক্ষুঅ`).
Longer `aZ`/`oZ` keep priority (`kkhaZ` → `ক্ষঅ্যা`). The rule reuses
`Ngkh`'s consonant context and existing following-`r` helper with final raw `h`.
Single `r` attaches without U+200D before `y`/`Z` (`kkhrZ` → `ক্ষ্র্য`),
unlike `kxry` → `ক্ষর‍্য`. Two `r` keys normally add ্রর; `rri` and
`rry`/`rrZ` retain priority. Longer runs resume ordinary matching
(`kkhrrri` → `ক্ষ্রররি`, `kkhrrrrrri` → `ক্ষ্ররররৃ`).

Repetition and selected adjacent sequences match the reference
(`kkhkkh` → `ক্ষক্ষ`, `kkhkh` → `ক্ষখ`, `NgkShkkh` → `ঙ্ক্ষক্ষ`).
Examples `rukkha` → `রুক্ষা` and `lokkho` → `লক্ষ` follow their raw spelling
without correction. Digit and copied-character boundaries reset context
(`kkh1a` → `ক্ষ১আ`, `kkh🙂a` → `ক্ষ🙂আ`); `k🙂kh` → `ক🙂খ` prevents
matching across a boundary. Copied decomposed য় remains U+09AF U+09BC.

The 330 independently authored [fixtures](../../tests/fixtures/conjunct-kkh.tsv)
were checked against the SHA-256-verified pinned parser before implementation.
They cover vowels/aliases and transitions, selected preceding contexts including
`ng`/`NG`, one through eight following `r` keys and their exceptions, repetition,
raw-spelling controls, all digits, boundaries, copied Unicode, and words.
All 8,740 reference cases match. Rust regressions also cover control-character
boundaries, separate calls, long mixed input, and explicit partial outputs for
unsupported overlaps. No upstream source, rules, fixtures, dependencies,
normalization, persistent state, performance measurement, or platform code added.

The initial reference comparison exposed five earlier-prefix conflicts:
`kk`/`nk`/`lk`/`sk`/`Shk` consume the first `k` before `kkh` can match.
Longer `kkhN` → ক্ষ্ণ and `kkhm` → ক্ষ্ম also take priority in the reference;
for example, `kkhN` consumes the `N` before `Ngkkh` can match in `kkhNgkkh`. At that step,
these were separate rules, excluded from compatibility fixtures and recorded as partial
output regressions. Other spellings, aliases, reph, and escapes remain gaps:

| Input | Engine at that step | Reference |
| --- | --- | --- |
| `kkkh` (resolved below) | কক্ষ | ক্কখ |
| `nkkh` | নক্ষ | ঙ্কখ |
| `lkkh` | লক্ষ | ল্কখ |
| `skkh` | সক্ষ | স্কখ |
| `Shkkh` | ষক্ষ | ষ্কখ |
| `kkhN` (resolved below) | ক্ষণ | ক্ষ্ণ |
| `kkhm` (resolved below) | ক্ষম | ক্ষ্ম |
| `kkhNgkkh` (resolved below) | ক্ষঙ্ক্ষ | ক্ষ্ণগক্ষ |
| `kkhNG` | ক্ষঞ | ক্ষ্ণগ |
| `kSh` (resolved below) | কষ | ক্ষ |
| `rrkkh` | ররক্ষ | র্ক্ষ |
| `kkH` | ককH | ক্ষ |
| `Kkh` | Kখ | ক্ষ |
| `kKh` | কKহ | ক্ষ |
| `kkhA` | ক্ষA | ক্ষা |
| `` kkh`a `` | `` ক্ষ`আ `` | ক্ষআ |
| `` kkh`h `` | `` ক্ষ`হ `` | ক্ষহ |
| `` k`kh `` | `` ক`খ `` | কখ |
| `kkh.` | ক্ষ. | ক্ষ। |

Gap probes at that step covered `kSh`, `kkkh`, `kkhN`, `kkhm`, `rrkkh`,
`kkH`, and `` kkh`a ``. The [next increment](#exact-ksh-conjunct) adds
exact standalone `kSh` → ক্ষ and its supported vowel/context interactions. Earlier-prefix
conflicts, other conjuncts, reph, uppercase aliases, punctuation/escapes,
composition, and platform integration remain separate.
Passing these fixtures does not establish full Avro compatibility.

The [later N-conjunct batch](#exact-kkhn-kshn-and-kxn-conjuncts)
resolves `kkhN` and `kkhNgkkh`; the outputs above record this earlier step.

## Exact kSh conjunct

Added on 2026-10-29: exact `kSh` produces ক্ষ (U+0995 U+09CD U+09B7),
matching before basic `k`. It shares `kkh`'s branch after reference checks
confirmed the same vowel context and following-`r` behavior. Earlier exact
`NgkSh` still wins. The 40 basic consonant sequences producing 35 letters
remain unchanged; `NGkSh` → `ঞক্ষ` and `ngkSh` → `ংক্ষ` now also match.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `kSh` | ক্ষ | U+0995 U+09CD U+09B7 |
| `kSha` | ক্ষা | U+0995 U+09CD U+09B7 U+09BE |
| `kShee` | ক্ষী | U+0995 U+09CD U+09B7 U+09C0 |
| `kShr` | ক্ষ্র | U+0995 U+09CD U+09B7 U+09CD U+09B0 |
| `kShrri` | ক্ষৃ | U+0995 U+09CD U+09B7 U+09C3 |
| `kShrr` | ক্ষ্রর | U+0995 U+09CD U+09B7 U+09CD U+09B0 U+09B0 |
| `kShry` | ক্ষ্র্য | U+0995 U+09CD U+09B7 U+09CD U+09B0 U+09CD U+09AF |
| `kShrry` | ক্ষরর‍্য | U+0995 U+09CD U+09B7 U+09B0 U+09B0 U+200D U+09CD U+09AF |
| `NGkSh` | ঞক্ষ | U+099E U+0995 U+09CD U+09B7 |
| `ngkSh` | ংক্ষ | U+0982 U+0995 U+09CD U+09B7 |

Supported vowel signs and aliases apply (`kShOI` → `ক্ষৈ`, `kShoo` → `ক্ষু`),
with existing transitions (`kShia` → `ক্ষিয়া`, `kShooo` → `ক্ষুঅ`).
Longer `aZ`/`oZ` keep priority (`kShaZ` → `ক্ষঅ্যা`). The existing helper
receives final raw `h`: single `r` attaches without U+200D before `y`/`Z`
(`kShrZ` → `ক্ষ্র্য`), unlike `kxry` → `ক্ষর‍্য`. Two `r` keys normally
add ্রর; `rri` and `rry`/`rrZ` retain priority. Longer runs resume ordinary
matching (`kShrrri` → `ক্ষ্রররি`, `kShrrrrrri` → `ক্ষ্ররররৃ`).

Repetition and selected adjacent sequences match the reference
(`kShkSh` → `ক্ষক্ষ`, `kShkkh` → `ক্ষক্ষ`, `kkhkSh` → `ক্ষক্ষ`).
Case is significant: `ksh` → `কশ` remains distinct from `kSh` → `ক্ষ`.
Examples `rukSha` → `রুক্ষা` and `lokSho` → `লক্ষ` follow raw spelling without
correction. Digit and copied-character boundaries reset context
(`kSh1a` → `ক্ষ১আ`, `kSh🙂a` → `ক্ষ🙂আ`); `k🙂Sh` → `ক🙂ষ` prevents
matching across a boundary. Copied decomposed য় remains U+09AF U+09BC.

The 332 independently authored [fixtures](../../tests/fixtures/conjunct-ksh.tsv)
were checked against the SHA-256-verified pinned parser before implementation.
They cover supported vowels/aliases, transitions, selected preceding contexts
including `ng`/`NG`, one through eight following `r` keys and their exceptions,
repetition, raw-spelling/case controls, all digits, boundaries, copied Unicode,
and words. All 9,072 reference cases match. Rust regressions also cover control
characters, separate calls, long mixed input, and partial outputs for remaining
gaps. No upstream source, rules, fixtures, dependencies, normalization,
persistent state, performance measurement, or platform code added.

Earlier `kk`/`nk`/`lk`/`sk`/`Shk` matches consume the first `k` before `kSh`
can match. Longer `kShN` → ক্ষ্ণ and `kShm` → ক্ষ্ম also take priority in the
reference; `kShN` consumes the `N` before `NgkSh` in `kShNgkSh`. At that step,
these were separate rules, excluded from compatibility fixtures and retained as partial
output regressions. Other spellings, aliases, reph, and escapes remain gaps:

| Input | Engine at that step | Reference |
| --- | --- | --- |
| `kkSh` (resolved below) | কক্ষ | ক্কষ |
| `nkSh` | নক্ষ | ঙ্কষ |
| `lkSh` | লক্ষ | ল্কষ |
| `skSh` | সক্ষ | স্কষ |
| `ShkSh` | ষক্ষ | ষ্কষ |
| `kShN` (resolved below) | ক্ষণ | ক্ষ্ণ |
| `kShm` (resolved below) | ক্ষম | ক্ষ্ম |
| `kShNgkSh` (resolved below) | ক্ষঙ্ক্ষ | ক্ষ্ণগক্ষ |
| `kShNG` | ক্ষঞ | ক্ষ্ণগ |
| `kShkk` (resolved below) | ক্ষকক | ক্ষক্ক |
| `rrkSh` | ররক্ষ | র্ক্ষ |
| `kSH` | কশH | ক্ষ |
| `KSh` | Kষ | ক্ষ |
| `kShA` | ক্ষA | ক্ষা |
| `` kSh`a `` | `` ক্ষ`আ `` | ক্ষআ |
| `` kSh`h `` | `` ক্ষ`হ `` | ক্ষহ |
| `` k`Sh `` | `` ক`ষ `` | কষ |
| `kSh.` | ক্ষ. | ক্ষ। |

Gap probes at that step covered `kkSh`, `kShN`, `kShm`, `kShNgkSh`, `rrkSh`,
`kSH`, and `` kSh`a ``. The next increment below adds exact
`kkhN`/`kShN`/`kxN` → ক্ষ্ণ and their supported vowel/context interactions,
checked independently for each spelling against the reference.
`kkhm`/`kShm`/`kxm`, unrelated earlier-prefix conflicts,
other conjuncts, reph, uppercase aliases, punctuation/escapes, composition, and platform integration
remain separate. Passing these fixtures does not establish full Avro compatibility.

The [later N-conjunct batch](#exact-kkhn-kshn-and-kxn-conjuncts)
resolves `kShN` and `kShNgkSh`; the outputs above record this earlier step.

## Exact kkhN, kShN and kxN conjuncts

Added on 2026-10-29: exact `kkhN`/`kShN`/`kxN` each produce ক্ষ্ণ
(U+0995 U+09CD U+09B7 U+09CD U+09A3), matching before shorter `kkh`/`kSh`/`kx`.
Independent checks confirmed shared vowel context and following-`r` behavior,
so the three forms share one branch. The 40 basic consonant sequences remain
unchanged. No upstream source, rule tables, fixtures, or dependencies were imported.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `kkhN` | ক্ষ্ণ | U+0995 U+09CD U+09B7 U+09CD U+09A3 |
| `kShNa` | ক্ষ্ণা | U+0995 U+09CD U+09B7 U+09CD U+09A3 U+09BE |
| `kxNee` | ক্ষ্ণী | U+0995 U+09CD U+09B7 U+09CD U+09A3 U+09C0 |
| `kxNr` | ক্ষ্ণ্র | U+0995 U+09CD U+09B7 U+09CD U+09A3 U+09CD U+09B0 |
| `kxNrri` | ক্ষ্ণৃ | U+0995 U+09CD U+09B7 U+09CD U+09A3 U+09C3 |
| `kxNry` | ক্ষ্ণ্র্য | U+0995 U+09CD U+09B7 U+09CD U+09A3 U+09CD U+09B0 U+09CD U+09AF |
| `kxNrry` | ক্ষ্ণরর‍্য | U+0995 U+09CD U+09B7 U+09CD U+09A3 U+09B0 U+09B0 U+200D U+09CD U+09AF |
| `NgkShN` | ঙ্ক্ষণ | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09A3 |
| `kShNgkSh` | ক্ষ্ণগক্ষ | U+0995 U+09CD U+09B7 U+09CD U+09A3 U+0997 U+0995 U+09CD U+09B7 |

All supported vowel signs and aliases apply, including `OI`/`OU`, `ee`/`oo`,
and `rri`; longer `aZ`/`oZ` keep priority. Existing transitions are preserved
(`kkhNia` → `ক্ষ্ণিয়া`, `kShNooo` → `ক্ষ্ণুঅ`). The final raw `N` selects
single-`r` attachment without U+200D before `y`/`Z`. In particular, `kxNry`
differs from `kxry` → `ক্ষর‍্য`. Two `r` keys normally add ্রর; `rri` and
`rry`/`rrZ` retain priority. One through eight following `r` keys were checked
for each spelling independently. This does not change basic `Nr` → `ণর`.

Earlier `Ngkkh`/`NgkSh`/`Ngkx` still consume their shorter conjunct before
the final `N`; `NgkkhN`/`NgkShN`/`NgkxN` all produce `ঙ্ক্ষণ`.
Case-distinct `NG`/`ng` prefixes allow the new forms (`NGkxN` → `ঞক্ষ্ণ`,
`ngkkhN` → `ংক্ষ্ণ`). Consuming `N` prevents a following `Ng` match:
`kkhNg`/`kShNg`/`kxNg` all produce `ক্ষ্ণগ`, and each can then match
`gkkh`/`gkSh`/`gkx` as `গক্ষ`. This resolves the former `kxNgx`, `kxNgk`,
`kxNgkh`, `kxNgkx`, `kxNgkkh`, and `kxNgkSh` gaps described above.
`kkhNG`/`kShNG`/`kxNG` now produce partial `ক্ষ্ণG`, while the reference
produces `ক্ষ্ণগ`: standalone uppercase `G` remains an alias gap, kept
separate from this batch as planned. They remain partial-output regressions.

The 1,231 independently authored fixtures
([410 `kkhN`](../../tests/fixtures/conjunct-kkhn.tsv),
[411 `kShN`](../../tests/fixtures/conjunct-kshn.tsv),
[410 `kxN`](../../tests/fixtures/conjunct-kxn.tsv)) were compared with the
SHA-256-verified pinned parser. The original 1,222 expectations were checked
before implementation; nine additional `g`-overlap cases were checked afterward.
They cover exact Unicode,
vowels/aliases and transitions, preceding contexts, nasal overlaps and priority,
following-`r` exceptions, repetition, raw spelling, all digits, boundaries,
copied Unicode, and selected words (`tIkShNo` → `তীক্ষ্ণ`). All 10,303 reference
cases match. Rust regressions additionally cover control-character boundaries,
separate calls, long mixed input, and partial outputs for remaining gaps.

| Input | Engine at that step | Reference |
| --- | --- | --- |
| `kkShN` | কক্ষ্ণ | ক্কষ্ণ |
| `kShm` (resolved below) | ক্ষম | ক্ষ্ম |
| `kShNG` | ক্ষ্ণG | ক্ষ্ণগ |
| `kShNkk` | ক্ষ্ণকক | ক্ষ্ণক্ক |
| `rrkShN` | ররক্ষ্ণ | র্ক্ষ্ণ |
| `kSHN` | কশHণ | ক্ষ্ণ |
| `` kShN`a `` | `` ক্ষ্ণ`আ `` | ক্ষ্ণআ |

Gap probes at that step covered these seven inputs. The next planned batch was exact
`kkhm`/`kShm`/`kxm` → ক্ষ্ম with independently checked vowels, following `r`,
and overlaps. Earlier-prefix conflicts, other conjuncts, reph, uppercase aliases,
punctuation/escapes, composition, and platform integration remain separate.
No normalization, persistent state, performance measurement, or platform
validation added. Passing these cases does not establish full Avro compatibility.

The [next increment](#exact-kkhm-kshm-and-kxm-conjuncts) resolves `kShm`;
the partial output above records this earlier step.

## Exact kkhm, kShm and kxm conjuncts

Added on 2026-10-29: exact `kkhm`/`kShm`/`kxm` each produce ক্ষ্ম
(U+0995 U+09CD U+09B7 U+09CD U+09AE), matching before shorter `kkh`/`kSh`/`kx`.
Each spelling's vowel context and following-`r` behavior was checked independently
before sharing one branch and the existing helper with final raw `m`.
No upstream source, rule tables, fixtures, or dependencies were imported.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `kkhm` | ক্ষ্ম | U+0995 U+09CD U+09B7 U+09CD U+09AE |
| `kShma` | ক্ষ্মা | U+0995 U+09CD U+09B7 U+09CD U+09AE U+09BE |
| `kxmI` | ক্ষ্মী | U+0995 U+09CD U+09B7 U+09CD U+09AE U+09C0 |
| `kxmr` | ক্ষ্ম্র | U+0995 U+09CD U+09B7 U+09CD U+09AE U+09CD U+09B0 |
| `kxmrri` | ক্ষ্মৃ | U+0995 U+09CD U+09B7 U+09CD U+09AE U+09C3 |
| `kxmry` | ক্ষ্ম্র্য | U+0995 U+09CD U+09B7 U+09CD U+09AE U+09CD U+09B0 U+09CD U+09AF |
| `kxmrry` | ক্ষ্মরর‍্য | U+0995 U+09CD U+09B7 U+09CD U+09AE U+09B0 U+09B0 U+200D U+09CD U+09AF |
| `NgkShm` | ঙ্ক্ষম | U+0999 U+09CD U+0995 U+09CD U+09B7 U+09AE |
| `kShmng` | ক্ষ্মং | U+0995 U+09CD U+09B7 U+09CD U+09AE U+0982 |

Supported vowels and aliases include `OI`/`OU`, `ee`/`oo`, and `rri`;
longer `aZ`/`oZ` keep priority. Existing vowel transitions are preserved
(`kkhmia` → `ক্ষ্মিয়া`, `kShmooo` → `ক্ষ্মুঅ`). Single `r` attaches without
U+200D before `y`/`Z`. Two `r` keys normally add ্রর, while `rri` and
`rry`/`rrZ` keep priority. One through eight following `r` keys were checked
for each spelling independently. That increment did not implement basic `mr` → ম্র;
the [nasal/h batch](conjunct-batches.md#nasal-and-h-conjunct-batch) now adds it.

Earlier `Ngkkh`/`NgkSh`/`Ngkx` still consume their shorter form before the final
`m`, producing `ঙ্ক্ষম` rather than `ঙ্ক্ষ্ম`. Case-distinct `NG`/`ng` allow the
new forms (`NGkxm` → `ঞক্ষ্ম`, `ngkkhm` → `ংক্ষ্ম`). Consuming `m` prevents
it joining the next `m` or nasal sequence: `kShmm` → `ক্ষ্মম`,
`kShmn` → `ক্ষ্মন`, `kShmNg` → `ক্ষ্মঙ`, `kShmNG` → `ক্ষ্মঞ`, and
`kShmng` → `ক্ষ্মং`. Following lowercase `ng` still uses its existing vowel
priority (`kShmnga` → `ক্ষ্মঙ্গা`, `kShmngee` → `ক্ষ্মঙ্গেএ`). Existing
`kkhN`/`kShN`/`kxN` matching stays separate.

All 1,196 independently authored fixtures
([399 `kkhm`](../../tests/fixtures/conjunct-kkhm.tsv),
[399 `kShm`](../../tests/fixtures/conjunct-kshm.tsv),
[398 `kxm`](../../tests/fixtures/conjunct-kxm.tsv)) were verified against the
SHA-256-checked pinned parser before implementation. They cover exact Unicode,
vowels/aliases and transitions, preceding contexts, earlier and adjacent matches,
following-`r` exceptions, nasal overlaps, repetition, raw spelling, all digits,
boundaries, copied Unicode, and words (`lokkhmI`/`lokShmI`/`lokxmI` → `লক্ষ্মী`,
`sUkkhmo`/`sUkShmo`/`sUkxmo` → `সূক্ষ্ম`). All 11,499 reference cases match.
Rust regressions also cover control characters, separate calls, long mixed
input, and partial outputs for remaining gaps.

| Input | Engine at that step | Reference |
| --- | --- | --- |
| `kkShm` | কক্ষ্ম | ক্কষ্ম |
| `kShmmm` | ক্ষ্মমম | ক্ষ্মম্ম |
| `NgkShmr` | ঙ্ক্ষমর | ঙ্ক্ষম্র |
| `kShM` | ক্ষM | ক্ষ্ম |
| `kShmgr` | ক্ষ্মগর | ক্ষ্মগ্র |
| `rrkShm` | ররক্ষ্ম | র্ক্ষ্ম |
| `` kShm`a `` | `` ক্ষ্ম`আ `` | ক্ষ্মআ |
| `mng` | মং | ম্নগ |
| `kShNG` | ক্ষ্ণG | ক্ষ্ণগ |

Probes at that step covered these nine gaps. Earlier `kk`/`nk`/`lk`/`sk`/`Shk`
matches consumed the initial `k` before the selected form; all five
prefixes were checked for each spelling and retained as partial-output regressions
at that step. The [later `kk` increment](#exact-kk-conjunct) changes the `k`-prefix
outputs; at that step, `kkShm` still reached an unimplemented `Shm` rule.
The [later `ShN`/`Shm` batch](#exact-shn-and-shm-conjuncts) resolves it.
Basic `mr`/`mm`/`mn` and the `mng`/`kShmmm`/`NgkShmr` gaps are now resolved
by the [nasal/h batch](conjunct-batches.md#nasal-and-h-conjunct-batch). At that step, adjacent
unimplemented conjuncts, uppercase aliases, reph, and punctuation/escapes remained separate. The next planned step was to check
exact `kk` → ক্ক and its priority over existing k-conjuncts against the reference.
Composition and Fcitx5 remain later work. No normalization, persistent state,
performance measurement, or platform validation added; full Avro compatibility
is not established.

## Exact kk conjunct

Added on 2026-10-29: exact `kk` produces ক্ক (U+0995 U+09CD U+0995).
It matches after longer `kkh`/`kkhN`/`kkhm` and earlier `Ng` forms, before basic
`k`/`kh`. Its vowel context and following-`r` behavior were independently checked
before reusing the existing helper with final raw `k`. No upstream code, rule
tables, fixtures, or dependencies were imported.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `kk` | ক্ক | U+0995 U+09CD U+0995 |
| `kka` | ক্কা | U+0995 U+09CD U+0995 U+09BE |
| `kkI` | ক্কী | U+0995 U+09CD U+0995 U+09C0 |
| `kkr` | ক্ক্র | U+0995 U+09CD U+0995 U+09CD U+09B0 |
| `kkrri` | ক্কৃ | U+0995 U+09CD U+0995 U+09C3 |
| `kkry` | ক্ক্র্য | U+0995 U+09CD U+0995 U+09CD U+09B0 U+09CD U+09AF |
| `kkrry` | ক্করর‍্য | U+0995 U+09CD U+0995 U+09B0 U+09B0 U+200D U+09CD U+09AF |
| `kkkh` | ক্কখ | U+0995 U+09CD U+0995 U+0996 |
| `kkSh` | ক্কষ | U+0995 U+09CD U+0995 U+09B7 |
| `kkx` | ক্কক্স | U+0995 U+09CD U+0995 U+0995 U+09CD U+09B8 |
| `Ngkk` | ঙ্কক | U+0999 U+09CD U+0995 U+0995 |

Supported vowels include `OI`/`OU`, `ee`/`oo`, and `rri`. Longer `aZ`/`oZ`
keep priority (`kkaZ` → `ক্কঅ্যা`). Existing vowel transitions are preserved
(`kkia` → `ক্কিয়া`, `kkooo` → `ক্কুঅ`). Single `r` attaches without U+200D
before `y`/`Z`. Two `r` keys normally add ্রর, except `rri` and `rry`/`rrZ`.
One through eight following `r` keys were checked, along with following vowels,
ya forms, `Y`, `w`, and `x`. That step did not implement basic `kr` → ক্র;
it is covered by the later
[basic following-`r` batch](#following-r-after-basic-k-kh-and-sh).

Matching consumes input from left to right. `kkh`, `kkhN`, and `kkhm` keep
their existing priority over `kk`, so ক্ষ/ক্ষ্ণ/ক্ষ্ম forms are preserved.
But the initial `kk` prevents a `kkh`/`kSh`/`kx` match starting at its second
key. This corrects earlier partial outputs for `kkkh`, `kkSh`, `kkx`,
`kkkhN` → `ক্কখণ`, `kkkhm` → `ক্কখম`, `kkxN` → `ক্কক্সণ`, and
`kkxm` → `ক্কক্সম`. At that step it exposed separate `ShN`/`Shm` gaps in `kkShN`/`kkShm`,
resolved by the [next batch](#exact-shn-and-shm-conjuncts).
Earlier `Ngk` still consumes the first `k` in `Ngkk`; longer `Ngkkh` and
its trailing `N`/`m` behavior stay unchanged. Case-distinct `NGkk` → `ঞক্ক`
and `ngkk` → `ংক্ক` now match. Repeated and adjacent matches work
(`kkkk` → `ক্কক্ক`, `kkhkk` → `ক্ষক্ক`, `kkkkh` → `ক্কক্ষ`).

All 501 [independently authored fixtures](../../tests/fixtures/conjunct-kk.tsv)
were verified against the SHA-256-checked pinned parser before implementation.
They cover Unicode, vowels/aliases and transitions, preceding contexts,
following-`r` priority, overlaps with existing k-conjuncts and `Ng` forms,
one through twelve `k` keys, all digits, boundaries, copied Unicode,
raw-spelling controls, and words (`Dhakka` → `ঢাক্কা`, `dhakka` → `ধাক্কা`,
`pakka` → `পাক্কা`, `akkel` → `আক্কেল`). All 12,000 reference cases match.
Rust regressions also cover control boundaries, separate calls, long mixed
input, and explicit partial outputs for remaining gaps.

| Input | Engine at that step | Reference |
| --- | --- | --- |
| `kkShN` | ক্কষণ | ক্কষ্ণ |
| `kkShm` | ক্কষম | ক্কষ্ম |
| `kkkhr` | ক্কখর | ক্কখ্র |
| `kkShr` | ক্কষর | ক্কষ্র |
| `Ngkkr` | ঙ্ককর | ঙ্কক্র |
| `nkk` | নক্ক | ঙ্কক |
| `kkH` | ক্কH | ক্ষ |
| `rrkk` | ররক্ক | র্ক্ক |
| `` kk`a `` | `` ক্ক`আ `` | ক্কআ |

Probes at that step covered these nine gaps. `lk`/`sk`/`Shk`, basic following-`r`
attachment, uppercase aliases (including `kK`/`Kk`/`KK` and `kkhNG`), reph,
and punctuation/escapes remained separate. The next planned batch was exact
`ShN`/`Shm` → ষ্ণ/ষ্ম, independently checking vowel/context and following-`r`
behavior, plus `kkShN`/`kkShm` and existing `kShN`/`kShm` priority.
Composition and Fcitx5 remain later work. No normalization, persistent state,
performance measurement, or platform validation added; full Avro compatibility
is not established.

## Exact ShN and Shm conjuncts

Added on 2026-10-29: exact `ShN` produces ষ্ণ (U+09B7 U+09CD U+09A3) and
`Shm` produces ষ্ম (U+09B7 U+09CD U+09AE), before basic `Sh` matching.
Each spelling's Unicode, vowel/context behavior, following-`r` priority, and
nasal overlaps were independently checked against the pinned parser. Two small
branches reuse the existing helper with final raw `N` and `m` respectively.
No upstream code, rule tables, fixtures, or dependencies were imported.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `ShN` | ষ্ণ | U+09B7 U+09CD U+09A3 |
| `Shm` | ষ্ম | U+09B7 U+09CD U+09AE |
| `ShNa` | ষ্ণা | U+09B7 U+09CD U+09A3 U+09BE |
| `ShmI` | ষ্মী | U+09B7 U+09CD U+09AE U+09C0 |
| `ShNr` | ষ্ণ্র | U+09B7 U+09CD U+09A3 U+09CD U+09B0 |
| `Shmrri` | ষ্মৃ | U+09B7 U+09CD U+09AE U+09C3 |
| `Shmry` | ষ্ম্র্য | U+09B7 U+09CD U+09AE U+09CD U+09B0 U+09CD U+09AF |
| `ShNrry` | ষ্ণরর‍্য | U+09B7 U+09CD U+09A3 U+09B0 U+09B0 U+200D U+09CD U+09AF |
| `kkShN` | ক্কষ্ণ | U+0995 U+09CD U+0995 U+09B7 U+09CD U+09A3 |
| `kkShm` | ক্কষ্ম | U+0995 U+09CD U+0995 U+09B7 U+09CD U+09AE |
| `ShNgx` | ষ্ণগক্স | U+09B7 U+09CD U+09A3 U+0997 U+0995 U+09CD U+09B8 |
| `Shmng` | ষ্মং | U+09B7 U+09CD U+09AE U+0982 |

Both spellings support the existing vowels and aliases, including `OI`/`OU`,
`ee`/`oo`, and `rri`. Longer `aZ`/`oZ` keep priority (`ShNaZ` → `ষ্ণঅ্যা`).
Vowel transitions remain unchanged (`ShNia` → `ষ্ণিয়া`, `Shmooo` → `ষ্মুঅ`).
Single `r` attaches without U+200D before `y`/`Z`; two `r` keys normally add
্রর, except `rri` and `rry`/`rrZ`. Each spelling was checked with one through
eight following `r` keys and following vowels/ya forms/`Y`/`w`/`x` independently.
That step did not implement basic `Shr` → ষ্র; it is covered by the later
[basic following-`r` batch](#following-r-after-basic-k-kh-and-sh).

Earlier `kShN`/`kShm` retain their ক্ষ্ণ/ক্ষ্ম matches; `NgkSh` still consumes
its shorter form before the final nasal (`NgkShN` → `ঙ্ক্ষণ`, `NgkShm` → `ঙ্ক্ষম`).
After `kk`, the remaining `ShN`/`Shm` now match, resolving `kkShN`/`kkShm`.
Consuming the `N` before a following `g` prevents the former `Ng` match,
resolving `ShNgx`, `ShNgk` → `ষ্ণগক`, `ShNgkh` → `ষ্ণগখ`, and
`ShNgkx`/`ShNgkkh`/`ShNgkSh` → `ষ্ণগক্ষ`. Following uppercase `G` remains
a separate normalization gap. Consuming `m` keeps the next nasal separate:
`Shmm` → `ষ্মম`, `Shmn` → `ষ্মন`, `ShmNg` → `ষ্মঙ`, `ShmNG` → `ষ্মঞ`,
`Shmng` → `ষ্মং`. Following lowercase `ng` keeps its existing vowel priority
(`Shmngee` → `ষ্মঙ্গেএ`, `Shmngoo` → `ষ্মঙ্গঅ`).

All 933 independently authored fixtures
([465 `ShN`](../../tests/fixtures/conjunct-shn.tsv),
[468 `Shm`](../../tests/fixtures/conjunct-shm.tsv)) were verified against the
SHA-256-checked pinned parser before implementation. They cover Unicode,
vowels/aliases and transitions, preceding contexts, following-`r` priority,
nasal overlaps, earlier/adjacent matches, repetition, all digits, boundaries,
copied Unicode, raw-spelling controls, and words (`biShNu` → `বিষ্ণু`,
`uShNo` → `উষ্ণ`, `uShma` → `উষ্মা`, `uShmota` → `উষ্মতা`). All 12,933
reference cases match. Rust regressions also cover control boundaries, separate
calls, long mixed input, and explicit partial outputs for remaining gaps.

| Input | Engine at that step | Reference |
| --- | --- | --- |
| `ShNG` | ষ্ণG | ষ্ণগ |
| `ShNgr` | ষ্ণগর | ষ্ণগ্র |
| `Shmgr` | ষ্মগর | ষ্মগ্র |
| `Shmmm` | ষ্মমম | ষ্মম্ম |
| `ShNmng` | ষ্ণমং | ষ্ণম্নগ |
| `NgkShmr` | ঙ্ক্ষমর | ঙ্ক্ষম্র |
| `ShM` | ষM | ষ্ম |
| `rrShN` | ররষ্ণ | র্ষ্ণ |
| `` Shm`a `` | `` ষ্ম`আ `` | ষ্মআ |

Probes at that step covered these nine gaps. The later
[basic `g`/`gh` batch](#following-r-after-basic-g-and-gh) resolves `ShNgr`/`Shmgr`.
The [nasal/h batch](conjunct-batches.md#nasal-and-h-conjunct-batch) now resolves basic `mr`/`mm`/`mn`
and the `Shmmm`/`ShNmng`/`NgkShmr` gaps. Earlier `nk`/`lk`/`sk`/`Shk`,
lowercase `shn`/`shm` and `Sm`, uppercase aliases, reph, and punctuation/escapes
remain separate. The next
planned batch at that step was following `r` after basic `k`/`kh`/`Sh`,
independently checking each spelling's attachment, longer `r` runs, ya joiners,
and priority against existing conjuncts. Composition and Fcitx5 remain later work. No normalization,
persistent state, performance measurement, or platform validation added; full
Avro compatibility is not established.

## Following r after basic k, kh and Sh

Added on 2026-10-29: basic `k`, `kh`, and `Sh` attach following `r` as
্র (U+09CD U+09B0). Each spelling was independently checked against the
SHA-256-verified pinned parser before implementation. The basic-consonant
branch now calls the existing helper with final raw key `k` or `h` for these
three spellings. This is an independently implemented behavioral extension;
no upstream source, tables, fixtures, or dependencies were imported.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `kr` | ক্র | U+0995 U+09CD U+09B0 |
| `khr` | খ্র | U+0996 U+09CD U+09B0 |
| `Shr` | ষ্র | U+09B7 U+09CD U+09B0 |
| `kri` | ক্রি | U+0995 U+09CD U+09B0 U+09BF |
| `khry` | খ্র্য | U+0996 U+09CD U+09B0 U+09CD U+09AF |
| `ShrZ` | ষ্র্য | U+09B7 U+09CD U+09B0 U+09CD U+09AF |
| `krr` | ক্রর | U+0995 U+09CD U+09B0 U+09B0 |
| `khrri` | খৃ | U+0996 U+09C3 |
| `Shrry` | ষরর‍্য | U+09B7 U+09B0 U+09B0 U+200D U+09CD U+09AF |
| `kkkhr` | ক্কখ্র | U+0995 U+09CD U+0995 U+0996 U+09CD U+09B0 |
| `kkShr` | ক্কষ্র | U+0995 U+09CD U+0995 U+09B7 U+09CD U+09B0 |
| `Ngkkr` | ঙ্কক্র | U+0999 U+09CD U+0995 U+0995 U+09CD U+09B0 |

Single `r` attaches without U+200D and keeps consonant context for supported
vowels, aliases, and ya forms. Two `r` keys normally add ্রর; `rri` instead
produces the vowel sign ৃ, while `rry`/`rrZ` leave রর followed by U+200D and
ya-phala (্য). Each spelling was checked with one through eight `r` keys,
following vowels/aliases, `y`/`Z`/`Y`, `w`, and `x`. Existing vowel transitions
and longer `aZ`/`oZ` priority remain (`kraZ` → `ক্রঅ্যা`).

Earlier `kk`, `kkh`/`kSh`, their `N`/`m` conjuncts, `kxN`/`kxm`, `ShN`/`Shm`,
and `Ng` matches keep priority. The basic keys left after those matches now
attach `r`, resolving the three overlap gaps in the table. For example,
`Ngkkhr` still produces ঙ্ক্ষ্র through the earlier `Ngkkh` match, while
`kkkhr` uses `kk` followed by basic `kh`. Raw spelling still matters:
`kR` → `কড়`, `khR` → `খড়`, `ShR` → `ষড়`; at that step `qr` gave partial `কর`,
resolved by the later [following-r batch](case-symbols-reph.md#following-r-after-q-z-r-and-rh).
Copied Unicode resets context (`কr` → `কর`, `খr` → `খর`, `ষr` → `ষর`).

The 1,427 independently authored fixtures
([475 `k`](../../tests/fixtures/k-following-r.tsv),
[476 `kh`](../../tests/fixtures/kh-following-r.tsv),
[476 `Sh`](../../tests/fixtures/sh-following-r.tsv)) cover exact Unicode,
vowels/aliases and transitions, preceding contexts, longer `r` runs and
exceptions, earlier matches, repetition, all digits, boundaries, copied
Unicode, spelling controls, and examples (`kromo` → `ক্রম`, `krriShNo` → `কৃষ্ণ`).
All 14,360 reference cases match. Rust regressions also check control-character
boundaries, separate calls, and long mixed input.

At that step, other basic following-`r` forms (`gr`/`ghr`/`hr`/`mr`/`qr`), earlier
`nk`/`lk`/`sk`/`Shk` and `gN` matches, uppercase aliases, reph, and
punctuation/escapes remained incomplete. The next proposed batch was
[basic `g`/`gh` following `r`](#following-r-after-basic-g-and-gh). Composition and Fcitx5
remain later work. No performance or platform support claim is added.

## Following r after basic g and gh

Added on 2026-10-29: basic `gr` produces গ্র (U+0997 U+09CD U+09B0), and
`ghr` produces ঘ্র (U+0998 U+09CD U+09B0). Each spelling's exact Unicode,
vowel/ya context, repeated `r`, and overlapping matches were independently
checked against the SHA-256-verified pinned parser before implementation.
The basic-consonant branch reuses the existing following-`r` helper: final raw
`g` now allows single-r attachment, and `gh` uses its final `h`. No upstream
source, rule tables, fixtures, or dependencies were imported.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `gr` | গ্র | U+0997 U+09CD U+09B0 |
| `ghr` | ঘ্র | U+0998 U+09CD U+09B0 |
| `grI` | গ্রী | U+0997 U+09CD U+09B0 U+09C0 |
| `ghry` | ঘ্র্য | U+0998 U+09CD U+09B0 U+09CD U+09AF |
| `grr` | গ্রর | U+0997 U+09CD U+09B0 U+09B0 |
| `ghrri` | ঘৃ | U+0998 U+09C3 |
| `grry` | গরর‍্য | U+0997 U+09B0 U+09B0 U+200D U+09CD U+09AF |
| `ShNgr` | ষ্ণগ্র | U+09B7 U+09CD U+09A3 U+0997 U+09CD U+09B0 |
| `Shmgr` | ষ্মগ্র | U+09B7 U+09CD U+09AE U+0997 U+09CD U+09B0 |
| `kShmgr` | ক্ষ্মগ্র | U+0995 U+09CD U+09B7 U+09CD U+09AE U+0997 U+09CD U+09B0 |

Both spellings keep consonant context for supported vowels and aliases, including
`OI`/`OU`, `ee`/`oo`, and ya forms. Single `r` attaches without U+200D;
two `r` keys normally add ্রর. The `rri` exception gives the vowel sign ৃ;
`rry`/`rrZ` leave রর followed by U+200D and ya-phala (্য). Each spelling
was checked with one through eight `r` keys, vowels/aliases, `y`/`Z`/`Y`, `w`,
and `x`. Vowel transitions and longer `aZ`/`oZ` priority stay unchanged.

Existing `Ng` forms and k-conjuncts keep priority. The `g` remaining after
`ShN`, `Shm`, and the ক্ষ্ম spellings now attaches `r`, resolving `ShNgr`,
`Shmgr`, `kkhmgr`, `kShmgr`, and `kxmgr`. Raw matches still control behavior:
`Ngr` → `ঙর` and `Ngrri` → `ঙররি` consume `g` before the basic branch;
`NGgr` → `ঞগ্র` and `ngghr` → `ংঘ্র` leave basic `g`/`gh` available.
Copied Unicode resets context (`গr` → `গর`, `ঘr` → `ঘর`), as do digits
and separators. Case distinctions remain (`gR` → `গড়`, `ghR` → `ঘড়`).

The 948 independently authored fixtures
([475 `g`](../../tests/fixtures/g-following-r.tsv),
[473 `gh`](../../tests/fixtures/gh-following-r.tsv)) cover exact Unicode,
vowels/aliases and transitions, preceding contexts, earlier matches, longer `r`
runs and exceptions, repetition, all digits, boundaries, copied Unicode,
spelling controls, and words (`grIShmo` → `গ্রীষ্ম`, `ghraN` → `ঘ্রাণ`,
`ghrriNa` → `ঘৃণা`). All 15,308 reference cases match. Rust regressions also
cover control-character boundaries, separate calls, long mixed input, and
explicit partial outputs for earlier matches outside this slice.

| Input | Engine at that step | Reference |
| --- | --- | --- |
| `Nggr` | ঙগ্র | ঙ্গ্র |
| `Ngghr` | ঙঘ্র | ঙ্ঘ্র |
| `dgr` | দগ্র | দ্গ্র |
| `Rghr` | ড়ঘ্র | ড়্গহ্র |
| `ggr` | গগ্র | জ্ঞ্র |
| `gNgr` | গঙর | গ্ণগ্র |

At that step, the reference's earlier `dg`/`dgh`, `Rg`, `gg`, `gN`, and `Ngg`/`Nggh`
matches remained separate gaps. The nine reference probes then replaced
resolved `ShNgr`/`Shmgr` with `Nggr`/`Ngghr`. Exact `Ngg`/`Nggh` is the next
batch completed [below](#exact-ngg-and-nggh-conjuncts). Other basic following-`r` forms,
uppercase aliases, reph, punctuation/escapes, composition, and Fcitx5 remain
incomplete. No performance measurement or platform validation was added.

## Exact Ngg and Nggh conjuncts

Added on 2026-10-29: exact `Ngg` produces ঙ্গ (U+0999 U+09CD U+0997), and
`Nggh` produces ঙ্ঘ (U+0999 U+09CD U+0998). Each spelling was independently
checked against the SHA-256-verified pinned parser for exact Unicode, vowels,
ya forms, following `r`, and overlapping matches before engine changes.
The independently authored branches match `Nggh` before `Ngg`, then before
basic `Ng` and `g`/`gh`, and reuse the existing following-`r` helper with final
raw `h`/`g`. No upstream source, tables, fixtures, or dependencies were imported.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `Ngg` | ঙ্গ | U+0999 U+09CD U+0997 |
| `Nggh` | ঙ্ঘ | U+0999 U+09CD U+0998 |
| `Nggi` | ঙ্গি | U+0999 U+09CD U+0997 U+09BF |
| `Ngghy` | ঙ্ঘ্য | U+0999 U+09CD U+0998 U+09CD U+09AF |
| `Nggr` | ঙ্গ্র | U+0999 U+09CD U+0997 U+09CD U+09B0 |
| `Ngghr` | ঙ্ঘ্র | U+0999 U+09CD U+0998 U+09CD U+09B0 |
| `Nggrri` | ঙ্গৃ | U+0999 U+09CD U+0997 U+09C3 |
| `NgghrrZ` | ঙ্ঘরর‍্য | U+0999 U+09CD U+0998 U+09B0 U+09B0 U+200D U+09CD U+09AF |
| `Nggg` | ঙ্গগ | U+0999 U+09CD U+0997 U+0997 |
| `NggN` | ঙ্গণ | U+0999 U+09CD U+0997 U+09A3 |
| `NgNggr` | ঙঙ্গ্র | U+0999 U+0999 U+09CD U+0997 U+09CD U+09B0 |

Both establish consonant context for all supported vowels and aliases,
including `ee`/`oo`, `OI`/`OU`, and `rri`, and for ya forms without U+200D.
Longer `aZ`/`oZ` keep priority (`NggaZ` → `ঙ্গঅ্যা`). Single `r` attaches as
্র without a joiner; two `r` keys normally add ্রর. The `rri` exception produces
ৃ, while `rry`/`rrZ` leave রর followed by U+200D and ya-phala. Each spelling
was independently checked with one through eight `r` keys, supported vowels,
`y`/`Z`/`Y`, `w`, and `x`.

Consuming the final `g` prevents a later `gg`/`gN` match from starting there
(`Nggg`/`NggN` above); `Ngggh` becomes ঙ্গঘ through `Ngg` then basic `gh`.
Existing `Ng`/`ng`/`NG` and k-conjuncts retain priority. In particular,
`ShN`, `kkhN`, `kShN`, and `kxN` consume `N` first, leaving a separate `gg`
gap. Those are recorded as partial engine outputs, not compatibility fixtures.
Other earlier nasal matches also remain gaps:

| Input | Engine at that step | Reference |
| --- | --- | --- |
| `gNgg` | গঙ্গ | গ্ণজ্ঞ |
| `NNgg` | ণঙ্গ | ণ্ণজ্ঞ |
| `hNgg` | হঙ্গ | হ্ণজ্ঞ |
| `ShNggr` | ষ্ণগগ্র | ষ্ণজ্ঞ্র |
| `kShNgghr` | ক্ষ্ণগঘ্র | ক্ষ্ণজ্ঞহ্র |

Case still matters (`NGgr` → `ঞগ্র`, `nggr` → `ংগ্র`), as do raw boundaries:
copied ঙ্গ/ঙ্ঘ resets context (`ঙ্গr` → `ঙ্গর`), as do digits and separators.
The 1,062 independently authored fixtures
([531 `Ngg`](../../tests/fixtures/conjunct-ngg.tsv),
[531 `Nggh`](../../tests/fixtures/conjunct-nggh.tsv)) cover vowels and transitions,
preceding contexts, following `r` and exceptions, existing matches, adjacent
consonants/nasals, repetition, all digits, boundaries, copied Unicode, spelling
controls, and words (`bhaNgga` → `ভাঙ্গা`, `loNgghon` → `লঙ্ঘন`).
All 16,370 reference cases match. Rust regressions also cover control-character
boundaries, separate calls, long mixed input, and the partial outputs above.

The nine reference probes now replace resolved `Nggr`/`Ngghr` with
`ShNggr`/`kShNgghr`. The next planned batch investigates exact `gg`/`gN`/`NN`/`hN`,
including those exposed overlaps, subject to independent checks and the
[larger-batch workflow decision](../v1.md#small-development-steps). These four spellings,
`dg`/`dgh`/`Rg`, other following-`r` forms, uppercase aliases, reph, and
punctuation/escapes remain incomplete. Composition and Fcitx5 remain later
work. No performance measurement or platform validation was added.
