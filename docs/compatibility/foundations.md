# Phonetic foundations and basic consonants

Historical compatibility evidence, grouped by rule family. The outputs, counts
and unresolved gaps below describe each dated implementation stage. Use the
[current requirements](../v1.md), [compatibility policy](../compatibility.md)
and regression fixtures for current behavior. These records do not form a bug
tracker. Other rule families are indexed in
[Historical conversion increments](../compatibility.md#historical-conversion-increments).

## First conversion slice

Implemented on 2026-10-28 as a single Rust library package, `jong-bangla-core`.
`transliterate(&str) -> String` performs conversion without platform APIs, mutable
composition state, external dependencies, or input persistence. Rust 2024 edition
and Rust/Cargo 1.99.1 are the initial development baseline, matching the validated
current stable toolchain. Older toolchains have not been tested.

The initial sequence set is deliberately small; the vowel groups below extend
this baseline:

| Raw input | Output | Unicode |
| --- | --- | --- |
| `k`, `kh` | ক, খ | U+0995, U+0996 |
| `g`, `gh` | গ, ঘ | U+0997, U+0998 |
| `t`, `th` | ত, থ | U+09A4, U+09A5 |
| `T`, `Th` | ট, ঠ | U+099F, U+09A0 |
| `n`, `N` | ন, ণ | U+09A8, U+09A3 |
| `b`, `bh` | ব, ভ | U+09AC, U+09AD |
| `m` | ম | U+09AE |
| `0`–`9` | ০–৯ | U+09E6–U+09EF |

In the initial slice, the longest supported consonant sequence was selected at
each input position, with exact case matching. Otherwise one complete Unicode
character was copied unchanged. The vowel groups add context below.
Unsupported sequences can contain supported parts, so preservation applies to
unmatched characters, not necessarily an entire word. No Unicode normalization
is performed. Existing Bangla, non-ASCII digits, and other unmatched Unicode
characters are preserved. This slice does not provide composition controls;
those require the later controller. The originally planned literal Latin
candidate was deferred beyond v1 on 2026-10-29.

Reference-checked cases cover the 13 consonant sequences individually, all ten
digits individually and together, `kh12T`, `t T th Th n N`, and `[2026]`.
The fixtures were authored for this project; no upstream tests or rule tables
were imported. The external reference parser was downloaded only to a temporary
directory and evaluated for comparison with Node.js v24.21.0. Its SHA-256 is
`312ed3438ebf0a69f6de38036572ec39cdbafe3ef53f500caa402aaa704c2b32`.

Initial gaps observed with the same reference parser (`a` and `ka` are now
resolved by the first vowel group below):

| Input | Initial slice | Reference | Missing behavior |
| --- | --- | --- | --- |
| `a` | a | আ (U+0986) | Independent vowels |
| `ka` | কa | কা (U+0995 U+09BE) | Contextual vowel signs |
| `kkh` | কখ | ক্ষ (U+0995 U+09CD U+09B7) | Conjunct sequences |
| `K` | K | ক (U+0995) | Case normalization for some letters |
| `` k`h `` | ক`h | কহ (U+0995 U+09B9) | Escape handling and unsupported `h` |

These are temporary coverage limits, not intended v1 behavior. Punctuation and
backticks are currently literal; they do not commit text or apply phonetic
rules. Arbitrary concatenations of supported consonants are not a compatibility
claim because longer or contextual rules are still absent. Backspace, commit,
cancel, focus handling, and platform testing remain later work.

## First vowel group

Added on 2026-10-28: lowercase `a` and `i`, with context tracked locally during
each conversion call. This is transliteration context, not editable composition
state, and nothing is retained between calls.

| Context | `a` | `i` |
| --- | --- | --- |
| Start, or after a digit/unmatched character | আ (U+0986) | ই (U+0987) |
| Immediately after a supported consonant token | া (U+09BE) | ি (U+09BF) |
| Immediately after lowercase `i` | য়া (U+09DF U+09BE) | ই (U+0987) |
| Immediately after lowercase `a` | আ (U+0986) | ই (U+0987) |

For example, `ka` now produces `কা`, `ki` produces `কি`, `ami` produces `আমি`,
and `kia` produces `কিয়া`. The vowel sign for `i` is encoded after its consonant
(U+0995 U+09BF in `কি`), even though a font displays the sign to its left. The
`য়` in the `ia` sequence is U+09DF, matching the reference exactly; the engine
does not normalize or substitute a visually similar Unicode sequence.

Only recognized consonant tokens establish consonant context. Existing Bangla,
emoji, punctuation, whitespace, combining marks, digits, and unsupported Latin
letters end that context. Thus `কi` produces `কই`, and `k1a` produces `ক১আ`.
This prevents vowel signs from attaching to copied Unicode text. Vowel context
also ends at such characters: `i a` produces `ই আ`, without an inserted `য়`.

The 66 independently authored [vowel cases](../../tests/fixtures/vowels.tsv) cover
each supported consonant with both vowels, repeated and adjacent vowels, digits,
word separators, mixed Unicode, and several words. Their expected output and
code points were checked against the pinned parser before the Rust rules were
implemented. Together with the original 27 cases, all 93 match. The Rust tests
also check control-character boundaries, combining marks, and separate calls.

That increment left uppercase `A`/`I`, other vowels, and context after unsupported
Latin consonants unimplemented. The next group below adds `u`/`U`.
At this step, `qa` produced `qআ` while the reference produces `কা`;
the later [lowercase `q` increment](#basic-lowercase-q-consonant) resolves that gap.
Backtick escapes still pass through literally: `` i` `` produces `ই` followed
by a backtick, while the reference produces U+09BF alone. No broader compatibility,
composition, or platform support is established by this increment.

## Second vowel group

Added on 2026-10-28: case-sensitive `u` and `U`, extending the same conversion-local
context used by `a`/`i`.

| Context | `u` | `U` |
| --- | --- | --- |
| Start, or after a digit/unmatched character | উ (U+0989) | ঊ (U+098A) |
| Immediately after a supported consonant token | ু (U+09C1) | ূ (U+09C2) |
| Immediately after any supported vowel | উ (U+0989) | ঊ (U+098A) |

An `a` immediately after `u` or `U` produces য়া (U+09DF U+09BE), as it already
does after `i`. Thus `kua` → `কুয়া` and `kUa` → `কূয়া`. An `i` after either form
remains independent: `kui` → `কুই`, `kUi` → `কূই`. Repeated vowels are separate:
`uu` → `উউ`, `uU` → `উঊ`, `Uu` → `ঊউ`, `UU` → `ঊঊ`.

Case remains meaningful: `bhumi` → `ভুমি`, `bhUmi` → `ভূমি`. Both results follow
the typed sequence without a dictionary or spelling correction. Other examples
include `tumi` → `তুমি` and `khuki` → `খুকি`.

The 80 new [fixtures](../../tests/fixtures/vowels-u.tsv) were independently authored
and reference-checked before the Rust changes. They cover both vowels with all
13 supported consonants, all vowel pairs involving `u`/`U` and existing `a`/`i`,
neighboring-vowel transitions, digits, boundaries, mixed Unicode, and words.
All 173 cases now match the pinned parser. Existing context boundaries and
per-call reset behavior apply to both new vowels; for example, `কU` → `কঊ`,
`k1u` → `ক১উ`, and `u a` → `উ আ`.

That increment left uppercase `A`/`I`, remaining vowels, unsupported consonants,
conjuncts, and phonetic punctuation/escapes unimplemented. The next group below
adds `I`. In particular, `` u` `` remains `উ` followed
by a backtick rather than the reference's standalone U+09C1 sign. The gap probes
at that step were `I`, `kkh`, `K`, `` k`h ``, and `` u` ``.
No dependencies, composition controls, or platform integration were added.

## Third vowel group

Added on 2026-10-28: uppercase `I`, preserving the distinction from lowercase `i`.

| Context | `I` output |
| --- | --- |
| Start, or after a digit/unmatched character or supported vowel | ঈ (U+0988) |
| Immediately after a supported consonant token | ী (U+09C0) |

For example, `ki` → `কি` (U+0995 U+09BF), while `kI` → `কী` (U+0995 U+09C0).
The engine follows the typed case without spelling correction: `nIti` → `নীতি`,
`bhUmI` → `ভূমী`. An `a` immediately after `I` produces য়া (U+09DF U+09BE),
as it already does after `i`/`u`/`U`: `kIa` → `কীয়া`. Other adjacent vowels stay
independent; for example, `Iu` → `ঈউ`, and repeated `II` → `ঈঈ`.

The 52 independently authored [fixtures](../../tests/fixtures/vowels-i-long.tsv)
were checked against the pinned parser before the Rust changes. They cover `I`
after all 13 supported consonants, every pair involving `I` and an existing vowel,
longer vowel transitions, digits, separators, mixed Unicode, and words. All 225
cases match the reference. Boundary and separate-call regressions now include
`I`; copied Bangla still ends consonant context (`কI` → `কঈ`).

Uppercase `A`, remaining vowels, unsupported consonants, conjuncts, phonetic
punctuation/escapes, and composition/platform integration remain incomplete.
For example, `` I` `` remains `ঈ` followed by a backtick, while the reference
produces the standalone U+09C0 sign. Gap probes at that step covered `e`, `kkh`,
`K`, `` k`h ``, and `` I` ``; the next group below adds `e`. No broader compatibility
or performance claim is made.

## Fourth vowel group

Added on 2026-10-28: lowercase `e` and the two-key sequence `ee`. The longest
supported sequence is matched first, so `ee` is one long vowel rather than two
independent `e` vowels. It shares the existing uppercase `I` conversion.

| Context | `e` output | `ee` output |
| --- | --- | --- |
| Start, or after a digit/unmatched character or supported vowel | এ (U+098F) | ঈ (U+0988) |
| Immediately after a supported consonant token | ে (U+09C7) | ী (U+09C0) |

For example, `ke` → `কে` (U+0995 U+09C7), and `kee` → `কী` (U+0995 U+09C0).
Longer runs remain greedy: `eee` → `ঈএ`, `eeee` → `ঈঈ`, and `keee` → `কীএ`.
An `a` following either form produces য়া (U+09DF U+09BE): `kea` → `কেয়া`,
`keea` → `কীয়া`. Other adjacent vowels stay independent; `ie` → `ইএ`,
`ei` → `এই`, and `eu` → `এউ`.

The 92 independently authored [fixtures](../../tests/fixtures/vowels-e.tsv) were
checked against the pinned parser. They cover `e` and `ee` after all 13 supported
consonants, neighboring vowels, longer runs, digits, boundaries, mixed Unicode,
and words such as `mene` → `মেনে` and `buke` → `বুকে`. All 317 cases match.
Context resets at copied characters and between calls as before: `কe` → `কএ`,
`কee` → `কঈ`, and `e a` → `এ আ`.

Uppercase `A`/`E`, remaining vowels, unsupported consonants, conjuncts, phonetic
punctuation/escapes, and composition/platform integration remain incomplete.
For example, `` e` `` remains `এ` followed by a backtick instead of the reference's
standalone U+09C7 sign. At that increment, `kemon` produced `কেমoন`, with
unsupported `o` preserved; the next group below resolves it. Gap probes at that
step covered `o`, `kkh`, `K`, `` k`h ``, and `` e` ``.
This increment adds no dependencies or broader support/performance claims.

## Fifth vowel group

Added on 2026-10-28: case-sensitive `o`/`O` and greedy `oo`, which aliases short
`u`. Context now retains the last raw vowel key as well as distinguishing vowels
from supported consonants and copied characters. It remains local to one call.

| Context | `o` output | `O` output | `oo` output |
| --- | --- | --- | --- |
| Start, or after a digit/unmatched character | অ (U+0985) | ও (U+0993) | উ (U+0989) |
| Immediately after a supported consonant | No character | ো (U+09CB) | ু (U+09C1) |
| After a supported raw vowel key other than lowercase `o` | ও (U+0993) | ও (U+0993) | উ (U+0989) |
| After a raw lowercase `o`, including the end of an `oo` token | অ (U+0985) | ও (U+0993) | উ (U+0989) |

Greedy matching applies before context: a leading `oo` is one token, not two
single `o` tokens. Examples: `ko` → `ক`, `kO` → `কো`, `koo` → `কু`,
`ooo` → `উঅ`, and `oooo` → `উউ`. The uppercase `O` sign is the single code point
U+09CB, matching the reference without normalization.

After lowercase `o` has added no character, it still establishes vowel context.
Thus `koO` → `কও`, rather than adding a sign to the consonant. The raw key also
matters after aliases: `eeo` → `ঈও` (last raw key `e`), while `ooo` → `উঅ`
(last key of `oo` is `o`). This is why context does not follow the output glyphs
or just the normalized alias (`I`/`u`).

An `a` after any of the new forms produces য়া (U+09DF U+09BE): `koa` → `কয়া`,
`kOa` → `কোয়া`, and `kooa` → `কুয়া`. Context after raw `a` is now retained too,
so `ao` → `আও`; repeated `aa` continues to produce `আআ`. Digits, whitespace,
copied Unicode, and unsupported characters reset context as before.

The 156 independently authored [fixtures](../../tests/fixtures/vowels-o.tsv) were
checked against the pinned parser before Rust implementation. They cover all
13 supported consonants with all three forms, neighboring vowels and aliases,
longer runs, boundaries, Unicode, and words. All 473 cases match. Examples now
include `kemon` → `কেমন`, `onek` → `অনেক`, and `tOmake` → `তোমাকে`.

That increment deferred the two-key vowels `OI`/`OU`: it produced `ওঈ`/`ওঊ`, while
the reference produces ঐ (U+0990)/ঔ (U+0994). The next group below resolves this.
Uppercase `A`/`E`, other phonetic sequences, unsupported consonants, conjuncts,
punctuation/escapes, composition, and platform integration remain incomplete.
For example, `` O` `` still produces `ও` followed by a backtick instead of U+09CB.
Gap probes at that step covered `OI`, `kkh`, `K`, `` k`h ``, and `` O` ``. This increment
adds no dependencies or broader compatibility/performance claims.

## Sixth vowel group

Added on 2026-10-28: the case-sensitive two-key vowels `OI` and `OU`. Each pair
matches before single `O` and consumes two ASCII keys at a valid UTF-8 boundary.

| Context | `OI` output | `OU` output |
| --- | --- | --- |
| Start, or after a digit/unmatched character or supported vowel | ঐ (U+0990) | ঔ (U+0994) |
| Immediately after a supported consonant | ৈ (U+09C8) | ৌ (U+09CC) |

For example, `kOI` → `কৈ` (U+0995 U+09C8), `kOU` → `কৌ` (U+0995 U+09CC),
and `nOUka` → `নৌকা`. Both dependent signs are emitted as single code points,
without normalization or substituting visually similar sequences.

The match is exact: `OI` → `ঐ`, but `Oi` → `ওই`, `oI` → `অঈ`, and `oi` → `অই`.
Likewise, `OU` → `ঔ`, while `Ou` → `ওউ`, `oU` → `অঊ`, and `ou` → `অউ`.
Adjacent pairs remain separate: `OIOU` → `ঐঔ` and `OUOI` → `ঔঐ`.

Conversion context retains the pair's final raw key (`I` or `U`), rather than
its initial `O`. Existing following-vowel behavior applies: `OIa` → `ঐয়া`,
`OUa` → `ঔয়া`, `OIo` → `ঐও`, and `OUoo` → `ঔউ`. Copied characters reset context,
and separate calls share no state; `কOI` → `কঐ` and `OU a` → `ঔ আ`.

The 150 independently authored [fixtures](../../tests/fixtures/vowels-oi-ou.tsv)
were checked against the pinned parser before Rust implementation. They cover
all 13 supported consonants, existing vowels and aliases before/after each pair,
longer transitions, case variants, digits, boundaries, mixed Unicode, and words.
All 623 reference cases match. No dependencies or platform code were added.

That increment left `rri` (ঋ/ৃ), uppercase `A`/`E`, unsupported consonants,
other phonetic sequences, conjuncts, punctuation/escapes, composition, and platform
integration incomplete. For example, `` OU` `` still produces `ঔ` followed
by a backtick instead of the reference's standalone U+09CC sign. Gap probes at
that step covered `rri`, `kkh`, `K`, `` k`h ``, and `` OU` ``; the next group below
adds `rri`. No broader compatibility
or performance claim is made.

## Seventh vowel group

Added on 2026-10-28: exact lowercase `rri`, matched before individual consonants
and consumed as three ASCII keys at a valid UTF-8 boundary.

| Context | `rri` output |
| --- | --- |
| Start, or after a digit/unmatched character or supported vowel | ঋ (U+098B) |
| Immediately after a supported consonant | ৃ (U+09C3) |

The later [following-`rri` increment](#following-rri-after-ng-ng-and-ng) handles
the matching-order exception after `Ng`/`NG`/`ng`; these were not in this initial set.

For example, `krri` → `কৃ` (U+0995 U+09C3), `krriti` → `কৃতি`, and
`rriN` → `ঋণ`. The sign is emitted as the single code point U+09C3; the engine
does not normalize or substitute visually similar Unicode sequences.

Following-vowel context uses the final raw `i`: `rria` → `ঋয়া`, `rrio` → `ঋও`,
and `krriooa` → `কৃউয়া`. Adjacent patterns remain separate (`rrirri` → `ঋঋ`).
Copied characters and digits reset context: `কrri` → `কঋ`, `k1rri` → `ক১ঋ`,
and `rri a` → `ঋ আ`. Separate calls share no state.

The 84 independently authored [fixtures](../../tests/fixtures/vowels-rri.tsv) were
checked against the pinned parser before Rust implementation. They cover all
13 supported consonants, existing vowels and aliases on either side, repetition,
longer transitions, digits, boundaries, copied Unicode, and words. All 707
reference cases match. Principal forms for all 11 basic vowels are implemented;
this does not establish full vowel-context or Avro compatibility.

That increment left standalone `r`/`rr` and their case variants unsupported.
The longer runs interacted with that matching, exposing these initial gaps:

| Input | Initial `rri` slice | Reference |
| --- | --- | --- |
| `rrri` | rঋ | রররি |
| `rrrri` | rrঋ | ররৃ |
| `Rri` | Rrই | ড়্রি |

The next `r`/`rr` group below resolves the overlapping lowercase runs. The `Rri`
case remains incomplete because related conjunct behavior is still missing;
basic uppercase `R` is now implemented in the `R`/`Rh` group below. Uppercase
`A`/`E`, other consonants, conjuncts, punctuation/escapes, composition, and platform integration remain
incomplete. In particular, `` rri` `` still produces `ঋ` followed by a backtick
instead of the reference's standalone U+09C3 sign. Gap probes at that step covered
`r`, `rrri`, `Rri`, `kkh`, and `` rri` ``. No dependencies or broader support/performance
claims were added.

## Basic r and rr consonants

Added on 2026-10-28: lowercase `r` → র (U+09B0) and `rr` → রর
(U+09B0 U+09B0) in the basic matching subset. There are now 15 consonant input
sequences producing 14 distinct consonant letters.

Matching prioritizes `rri` over `rr`, then `r`. This retains `rri` → `ঋ` and
`krri` → `কৃ`, while fixing `rrri` → `রররি` (U+09B0 U+09B0 U+09B0 U+09BF)
and `rrrri` → `ররৃ` (U+09B0 U+09B0 U+09C3). In the latter, the first `rr` is
followed by `rri`, which supplies a dependent vowel sign. `rrI` → `ররী` stays
distinct from `rri` → `ঋ`.

Both consonant patterns establish consonant context. Examples: `ra` → `রা`,
`ri` → `রি`, `ro` → `র`, `rra` → `ররা`, and `rre` → `ররে`. Copied Unicode,
digits, and separators still reset context: `r1a` → `র১আ`, `r🙂a` → `র🙂আ`,
and `rকa` → `রকআ`. No state is shared between calls.

The 115 independently authored [fixtures](../../tests/fixtures/consonants-r.tsv)
were checked against the pinned parser before Rust implementation. They cover
both patterns, supported vowels/aliases, overlapping `rri` runs, basic `r`
before supported consonants, boundaries, Unicode, and words such as `ram` → `রাম`,
`rani` → `রানি`, and `kora` → `করা`. All 822 reference cases match.

This increment does not implement the reference's context-sensitive conjunct/reph
forms. Examples at that step (`kr` is now covered by the
[basic following-`r` batch](exact-conjuncts.md#following-r-after-basic-k-kh-and-sh)):

| Input | Engine at that step | Reference |
| --- | --- | --- |
| `kr` | কর | ক্র (U+0995 U+09CD U+09B0) |
| `rrk` | ররক | র্ক (U+09B0 U+09CD U+0995) |
| `rrr` | ররর | র্র (U+09B0 U+09CD U+09B0) |
| `Rri` | ড়রি | ড়্রি (U+09DC U+09CD U+09B0 U+09BF) |

These are explicit coverage limits, not intended v1 behavior. Other remaining
consonants, uppercase aliases, punctuation/escapes, composition, and platform
integration also remain incomplete. Gap probes at that step covered `kr`, `rrk`,
`rrr`, `Rri`, and `` rri` ``. No dependencies or broader compatibility/performance claims
were added.

## Basic p, ph and f consonants

Added on 2026-10-28: lowercase `p`, `ph`, and `f`.

| Input | Output | Unicode |
| --- | --- | --- |
| `p` | প | U+09AA |
| `ph` | ফ | U+09AB |
| `f` | ফ | U+09AB |

The existing longest-match rule consumes `ph` as one two-key pattern before
single `p`. Both spellings of ফ establish the same consonant context: `phi` and
`fi` → `ফি`, `phrri` and `frri` → `ফৃ`. Other examples include `pani` → `পানি`,
`pakhi` → `পাখি`, and `phOn`/`fOn` → `ফোন`. The core now implements 18 consonant
input sequences producing 16 distinct letters.

The 115 independently authored [fixtures](../../tests/fixtures/consonants-p-ph-f.tsv)
were checked against the pinned parser before Rust changes. They cover the three
patterns, all supported vowels/aliases before and after them, digits, separators,
copied Unicode, and words. All 937 reference cases match. Context resets remain
unchanged: `p1a` → `প১আ`, `ph🙂a` → `ফ🙂আ`, and `fকa` → `ফকআ`.

Uppercase aliases, conjuncts, and larger overlapping sequences remain incomplete:

| Input | Engine at that step | Reference |
| --- | --- | --- |
| `pr` | পর | প্র (U+09AA U+09CD U+09B0) |
| `pph` | পফ | প্পহ (U+09AA U+09CD U+09AA U+09B9) |
| `P` | P | প (U+09AA) |
| `F` | F | ফ (U+09AB) |
| `` p`h `` | `` প`হ `` | পহ (U+09AA U+09B9) |

The last example still needs escape handling; the `l`/`h` group below adds
standalone `h`.
Matching `ph` does not establish handling of all sequences containing `p` and `h`.
Other remaining consonants, conjunct/reph forms, punctuation, composition, and
platform integration remain incomplete. Gap probes at that step covered `pr`, `pph`,
`P`, `F`, and `` p`h ``. No dependencies or broader compatibility/performance
claims were added.

## Basic c, ch, j and jh consonants

Added on 2026-10-28: exact lowercase `c`, `ch`, `j`, and `jh`.

| Input | Output | Unicode |
| --- | --- | --- |
| `c` | চ | U+099A |
| `ch` | ছ | U+099B |
| `j` | জ | U+099C |
| `jh` | ঝ | U+099D |

The existing longest-match rule selects `ch` and `jh` before `c` and `j`.
All four establish consonant context for supported vowel signs: `ci` → `চি`,
`chI` → `ছী`, `jOU` → `জৌ`, and `jhrri` → `ঝৃ`. Examples include `cabi` → `চাবি`,
`chabi` → `ছাবি`, `jani` → `জানি`, and `jhuri` → `ঝুরি`. The core now implements
22 consonant input sequences producing 20 distinct letters.

The 148 independently authored [fixtures](../../tests/fixtures/consonants-c-ch-j-jh.tsv)
were checked against the pinned parser before Rust changes. They cover all four
patterns alone, with every supported vowel/alias before and after them, digits,
separators, copied Unicode, and words. All 1,085 reference cases match. Existing
boundary behavior remains: `ch1a` → `ছ১আ`, `jh🙂a` → `ঝ🙂আ`, and `jকa` → `জকআ`.

At that step, conjuncts, uppercase variants, and escapes remained incomplete.
The later [remaining conjunct batch](conjunct-batches.md#remaining-exact-conjunct-batch) resolves
`cch`/`jjh` and adds following `r` after `c`/`ch`/`j`/`jh`.

| Input | Engine at that step | Reference |
| --- | --- | --- |
| `cch` | চছ | চ্ছ (U+099A U+09CD U+099B) |
| `jjh` | জঝ | জ্ঝ (U+099C U+09CD U+099D) |
| `C` | C | চ (U+099A) |
| `Jh` | Jহ | জহ (U+099C U+09B9) |
| `` c`h `` | `` চ`হ `` | চহ (U+099A U+09B9) |

Case is significant: reference `Jh` produces জহ, while lowercase `jh` produces
ঝ. No blanket case normalization was added. Other remaining consonants,
conjunct/reph forms, punctuation, composition, and platform integration remain
incomplete. Gap probes at that step covered the five inputs above. No dependencies
or broader compatibility/performance claims were added.

## Basic d, dh, D and Dh consonants

Added on 2026-10-28: exact `d`, `dh`, `D`, and `Dh`.

| Input | Output | Unicode |
| --- | --- | --- |
| `d` | দ | U+09A6 |
| `dh` | ধ | U+09A7 |
| `D` | ড | U+09A1 |
| `Dh` | ঢ | U+09A2 |

The existing longest-match rule selects `dh` before `d` and `Dh` before `D`.
Case distinguishes দ/ধ from ড/ঢ: `da dha Da Dha` → `দা ধা ডা ঢা`.
All four establish consonant context for supported vowel signs, including
`di` → `দি`, `dhI` → `ধী`, `DOI` → `ডৈ`, and `Dhrri` → `ঢৃ`.
The core now implements 26 consonant input sequences producing 24 distinct letters.

The 164 independently authored [fixtures](../../tests/fixtures/consonants-d-dh.tsv)
were checked against the pinned parser. They cover all four
patterns alone, every supported vowel/alias before and after them, following-vowel
transitions, digits, boundaries, copied Unicode, case distinctions, and words.
All 1,249 reference cases match. Examples include `din` → `দিন`, `dhan` → `ধান`,
`Dan` → `ডান`, `Dhaka` → `ঢাকা`, and `dOkan` → `দোকান`.
Copied characters still reset context: `dh1a` → `ধ১আ`, `Dh🙂a` → `ঢ🙂আ`,
and `Dকa` → `ডকআ`. Separate calls share no state.

Conjuncts, uppercase-`H` aliases, and escapes remain incomplete:

| Input | Engine at that step | Reference |
| --- | --- | --- |
| `ddh` | দধ | দ্ধ (U+09A6 U+09CD U+09A7) |
| `DDh` | ডঢ | ড্ডহ (U+09A1 U+09CD U+09A1 U+09B9) |
| `dH` | দH | ধ (U+09A7) |
| `DH` | ডH | ঢ (U+09A2) |
| `` d`h `` | `` দ`হ `` | দহ (U+09A6 U+09B9) |

Gap probes at that step covered these five inputs. The later
[d/dh batch](conjunct-batches.md#d-and-dh-conjunct-batch) resolves `ddh` and `DDh`. Uppercase `A` remains unsupported;
use `dhan`/`Dan` in this slice. Other remaining consonants, conjunct/reph forms,
punctuation, composition, and platform integration remain incomplete.
No dependencies or broader compatibility/performance claims were added.

## Basic l and h consonants

Added on 2026-10-28: exact lowercase `l` → ল (U+09B2) and `h` → হ (U+09B9).
Both establish consonant context for supported vowels: `li` → `লি`, `hU` → `হূ`,
`lOI` → `লৈ`, and `hrri` → `হৃ`. The core now implements 28 consonant input
sequences producing 26 distinct letters.

The longest-match rule still selects the existing two-key consonants before
standalone `h`: `kh` → `খ`, while `khh` → `খহ` and `khha` → `খহা`.
The same checks cover `gh`, `th`, `Th`, `bh`, `ph`, `ch`, `jh`, `dh`, and `Dh`.
Space still separates matches: `k h` → `ক হ`, `d h D h` → `দ হ ড হ`.
No conjunct or escape rules were added; a backtick remains literal even though
its following `h` now converts (`` d`h `` → `` দ`হ ``).

The 110 independently authored [fixtures](../../tests/fixtures/consonants-l-h.tsv)
were checked against the pinned parser before Rust implementation. They cover
both letters alone, all supported vowels/aliases on either side, following-vowel
transitions, existing two-key consonants followed by `h`/`ha`, digits, boundaries,
copied Unicode, and words. All 1,359 reference cases match. Examples include
`lal` → `লাল`, `holud` → `হলুদ`, `likhi` → `লিখি`, `bhalO` → `ভালো`, and
`DhOl` → `ঢোল`. Copied characters still reset context: `l1a` → `ল১আ`,
`h🙂a` → `হ🙂আ`, and `hকa` → `হকআ`. Separate calls share no state.

Conjuncts, uppercase aliases, and escapes remain incomplete:

| Input | Engine at that step | Reference |
| --- | --- | --- |
| `ll` | লল | ল্ল (U+09B2 U+09CD U+09B2) |
| `hl` | হল | হ্ল (U+09B9 U+09CD U+09B2) |
| `L` | L | ল (U+09B2) |
| `H` | H | হ (U+09B9) |
| `` l`h `` | `` ল`হ `` | লহ (U+09B2 U+09B9) |

Gap probes at that step covered these five inputs. The later
[nasal/h batch](conjunct-batches.md#nasal-and-h-conjunct-batch) resolves `hl`. Remaining consonants, conjunct/reph
forms, other uppercase aliases, punctuation, composition, and platform integration
remain incomplete. No dependencies or broader compatibility/performance claims
were added.

## Confirmed s, sh, S and Sh mapping

Confirmed by the user and implemented on 2026-10-28:

| Input | Output | Unicode |
| --- | --- | --- |
| `s` | স | U+09B8 |
| `sh` | শ | U+09B6 |
| `S` | শ | U+09B6 |
| `Sh` | ষ | U+09B7 |

All four standalone forms match the SHA-256-verified
[pinned reference](../compatibility.md#phonetic-behavior-reference), checked with Node.js v24.21.0.
This corrects the earlier planned three-form shorthand: uppercase `S` produces
শ, while `Sh` produces ষ. Case and longest matching matter: `sh` must match
before `s`, and `Sh` before `S`.

All four establish consonant context for supported vowels: `sI` → `সী`,
`shU` → `শূ`, `SOI` → `শৈ`, and `Shrri` → `ষৃ`. `sh` and `S` produce the same
letter, while case distinguishes `Sh` → `ষ`. The core now implements 32 consonant
input sequences producing 29 distinct letters.

The 174 independently authored [fixtures](../../tests/fixtures/consonants-s-sh.tsv)
were checked against the pinned parser before Rust implementation. They cover
all supported vowels/aliases on either side, following-vowel transitions,
case distinctions, overlapping sequences, digits, boundaries, copied Unicode,
and words. All 1,533 reference cases match. Examples include `sokal` → `সকাল`,
`shishu`/`SiSu` → `শিশু`, and `bhaSha` → `ভাষা`. The engine follows the raw keys:
`sisu` → `সিসু`, without spelling correction. Longer matching includes `ssh` → `সশ`,
`shSh` → `শষ`, and `Shsh` → `ষশ`; extra `h` remains separate after a two-key
match (`shh` → `শহ`, `Shh` → `ষহ`). Spaces separate keys (`s h S h` → `স হ শ হ`).

Copied characters still reset context: `sh1a` → `শ১আ`, `Sh🙂a` → `ষ🙂আ`,
and `Sকa` → `শকআ`. Separate calls share no state.

At that step, conjuncts, uppercase-`H` aliases, and escapes were incomplete:

| Input | Prior partial engine | Reference |
| --- | --- | --- |
| `sk` | সক | স্ক (U+09B8 U+09CD U+0995) |
| `st` | সত | স্ত (U+09B8 U+09CD U+09A4) |
| `ShT` | ষট | ষ্ট (U+09B7 U+09CD U+099F) |
| `sH` | সH | শ (U+09B6) |
| `` s`h `` | `` স`হ `` | সহ (U+09B8 U+09B9) |

Gap probes at that step covered these five inputs. The consuming k-family batch
resolves `sk`; the [s/Sh stop batch](conjunct-batches.md#s-and-sh-stop-conjunct-batch) resolves
`st`/`ShT`. Remaining consonants, conjunct/reph
forms, other uppercase aliases, punctuation, composition, and platform integration
remain incomplete. No dependencies or broader compatibility/performance claims
were added.

## Basic uppercase R and Rh consonants

Added on 2026-10-28: exact `R` → ড় (U+09DC) and `Rh` → ঢ় (U+09DD).
The existing longest-match rule selects `Rh` before `R`. Both establish consonant
context for supported vowels: `Ri` → `ড়ি`, `RhU` → `ঢ়ূ`, `ROI` → `ড়ৈ`, and
`Rhrri` → `ঢ়ৃ`. The core now implements 34 consonant input sequences producing
31 distinct letters.

Matching remains case-sensitive: `r R Rh` → `র ড় ঢ়`. The lowercase `rri` vowel
still takes priority after either new consonant (`Rrri` → `ড়ৃ`, `RrriR` → `ড়ৃড়`);
this does not add general conjunct handling. An extra `h` after `Rh` remains
separate (`Rhh` → `ঢ়হ`), and a space interrupts matching (`R h` → `ড় হ`).

The 94 independently authored [fixtures](../../tests/fixtures/consonants-r-retroflex.tsv)
were checked against the pinned parser before Rust implementation. They cover
all supported vowels/aliases on either side, following-vowel transitions,
lowercase `r`/`rri` interactions, digits, boundaries, copied Unicode, and words.
All 1,627 reference cases match. Examples include `baRi` → `বাড়ি`, `gaRi` → `গাড়ি`,
`gaRh` → `গাঢ়`, and `drriRh` → `দৃঢ়`. Copied characters still reset context:
`R1a` → `ড়১আ`, `Rh🙂a` → `ঢ়🙂আ`, and `Rকa` → `ড়কআ`. Separate calls share no state.

Generated letters use single U+09DC/U+09DD code points, matching the reference.
Copied decomposed letters remain unchanged: the initial ড় in `ড়Ri` → `ড়ড়ি`
keeps U+09A1 U+09BC, followed by generated U+09DC U+09BF. The equivalent fixture
for ঢ় retains U+09A2 U+09BC before U+09DD U+09BF. No Unicode normalization occurs.

Conjuncts, uppercase-`H` aliases, and escapes remain incomplete:

| Input | Engine at that step | Reference |
| --- | --- | --- |
| `Rri` | ড়রি | ড়্রি (U+09DC U+09CD U+09B0 U+09BF) |
| `Rr` | ড়র | ড়্র (U+09DC U+09CD U+09B0) |
| `Rhr` | ঢ়র | ঢ়্র (U+09DD U+09CD U+09B0) |
| `RH` | ড়H | ঢ় (U+09DD) |
| `` R`h `` | `` ড়`হ `` | ড়হ (U+09DC U+09B9) |

Gap probes at that step covered these five inputs. Remaining consonants, conjunct/reph
forms, other uppercase aliases, punctuation, composition, and platform integration
remain incomplete. No dependencies or broader compatibility/performance claims
were added.

The later [q/z/R/Rh following-r batch](case-symbols-reph.md#following-r-after-q-z-r-and-rh)
resolves the basic following-r gaps above. Other outputs in the table are
historical; see the current handoff for remaining limitations.

## Basic lowercase z consonant

Added on 2026-10-28: exact lowercase `z` → য (U+09AF), distinct from `j` → জ
(U+099C). It establishes consonant context for supported vowels: `zi` → `যি`,
`zU` → `যূ`, `zOI` → `যৈ`, and `zrri` → `যৃ`. The core now implements
35 consonant input sequences producing 32 distinct letters.

The 51 independently authored [fixtures](../../tests/fixtures/consonant-z.tsv)
were checked against the pinned parser before Rust implementation. They cover
all supported vowels/aliases on either side, following-vowel transitions,
repeated and neighboring input, boundaries, digits, copied Unicode, and words.
All 1,678 reference cases match. Examples include `zai` → `যাই`, `zabe` → `যাবে`,
`zodi` → `যদি`, `zokhon` → `যখন`, and `zOg` → `যোগ`. Raw case stays meaningful:
`zini` → `যিনি`, `zIni` → `যীনি`, without spelling correction.

Ordinary consonant adjacency is preserved in the selected cases: `kz` → `কয`,
`zk` → `যক`, and `zz` → `যয`. These are not automatic conjuncts. Copied characters
still reset context: `z1a` → `য১আ`, `z🙂a` → `য🙂আ`, and `zকa` → `যকআ`.
Separate calls share no state.

Uppercase `Z` produces the reference's য-ফলা sequence ্য (U+09CD U+09AF),
which joins onto a preceding consonant. It is not an alias for lowercase `z`.
Uppercase `Z` is now implemented in the [later increment](#uppercase-z-with-az-and-oz-forms).
Other conjuncts and escapes remain incomplete:

| Input | Engine at that step | Reference |
| --- | --- | --- |
| `zr` | যর | য্র (U+09AF U+09CD U+09B0) |
| `` z`h `` | `` য`হ `` | যহ (U+09AF U+09B9) |

Gap probes at that step covered these two inputs plus the now-resolved `Z`,
`kZ`, and `zZ`. Remaining consonants, conjunct/reph forms, other aliases,
punctuation, composition, and platform integration remain incomplete.
No dependencies or broader compatibility/performance claims were added.

The later [q/z/R/Rh following-r batch](case-symbols-reph.md#following-r-after-q-z-r-and-rh)
resolves the basic following-r gaps above. Other outputs in the table are
historical; see the current handoff for remaining limitations.

## Basic Ng and NG consonants

Added on 2026-10-28: exact `Ng` → ঙ (U+0999) and `NG` → ঞ (U+099E).
Both two-key patterns match before single `N` → ণ, preserving the distinctions
in `n N Ng NG` → `ন ণ ঙ ঞ`. They establish consonant context for vowel signs:
`Ngi` → `ঙি`, `NGU` → `ঞূ`, and `NgOI` → `ঙৈ`. The core now implements
37 consonant input sequences producing 34 distinct letters.

The 88 independently authored [fixtures](../../tests/fixtures/consonants-ng-nj.tsv)
were checked against the pinned parser before Rust implementation. They cover
both forms alone, supported vowels/aliases on either side except the following
`rri` exception below, following-vowel transitions, repeated and neighboring
input, case distinctions, digits, boundaries, copied Unicode, and words.
All 1,766 reference cases match. Examples include `aNgul` → `আঙুল`,
`raNga` → `রাঙা`, `aNgur` → `আঙুর`, and raw `baNgla` → `বাঙলা`, without spelling
correction. Separate calls share no state. Digits and copied characters still
reset context: `Ng1a` → `ঙ১আ`, `NG🙂a` → `ঞ🙂আ`, and `Ngকa` → `ঙকআ`.

The initial reference check rejected two prepared expectations: the reference
does not use the ৃ sign in `Ngrri` or `NGrri`. These cases were excluded from
that increment's compatibility fixtures and recorded as gaps. They are now
covered by the [following-`rri` increment](#following-rri-after-ng-ng-and-ng) below.

At that step, conjuncts and escapes remained incomplete. Lowercase `ng` is
handled in the next section, and the later [exact `Ngk` increment](exact-conjuncts.md#exact-ngk-conjunct)
resolves the `Ngk` case below. The [remaining conjunct batch](conjunct-batches.md#remaining-exact-conjunct-batch)
also resolves `NGc`/`NGch`.

| Input | Engine at that step | Reference |
| --- | --- | --- |
| `Ngk` | ঙক | ঙ্ক (U+0999 U+09CD U+0995) |
| `NGc` | ঞচ | ঞ্চ (U+099E U+09CD U+099A) |
| `NGch` | ঞছ | ঞ্ছ (U+099E U+09CD U+099B) |
| `` N`g `` | `` ণ`গ `` | ণগ (U+09A3 U+0997) |

Gap probes at that step covered lowercase `ng`, `Ngrri`, `NGrri`, and the four
inputs above. The first three are now resolved by the later increments.
Remaining consonants, conjunct/reph
forms, other aliases, punctuation, composition, and platform integration remain
incomplete. No dependencies or broader compatibility/performance claims were added.

## Lowercase ng sign and vowel forms

Added on 2026-10-28: exact lowercase `ng` → ং (U+0982), the anusvara sign,
matching before single `n`. It remains distinct from `Ng` → ঙ and `NG` → ঞ.
The 37 consonant sequences producing 34 letters remain unchanged; this step
adds a sign and selected forms involving the ঙ্গ conjunct (U+0999 U+09CD U+0997).

The reference requires longer vowel forms to match before bare `ng`:

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `ng` | ং | U+0982 |
| `nga` | ঙ্গা | U+0999 U+09CD U+0997 U+09BE |
| `ngi` / `ngI` | ঙ্গি / ঙ্গী | U+0999 U+09CD U+0997 with U+09BF / U+09C0 |
| `ngu` / `ngU` | ঙ্গু / ঙ্গূ | U+0999 U+09CD U+0997 with U+09C1 / U+09C2 |
| `nge` | ঙ্গে | U+0999 U+09CD U+0997 U+09C7 |
| `ngo` | ঙ্গ | U+0999 U+09CD U+0997 |
| `ngO` | ঙ্গো | U+0999 U+09CD U+0997 U+09CB |
| `ngOI` / `ngOU` | ঙ্গৈ / ঙ্গৌ | U+0999 U+09CD U+0997 with U+09C8 / U+09CC |

These forms consume the listed vowel keys before ordinary `ee`/`oo` aliases:
`ngee` → `ঙ্গেএ`, `ngoo` → `ঙ্গঅ`, `ngeee` → `ঙ্গেঈ`, and `ngooo` → `ঙ্গউ`.
The final raw vowel key establishes subsequent context: `ngia` → `ঙ্গিয়া`,
`ngoa` → `ঙ্গয়া`, and `ngOIo` → `ঙ্গৈও`. No spelling correction is involved.
Bare `ng` retains the existing raw-consonant context; the following-`rri` increment
below handles its `ngr` prefix. Digits and copied characters reset context (`ng1a` → `ং১আ`,
`ng🙂a` → `ং🙂আ`); calls share no state.

The 110 independently authored [fixtures](../../tests/fixtures/sign-ng.tsv) were
checked against the SHA-256-verified pinned parser before Rust implementation.
They cover vowel prefixes and suffixes, vowel transitions and repeated keys,
neighboring consonants, repeated signs, `Ng`/`NG` distinctions, digits, boundaries,
copied Unicode, and words. All 1,876 reference cases match. Examples include
`bangla` → `বাংলা`, `rong` → `রং`, and `song` → `সং`.

At that step, longer overlaps, case variants, and escapes remained incomplete.
The [nasal/h batch](conjunct-batches.md#nasal-and-h-conjunct-batch) now resolves `ngh` and `nng`:

| Input | Partial engine at that step | Reference |
| --- | --- | --- |
| `ngh` | ংহ | ঙ্ঘ (U+0999 U+09CD U+0998) |
| `nng` | নং | ন্নগ (U+09A8 U+09CD U+09A8 U+0997) |
| `nG` | নG | নগ (U+09A8 U+0997) |
| `` ng`a `` | `` ং`আ `` | ংআ (U+0982 U+0986) |

Gap probes at that step covered these four inputs plus `ngrri`/`Ngrri`/`NGrri`,
which are now resolved below. Other remaining consonants, conjunct/reph forms, aliases, punctuation,
composition, and platform integration remain incomplete. No dependencies or
broader compatibility/performance claims were added.

## Following rri after Ng, NG and ng

Fixed on 2026-10-28: `rri` and longer `r` runs after `Ng`, `NG`, and `ng`.
Reference probes show that matching each of `Ngr`/`NGr`/`ngr` before processing
the remaining input reproduces these cases. The first `r` is emitted as র with
the nasal form, establishing consonant context; the remaining input uses the
existing `r`/`rr`/`rri` rules. This is a matching-order fix, not spelling correction.
The basic inventory remains 37 consonant sequences for 34 distinct letters;
these three prefixes are additional matching forms.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `Ngrri` | ঙররি | U+0999 U+09B0 U+09B0 U+09BF |
| `NGrri` | ঞররি | U+099E U+09B0 U+09B0 U+09BF |
| `ngrri` | ংররি | U+0982 U+09B0 U+09B0 U+09BF |
| `Ngrrri` | ঙরৃ | U+0999 U+09B0 U+09C3 |
| `Ngrrrri` | ঙররররি | U+0999 U+09B0 U+09B0 U+09B0 U+09B0 U+09BF |

In `Ngrri`, consuming `Ngr` leaves `ri`; in `Ngrrri`, it leaves `rri`, which
produces the ৃ sign after র. Following vowels retain raw-`i` context:
`Ngrria` → `ঙররিয়া` and `Ngrrio` → `ঙররিও`. An intervening vowel or copied
character separates the matches: `Ngirri` → `ঙিঋ`, `Ng🙂rri` → `ঙ🙂ঋ`.
Other multi-key consonants retain their existing vowel behavior, including
`khrri` → `খৃ`, `phrri` → `ফৃ`, and `Rhrri` → `ঢ়ৃ`; the exception is not generalized.
Copied characters and digits reset context, and separate calls share no state.

The 274 independently authored [fixtures](../../tests/fixtures/nasal-rri.tsv) were
checked against the SHA-256-verified pinned parser before implementation. They
cover all three prefixes, one through ten `r` keys before `i` and following
`a`/`o`, shorter runs without `i`, other vowels/aliases, repetition, case
distinctions, boundaries, digits, copied Unicode, and controls for other
consonants. The new Rust regression first reproduced the `Ngrri` mismatch, then
passed after the fix. All 2,150 reference cases now match.

Gap probes at that step covered `ngh`, `nng`, `nG`, the escape `` ng`a ``, `Ngk`, `NGc`,
and `NGch`, with their partial outputs documented above. Other remaining letters,
conjunct/reph forms, aliases, punctuation/escapes, composition, and platform
integration remain incomplete. No dependencies or broader compatibility,
performance, or platform-support claims were added.

## Basic uppercase Y consonant

Added on 2026-10-28: exact uppercase `Y` → য় (U+09DF). It establishes consonant
context for supported vowels and aliases: `Yi` → `য়ি`, `YI` → `য়ী`,
`YOI` → `য়ৈ`, and `Yrri` → `য়ৃ`. The core now implements 38 basic consonant
sequences producing 35 distinct letters, alongside the existing ng-vowel forms
and nasal-plus-`r` prefixes.

The 142 independently authored [fixtures](../../tests/fixtures/consonant-y-uppercase.tsv)
were checked against the SHA-256-verified pinned parser before implementation.
They cover every supported vowel/alias on either side, following-vowel
transitions, ordinary consonant adjacency, repeated `Y`, digits, boundaries,
copied Unicode, and words. All 2,292 reference cases match. Examples include
`zaY` → `যায়`, `hoY` → `হয়`, `hoYe` → `হয়ে`, `maYa` → `মায়া`, and
`poYla` → `পয়লা`. No spelling correction is involved.

Ordinary adjacency remains separate: `kY` → `কয়`, `Yk` → `য়ক`, and `YY` → `য়য়`.
An `a` after a supported vowel can introduce a second য়, as in `Yia` → `য়িয়া`
(U+09DF U+09BF U+09DF U+09BE). Generated য় is always single U+09DF.
Copied decomposed য় remains U+09AF U+09BC in `য়Yi` → `য়য়ি`, followed by
generated U+09DF U+09BF; no Unicode normalization occurs. Digits and copied
characters reset context (`Y1a` → `য়১আ`, `Y🙂a` → `য়🙂আ`), and calls share no state.

Lowercase `y` is context-sensitive: standalone `y` produces ইয়,
while `Yy` produces য়্য. It is not an alias for uppercase `Y`; the
[next increment](#contextual-lowercase-y) implements these forms.
Uppercase `Z` is covered [below](#uppercase-z-with-az-and-oz-forms).
The [following-`r` increment](#following-r-after-uppercase-y) below resolves
`Yr` from this step. Reph forms and escapes remain incomplete:

| Input | Partial engine at this step | Reference |
| --- | --- | --- |
| `Yr` | য়র | য়্র (U+09DF U+09CD U+09B0) |
| `rrY` | ররয় | র্য় (U+09B0 U+09CD U+09DF) |
| `` Y`a `` | `` য়`আ `` | য়আ (U+09DF U+0986) |
| `` Y`h `` | `` য়`হ `` | য়হ (U+09DF U+09B9) |

Gap probes at that step covered these four inputs plus the now-resolved `y`,
`Yy`, and `YZ`. Other remaining letters,
conjunct/reph forms, aliases, punctuation/escapes, composition, and platform
integration remain incomplete. No dependencies or broader compatibility,
performance, or platform-support claims were added.

## Contextual lowercase y

Added on 2026-10-28: exact lowercase `y`, distinct from uppercase `Y`.
This is deterministic conversion context within one call, with no composition
state or spelling correction. The 38 basic consonant sequences (35 letters)
remain unchanged; `y` adds context-dependent forms.

| Previous matched context | Output for `y` | Exact Unicode |
| --- | --- | --- |
| Start, digit, or copied character | ইয় | U+0987 U+09DF |
| Supported vowel/alias, including silent lowercase `o` | য় | U+09DF |
| Supported consonant, including bare `ng` and repeated `y` | ্য | U+09CD U+09AF |
| Basic `r`/`rr` | ‍্য | U+200D U+09CD U+09AF |

For example, `y` → `ইয়`, `ay` → `আয়`, `ky` → `ক্য`, `kiya` → `কিয়া`, and
`koy` → `কয়`. Every form establishes consonant context for subsequent vowels:
`ya` → `ইয়া`, `yi` → `ইয়ি`, `yrri` → `ইয়ৃ`, and `kya` → `ক্যা`.
Repeated keys append ্য (`yy` → `ইয়্য`, `kyy` → `ক্য্য`). Uppercase `Y` always
produces য় on its own: `kY` → `কয়`, unlike `ky` → `ক্য`.

Basic `r` and `rr` retain a flag for adding U+200D, the zero-width joiner,
before a following lowercase `y`. This preserves the reference's exact Unicode:
`ry` → `র‍্য` (U+09B0 U+200D U+09CD U+09AF), and `rry` → `রর‍্য`.
The existing `Ngr`/`NGr`/`ngr` prefixes do not set that flag:
`Ngry` → `ঙর্য` (U+0999 U+09B0 U+09CD U+09AF), while `Ngrry` → `ঙরর‍্য`.
No inspection of output glyphs or Unicode normalization is used. Generated য়
is U+09DF, while copied decomposed য় retains U+09AF U+09BC (`য়y` → `য়ইয়`).

The 338 independently authored [fixtures](../../tests/fixtures/consonant-y-lowercase.tsv)
were checked against the SHA-256-verified pinned parser before implementation.
They cover every supported consonant before `y`/`ya`, every supported vowel/alias
before `y` both independently and after `k`, following vowel signs, repeated
keys, `r` joiners and nasal-prefix exceptions, digits, boundaries, copied Unicode,
case distinctions, and words. All 2,630 reference cases match. Examples include
`may` → `মায়`, `hoye` → `হয়ে`, `maya` → `মায়া`, and `byatha` → `ব্যাথা`.
The latter follows the raw input without correcting its spelling.

Digits and copied characters reset context (`1y` → `১ইয়`, `কy` → `কইয়`,
`r🙂y` → `র🙂ইয়`, `y1a` → `ইয়১আ`). Unsupported Latin letters still end the
implemented context; matching their reference behavior requires later rules.
Separate calls share no state. Existing Unicode-boundary, control-character,
separate-call, and long-buffer regressions include lowercase `y`.

Uppercase `Z` is covered in the [next increment](#uppercase-z-with-az-and-oz-forms).
The [following-`r` increment](#following-r-after-lowercase-y-and-uppercase-z)
below resolves the first two gaps from this step. Other conjunct/reph forms and
escapes remain incomplete; the [uppercase `Y` increment](#following-r-after-uppercase-y)
also resolves `Yr` below:

| Input | Partial engine at this step | Reference |
| --- | --- | --- |
| `yrr` | ইয়রর | ইয়্রর (U+0987 U+09DF U+09CD U+09B0 U+09B0) |
| `yrrri` | ইয়রররি | ইয়্রররি (U+0987 U+09DF U+09CD U+09B0 U+09B0 U+09B0 U+09BF) |
| `Yr` | য়র | য়্র (U+09DF U+09CD U+09B0) |
| `rrY` | ররয় | র্য় (U+09B0 U+09CD U+09DF) |
| `` y`a `` | `` ইয়`আ `` | ইয়আ (U+0987 U+09DF U+0986) |
| `` y`h `` | `` ইয়`হ `` | ইয়হ (U+0987 U+09DF U+09B9) |

Gap probes at that step covered these six inputs plus the now-resolved `yZ`.
Remaining letters, aliases,
punctuation/escapes, composition, and platform integration remain incomplete.
No dependencies or broader compatibility, performance, or platform claims added.

## Uppercase Z with aZ and oZ forms

Added on 2026-10-28: exact uppercase `Z` produces the য-ফলা sequence ্য
(U+09CD U+09AF), which attaches য to a preceding character. It also produces
those two code points at the start, after a digit, or after copied Unicode:
`Z` → `্য`, `1Z` → `১্য`, and `কZa` → `ক্যা`. This is explicit output requested
by `Z`, without inferring consonant context from copied Bangla.
The 38 basic consonant sequences producing 35 letters remain unchanged.

`Z` establishes consonant context for following vowels/aliases (`Za` → `্যা`,
`Zee` → `্যী`, `ZOI` → `্যৈ`, `Zrri` → `্যৃ`) and lowercase `y`/repeated `Z`
(`Zy`/`ZZ` → `্য্য`). Case remains significant: `z` → `য`, `y` → `ইয়`,
`Y` → `য়`, and `Z` → `্য`. After `k`, `kz` → `কয`, `ky`/`kZ` → `ক্য`,
and `kY` → `কয়`.

Basic `r`/`rr` adds U+200D before `Z`, using the same conversion-local flag as
lowercase `y`: `rZ` → `র‍্য` (U+09B0 U+200D U+09CD U+09AF).
Nasal-plus-`r` prefixes omit it (`NgrZ` → `ঙর্য`); copied র does not set it
(`রZ` → `র্য`, U+09B0 U+09CD U+09AF). Copied Unicode and digits end previous
context (`r🙂Z` → `র🙂্য`, `Z1a` → `্য১আ`), and calls share no state.
Generated য় in lowercase-`y`/uppercase-`Y` controls stays U+09DF; copied decomposed
য় in `য়Za` retains U+09AF U+09BC before generated U+09CD U+09AF U+09BE.
No Unicode normalization occurs.

The reference also requires two longer matches before ordinary vowel handling:

| Input sequence | Output | Exact Unicode |
| --- | --- | --- |
| `aZ` | অ্যা | U+0985 U+09CD U+09AF U+09BE |
| `oZ` | অ্য | U+0985 U+09CD U+09AF |

These use independent অ even after a supported consonant or vowel:
`kaZ` → `কঅ্যা`, `koZ` → `কঅ্য`, `iaZ` → `ইঅ্যা`, and `aoZ` → `আঅ্য`.
They consume both ASCII keys and establish consonant context from final `Z`.
Following vowels therefore add signs even after the া already in `aZ`:
`aZa` → `অ্যাা` (U+0985 U+09CD U+09AF U+09BE U+09BE).
This reproduces the exact reference output without correcting or normalizing it.

Existing longer vowel matches keep their priority: `ooZ` → `উ্য`, rather than
splitting into `o` plus `oZ`. Selected `ng`-vowel matches also consume their vowel
first: `ngaZ` → `ঙ্গা্য`, `ngoZ` → `ঙ্গ্য`, and `ngooZ` → `ঙ্গঅ্য`.
Uppercase aliases such as `AZ` remain outside this increment; uppercase `A`
itself is still unsupported.

The 398 independently authored [fixtures](../../tests/fixtures/consonant-z-uppercase.tsv)
were checked against the SHA-256-verified pinned parser before implementation.
They cover every supported consonant before `Z`/`Za`, vowels/aliases on both
sides, longer `aZ`/`oZ` priority and following context, ng-vowel overlaps, repeated
keys, joiner distinctions, digits, boundaries, copied Unicode, and case controls.
All 3,028 reference cases match. Examples include `bZatha` → `ব্যাথা` and
`baZtha` → `বঅ্যাথা`, preserving the typed sequence without spelling correction.

The [following-`r` increment](#following-r-after-lowercase-y-and-uppercase-z)
below resolves the first three gaps from this step. Aliases, reph, and escapes
remain incomplete:

| Input | Partial engine at this step | Reference |
| --- | --- | --- |
| `Zrr` | ্যরর | ্য্রর (U+09CD U+09AF U+09CD U+09B0 U+09B0) |
| `Zrrri` | ্যরররি | ্য্রররি (U+09CD U+09AF U+09CD U+09B0 U+09B0 U+09B0 U+09BF) |
| `Zry` | ্যর‍্য | ্য্র্য (U+09CD U+09AF U+09CD U+09B0 U+09CD U+09AF) |
| `AZ` | A্য | অ্যা (U+0985 U+09CD U+09AF U+09BE) |
| `rrY` | ররয় | র্য় (U+09B0 U+09CD U+09DF) |
| `` Z`a `` | `` ্য`আ `` | ্যআ (U+09CD U+09AF U+0986) |
| `` Z`h `` | `` ্য`হ `` | ্যহ (U+09CD U+09AF U+09B9) |

Gap probes at that step covered these seven inputs. Other remaining letters, longer
consonant matches, aliases, punctuation/escapes, composition, and platform
integration remain incomplete. No dependencies or broader compatibility,
performance, or platform-support claims added.

## Following r after lowercase y and uppercase Z

Added on 2026-10-28: matching priority for `r` immediately after lowercase `y`
and uppercase `Z`, including the final `Z` in `aZ`/`oZ`. The existing contextual
output of `y`/`Z` is preserved; the added rules consume selected following ASCII
keys before ordinary matching resumes. The 38 basic consonant sequences
producing 35 letters are unchanged.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `yr` | ইয়র | U+0987 U+09DF U+09B0 |
| `yrr` | ইয়্রর | U+0987 U+09DF U+09CD U+09B0 U+09B0 |
| `yrri` | ইয়ৃ | U+0987 U+09DF U+09C3 |
| `yrrri` | ইয়্রররি | U+0987 U+09DF U+09CD U+09B0 U+09B0 U+09B0 U+09BF |
| `yrrrri` | ইয়্ররৃ | U+0987 U+09DF U+09CD U+09B0 U+09B0 U+09C3 |
| `yry` | ইয়র‍্য | U+0987 U+09DF U+09B0 U+200D U+09CD U+09AF |
| `Zry` / `ZrZ` | ্য্র্য | U+09CD U+09AF U+09CD U+09B0 U+09CD U+09AF |
| `yrry` | ইয়রর‍্য | U+0987 U+09DF U+09B0 U+09B0 U+200D U+09CD U+09AF |

After `y`/`Z`, two `r` keys normally produce ্রর (U+09CD U+09B0 U+09B0).
They consume those two keys before the remainder is matched: `yrrri` leaves
`ri`, while `yrrrri` leaves `rri`. Existing `rri` and `rry`/`rrZ` take priority
over that two-key attachment. Thus `yrri` still adds ৃ, and `yrry`/`yrrZ`
still add রর‍্য with U+200D. Longer runs resume ordinary matching after the
first pair (`yrrry` → `ইয়্ররর‍্য`). Single `yr`/`Zr` stays separate.

The single-`r` exception is specific to uppercase `Z`: before `y` or `Z`, it
adds ্র (U+09CD U+09B0) and leaves the final `y`/`Z` to add ্য without U+200D.
Lowercase `yry`/`yrZ` retain ordinary র‍্য with U+200D. All these forms
establish consonant context for following vowels (`Zryi` → `্য্র্যি`,
`yrra` → `ইয়্ররা`). Existing following-vowel transitions still apply:
`yrrria` → `ইয়্রররিয়া` and `yrrio` → `ইয়ৃও`.

The same priority applies after `aZ`/`oZ`: `aZrr` → `অ্যা্রর`,
`oZry` → `অ্য্র্য`. Earlier matches keep their existing priority, including
`ngaZrr` → `ঙ্গা্য্রর` and `ngooZry` → `ঙ্গঅ্য্র্য`.
Repeated forms establish fresh context (`Zryrr` → `্য্র্য্রর`,
`Zryry` → `্য্র্যর‍্য`). No glyph inspection, normalization, or spelling
correction is performed.

The 418 independently authored [fixtures](../../tests/fixtures/ya-following-r.tsv)
were checked against the SHA-256-verified pinned parser before implementation.
They cover runs of one through eight `r` keys, `rri` overlaps, vowels/aliases,
`y`/`Z`/`Y` suffixes, differing preceding contexts, `aZ`/`oZ` priority,
repeated forms, all digits, boundaries, and copied Unicode. All 3,446 reference
cases match. Generated য় stays U+09DF; copied decomposed য় stays
U+09AF U+09BC. Digits and copied characters reset context (`yrr1a` → `ইয়্রর১আ`,
`y🙂rr` → `ইয়🙂রর`). Separate calls share no state. Rust tests also exercise
control-character boundaries and long mixed input; this is correctness coverage,
not a performance measurement.

Uppercase `Y` was deliberately separate at this step: `Yr` produced `য়র`,
`Yrr` produced `য়রর`, and `Yry` produced `য়র‍্য`, while the reference produces
`য়্র`, `য়্রর`, and `য়্র্য`. Existing `Yrri` → `য়ৃ` and `Yrry` → `য়রর‍্য`
are reference-checked controls. The [next increment](#following-r-after-uppercase-y)
resolves following-`r` matching after uppercase `Y`. Gap probes at that step covered
`Yr`, `Yrr`, `Yry`, `AZ`, `rrY`,
`` Z`a ``, and `` Z`h ``. Other conjunct/reph forms, remaining letters and aliases,
punctuation/escapes, composition, and platform integration remain incomplete.
No dependencies or broader compatibility, performance, or platform claims added.

## Following r after uppercase Y

Added on 2026-10-28: exact uppercase `Y` followed by lowercase `r` forms,
preserving য় as U+09DF. This extends the matching helper used by lowercase
`y` and uppercase `Z`; it still operates only on raw matched keys within one
conversion call. The 38 basic consonant sequences producing 35 letters are
unchanged.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `Yr` | য়্র | U+09DF U+09CD U+09B0 |
| `Yrr` | য়্রর | U+09DF U+09CD U+09B0 U+09B0 |
| `Yrri` | য়ৃ | U+09DF U+09C3 |
| `Yrrri` | য়্রররি | U+09DF U+09CD U+09B0 U+09B0 U+09B0 U+09BF |
| `Yrrrri` | য়্ররৃ | U+09DF U+09CD U+09B0 U+09B0 U+09C3 |
| `Yry` / `YrZ` | য়্র্য | U+09DF U+09CD U+09B0 U+09CD U+09AF |
| `Yrry` / `YrrZ` | য়রর‍্য | U+09DF U+09B0 U+09B0 U+200D U+09CD U+09AF |

A single `r` after `Y` adds ্র (U+09CD U+09B0), including before lowercase
`y` or uppercase `Z`, without setting the basic-`r` U+200D joiner flag.
Thus `Yry` shares the final ্র্য sequence with `Zry`, while lowercase `yry`
retains its joiner. Following vowels add signs (`Yri` → `য়্রি`,
`Yryi` → `য়্র্যি`), with existing transitions preserved (`Yria` → `য়্রিয়া`).

Two `r` keys share the priority established for `y`/`Z`: they normally add ্রর
and are consumed before matching resumes. Existing `rri` and `rry`/`rrZ`
take priority, preserving `Yrri` → `য়ৃ` and `Yrry` → `য়রর‍্য`.
Longer runs match their remainder normally: `Yrrri` leaves `ri` after the first
pair, and `Yrrrri` leaves `rri`. Repeated forms re-establish their own context
(`YryYrr` → `য়্র্যয়্রর`, `Yryry` → `য়্র্যর‍্য`). Other adjacency stays
separate (`kYr` → `কয়্র`, `Yyry` → `য়্যর‍্য`).

The 286 independently authored [fixtures](../../tests/fixtures/uppercase-y-following-r.tsv)
were checked against the SHA-256-verified pinned parser before implementation.
They cover one to eight `r` keys, `rri` overlaps, vowels/aliases and following-vowel
transitions, `y`/`Z` joiner distinctions, preceding vowels/consonants, repetition,
all digits, boundaries, and copied Unicode. All 3,732 reference cases match.
Copied decomposed য় remains U+09AF U+09BC before generated U+09DF
(`য়Yr` → `য়য়্র`); no normalization or spelling correction is performed.
Digits and copied characters reset context (`Y1r` → `য়১র`,
`Y🙂ry` → `য়🙂র‍্য`), and separate calls share no state. Rust regressions
also cover control characters and long mixed input without claiming performance.

At this step, lowercase `q` remained literal (`qa` produced `qআ`, versus reference
`কা`). The [next increment](#basic-lowercase-q-consonant) adds that basic mapping
and its vowel context. Gap probes at that step covered `q`, `qa`, `AZ`, `rrY`,
`` Y`a ``, `` Z`a ``, and
`` Z`h ``. Other remaining letters, conjunct/reph forms, aliases,
punctuation/escapes, composition, and platform integration remain incomplete.
No dependencies or broader compatibility, performance, or platform claims added.

## Basic lowercase q consonant

Added on 2026-10-28: exact lowercase `q` produces ক (U+0995) and establishes
consonant context for supported vowels and aliases. The basic inventory is now
39 input sequences producing 35 distinct letters; `q` adds another spelling
for ক. Matching still uses raw keys, without replacing `q` with `k` in the input.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `q` | ক | U+0995 |
| `qa` | কা | U+0995 U+09BE |
| `qi` | কি | U+0995 U+09BF |
| `qI` / `qee` | কী | U+0995 U+09C0 |
| `qOI` | কৈ | U+0995 U+09C8 |
| `qrri` | কৃ | U+0995 U+09C3 |
| `qy` / `qZ` | ক্য | U+0995 U+09CD U+09AF |
| `qY` | কয় | U+0995 U+09DF |

All supported vowels/aliases follow existing consonant context, including silent
lowercase `o` (`qo` → `ক`) and subsequent vowel transitions (`qia` → `কিয়া`,
`qUa` → `কূয়া`). Existing longer `aZ`/`oZ` matches retain priority
(`qaZ` → `কঅ্যা`, `qoZ` → `কঅ্য`). Ordinary adjacency remains separate:
`qh` → `কহ`, `qq` → `কক`, and `qkh` → `কখ`. Existing `kh` still matches as খ.
The input's spelling and case are preserved in matching, without correction.
Examples include `qotha` → `কথা`, `qOtha` → `কোথা`, and `qanon` → `কানন`.

The 132 independently authored [fixtures](../../tests/fixtures/consonant-q.tsv)
were checked against the SHA-256-verified pinned parser before implementation.
They cover every supported vowel/alias before and after `q`, following-vowel
transitions, ordinary adjacency, repeated `q`, lowercase `y`/uppercase `Y`/`Z`
distinctions, digits, boundaries, copied Unicode, and words. All 3,864 reference
cases match. Copied characters and digits reset context (`q🙂a` → `ক🙂আ`,
`q1a` → `ক১আ`), and separate calls share no state. Rust regressions also cover
control-character boundaries and long mixed input; no performance result claimed.

Uppercase aliases, conjunct/reph forms, and escapes remain incomplete:

| Input | Engine at that step | Reference |
| --- | --- | --- |
| `Q` | Q | ক (U+0995) |
| `qr` | কর | ক্র (U+0995 U+09CD U+09B0) |
| `` q`a `` | `` ক`আ `` | কআ (U+0995 U+0986) |
| `` q`h `` | `` ক`হ `` | কহ (U+0995 U+09B9) |

Gap probes at that step covered `v`, `Q`, `qr`, `AZ`, `rrY`, `` q`a ``, and `` q`h ``.
The [next increment](#basic-lowercase-v-consonant) adds basic lowercase `v` → ভ
and its vowel context.
Other remaining letters, conjunct/reph forms, aliases, punctuation/escapes,
composition, and platform integration remain incomplete. No dependencies or
broader compatibility, performance, or platform claims added.

The later [q/z/R/Rh following-r batch](case-symbols-reph.md#following-r-after-q-z-r-and-rh)
resolves the basic following-r gaps above. Other outputs in the table are
historical; see the current handoff for remaining limitations.

## Basic lowercase v consonant

Added on 2026-10-28: exact lowercase `v` produces ভ (U+09AD) and establishes
consonant context for supported vowels and aliases, sharing that basic output
with existing `bh`. The basic inventory is now 40 input sequences producing
35 distinct letters. Matching remains case-sensitive and uses the raw keys.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `v` | ভ | U+09AD |
| `va` | ভা | U+09AD U+09BE |
| `vi` | ভি | U+09AD U+09BF |
| `vI` / `vee` | ভী | U+09AD U+09C0 |
| `vU` | ভূ | U+09AD U+09C2 |
| `vOI` | ভৈ | U+09AD U+09C8 |
| `vrri` | ভৃ | U+09AD U+09C3 |
| `vy` / `vZ` | ভ্য | U+09AD U+09CD U+09AF |
| `vY` | ভয় | U+09AD U+09DF |

All supported vowels/aliases follow existing consonant context, including silent
lowercase `o` (`vo` → `ভ`) and subsequent vowel transitions (`via` → `ভিয়া`,
`vua` → `ভুয়া`). Existing longer `aZ`/`oZ` matches retain priority
(`vaZ` → `ভঅ্যা`, `voZ` → `ভঅ্য`). Ordinary adjacency remains separate:
`vh` → `ভহ`, `vv` → `ভভ`, and `vbh` → `ভভ`. Existing `bh` still matches as ভ.
Words follow the typed spelling without correction: `valO` → `ভালো`,
`vumi` → `ভুমি`, `vUmi` → `ভূমি`, and `vasha` → `ভাশা`.

The 136 independently authored [fixtures](../../tests/fixtures/consonant-v.tsv)
were checked against the SHA-256-verified pinned parser before implementation.
They cover every supported vowel/alias before and after `v`, following-vowel
transitions, ordinary adjacency and `bh` controls, repetition, `y`/`Y`/`Z`
distinctions, digits, boundaries, copied Unicode, and words. All 4,000 reference
cases match. Copied characters and digits reset context (`v🙂a` → `ভ🙂আ`,
`v1a` → `ভ১আ`), and separate calls share no state. Rust regressions also cover
control-character boundaries and long mixed input; no performance result claimed.

Uppercase aliases, conjunct/reph forms, and escapes remain incomplete:

| Input | Engine at that step | Reference |
| --- | --- | --- |
| `V` | V | ভ (U+09AD) |
| `vr` | ভর | ভ্র (U+09AD U+09CD U+09B0) |
| `` v`a `` | `` ভ`আ `` | ভআ (U+09AD U+0986) |
| `` v`h `` | `` ভ`হ `` | ভহ (U+09AD U+09B9) |

Gap probes at that step covered `w`, `V`, `vr`, `AZ`, `rrY`, `` v`a ``, and `` v`h ``.
The later [d/dh batch](conjunct-batches.md#d-and-dh-conjunct-batch) resolves `vr`.
The [next increment](#contextual-lowercase-w) adds lowercase `w` and its
context-dependent forms: ও independently (`w`) and ্ব after a consonant (`kw`).
Other remaining letters, conjunct/reph forms, aliases, punctuation/escapes,
composition, and platform integration remain incomplete. No dependencies or
broader compatibility, performance, or platform claims added.

## Contextual lowercase w

Added on 2026-10-28: exact lowercase `w` produces ও (U+0993) independently
and after a supported vowel, or ্ব (U+09CD U+09AC) after a supported consonant.
This is a context rule; the 40 basic consonant sequences producing 35 letters
remain unchanged. Context comes from raw matched keys, not copied Bangla glyphs.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `w` | ও | U+0993 |
| `wa` | ওয়া | U+0993 U+09DF U+09BE |
| `wi` | ওয়ি | U+0993 U+09DF U+09BF |
| `wI` / `wee` | ওয়ী | U+0993 U+09DF U+09C0 |
| `wo` | ওয় | U+0993 U+09DF |
| `wOI` | ওয়ৈ | U+0993 U+09DF U+09C8 |
| `wrri` | ওৃ | U+0993 U+09C3 |
| `awa` | আওা | U+0986 U+0993 U+09BE |
| `kw` | ক্ব | U+0995 U+09CD U+09AC |
| `kwa` | ক্বা | U+0995 U+09CD U+09AC U+09BE |
| `ww` | ও্ব | U+0993 U+09CD U+09AC |
| `wy` / `wZ` | ও্য | U+0993 U+09CD U+09AF |
| `wY` | ওয় | U+0993 U+09DF |

At the start or immediately after a copied character/digit, `w` adds য়
(U+09DF) before a following supported raw vowel key: `a`/`i`/`I`/`u`/`U`/`e`/`o`/`O`.
This also covers aliases starting with those keys (`woo` → `ওয়ু`,
`wOU` → `ওয়ৌ`). It does not consume the vowel: ordinary vowel/alias matching
continues. Longer `aZ`/`oZ` still match first at the next position, so
`waZ` → `ওয়অ্যা` and `woZ` → `ওয়অ্য`. The vowel `rri` begins with `r`
and does not insert য় (`wrri` → `ওৃ`).

After a supported vowel, `w` adds only ও even before another vowel:
`awa` → `আওা`, `iwa` → `ইওা`, `awaZ` → `আওঅ্যা`. After a supported
consonant, it adds ্ব (`rw` → `র্ব`, `Yw` → `য়্ব`, `ngw` → `ং্ব`).
Every form establishes consonant context without a U+200D joiner, including
independent `w`: `www` → `ও্ব্ব`, `wwa` → `ও্বা`, `kwrri` → `ক্বৃ`.
Following vowel transitions remain unchanged (`wia` → `ওয়িয়া`, `woa` → `ওয়য়া`).
The engine preserves these exact reference sequences without normalization or
spelling correction. Examples include `hawa` → `হাওা`, `dwara` → `দ্বারা`,
and `swamI` → `স্বামী`.

The 311 independently authored [fixtures](../../tests/fixtures/consonant-w.tsv)
were checked against the SHA-256-verified pinned parser before implementation.
They cover every basic consonant before `w` except the separate `rrw` reph
gap, supported context forms, all supported vowels/aliases before and after `w`,
following-vowel transitions, repetition, `y`/`Y`/`Z` distinctions, digits,
boundaries, copied Unicode, and words. All 4,311 reference cases match.
Digits and copied characters reset context (`w1a` → `ও১আ`,
`k🙂wa` → `ক🙂ওয়া`); copied decomposed য় remains U+09AF U+09BC.
Separate calls share no state. Rust regressions also cover control-character
boundaries and long mixed input; no performance result claimed.

Uppercase aliases, following-`r` attachments, reph, and escapes remain incomplete:

| Input | Engine at that step | Reference |
| --- | --- | --- |
| `W` | W | ও (U+0993) |
| `wA` | ওA | ওয়া (U+0993 U+09DF U+09BE) |
| `wrr` | ওরর | ও্রর (U+0993 U+09CD U+09B0 U+09B0) |
| `wrrri` | ওরররি | ও্রররি (U+0993 U+09CD U+09B0 U+09B0 U+09B0 U+09BF) |
| `rrw` | রর্ব | র্্ব (U+09B0 U+09CD U+09CD U+09AC) |
| `` w`a `` | `` ও`আ `` | ওআ (U+0993 U+0986) |
| `` w`h `` | `` ও`হ `` | ওহ (U+0993 U+09B9) |

Gap probes at that step covered `W`, `wrr`, `wrrri`, `rrw`, `AZ`, `` w`a ``, and `` w`h ``.
The [next increment](#following-r-after-lowercase-w) resolves following-`r`
priority after lowercase `w`, keeping reph and uppercase aliases separate.
Other remaining letters, conjunct/reph forms, aliases, punctuation/escapes, composition, and platform
integration remain incomplete. No dependencies or broader compatibility,
performance, or platform claims added.

## Following r after lowercase w

Added on 2026-10-28: selected following-`r` forms after exact lowercase `w`.
They share lowercase `y`'s two-`r` matching priority and exceptions, reusing the
existing helper. The helper is now named `consume_following_r_prefix` to cover
all four callers (`y`/`Z`/`Y`/`w`). The 40 basic consonant sequences producing
35 letters remain unchanged.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `wr` | ওর | U+0993 U+09B0 |
| `wrr` | ও্রর | U+0993 U+09CD U+09B0 U+09B0 |
| `wrri` | ওৃ | U+0993 U+09C3 |
| `wrrri` | ও্রররি | U+0993 U+09CD U+09B0 U+09B0 U+09B0 U+09BF |
| `wrrrri` | ও্ররৃ | U+0993 U+09CD U+09B0 U+09B0 U+09C3 |
| `wry` / `wrZ` | ওর‍্য | U+0993 U+09B0 U+200D U+09CD U+09AF |
| `wrry` / `wrrZ` | ওরর‍্য | U+0993 U+09B0 U+09B0 U+200D U+09CD U+09AF |
| `kwrr` | ক্ব্রর | U+0995 U+09CD U+09AC U+09CD U+09B0 U+09B0 |
| `awrr` | আও্রর | U+0986 U+0993 U+09CD U+09B0 U+09B0 |

Two `r` keys after `w` normally add ্রর (U+09CD U+09B0 U+09B0). Those keys
are consumed before ordinary matching resumes: `wrrri` leaves `ri`, and
`wrrrri` leaves `rri`. Existing `rri` and `rry`/`rrZ` retain priority:
`wrri` → `ওৃ`, `wrry` → `ওরর‍্য`. A single `r` stays separate, including
before `y`/`Z`; `wry` keeps U+200D, unlike `Zry`/`Yry`.
Following vowels and aliases use ordinary consonant context (`wrri` → `ওৃ`,
`wrree` → `ও্ররী`), with transitions preserved (`wrrria` → `ও্রররিয়া`).

The rule follows the raw `w` key across all its supported contexts:
`kwrr` → `ক্ব্রর`, `awrr` → `আও্রর`, `wwrr` → `ও্ব্রর`.
Repetition starts fresh context (`wrrwrr` → `ও্রর্ব্রর`), while existing
`aZ`/`oZ` priority is preserved (`waZrr` → `ওয়অ্যা্রর`). Because `wrr`
consumes both `r` keys before the next `w`, `wrrw` → `ও্রর্ব` does not
invoke the separate, still-missing `rrw` reph rule. No output normalization
or spelling correction is performed.

The 385 independently authored [fixtures](../../tests/fixtures/w-following-r.tsv)
were checked against the SHA-256-verified pinned parser before implementation.
They cover runs of one through eight `r` keys, `rri` and `rry`/`rrZ`
exceptions, vowels/aliases and transitions, preceding contexts, repetitions,
case distinctions, all digits, boundaries, and copied Unicode. All 4,696
reference cases match. Copied decomposed য় remains U+09AF U+09BC.
Digits and copied characters reset context (`w1rr` → `ও১রর`,
`wrr🙂ry` → `ও্রর🙂র‍্য`), and separate calls share no state. Rust regressions
also cover control characters and long mixed input; no performance result claimed.

Gap probes at that step covered `x`, `kx`, `W`, `rrw`, `AZ`, `` w`a ``, and `` w`h ``.
Lowercase `x` was still literal in the engine, while the reference produces
এক্স (U+098F U+0995 U+09CD U+09B8) independently and ক্ষ
(U+0995 U+09CD U+09B7) in `kx`. The
[next increment](#contextual-lowercase-x-and-exact-kx) adds those forms.
Uppercase aliases, `rrw` and other reph/conjunct forms,
punctuation/escapes, composition, and platform integration remain incomplete.
No dependencies or broader compatibility, performance, or platform claims added.

## Contextual lowercase x and exact kx

Added on 2026-10-28: exact lowercase `x` produces এক্স at the start or after
a copied character/digit, and ক্স after supported converted input. Exact `kx`
produces ক্ষ, matching before single `k`. This increment includes that two-key
form because it was an explicit gap in the planned `x` slice; longer matches
such as `Ngx` remain separate. The inventory of 40 basic consonant sequences
producing 35 letters is unchanged; `kx` is an added conjunct sequence.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `x` | এক্স | U+098F U+0995 U+09CD U+09B8 |
| `xa` | এক্সা | U+098F U+0995 U+09CD U+09B8 U+09BE |
| `xi` | এক্সি | U+098F U+0995 U+09CD U+09B8 U+09BF |
| `ax` | আক্স | U+0986 U+0995 U+09CD U+09B8 |
| `qx` | কক্স | U+0995 U+0995 U+09CD U+09B8 |
| `kx` | ক্ষ | U+0995 U+09CD U+09B7 |
| `kxa` | ক্ষা | U+0995 U+09CD U+09B7 U+09BE |
| `kxrri` | ক্ষৃ | U+0995 U+09CD U+09B7 U+09C3 |
| `xx` | এক্সক্স | U+098F U+0995 U+09CD U+09B8 U+0995 U+09CD U+09B8 |
| `xy` / `xZ` | এক্স্য | U+098F U+0995 U+09CD U+09B8 U+09CD U+09AF |
| `kxY` | ক্ষয় | U+0995 U+09CD U+09B7 U+09DF |

Context comes from supported raw matches, not copied Bangla. Both `x` and `kx`
establish consonant context without a U+200D joiner, supporting vowel signs
and aliases (`xee` → `এক্সী`, `kxOU` → `ক্ষৌ`) and following transitions
(`xia` → `এক্সিয়া`, `xoa` → `এক্সয়া`). Repeated `x` adds ক্স
after the first (`xxx` → `এক্সক্সক্স`, `kxx` → `ক্ষক্স`). Existing longer
`aZ`/`oZ` matches keep priority (`xaZ` → `এক্সঅ্যা`, `kxoZ` → `ক্ষঅ্য`).
Other supported adjacency remains distinct (`qx` → `কক্স`, `khx` → `খক্স`,
`NGx` → `ঞক্স`). `xr` stays separate (`xr` → `এক্সর`), `xrri` adds ৃ,
and `xry` retains the basic-`r` U+200D joiner. No spelling correction or
normalization is performed.

The 392 independently authored [fixtures](../../tests/fixtures/consonant-x.tsv)
were checked against the SHA-256-verified pinned parser before implementation.
They cover all basic consonants before `x` except the separate `Ngx`/`rrx`
gaps, all supported vowels/aliases before and after the selected forms,
vowel transitions, repetition, `y`/`Y`/`Z` distinctions, raw-spelling controls,
digits, boundaries, copied Unicode, and words. All 5,088 reference cases match.
Digits and copied characters reset context (`1xa` → `১এক্সা`,
`k🙂xa` → `ক🙂এক্সা`); copied decomposed য় stays U+09AF U+09BC.
Separate calls share no state. Rust regressions also cover control-character
boundaries and long mixed input; no performance result claimed.

At that step, longer matches, following-`r` attachments, reph, uppercase aliases,
and escapes remained incomplete:

| Input | Engine at that step | Reference |
| --- | --- | --- |
| `Ngx` | ঙক্স | ঙ্ষ (U+0999 U+09CD U+09B7) |
| `kkx` (resolved below) | কক্ষ | ক্কক্স (U+0995 U+09CD U+0995 U+0995 U+09CD U+09B8) |
| `xrr` | এক্সরর | এক্স্রর (U+098F U+0995 U+09CD U+09B8 U+09CD U+09B0 U+09B0) |
| `kxrr` | ক্ষরর | ক্ষ্রর (U+0995 U+09CD U+09B7 U+09CD U+09B0 U+09B0) |
| `rrx` | ররক্স | র্ক্স (U+09B0 U+09CD U+0995 U+09CD U+09B8) |
| `X` | X | এক্স (U+098F U+0995 U+09CD U+09B8) |
| `` x`a `` | `` এক্স`আ `` | এক্সআ (U+098F U+0995 U+09CD U+09B8 U+0986) |
| `` x`h `` | `` এক্স`হ `` | এক্সহ (U+098F U+0995 U+09CD U+09B8 U+09B9) |

Gap probes at that step covered `Ngx`, `kkx`, `xrr`, `kxrr`, `X`, `` x`a ``, and `` x`h ``.
The [next increment](#following-r-after-lowercase-x-and-exact-kx) resolves
following-`r` priority after `x` and exact `kx`, keeping longer matches, reph,
and uppercase aliases separate. Other letter
forms, conjuncts, punctuation/escapes, composition, and platform integration
remain incomplete. No dependencies or broader compatibility, performance,
or platform claims added.

## Following r after lowercase x and exact kx

Added on 2026-10-28: selected following-`r` forms after lowercase `x` and exact
`kx`, reusing the existing raw-key helper. Both share the two-`r` matching
priority and exceptions of lowercase `y`/`w`. The 40 basic consonant sequences
producing 35 letters and the existing `kx` conjunct remain unchanged.

| Input | Output | Exact Unicode |
| --- | --- | --- |
| `xr` | এক্সর | U+098F U+0995 U+09CD U+09B8 U+09B0 |
| `xrr` | এক্স্রর | U+098F U+0995 U+09CD U+09B8 U+09CD U+09B0 U+09B0 |
| `xrri` | এক্সৃ | U+098F U+0995 U+09CD U+09B8 U+09C3 |
| `xrrri` | এক্স্রররি | U+098F U+0995 U+09CD U+09B8 U+09CD U+09B0 U+09B0 U+09B0 U+09BF |
| `xrrrri` | এক্স্ররৃ | U+098F U+0995 U+09CD U+09B8 U+09CD U+09B0 U+09B0 U+09C3 |
| `xry` / `xrZ` | এক্সর‍্য | U+098F U+0995 U+09CD U+09B8 U+09B0 U+200D U+09CD U+09AF |
| `xrry` / `xrrZ` | এক্সরর‍্য | U+098F U+0995 U+09CD U+09B8 U+09B0 U+09B0 U+200D U+09CD U+09AF |
| `kxrr` | ক্ষ্রর | U+0995 U+09CD U+09B7 U+09CD U+09B0 U+09B0 |
| `kxrri` | ক্ষৃ | U+0995 U+09CD U+09B7 U+09C3 |
| `kxrrri` | ক্ষ্রররি | U+0995 U+09CD U+09B7 U+09CD U+09B0 U+09B0 U+09B0 U+09BF |
| `kxrrrri` | ক্ষ্ররৃ | U+0995 U+09CD U+09B7 U+09CD U+09B0 U+09B0 U+09C3 |
| `axrr` | আক্স্রর | U+0986 U+0995 U+09CD U+09B8 U+09CD U+09B0 U+09B0 |

Two `r` keys normally add ্রর (U+09CD U+09B0 U+09B0) and are consumed
before ordinary matching resumes. Thus `xrrri` leaves `ri`, and `xrrrri`
leaves `rri`. Existing `rri` and `rry`/`rrZ` matches retain priority:
`xrri` → `এক্সৃ`, `xrry` → `এক্সরর‍্য`. A single `xr`/`kxr` stays separate,
including before `y`/`Z`, and preserves the basic-`r` U+200D joiner.
These rules apply in every supported preceding context (`qxrr` → `কক্স্রর`,
`akxrr` → `আক্ষ্রর`) and in repetitions (`xrrxrr` → `এক্স্ররক্স্রর`).
Because `xrr` consumes both `r` keys before a following `x` or `kx`, those
repetitions do not invoke the separate, still-missing `rrx`/`rrkx` reph rules.
Vowels and aliases use ordinary consonant context (`xrree` → `এক্স্ররী`),
with following transitions preserved (`xrrria` → `এক্স্রররিয়া`).
No output normalization or spelling correction is performed.

The 755 independently authored [fixtures](../../tests/fixtures/x-following-r.tsv)
were checked against the SHA-256-verified pinned parser before implementation.
They cover one through eight `r` keys, `rri` and `rry`/`rrZ` exceptions,
vowels/aliases and transitions, preceding contexts, repetitions, digits,
boundaries, and copied Unicode. All 5,843 reference cases match. Digits and
copied characters reset context (`x1rr` → `এক্স১রর`,
`kxrr🙂ry` → `ক্ষ্রর🙂র‍্য`); copied decomposed য় stays U+09AF U+09BC.
Separate calls share no state. Rust regressions also cover control-character
boundaries and long mixed input; no performance result claimed.

Gap probes at that step covered `Ngx`, `kkx`, `rrx`, `rrkx`, `X`, `` x`a ``, and `` x`h ``.
The earlier gap table records their exact reference output except `rrkx`:
current `ররক্ষ`, reference `র্ক্ষ` (U+09B0 U+09CD U+0995 U+09CD U+09B7).
The [next increment](exact-conjuncts.md#exact-ngx-conjunct) adds exact `Ngx` → ঙ্ষ and its
supported vowel/context interactions. At that step, `kkx`, reph, uppercase aliases, other
conjuncts, punctuation/escapes, composition, and platform integration remained separate.
The [later `kk` increment](exact-conjuncts.md#exact-kk-conjunct) resolves `kkx`.
No dependencies or broader compatibility, performance, or platform claims added.
