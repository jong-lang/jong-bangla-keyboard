# Phonetic compatibility

This guide owns reference provenance, the exact Unicode preservation policy and
compatibility evidence. Current product/API requirements are in [v1.md](v1.md).
Use [reference-checks.md](reference-checks.md) to reproduce comparisons. Counts
below are recorded fixture coverage; tests and fixtures remain the exact source
of implemented examples.

## Phonetic behavior reference

Selected on 2026-10-28: **jsAvroPhonetic v1.1.4**, from
[torifat/jsAvroPhonetic](https://github.com/torifat/jsAvroPhonetic), pinned to
commit [`d3790172ebff92d43f0294bc51fed1fca7c80039`](https://github.com/torifat/jsAvroPhonetic/tree/d3790172ebff92d43f0294bc51fed1fca7c80039).

[OmicronLab's developer resources](https://www.omicronlab.com/developers.html)
identify this project as its official JavaScript implementation. It offers a
conversion reference that can be exercised independently of a desktop input
method. `git ls-remote` confirmed v1.1.4 as the newest published tag on the
selection date; the pinned `bower.json` also reports 1.1.4. The repository's
current default branch is a different revision. Pinning the tagged revision
keeps future comparisons repeatable rather than following a moving branch.

The scope is deterministic phonetic conversion to Unicode Bangla. Dictionary
suggestions, autocorrection, candidate ranking, and browser UI behavior are
outside this comparison. Composition controls remain this project's separate
decisions. This reference selection does not establish parity with all Avro
implementations or current Avro Keyboard for Windows.

The [README at the pinned revision](https://github.com/torifat/jsAvroPhonetic/blob/d3790172ebff92d43f0294bc51fed1fca7c80039/README.md)
declares MPL-1.1. It is a behavior reference, not a dependency or a source of
copied code: no upstream engine, rule tables, or fixtures have been imported into
the project.
Our implementation and initial examples are independently authored under
the project's MIT license. Any later import requires its own provenance and
license review.

All 522,933 authored cases (27 initial, 66 `a`/`i`, 80 `u`/`U`, 52 `I`, 92 `e`/`ee`,
156 `o`/`O`/`oo`, 150 `OI`/`OU`, 84 `rri`, 115 `r`/`rr`, 115 `p`/`ph`/`f`,
148 `c`/`ch`/`j`/`jh`, 164 `d`/`dh`/`D`/`Dh`, 110 `l`/`h`,
174 `s`/`sh`/`S`/`Sh`, 94 `R`/`Rh`, 51 `z`, 88 `Ng`/`NG`, 110 `ng`,
274 following-`rri` cases, 142 uppercase `Y`, 338 lowercase `y`,
398 uppercase `Z`, 418 following-`r` cases after `y`/`Z`,
286 following-`r` cases after uppercase `Y`, 132 lowercase `q`, 136 lowercase `v`,
311 lowercase `w`, 385 following-`r` cases after lowercase `w`, 392 lowercase `x`/`kx`,
755 following-`r` cases after `x`/`kx`, 322 exact `Ngx`, 433 exact `Ngk`,
454 exact `Ngkh`, 432 exact `Ngkx`, 458 exact `Ngkkh`, 468 exact `NgkSh`,
330 exact `kkh`, 332 exact `kSh`, 410 exact `kkhN`, 411 exact `kShN`,
410 exact `kxN`, 399 exact `kkhm`, 399 exact `kShm`, 398 exact `kxm`,
501 exact `kk`, 465 exact `ShN`, 468 exact `Shm`,
475 following-`r` cases after basic `k`, 476 after basic `kh`, 476 after basic `Sh`,
475 after basic `g`, 473 after basic `gh`, 531 exact `Ngg`, 531 exact `Nggh`,
716 exact `gg`, 692 exact `gN`, 677 exact `NN`, 691 exact `hN`, 664 exact `gn`,
659 exact `ghn`, 658 exact `hn`, 648 exact `dg`, 647 exact `dgh`, 648 exact `Rg`,
396/391/396 following-`r` cases after basic `h`/`n`/`N`,
843 exact `ngh`, 856 exact `nn`, 855 exact `Nn`, 861 exact `mn`,
864 exact `hm`, 855 exact `hl`, 865 exact `nm`, 856 exact `Nm`,
860 exact `mm`, 859 exact `ml`, 869 exact `Ngm`, 858 exact `gm`,
527/522 following-`r` cases after basic `m`/`l`,
961 exact `ddh`, 956 exact `dd`, 955 each `dhn`/`dhm`/`dm`,
958 each `dbh`/`dv`, 957 exact `DD`, 576 each basic `d`/`dh`/`D` attachment,
575 basic `Dh`, 577 basic `b`, and 576 each basic `bh`/`v` attachment;
1,155 `ndh`, 1,135 `nd`, 1,164 `nD`, 1,129 `NDh`, 1,122 `ND`,
1,155 `nth`, 1,139 `nt`, 1,154 `nTh`, 1,140 `nT`, 1,136 `NTh`, 1,122 `NT`,
751 each basic `t`/`th`/`T`/`Th` attachment;
1,366 `tth`, 1,357 `tt`, 1,359 `tn`, 1,358 `tm`, 1,344 `TT`, 1,346 `Tm`;
1,443 `kt`, 1,442 `kT`, 1,440 `kl`, and 2,083 k-family controls;
1,717 `nkh`, 1,737 `nk`, 1,668 `lkh`, 1,687 `lk`, 1,731 each `skl`/`skh`,
1,750 `sk`, 1,779 `Shk`, 1,745 `ksh`, 1,730 `ks`,
1,177/1,191/1,191 basic `s`/`sh`/`S` attachment, and 960 case controls;
1,903 `gl`, 1,904 each `ll`/`bhl`, 1,889 each `bl`/`fl`, 1,882 `pl`,
1,897 `sl`, 1,911 `shl`, 1,890 `phl`, 1,896 `vl`, 1,910 `Sl`,
3,863 each basic `p`/`ph`/`f` attachment, and 2,240 l-ending controls;
2,000 `mbh`, 1,985 each `mb`/`mp`/`shm`, 1,984 each `mv`/`mf`/`lm`/`Sm`,
1,999 each `mph`/`mpl`, 1,970 `sm`, and 1,600 m-prefix/m-ending controls;
2,109 each `lgh`/`lbh`/`lph`/`ldh`, 2,094 each `lg`/`lb`/`lv`/`lD`,
2,095 each `lp`/`lT`, and 1,600 l-prefix controls;
2,175 each `sph`/`spl`, 2,163 `sp`, 2,160 `sf`, 2,204 `Shph`,
2,192 `Shp`, 2,189 `Shf`, and 2,445 s/Sh labial controls;
2,236 each `bb`/`pp`, 2,240 each `pn`/`Sn`, 2,227 `sn`,
2,241 `shn`, and 2,608 repetition/n-ending controls;
2,300 each `ns`/`nsh`/`ps`/`psh`, and 1,896 ns/ps controls;
2,377 each `sth`/`ShT`, 2,362 each `st`/`sT`, 2,391 `ShTh`,
2,376 `sht`, 2,361 `St`, and 3,484 s/Sh stop controls;
108,815 remaining-conjunct batch rows, with independent per-spelling manifests
in the [batch record](compatibility/conjunct-batches.md#remaining-exact-conjunct-batch);
109,246 selective ASCII case-alias rows in the [case batch](compatibility/case-symbols-reph.md#selective-ascii-case-alias-batch);
6,169 explicit G/J rows in the [G/J batch](compatibility/case-symbols-reph.md#explicit-gj-spelling-batch);
10,824 punctuation/symbol rows in the [symbol batch](compatibility/case-symbols-reph.md#punctuation-and-symbol-batch);
22,167 vowel-sign escape rows in the [escape batch](compatibility/case-symbols-reph.md#vowel-sign-escape-batch);
4,067 final t-escape rows in the [final-escape record](compatibility/case-symbols-reph.md#final-t-escape);
3,383 q/z/R/Rh following-r rows in the [batch record](compatibility/case-symbols-reph.md#following-r-after-q-z-r-and-rh);
13,403 reph rows in the [reph record](compatibility/case-symbols-reph.md#reph-batch))
have been compared against this exact revision's
`OmicronLab.Avro.Phonetic.parse(input)` entry point.
The invocation is documented in the
[reference-check guide](reference-checks.md#repeat-the-reference-comparison), inputs
and code points in the [initial](../tests/fixtures/reference.tsv),
[`a`/`i`](../tests/fixtures/vowels.tsv), [`u`/`U`](../tests/fixtures/vowels-u.tsv),
[`I`](../tests/fixtures/vowels-i-long.tsv), [`e`/`ee`](../tests/fixtures/vowels-e.tsv),
[`o`/`O`/`oo`](../tests/fixtures/vowels-o.tsv),
[`OI`/`OU`](../tests/fixtures/vowels-oi-ou.tsv), [`rri`](../tests/fixtures/vowels-rri.tsv),
[`r`/`rr`](../tests/fixtures/consonants-r.tsv),
[`p`/`ph`/`f`](../tests/fixtures/consonants-p-ph-f.tsv),
[`c`/`ch`/`j`/`jh`](../tests/fixtures/consonants-c-ch-j-jh.tsv),
[`d`/`dh`/`D`/`Dh`](../tests/fixtures/consonants-d-dh.tsv),
[`l`/`h`](../tests/fixtures/consonants-l-h.tsv),
[`s`/`sh`/`S`/`Sh`](../tests/fixtures/consonants-s-sh.tsv),
[`R`/`Rh`](../tests/fixtures/consonants-r-retroflex.tsv),
[`z`](../tests/fixtures/consonant-z.tsv),
[`Ng`/`NG`](../tests/fixtures/consonants-ng-nj.tsv),
[`ng`](../tests/fixtures/sign-ng.tsv),
[following-`rri`](../tests/fixtures/nasal-rri.tsv),
[`Y`](../tests/fixtures/consonant-y-uppercase.tsv),
[`y`](../tests/fixtures/consonant-y-lowercase.tsv),
[`Z`](../tests/fixtures/consonant-z-uppercase.tsv),
[following-`r`](../tests/fixtures/ya-following-r.tsv),
[`Y` following-`r`](../tests/fixtures/uppercase-y-following-r.tsv),
[`q`](../tests/fixtures/consonant-q.tsv),
[`v`](../tests/fixtures/consonant-v.tsv),
[`w`](../tests/fixtures/consonant-w.tsv),
[`w` following-`r`](../tests/fixtures/w-following-r.tsv),
[`x` fixtures](../tests/fixtures/consonant-x.tsv),
[`x`/`kx` following-`r`](../tests/fixtures/x-following-r.tsv),
[`Ngx` fixtures](../tests/fixtures/conjunct-ngx.tsv),
[`Ngk` fixtures](../tests/fixtures/conjunct-ngk.tsv),
[`Ngkh` fixtures](../tests/fixtures/conjunct-ngkh.tsv),
[`Ngkx` fixtures](../tests/fixtures/conjunct-ngkx.tsv),
[`Ngkkh` fixtures](../tests/fixtures/conjunct-ngkkh.tsv),
[`NgkSh` fixtures](../tests/fixtures/conjunct-ngksh.tsv),
[`kkh` fixtures](../tests/fixtures/conjunct-kkh.tsv),
[`kSh` fixtures](../tests/fixtures/conjunct-ksh.tsv),
[`kkhN` fixtures](../tests/fixtures/conjunct-kkhn.tsv),
[`kShN` fixtures](../tests/fixtures/conjunct-kshn.tsv),
[`kxN` fixtures](../tests/fixtures/conjunct-kxn.tsv),
[`kkhm` fixtures](../tests/fixtures/conjunct-kkhm.tsv),
[`kShm` fixtures](../tests/fixtures/conjunct-kshm.tsv),
[`kxm` fixtures](../tests/fixtures/conjunct-kxm.tsv),
[`kk` fixtures](../tests/fixtures/conjunct-kk.tsv),
[`ShN` fixtures](../tests/fixtures/conjunct-shn.tsv),
[`Shm` fixtures](../tests/fixtures/conjunct-shm.tsv),
[`k` following-`r`](../tests/fixtures/k-following-r.tsv),
[`kh` following-`r`](../tests/fixtures/kh-following-r.tsv),
[`Sh` following-`r`](../tests/fixtures/sh-following-r.tsv),
[`g` following-`r`](../tests/fixtures/g-following-r.tsv),
[`gh` following-`r`](../tests/fixtures/gh-following-r.tsv),
[`Ngg`](../tests/fixtures/conjunct-ngg.tsv),
[`Nggh`](../tests/fixtures/conjunct-nggh.tsv),
[`gg` fixtures](../tests/fixtures/conjunct-gg.tsv),
[`gN` fixtures](../tests/fixtures/conjunct-g-n.tsv),
[`NN` fixtures](../tests/fixtures/conjunct-nn.tsv),
[`hN` fixtures](../tests/fixtures/conjunct-h-n.tsv),
[`gn` fixtures](../tests/fixtures/conjunct-gn.tsv),
[`ghn` fixtures](../tests/fixtures/conjunct-ghn.tsv),
[`hn` fixtures](../tests/fixtures/conjunct-hn.tsv),
[`dg` fixtures](../tests/fixtures/conjunct-dg.tsv),
[`dgh` fixtures](../tests/fixtures/conjunct-dgh.tsv),
[`Rg` fixtures](../tests/fixtures/conjunct-r-g.tsv),
[`h` fixtures](../tests/fixtures/h-following-r.tsv),
[`n` fixtures](../tests/fixtures/n-following-r.tsv),
[`N` fixtures](../tests/fixtures/n-retroflex-following-r.tsv),
[`ngh` fixtures](../tests/fixtures/conjunct-ngh.tsv),
[`nn` fixtures](../tests/fixtures/conjunct-n-lower-pair.tsv),
[`Nn` fixtures](../tests/fixtures/conjunct-n-mixed-pair.tsv),
[`mn` fixtures](../tests/fixtures/conjunct-mn.tsv),
[`hm` fixtures](../tests/fixtures/conjunct-hm.tsv),
[`hl` fixtures](../tests/fixtures/conjunct-hl.tsv),
[`nm` fixtures](../tests/fixtures/conjunct-nm.tsv),
[`Nm` fixtures](../tests/fixtures/conjunct-n-retroflex-m.tsv),
[`mm` fixtures](../tests/fixtures/conjunct-mm.tsv),
[`ml` fixtures](../tests/fixtures/conjunct-ml.tsv),
[`Ngm` fixtures](../tests/fixtures/conjunct-ng-m.tsv),
[`gm` fixtures](../tests/fixtures/conjunct-gm.tsv),
[`m` following-`r` fixtures](../tests/fixtures/m-following-r.tsv),
[`l` following-`r` fixtures](../tests/fixtures/l-following-r.tsv),
[`ddh` fixtures](../tests/fixtures/conjunct-ddh.tsv),
[`dd` fixtures](../tests/fixtures/conjunct-dd.tsv),
[`dhn` fixtures](../tests/fixtures/conjunct-dhn.tsv),
[`dhm` fixtures](../tests/fixtures/conjunct-dhm.tsv),
[`dm` fixtures](../tests/fixtures/conjunct-dm.tsv),
[`dbh` fixtures](../tests/fixtures/conjunct-dbh.tsv),
[`dv` fixtures](../tests/fixtures/conjunct-dv.tsv),
[`DD` fixtures](../tests/fixtures/conjunct-d-retroflex-pair.tsv),
[`d` following-`r` fixtures](../tests/fixtures/d-following-r.tsv),
[`dh` following-`r` fixtures](../tests/fixtures/dh-following-r.tsv),
[`D` following-`r` fixtures](../tests/fixtures/d-retroflex-following-r.tsv),
[`Dh` following-`r` fixtures](../tests/fixtures/dh-retroflex-following-r.tsv),
[`b` following-`r` fixtures](../tests/fixtures/b-following-r.tsv),
[`bh` following-`r` fixtures](../tests/fixtures/bh-following-r.tsv),
[`v` following-`r` fixtures](../tests/fixtures/v-following-r.tsv),
[`ndh` fixtures](../tests/fixtures/conjunct-ndh.tsv),
[`nd` fixtures](../tests/fixtures/conjunct-nd.tsv),
[`nD` fixtures](../tests/fixtures/conjunct-n-d-retroflex.tsv),
[`NDh` fixtures](../tests/fixtures/conjunct-n-retroflex-dh-retroflex.tsv),
[`ND` fixtures](../tests/fixtures/conjunct-n-retroflex-d-retroflex.tsv),
[`nth` fixtures](../tests/fixtures/conjunct-nth.tsv),
[`nt` fixtures](../tests/fixtures/conjunct-nt.tsv),
[`nTh` fixtures](../tests/fixtures/conjunct-n-th-retroflex.tsv),
[`nT` fixtures](../tests/fixtures/conjunct-n-t-retroflex.tsv),
[`NTh` fixtures](../tests/fixtures/conjunct-n-retroflex-th-retroflex.tsv),
[`NT` fixtures](../tests/fixtures/conjunct-n-retroflex-t-retroflex.tsv),
[`t` following-`r` fixtures](../tests/fixtures/t-following-r.tsv),
[`th` following-`r` fixtures](../tests/fixtures/th-following-r.tsv),
[`T` following-`r` fixtures](../tests/fixtures/t-retroflex-following-r.tsv),
[`Th` following-`r` fixtures](../tests/fixtures/th-retroflex-following-r.tsv),
[`tth` fixtures](../tests/fixtures/conjunct-tth.tsv),
[`tt` fixtures](../tests/fixtures/conjunct-tt.tsv),
[`tn` fixtures](../tests/fixtures/conjunct-tn.tsv),
[`tm` fixtures](../tests/fixtures/conjunct-tm.tsv),
[`TT` fixtures](../tests/fixtures/conjunct-t-retroflex-pair.tsv),
[`Tm` fixtures](../tests/fixtures/conjunct-t-retroflex-m.tsv),
[`kt` fixtures](../tests/fixtures/conjunct-kt.tsv),
[`kT` fixtures](../tests/fixtures/conjunct-k-t-retroflex.tsv),
[`kl` fixtures](../tests/fixtures/conjunct-kl.tsv),
[k-family controls](../tests/fixtures/k-family-controls.tsv),
[`nkh` fixtures](../tests/fixtures/conjunct-nkh.tsv),
[`nk` fixtures](../tests/fixtures/conjunct-nk.tsv),
[`lkh` fixtures](../tests/fixtures/conjunct-lkh.tsv),
[`lk` fixtures](../tests/fixtures/conjunct-lk.tsv),
[`skl` fixtures](../tests/fixtures/conjunct-skl.tsv),
[`skh` fixtures](../tests/fixtures/conjunct-skh.tsv),
[`sk` fixtures](../tests/fixtures/conjunct-sk.tsv),
[`Shk` fixtures](../tests/fixtures/conjunct-sh-k.tsv),
[`ksh` fixtures](../tests/fixtures/conjunct-ksh-priority.tsv),
[`ks` fixtures](../tests/fixtures/conjunct-ks.tsv),
[`s` following-`r` fixtures](../tests/fixtures/s-following-r.tsv),
[`sh` following-`r` fixtures](../tests/fixtures/sh-lowercase-following-r.tsv),
[`S` following-`r` fixtures](../tests/fixtures/s-uppercase-following-r.tsv),
[consuming k-family controls](../tests/fixtures/consuming-k-controls.tsv),
[`gl` fixtures](../tests/fixtures/conjunct-gl.tsv),
[`ll` fixtures](../tests/fixtures/conjunct-ll.tsv),
[`bl` fixtures](../tests/fixtures/conjunct-bl.tsv),
[`pl` fixtures](../tests/fixtures/conjunct-pl.tsv),
[`sl` fixtures](../tests/fixtures/conjunct-sl.tsv),
[`shl` fixtures](../tests/fixtures/conjunct-sh-lowercase-l.tsv),
[`bhl` fixtures](../tests/fixtures/conjunct-bhl.tsv),
[`phl` fixtures](../tests/fixtures/conjunct-phl.tsv),
[`vl` fixtures](../tests/fixtures/conjunct-vl.tsv),
[`fl` fixtures](../tests/fixtures/conjunct-fl.tsv),
[`Sl` fixtures](../tests/fixtures/conjunct-s-uppercase-l.tsv),
[`p` following-`r` fixtures](../tests/fixtures/p-following-r.tsv),
[`ph` following-`r` fixtures](../tests/fixtures/ph-following-r.tsv),
[`f` following-`r` fixtures](../tests/fixtures/f-following-r.tsv),
[l-ending controls](../tests/fixtures/l-ending-controls.tsv),
[`mbh` fixtures](../tests/fixtures/conjunct-mbh.tsv),
[`mb` fixtures](../tests/fixtures/conjunct-mb.tsv),
[`mv` fixtures](../tests/fixtures/conjunct-mv.tsv),
[`mph` fixtures](../tests/fixtures/conjunct-mph.tsv),
[`mpl` fixtures](../tests/fixtures/conjunct-mpl.tsv),
[`mp` fixtures](../tests/fixtures/conjunct-mp.tsv),
[`mf` fixtures](../tests/fixtures/conjunct-mf.tsv),
[`lm` fixtures](../tests/fixtures/conjunct-lm.tsv),
[`sm` fixtures](../tests/fixtures/conjunct-sm.tsv),
[`shm` fixtures](../tests/fixtures/conjunct-sh-lowercase-m.tsv),
[`Sm` fixtures](../tests/fixtures/conjunct-s-uppercase-m.tsv),
[m-prefix and m-ending controls](../tests/fixtures/m-labial-controls.tsv),
[`lgh` fixtures](../tests/fixtures/conjunct-lgh.tsv),
[`lg` fixtures](../tests/fixtures/conjunct-lg.tsv),
[`lbh` fixtures](../tests/fixtures/conjunct-lbh.tsv),
[`lb` fixtures](../tests/fixtures/conjunct-lb.tsv),
[`lv` fixtures](../tests/fixtures/conjunct-lv.tsv),
[`lph` fixtures](../tests/fixtures/conjunct-lph.tsv),
[`lp` fixtures](../tests/fixtures/conjunct-lp.tsv),
[`lT` fixtures](../tests/fixtures/conjunct-l-t-retroflex.tsv),
[`lD` fixtures](../tests/fixtures/conjunct-l-d-retroflex.tsv),
[`ldh` fixtures](../tests/fixtures/conjunct-ldh.tsv),
[l-prefix controls](../tests/fixtures/l-prefix-controls.tsv),
[`sph` fixtures](../tests/fixtures/conjunct-sph.tsv),
[`spl` fixtures](../tests/fixtures/conjunct-spl.tsv),
[`sp` fixtures](../tests/fixtures/conjunct-sp.tsv),
[`sf` fixtures](../tests/fixtures/conjunct-sf.tsv),
[`Shph` fixtures](../tests/fixtures/conjunct-sh-ph.tsv),
[`Shp` fixtures](../tests/fixtures/conjunct-sh-p.tsv),
[`Shf` fixtures](../tests/fixtures/conjunct-sh-f.tsv),
[s/Sh labial controls](../tests/fixtures/s-labial-controls.tsv),
[`bb` fixtures](../tests/fixtures/conjunct-bb.tsv),
[`pp` fixtures](../tests/fixtures/conjunct-pp.tsv),
[`pn` fixtures](../tests/fixtures/conjunct-pn.tsv),
[`sn` fixtures](../tests/fixtures/conjunct-sn.tsv),
[`shn` fixtures](../tests/fixtures/conjunct-sh-lowercase-n.tsv),
[`Sn` fixtures](../tests/fixtures/conjunct-s-uppercase-n.tsv),
[repetition/n-ending controls](../tests/fixtures/repeat-n-controls.tsv),
[`ns` fixtures](../tests/fixtures/conjunct-ns.tsv),
[`nsh` fixtures](../tests/fixtures/conjunct-nsh.tsv),
[`ps` fixtures](../tests/fixtures/conjunct-ps.tsv),
[`psh` fixtures](../tests/fixtures/conjunct-psh.tsv),
[ns/ps controls](../tests/fixtures/ns-ps-controls.tsv),
[`st` fixtures](../tests/fixtures/conjunct-st.tsv),
[`sth` fixtures](../tests/fixtures/conjunct-sth.tsv),
[`sT` fixtures](../tests/fixtures/conjunct-s-t-retroflex.tsv),
[`ShT` fixtures](../tests/fixtures/conjunct-sh-t-retroflex.tsv),
[`ShTh` fixtures](../tests/fixtures/conjunct-sh-th-retroflex.tsv),
[`sht` fixtures](../tests/fixtures/conjunct-sh-lowercase-t.tsv),
[`St` fixtures](../tests/fixtures/conjunct-s-uppercase-t.tsv),
[s/Sh stop controls](../tests/fixtures/s-stop-controls.tsv),
the [remaining conjunct batch](compatibility/conjunct-batches.md#remaining-exact-conjunct-batch),
the [symbol batch](compatibility/case-symbols-reph.md#punctuation-and-symbol-batch),
the [vowel-escape batch](compatibility/case-symbols-reph.md#vowel-sign-escape-batch),
the [final-escape record](compatibility/case-symbols-reph.md#final-t-escape), and actual checks
in the [progress log](progress.md). Passing this set establishes only these cases.

## Unicode case-preservation policy

**Decision, 2026-10-30:** retain the existing v1 contract: unsupported Unicode
scalars keep their exact case and code points. Do not apply Unicode lowercasing,
case folding, or normalization. The supported ASCII aliases and case-sensitive
phonetic rules remain unchanged. An unsupported character separates phonetic
matches and resets their context; supported parts of the surrounding input still
convert. For example, `kÉi` → `কÉই`, not a vowel sign attached across É.
This makes the preservation contract explicit without changing engine behavior.

The tradeoff is intentional reference incompatibility beyond the three original
probes İ/É/Σ. Preserving copied letters avoids silently changing unrelated scripts
or turning Unicode lookalikes into phonetic keys. Adopting the pinned parser's
behavior would improve compatibility for these inputs but change both copied
text and matches spanning newly created ASCII. A separate compatibility mode is
not required for v1 and is not introduced by this review. This decision narrows
the compatibility claim; it does not establish full Avro parity.

The pinned parser's
[`fixString` implementation](https://github.com/torifat/jsAvroPhonetic/blob/d3790172ebff92d43f0294bc51fed1fca7c80039/src/avro-lib.js#L160-L170)
lowercases each non-case-sensitive UTF-16 code unit before phonetic matching.
It is not equivalent to lowercasing the entire string or iterating Unicode
scalars. Exact observations from the independently authored
[policy fixture](../tests/fixtures/unicode-case-policy.tsv):

| Input | Engine output | Engine code points | Pinned reference output | Reference code points |
| --- | --- | --- | --- | --- |
| İ (U+0130) | İ | U+0130 | ই̇ | U+0987 U+0307 |
| É (U+00C9) | É | U+00C9 | é | U+00E9 |
| Σ (U+03A3) | Σ | U+03A3 | σ | U+03C3 |
| kİ | কİ | U+0995 U+0130 | কি̇ | U+0995 U+09BF U+0307 |
| rrİ | ররİ | U+09B0 U+09B0 U+0130 | ঋ̇ | U+098B U+0307 |
| İa | İআ | U+0130 U+0986 | ই̇আ | U+0987 U+0307 U+0986 |
| Kh (U+212A + h) | Kহ | U+212A U+09B9 | খ | U+0996 |
| Ａ (U+FF21) | Ａ | U+FF21 | ａ | U+FF41 |
| ΟΣ (U+039F U+03A3) | ΟΣ | U+039F U+03A3 | οσ | U+03BF U+03C3 |
| 𐐀 (U+10400) | 𐐀 | U+10400 | 𐐀 | U+10400 |

İ expands to ASCII i plus U+0307 in the reference. The new i can supply a vowel
sign (`kİ`), complete rri (`rrİ`), or precede a combining-mark boundary (`İa`).
The mark remains, including duplicate dots in İ + U+0307. Kelvin sign K becomes
ASCII k and can join a following h, r or x. É changes to é without creating a
phonetic key; decomposed ASCII E + U+0301 independently converts to এ + U+0301
in both engines. Preserving unmatched characters does not preserve every
visually equivalent spelling as a whole.

For Greek ΟΣ, the reference produces οσ, whereas whole-string default lowercasing
produces ος. For supplementary Deseret 𐐀, the reference preserves the surrogate
pair, whereas Unicode scalar lowercasing would produce 𐐨 (U+10428).
[Unicode 17.0, section 3.13](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-3/)
describes context-dependent default casing, including final sigma. A generic
Unicode lowercase call would therefore change preservation and still fail to
reproduce the pinned parser. The parser file is pinned, but its JavaScript
runtime supplies casing tables: these observations used Node v24.21.0, Unicode
17.0 and ICU 78.3. They are not a guarantee about every runtime or Avro variant.

**Evidence:** 60 separate policy rows record independently authored exact engine
and reference outputs: 51 deliberate differences and nine agreements. Coverage
includes each original probe with preceding k/rr and following vowels, y/r/x/w;
combining marks, an escape, emoji/ZWJ, copied Bangla/digits, ASCII aliases,
Kelvin/fullwidth letters, Greek context, supplementary Deseret, and ẞ/ß.
The [Rust tests](../tests/unicode_case.rs) check engine output/code points plus
incremental preedit, scalar Backspace and commit. The
[reference checker](../tools/check-reference.mjs) verifies every reference column
against the SHA-256-pinned parser and validates both code-point columns.
Policy rows are separate from the **522,933 parity fixture rows**; agreement
controls do not inflate that count. Existing generated-audit evidence retains
its original three-probe scope. This bounded review does not enumerate every
Unicode casing difference, rerun desktop tests, or measure resources.

## Historical conversion increments

Dated implementation records are grouped below. Their counts, gap tables and
words such as "current" or "next" refer to that historical increment; they are
not current coverage limits or open bug reports. Preserve these records as
reference material, and use Git for new development chronology rather than
continuing to grow this archive.

- [Phonetic foundations and basic consonants](compatibility/foundations.md).
- [Exact nasal, k and Sh conjuncts](compatibility/exact-conjuncts.md).
- [Related conjunct batches](compatibility/conjunct-batches.md).
- [Case aliases, symbols, escapes and reph](compatibility/case-symbols-reph.md).
