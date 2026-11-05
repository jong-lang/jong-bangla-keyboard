# Case aliases, symbols, escapes and reph

Historical compatibility evidence, grouped by rule family. The outputs, counts
and unresolved gaps below describe each dated implementation stage. Use the
[current requirements](../v1.md), [compatibility policy](../compatibility.md)
and regression fixtures for current behavior. These records do not form a bug
tracker. Other rule families are indexed in
[Historical conversion increments](../compatibility.md#historical-conversion-increments).

## Selective ASCII case-alias batch

Added on 2026-10-29: the 14 ASCII capitals below alias their lowercase forms
before scanning. This completes 15 of the 27 uppercase/alternate spellings
from the standalone audit, including `AZ`. Scope was fixed after independently
checking each spelling and separating the explicit G/J behavior: `Jh` must
produce জহ, whereas `jh` produces ঝ. Folding G or J would also destroy
`Ng`/`NG` and other case-sensitive matches, so those forms are a separate batch.
No upstream source, rule tables, fixtures, dependencies, or normalization code
were imported. Implementation and expected fixtures are independently authored.

| Input | Alias | Standalone output | Exact Unicode | Fixture rows |
| --- | --- | --- | --- | --- |
| `A` | `a` | আ | U+0986 | [7543](../../tests/fixtures/case-alias-a.tsv) |
| `B` | `b` | ব | U+09AC | [5743](../../tests/fixtures/case-alias-b.tsv) |
| `C` | `c` | চ | U+099A | [5767](../../tests/fixtures/case-alias-c.tsv) |
| `E` | `e` | এ | U+098F | [2747](../../tests/fixtures/case-alias-e.tsv) |
| `F` | `f` | ফ | U+09AB | [2980](../../tests/fixtures/case-alias-f.tsv) |
| `H` | `h` | হ | U+09B9 | [14627](../../tests/fixtures/case-alias-h.tsv) |
| `K` | `k` | ক | U+0995 | [9211](../../tests/fixtures/case-alias-k.tsv) |
| `L` | `l` | ল | U+09B2 | [14048](../../tests/fixtures/case-alias-l.tsv) |
| `M` | `m` | ম | U+09AE | [11455](../../tests/fixtures/case-alias-m.tsv) |
| `P` | `p` | প | U+09AA | [8423](../../tests/fixtures/case-alias-p.tsv) |
| `Q` | `q` | ক | U+0995 | [893](../../tests/fixtures/case-alias-q.tsv) |
| `V` | `v` | ভ | U+09AD | [2948](../../tests/fixtures/case-alias-v.tsv) |
| `W` | `w` | ও | U+0993 | [1590](../../tests/fixtures/case-alias-w.tsv) |
| `X` | `x` | এক্স | U+098F U+0995 U+09CD U+09B8 | [2581](../../tests/fixtures/case-alias-x.tsv) |

[`Mixed-case fixtures`](../../tests/fixtures/case-alias-mixed.tsv) add 18,577 rows;
[`resolved partial-output assertions`](../../tests/fixtures/case-alias-resolved.tsv)
add 113. Together the 16 files contain **109,246** new rows. All **353,674**
earlier rows remain unchanged. The 107 old partial-output assertions now have
passing reference coverage; the extra six resolved rows cover QX/qXZ/qXYZ
and uppercase M after the three ক্ষ্ম spellings.

Every new row was checked independently against the SHA-256-verified pinned
parser before claiming support. Expected outputs and code points come from our
existing independently authored lowercase fixtures and explicit new examples;
they were not harvested from parser output. Per-letter rows cover vowels/ya,
preceding contexts, r runs and exceptions, neighboring matches, consumption,
and boundaries. Mixed-case rows exercise every combination of alias positions
in the covered basic/conjunct spellings and their supported contexts. A separate
**86,996** ASCII-letter pair/triple audit found no difference between the raw
reference input and input folded with exactly these 14 aliases. This is evidence
for the selected aliases, not blanket case folding or full compatibility.

Aliases apply everywhere in a match, including consumed-key boundaries:
`AZ` → অ্যা (U+0985 U+09CD U+09AF U+09BE), `kH` → খ, `SH` → ষ,
`NgK` → ঙ্ক, `KKHN` → ক্ষ্ণ, `KSHM` → ক্ষ্ম, `mB` → ম্ব,
and `ShM` → ষ্ম. `AA` → আআ and `WA` → ওয়া keep normalized raw vowel
context. `SPL` → শপ্ল, while `sPL` → স্প্ল: uppercase S stays distinct.
`kK` → ক্ক, `kkH` → ক্ষ, and `kSH` → ক্ষ preserve existing rule priority.
The input argument is never modified or retained. Calls without these capitals
borrow their input for scanning; affected calls use a temporary normalized copy.
No performance claim follows from this implementation choice.

Rust regressions check all internal splits of 15 selected mixed-case spellings
(25 split positions), separate calls, NUL/newline/tab, copied Bangla, combining
marks, emoji, Unicode lookalikes, and 1,024 repeated mixed-input segments.
An additional **313** authored boundary/case expectations match the pinned parser.
The 43 Unicode-contract cases and one G/J gap case are explicitly excluded
from parity evidence. Copied Unicode still passes through unchanged: for example,
this engine preserves `K` while the reference gives ক; the reference also
lowercases fullwidth `Ａ` to `ａ`. This batch preserves the documented Unicode
passthrough contract rather than adopting that unrelated reference behavior.

Normalization does not repair underlying gaps: `Qr` still gives কর against
reference ক্র, and `Qrr` remains separate r letters; reph and vowel-context
edges also remain. G/J spellings and aliases exposed after consumed keys stay
explicit gaps (`ShNG` → ষ্ণG against reference ষ্ণগ).
The standalone audit again checked **302** distinct inputs and now has **37**
discrepancies: 12 explicit G/J spellings (`Ghn`, `Gdh`, `GN`, `Gn`, `Gm`,
`Gl`, `GG`, `Gg`, `gG`, `Gh`, `G`, `J`) and 25 punctuation/symbol/escape
spellings. This excludes context interactions and is not a compatibility percentage.
Resolved `ShM` in the five reference-gap probes was replaced by `Jh`.

All **462,920** fixture rows match the pinned parser. Formatting, Clippy,
**280 integration tests**, one doctest, release/documentation builds, and
default/batch smoke checks passed; commands and limitations are in the
[handoff](../progress.md). Next, investigate the explicit G/J rules and their
consumed/fresh-key behavior without normalizing either letter. Composition,
Fcitx5, platform support, and performance remain unimplemented or unverified.

## Explicit G/J spelling batch

Added on 2026-10-29: all 12 remaining standalone G/J spellings are implemented
as explicit matches, without folding either letter. This supersedes the G/J
limitations recorded in older sections, including partial outputs after consumed
keys and separate calls split inside NG/cNG/jNG. The basic inventory now has
43 sequences producing the same 35 consonant letters; the nine new conjunct
spellings add no new letters. The 14 earlier case aliases are unchanged.
No upstream source, rule tables, fixtures or dependencies were imported.

| Spelling | Output | Exact Unicode | Fixture rows |
| --- | --- | --- | --- |
| `Ghn` | ঘ্ন | U+0998 U+09CD U+09A8 | [514](../../tests/fixtures/explicit-gj-ghn.tsv) |
| `Gdh` | গ্ধ | U+0997 U+09CD U+09A7 | [514](../../tests/fixtures/explicit-gj-gdh.tsv) |
| `GN` | গ্ণ | U+0997 U+09CD U+09A3 | [452](../../tests/fixtures/explicit-gj-g-n-retroflex.tsv) |
| `Gn` | গ্ন | U+0997 U+09CD U+09A8 | [452](../../tests/fixtures/explicit-gj-gn.tsv) |
| `Gm` | গ্ম | U+0997 U+09CD U+09AE | [514](../../tests/fixtures/explicit-gj-gm.tsv) |
| `Gl` | গ্ল | U+0997 U+09CD U+09B2 | [514](../../tests/fixtures/explicit-gj-gl.tsv) |
| `GG` | জ্ঞ | U+099C U+09CD U+099E | [452](../../tests/fixtures/explicit-gj-g-upper-pair.tsv) |
| `Gg` | জ্ঞ | U+099C U+09CD U+099E | [452](../../tests/fixtures/explicit-gj-g-upper-lower.tsv) |
| `gG` | জ্ঞ | U+099C U+09CD U+099E | [452](../../tests/fixtures/explicit-gj-g-lower-upper.tsv) |
| `Gh` | ঘ | U+0998 | [514](../../tests/fixtures/explicit-gj-gh.tsv) |
| `G` | গ | U+0997 | [452](../../tests/fixtures/explicit-gj-g-basic.tsv) |
| `J` | জ | U+099C | [452](../../tests/fixtures/explicit-gj-j-basic.tsv) |

The 12 per-spelling files and [435 control rows](../../tests/fixtures/explicit-gj-controls.tsv)
add **6,169** authored fixtures. Each spelling was independently checked against
the SHA-256-verified pinned parser for Unicode, preceding contexts, vowels/ya,
following-r runs and exceptions, aliases, boundaries and interactions with
existing matches. Expected outputs were authored before comparison, not
harvested from parser output. All **462,920** earlier fixture rows are unchanged.

Explicit matches preserve consumption: `GGh` → জ্ঞহ, `Ghnn` → ঘ্নন,
and `GNG` → গ্ণগ. `NG` → ঞ still consumes G; `nG` → নগ leaves G fresh,
while `ng` → ং and `Ng` → ঙ stay distinct. Earlier `ShN` consumes N
in `ShNG` → ষ্ণগ; the exposed G can begin another rule in `ShNGdh` → ষ্ণগ্ধ.
This also resolves `kkhNG`/`kShNG`/`kxNG` → ক্ষ্ণগ and split-call cases
such as separate `cN` → চণ and `G` → গ, while combined `cNG` → চ্ঞ.

`J` is only a basic consonant match: `Jh` → জহ, `JJ` → জজ,
`JNG` → জঞ and `nJ` → নজ remain distinct from lowercase `jh` → ঝ,
`jj` → জ্জ, `jNG` → জ্ঞ and `nj` → ঞ্জ. `Gdh` → গ্ধ differs from
`GDh` → গঢ because D remains case-sensitive. Uppercase H aliases work:
`GHn` → ঘ্ন and `GdH` → গ্ধ; `GHN` → ঘণ keeps uppercase N distinct.

All selected spellings attach single r without U+200D. Two following r keys
normally attach ্রর, while `rri` and `rry`/`rrZ` keep priority:
`Gr` → গ্র, `Grr` → গ্রর, `Grri` → গৃ, `Grrri` → গ্রররি,
`Grry` → গরর‍্য, `Jry` → জ্র্য. Control rows independently check
following r after exposed G and longer matches. Rust regressions cover every
internal split of ten multi-key selected spellings plus Jh/cNG/jNG/ShNG,
separate calls, UTF-8 boundaries, NUL/newline/tab/combining marks, unchanged
input ownership, and 1,024 repeated mixed-input segments. An additional **82**
authored boundary and repeated-input expectations match the pinned parser.
The initial targeted long-input test caught a mistaken GHN expectation (N is
not a lowercase-n alias); the corrected GHn case matches the reference.

The standalone audit again checked **302** distinct inputs: **25** discrepancies
remain, all punctuation/symbol/escape forms. This audit excludes context
interactions and is not a compatibility percentage. Reph, vowel-context edges,
following-r gaps after q/z/R/Rh, and reference Unicode-lowercasing differences
remain. The five reference-gap probes now use qr/zr/Rr/rrShN and escaped Shm.

All **469,089** fixture rows match the pinned parser. Formatting, Clippy,
**294 integration tests**, one doctest, release/documentation builds and
smoke checks passed; actual commands and limits are recorded in the
[handoff](../progress.md). Next, investigate the related punctuation/symbol forms;
vowel escapes, reph, composition and platform integration remain separate work.
No desktop support or performance claim follows from these checks.

## Punctuation and symbol batch

Added on 2026-10-29: 11 related spellings, independently authored and checked
against the pinned parser. This supersedes older literal-backtick and symbol
gap outputs recorded above; the earlier sections retain their original-step
evidence. No upstream code, rule tables, fixtures or dependencies were imported.

| Spelling | Output | Exact Unicode | Fixture rows |
| --- | --- | --- | --- |
| `.` | । | U+0964 | [980](../../tests/fixtures/symbols-period.tsv) |
| `..` | ।। | U+0964 U+0964 | [980](../../tests/fixtures/symbols-double-period.tsv) |
| `...` | ... | U+002E U+002E U+002E | [980](../../tests/fixtures/symbols-ellipsis.tsv) |
| `` .` `` | . | U+002E | [980](../../tests/fixtures/symbols-escaped-period.tsv) |
| `:` | ঃ | U+0983 | [980](../../tests/fixtures/symbols-colon.tsv) |
| `` :` `` | : | U+003A | [980](../../tests/fixtures/symbols-escaped-colon.tsv) |
| `^` | ঁ | U+0981 | [980](../../tests/fixtures/symbols-caret.tsv) |
| `` ^` `` | ^ | U+005E | [980](../../tests/fixtures/symbols-escaped-caret.tsv) |
| `,,` | ্‌ | U+09CD U+200C | [980](../../tests/fixtures/symbols-double-comma.tsv) |
| `$` | ৳ | U+09F3 | [980](../../tests/fixtures/symbols-dollar.tsv) |
| `` ` `` | empty | empty | [805](../../tests/fixtures/symbols-backtick.tsv) |

The 11 per-spelling files plus [219 controls](../../tests/fixtures/symbols-controls.tsv)
add **10,824** authored rows. Each spelling has independent Unicode, preceding
context, vowel/ya, following-r, conjunct, digit and Unicode-boundary evidence.
The double-comma output is exactly U+09CD (virama) followed by U+200C (zero-width
non-joiner), not U+200D. An ellipsis emits three literal ASCII periods.
All **469,089** earlier fixture rows are unchanged.

Matching consumes raw keys in verified order: ellipsis before double and single
period, and symbol escapes before their one-key forms. For example, four periods
produce three literal periods followed by a danda; five produce three literal
periods followed by two dandas. In `` ..` `` the double period consumes both
periods before the backtick is discarded, yielding ।।; in `` ....` `` an ellipsis
consumes three periods and the final escaped period emits one literal period.
Repeated escaped symbols, odd/even comma runs, backtick runs, and all 121 pairs
of selected spellings separated by a consonant are covered by the controls.

Every selected token resets raw phonetic context, even when its output is empty.
Thus `` k`a `` → কআ, `` r`y `` → রইয়, `` k`x `` → কএক্স, and
`` k`h `` → কহ, whereas `kh` → খ. A backtick does not copy the following key
literally: after the separator, the next raw key begins a fresh phonetic match.
No context is inferred from emitted or passed-through Bangla marks.

Standalone backtick removal belongs in this batch because it completes symbol
escapes and separates consonant matches without a vowel-sign dependency.
**Longer vowel escapes and t-double-backtick remain unimplemented.** Backticks
now disappear in those inputs, but the preceding ordinary vowel or t output is
still partial: `` a` `` currently yields আ rather than the reference sign া,
and ``` t`` ``` currently yields ত rather than ৎ. A later batch must match those
longer forms before their shorter vowel/consonant and backtick tokens; this is
not a general escape mechanism. This explicitly updates the old literal-backtick
limitations without claiming the longer forms work.

The controls migrate **53** previous literal-backtick assertions and two
period assertions to exact compatibility evidence, plus check the three
kkhm/kShm/kxm backtick-vowel forms previously asserted in a loop. Rust additionally
checks all seven internal split positions of the six multi-key forms, separate
calls, input ownership, NUL/newline/carriage-return/tab/Unicode boundaries, and
1,024 repeated mixed-input segments. **89** additional authored boundary and
repeated-input expectations independently match the reference.

All **479,913** fixture rows match the SHA-256-verified pinned parser.
Formatting, Clippy, **309 integration tests**, one doctest, release/documentation
builds, default/symbol smoke checks and documentation consistency checks passed;
actual commands and outcomes are in the [handoff](../progress.md).
The standalone audit checks 302 distinct inputs and now has **15 discrepancies**:
vowel-sign escapes (including aliases) and t-double-backtick. The new ellipsis
coverage is additional to that inventory. Context interactions are excluded from
the audit, so the count is not a compatibility percentage. Reph, vowel-context
edges, following-r gaps after q/z/R/Rh, and reference Unicode-lowercasing differences
remain. Next, investigate the vowel-sign escapes as one related batch;
t-double-backtick, reph, composition and platform work remain separate unless
reference evidence establishes a necessary shared dependency. No performance
or desktop-support claim follows from these checks.

## Vowel-sign escape batch

Added on 2026-10-29: all 13 vowel-sign escape spellings and five existing A/E
case variants. This supersedes the earlier vowel-escape gap outputs, including
the ordinary-vowel outputs recorded in the symbol batch. Earlier sections retain
the evidence from their original steps. No upstream code, rule tables, fixtures
or dependencies were imported; the public API and platform boundaries are unchanged.

| Spelling | Output | Exact Unicode | Fixture rows |
| --- | --- | --- | --- |
| `` a` `` | া | U+09BE | [1120](../../tests/fixtures/vowel-escape-a.tsv) |
| `` i` `` | ি | U+09BF | [1120](../../tests/fixtures/vowel-escape-i.tsv) |
| `` I` `` | ী | U+09C0 | [1120](../../tests/fixtures/vowel-escape-i-long.tsv) |
| `` u` `` | ু | U+09C1 | [1120](../../tests/fixtures/vowel-escape-u.tsv) |
| `` U` `` | ূ | U+09C2 | [1120](../../tests/fixtures/vowel-escape-u-long.tsv) |
| `` e` `` | ে | U+09C7 | [1120](../../tests/fixtures/vowel-escape-e.tsv) |
| `` ee` `` | ী | U+09C0 | [1120](../../tests/fixtures/vowel-escape-ee.tsv) |
| `` o` `` | empty | empty | [1120](../../tests/fixtures/vowel-escape-o.tsv) |
| `` O` `` | ো | U+09CB | [1120](../../tests/fixtures/vowel-escape-o-upper.tsv) |
| `` oo` `` | ু | U+09C1 | [1120](../../tests/fixtures/vowel-escape-oo.tsv) |
| `` OI` `` | ৈ | U+09C8 | [1120](../../tests/fixtures/vowel-escape-oi.tsv) |
| `` OU` `` | ৌ | U+09CC | [1120](../../tests/fixtures/vowel-escape-ou.tsv) |
| `` rri` `` | ৃ | U+09C3 | [1120](../../tests/fixtures/vowel-escape-rri.tsv) |
| `` A` `` | া | U+09BE | [1120](../../tests/fixtures/vowel-escape-a-upper.tsv) |
| `` E` `` | ে | U+09C7 | [1120](../../tests/fixtures/vowel-escape-e-upper.tsv) |
| `` eE` `` | ী | U+09C0 | [1120](../../tests/fixtures/vowel-escape-ee-lower-upper.tsv) |
| `` Ee` `` | ী | U+09C0 | [1120](../../tests/fixtures/vowel-escape-ee-upper-lower.tsv) |
| `` EE` `` | ী | U+09C0 | [1120](../../tests/fixtures/vowel-escape-ee-upper-pair.tsv) |

The 18 per-spelling files plus [2,007 controls](../../tests/fixtures/vowel-escape-controls.tsv)
add **22,167** authored rows. Each spelling independently checks Unicode, preceding
contexts, consumed keys, vowel/ya/following-r/conjunct/digit/Unicode suffixes,
repeated ticks, aliases and symbol interactions. The controls include all 324
ordered pairs of selected escape forms. All **479,913** earlier fixture rows
are unchanged; 13 old partial-output assertions are now covered by exact fixtures.

When the scanner reaches an escape, it consumes the vowel spelling together
with its backtick and writes the fixed sign shown above, irrespective of vowel
context. It then resets context, so a following key begins a fresh match:
`` a`a `` → াআ, `` a`y `` → াইয়, `` a`rri `` → াঋ, and
`` ko`a `` → কআ. Escaped lowercase o is explicitly empty; it still consumes
both keys and resets context. Extra backticks remain empty separators.
A preceding vowel does not insert য় before an escaped a: `` kia` `` → কিা.
Existing case normalization handles A/E inside longer matches; I/U/O and r/R
remain distinct. For example, `` eE` `` → ী while `` Oi` `` → ওি.

Earlier matches keep their verified priority and can consume keys before an
escape is reached. The ng forms consume one e/o: `` ngee` `` → ঙ্গেে and
`` ngoo` `` → ঙ্গ. Nasal-r forms consume the first r in `` Ngrri` `` → ঙররি,
whereas `` NGrrri` `` → ঞরৃ reaches a full rri escape after the prefix.
Basic rr similarly consumes the first two keys of `` rrri` `` → রররি;
`` rrrri` `` → ররৃ reaches the longer escape. The ordinary aZ/oZ matches
remain intact: `` aZ`a `` → অ্যাআ, versus `` a`Za `` → া্যা.
An earlier w still examines the upcoming raw vowel: `` wa` `` → ওয়া and
`` wo` `` → ওয়. An escape does not undo earlier consumption or lookahead.
These interactions have independent expectations, rather than inferring behavior
from another spelling with the same sign.

The implementation matches escapes before ordinary vowels and basic consonants,
including ordinary rri, while preserving ng/nasal-r priority. Rust additionally
checks **27** internal split positions across all 18 spellings, separate calls,
input ownership, NUL/newline/carriage-return/tab/Unicode boundaries and 1,024
repeated mixed-input segments. **173** extra authored boundary, split-call and
repeated-input expectations independently match the pinned parser.
During fixture authoring, overlapping rri spellings and w lookahead required
specific expected outputs; all final expectations passed independently before
implementation and in the final Rust checks.

All **502,080** fixture rows match the SHA-256-verified pinned parser.
Formatting, Clippy, **331 integration tests**, one doctest, release/documentation
builds, default/escape smoke checks and documentation consistency checks passed;
actual commands and outcomes are recorded in the [handoff](../progress.md).
The 302-input standalone audit now has **one discrepancy**, ``` t`` ```:
the engine emits ত while the reference emits ৎ (U+09CE). That form has no shared
implementation dependency with vowel-sign escapes and remains the next separate
step. The reference-gap probe now uses it instead of the resolved escaped a.
The audit excludes context interactions and is not a compatibility percentage.
Reph, vowel-context edges, following-r gaps after q/z/R/Rh and reference Unicode
lowercasing differences remain. Composition, Fcitx5 and performance validation
are still separate work; these checks establish no desktop-support claim.

## Final t escape

Added on 2026-10-29: the last standalone escape, lowercase t followed by two
backticks. This supersedes earlier partial outputs for that spelling, including
the gap in the vowel-sign batch. No upstream code, rule tables, fixtures or
dependencies were imported. A single-spelling step is appropriate here because
this is the only remaining related form in the standalone inventory; unrelated
following-r and reph changes remain separate.

| Spelling | Output | Exact Unicode | Fixture rows |
| --- | --- | --- | --- |
| ``` t`` ``` | ৎ | U+09CE | [1,995](../../tests/fixtures/final-escape-t.tsv) |

The output is the single Bangla khanda ta letter (ৎ), rather than ত followed by
a virama. The [1,596 consumption cases](../../tests/fixtures/final-escape-consumption.tsv)
and [476 controls](../../tests/fixtures/final-escape-controls.tsv) bring this step
to **4,067** independently authored rows. They cover exact Unicode, preceding
vowels/consonants/conjuncts, following vowels/ya/r, digits, case distinctions,
symbols, all 18 earlier vowel-escape spellings and repeated keys/backticks.
All **502,080** earlier fixture rows are unchanged. The old partial t-escape
assertion is replaced by exact fixture evidence.

The scanner matches all three raw keys before basic t. Both backticks belong
to the match and reset phonetic context, so ``` t``a ``` → ৎআ,
``` t``y ``` → ৎইয়, ``` t``rri ``` → ৎঋ and ``` t``ry ``` → ৎর‍্য.
The last example contains U+200D in the fresh r/ya match. Explicit vowel-sign
escapes still write their signs: ``` t``a` ``` → ৎা. Extra backticks are empty
separators. A single backtick does not produce khanda ta: `` t` `` → ত.
Uppercase T remains distinct: ``` T`` ``` → ট, while the existing H/K aliases
retain their behavior, including ``` tH`` ``` → থ and ``` Kt`` ``` → ক্ত.

Earlier conjunct matches retain consumed-key priority. In ``` nt`` ``` → ন্ত,
the nt match has already consumed t; similarly kt/st/sht/St/pt/tt retain their
conjunct output before the backticks disappear. A later fresh t can start the
escape: ``` ntt`` ``` → ন্তৎ, ``` ktt`` ``` → ক্তৎ and
``` ttt`` ``` → ত্তৎ. The consumption fixture independently checks 28 forms,
each with all 57 selected suffixes. Control rows also check runs of 1–12 t keys,
1–8 backticks and repeated complete escapes.

Rust additionally checks both internal split positions, independent calls,
input ownership, NUL/newline/carriage-return/tab/Unicode boundaries and 1,024
repeated mixed-input segments. **13** extra authored boundary, split-call and
repeated-input expectations independently match the pinned parser.

Reph remains a separate gap. The reference gives ``` rrt`` ``` → র্ৎ
(U+09B0 U+09CD U+09CE); the current engine gives ররৎ. This is independently
reference-checked, printed by a replacement gap probe, and retained as a partial
Rust assertion. Implementing the standalone t escape does not establish reph
compatibility.

All **506,147** fixture rows match the SHA-256-verified pinned parser.
Formatting, Clippy, **337 integration tests**, one doctest, release/documentation
builds, default/final-escape smoke checks and documentation consistency checks
passed; actual commands and outcomes are recorded in the [handoff](../progress.md).
The standalone audit checks 302 distinct inputs and now has **zero discrepancies**.
It excludes context interactions, so this is not full compatibility or a
compatibility percentage. Reph, vowel-context edges, following-r gaps after
q/z/R/Rh and reference Unicode-lowercasing differences remained at that step.
The next batch below resolves those four following-r families. Composition,
Fcitx5 and performance validation remain separate, unimplemented or unverified work.

## Following r after q, z, R and Rh

Added on 2026-10-29: independently checked following-r attachment after these
four basic spellings. This resolves their earlier partial outputs, including
`Rri`, `qr`/`Qr`, `zr`, `Rr` and `Rhr`. No upstream source, rule tables,
fixtures or dependencies were imported. Shared attachment code is extended only
after checking each raw spelling and its aliases independently.

| Basic spelling | Following r | Exact Unicode | Fixture rows |
| --- | --- | --- | --- |
| q | ক্র | U+0995 U+09CD U+09B0 | [1,066](../../tests/fixtures/following-r-q.tsv) |
| z | য্র | U+09AF U+09CD U+09B0 | [533](../../tests/fixtures/following-r-z.tsv) |
| R | ড়্র | U+09DC U+09CD U+09B0 | [533](../../tests/fixtures/following-r-r-retroflex.tsv) |
| Rh | ঢ়্র | U+09DD U+09CD U+09B0 | [1,066](../../tests/fixtures/following-r-rh-retroflex.tsv) |

The [185 controls](../../tests/fixtures/following-r-four-controls.tsv) bring the
batch to **3,383** independently authored rows. Each family checks raw context,
vowels/ya, 1–12 following r keys, the `rri`/`rry`/`rrZ` exceptions, symbols,
vowel-sign escapes, the t escape, copied Unicode, digits and interactions with
existing rules and the other selected families. `Q` aliases `q`; `RH` aliases
`Rh`. Lowercase r and uppercase R stay distinct; z and Z stay distinct.
Generated ড়/ঢ় retain U+09DC/U+09DD, with no Unicode normalization.

Single r attaches without U+200D: `qry` → ক্র্য, `zry` → য্র্য,
`Rry` → ড়্র্য and `Rhry` → ঢ়্র্য. Double r normally attaches the first r:
`qrr` → ক্রর, `zrr` → য্রর, `Rrr` → ড়্রর, `Rhrr` → ঢ়্রর.
`rri` remains a vowel: `qrri` → কৃ, `zrri` → যৃ, `Rrri` → ড়ৃ,
`Rhrri` → ঢ়ৃ. After that vowel, another rri is independent ঋ:
`qrrirri` → কৃঋ. The `rry`/`rrZ` exceptions leave rr to its own match,
which adds U+200D before ya: `qrry` → করর‍্য, `zrry` → যরর‍্য,
`RrrZ` → ড়রর‍্য and `RhrrZ` → ঢ়রর‍্য. Longer runs preserve the remaining
raw-key matching, including `qrrrri` → ক্ররৃ.

Earlier matches keep their priority. `Rg` consumes R, so `Rgr` → ড়্গ্র
continues through the verified g rule; an exposed R starts a fresh match:
`RgRr` → ড়্গড়্র. `Rh` wins before R and uses its final raw h for attachment;
`Rhhr` → ঢ়হ্র leaves the extra h separate. The nasal priority is unchanged:
`RhrNgrr` → ঢ়্রঙরর. Empty backticks still reset context: `` q`ry `` → কর‍্য,
while `` qr`a `` → ক্রআ and `` qrri`a `` → কৃআ.

Rust additionally checks UTF-8/control boundaries, input ownership, separate
calls, all three internal splits of `Rhry`, and 1,024 repeated mixed-input
segments. **45** extra authored expectations, including the long input, match
the pinned parser. All **506,147** earlier fixture rows are unchanged; six old
partial assertions have been replaced by exact supported fixtures. Reph remains
separate: reference `rrqr` → র্ক্র, `rrzr` → র্য্র and `rrRr` → র্ড়্র,
while the engine still produces ররক্র, ররয্র and ররড়্র. These remain explicit
partial assertions and reference-gap probes, alongside `rrShN` and the t escape.

The standalone inventory's prior zero discrepancies in 302 inputs do not measure
these context cases or establish full compatibility. Reph, vowel-context edges
and reference Unicode lowercasing remain. Next, independently investigate reph
across these families and existing conjunct/escape overlaps. Composition,
Fcitx5, desktop use and performance validation remain separate work.

All **509,530** fixture rows match the SHA-256-verified pinned parser. Formatting,
Clippy, **345 integration tests**, one doctest, release/documentation builds,
default/batch smoke checks and documentation consistency checks passed. Actual
commands, the migrated cchqr assertion and remaining limits are recorded in the
[handoff](../progress.md).

## Reph batch

Added on 2026-10-29: leading `rr` attaches র্ (U+09B0 U+09CD) before the
independently checked basic consonants and existing exact conjuncts. This
supersedes earlier reph gap outputs throughout these notes. No upstream code,
rule tables, fixtures or dependencies were imported; expectations reuse this
project's authored cases where applicable and are independently checked per row.

| Evidence | Rows | Scope |
| --- | --- | --- |
| [Basic spellings](../../tests/fixtures/reph-basic.tsv) | 2,322 | 43 spellings, including q/z/R/Rh and Q/RH; 54 contexts each |
| [Exact conjuncts](../../tests/fixtures/reph-conjuncts.tsv) | 8,964 | 166 existing spellings; 54 contexts each |
| [Contextual spellings](../../tests/fixtures/reph-contextual.tsv) | 179 | x/X, w/W and ng, with independent context expectations |
| [Controls](../../tests/fixtures/reph-controls.tsv) | 1,938 | Consumed/fresh r, aliases, symbols/escapes, runs and boundaries |

The shared scanner helper consumes only rr and leaves the next spelling to its
existing rule. Raw keys, including the preceding raw r, govern matching; copied
Bangla never supplies that context. `rrq` → র্ক, `rrz` → র্য, `rrR` → র্ড় and
`rrRh` → র্ঢ় have independently checked Unicode sequences. Existing conjunct
priority remains: `rrcch` → র্চ্ছ, `rrShN` → র্ষ্ণ, `rrNgkx` → র্ঙ্ক্ষ and
`rrkShNgghr` → র্ক্ষ্ণজ্ঞহ্র. An initial authored expectation for the last
example incorrectly retained a consumed N; the reference check corrected it
before adding the fixtures. Equal rendered shapes do not establish shared rules.

Vowels and following r retain their own matching: `rrqry` → র্ক্র্য without
U+200D, `rrqrry` → র্করর‍্য with U+200D, and `rrRrri` → র্ড়ৃ. Lowercase y and
uppercase Z do not trigger reph: `rry` and `rrZ` remain রর‍্য, including U+200D;
uppercase Y does attach (`rrY` → র্য়). Contextual x uses ক্স (`rrx` → র্ক্স),
while w adds its own virama (`rrw` → র্্ব). The double U+09CD in rrw is literal
reference output, not normalized. Lowercase ng keeps its special vowel and nasal-r
rules: `rrngee` → র্ঙ্গেএ and `rrngrrq` → র্ংররক.

An r already consumed by an earlier match cannot start reph: `krrq` → ক্ররক,
`Ngrrq` → ঙররক and `rrqrrq` → র্ক্ররক. The scanner checks the preceding raw key
even when it belongs to a different token. Exactly terminal `rrr` → র্র is an
exception: `rrr!` → ররর! and `rrrq` → রররক remain separate r letters. Runs of
2–12 r keys have independent controls, including vowels/ya and Unicode boundaries.
A backtick separates matches: `` r`rrq `` → রর্ক, while `` rr`q `` → ররক.
The t escape retains its context reset: ``` rrt``a ``` → র্ৎআ; earlier conjuncts
still consume t (``` rrnt`` ``` → র্ন্ত).

All **13,403** new rows match the pinned parser, and all **509,530** earlier rows
are unchanged. The earlier reph partial assertions and five gap probes are now
covered by exact fixtures. The old bDh assertion was also checked: বঢ already
matches the reference, so it is a control rather than a compatibility gap.
Rust additionally checks UTF-8/control boundaries, input ownership, every internal
split of rrRhry, independent calls, and 1,024 repeated mixed-input segments.
**49** extra authored expectations, including the long input, match the reference.

All **522,933** fixtures, formatting, Clippy, **352 integration tests**, one
doctest, release/documentation builds and smoke checks passed. A bounded follow-up
audit checked **1,350** vowel-pair inputs after six prefixes, including rrq, with
**zero discrepancies**; it does not establish complete context coverage. The
302-input standalone audit remains prior evidence, not a rerun in this step.
Actual commands and outcomes are in the [handoff](../progress.md).

Unicode case behavior remains an explicit difference: the engine preserves İ,
É and Σ, whereas the reference emits ই + U+0307, é and σ. Replacement reference
probes and a Rust assertion keep this visible. Adopting Unicode lowercasing would
change the documented preservation contract, so no policy change is assumed here.
The [mixed-context audit](#bounded-mixed-context-audit) below completes the next
bounded investigation; Unicode policy remains a separate decision.
Composition, Fcitx5, desktop use and performance remain unimplemented or unverified.

## Bounded mixed-context audit

Completed on 2026-10-29 without changing transliteration behavior. The original
MIT [audit tool](../../tools/audit-context.mjs) generates fixed input fragments,
checks the pinned parser's SHA-256, and compares its exact UTF-8 output with the
current Rust engine through the [batch transport](../../examples/audit_batch.rs).
No upstream rule tables, source or fixtures were imported. Every input is
compared independently; equal outputs do not infer shared matching behavior.

| Generated group | Distinct inputs within group | New discrepancies |
| --- | --- | --- |
| Mixed triples | 68,536 | 0 |
| Nasal/reph interactions | 4,854 | 0 |
| Consumed/exposed keys | 4,139 | 0 |
| ASCII aliases | 3,456 | 0 |
| Symbols and Unicode boundaries | 3,357 | 0 |
| Separate Unicode case probes | 3 | 0 (three known policy differences) |

There are **83,353 distinct inputs** across the overlapping groups, including
the three policy probes. Mixed triples combine 26 fragments after empty, k, ng
and rrq prefixes. Other groups combine nasal/reph fragments, earlier consuming
matches with newly exposed keys, aliases, symbols/escapes, digits, copied Bangla,
lowercase é, emoji, combining marks, joiners, NUL, newline, carriage return and
tab. Fragment boundaries deliberately permit longer overlapping matches; they
do not prescribe how the scanner must split a spelling. Exact sets and iteration
order live in the tool, rather than an exhaustive list in this document.

The [report](../evidence/mixed-context-audit.json) records tool and transport hashes,
per-group counts and output hashes, actual tool versions, and all three case
differences with code points. See the [reference-check command](../reference-checks.md#repeat-the-reference-comparison)
to reproduce it. A deliberately altered valid Bangla response was detected and
recorded with a failing exit status. Wrong parser hashes and malformed/truncated
or invalid UTF-8 batch requests were rejected. Empty output and control/Unicode
round trips passed. Audit-generated data contains no user typing.

All **522,933 existing fixture rows**, **352 integration tests**, one doctest,
formatting, Clippy, release/documentation builds and smoke checks passed again.
The generated audit is separate evidence, not additional authored fixture rows
or proof of full parity. The earlier 1,350-input vowel-pair and 302-input
standalone audits were not rerun. This step measures neither typing latency nor
desktop integration. Unicode preservation and all existing fixture files remain
unchanged; Unicode lowercasing still needed a separate policy decision at that
point. The [subsequent review](../compatibility.md#unicode-case-preservation-policy) retains preservation.

At completion of this audit, with no new gap identified in its scope, the next
milestone was **composition contract design**: settle interaction proposals and
define the reusable Rust controller's actions and outputs before implementation.
The audit itself did not settle interaction policies. The subsequent
[controller step](../v1.md#composition-controller-api) implements the core and records
the user-confirmed editing keys and punctuation policy. The subsequent
[adapter contract](../adapter-contract.md#adapter-interaction-contract) settles navigation and
focus/switching policies. The [Fcitx5 experiment](../fcitx5-validation.md#fcitx5-local-feasibility-result)
now validates synthetic routing; desktop validation stays separate.
