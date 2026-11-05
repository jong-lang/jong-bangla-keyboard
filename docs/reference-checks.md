# Reference compatibility checks

Run commands from the repository root. These checks are separate from ordinary
Rust tests and require an external pinned parser.

## Repeat the reference comparison

This optional development check uses Node.js (verified with the installed
v24.21.0 LTS-line runtime). Node is not needed to build or use the Rust library.
The independently authored [fixtures](../tests/fixtures) record raw input,
expected UTF-8 output and exact Unicode code points. Detailed per-rule coverage
and provenance are in the [behavior specification](compatibility.md#phonetic-behavior-reference).
The comparison calls
`OmicronLab.Avro.Phonetic.parse(input)` directly, without browser UI, dictionaries,
or autocorrection.

Download the upstream parser and its MPL-1.1 license to a temporary directory,
outside this project. These downloads require network access; subsequent checks
run locally. The checker verifies the parser's SHA-256 before evaluating it.

```sh
reference_dir="$(mktemp -d)"
curl --fail --location 'https://raw.githubusercontent.com/torifat/jsAvroPhonetic/d3790172ebff92d43f0294bc51fed1fca7c80039/src/avro-lib.js' --output "$reference_dir/avro-lib.js"
curl --fail --location 'https://raw.githubusercontent.com/torifat/jsAvroPhonetic/d3790172ebff92d43f0294bc51fed1fca7c80039/MPL-1.1.txt' --output "$reference_dir/MPL-1.1.txt"
node tools/check-reference.mjs "$reference_dir/avro-lib.js"
```

It checks the same 522,933 parity cases used by Rust tests, then separately checks
60 [Unicode policy cases](../tests/fixtures/unicode-case-policy.tsv). These record
independent engine/reference outputs and exact code points: 51 deliberate
differences and nine agreements. Rust tests check the engine columns; this script
checks the reference columns. Policy cases do not increase the parity count.
For example, the engine preserves `İ`, `É`, and `Σ`; the reference returns `ই̇`,
`é`, and `σ`. Expansion can also change phonetic matches: `rrİ` stays `ররİ`
here but becomes `ঋ̇` in the reference. See the
[decision and limits](compatibility.md#unicode-case-preservation-policy).
The original comparison and test tooling are MIT;
the upstream parser remains external and is not shipped with the library.

To repeat the broader generated context audit, using the same external parser:

```sh
node tools/audit-context.mjs "$reference_dir/avro-lib.js" /tmp/jong-context-audit.json
```

This builds and runs the `audit_batch` Rust example offline. Its binary UTF-8
transport preserves empty strings, newlines, NULs and other copied characters.
The command writes counts, hashes and every discrepancy with exact code points;
it exits unsuccessfully for any unexpected difference. The three known case
probes retain their original explicit outputs under the settled preservation
policy; the 60 focused policy cases above provide broader evidence. The
[recorded report](evidence/mixed-context-audit.json) contains the validated
results and tool versions. Group hashes cover ordered JSON arrays of
`[input, engine output, reference output]`; group counts overlap. Compare hashes
and counts when reproducing results with different tool versions.
