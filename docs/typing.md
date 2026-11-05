# Typing guide

Jong Bangla converts phonetic Latin keys into Bangla. Letter case and surrounding
keys can change the result. Conversion follows deterministic rules; it does not
correct spelling or predict words.

## Common examples

Run an example from the repository root:

```sh
cargo run --offline --example convert -- 'ami bangla'
```

Pass the input as one quoted argument. The example prints to the terminal; the
library performs no logging, file access or network access.

| Input | Output | Behavior |
| --- | --- | --- |
| `ami bangla` | `আমি বাংলা` | Basic words |
| `0123456789` | `০১২৩৪৫৬৭৮৯` | Bangla digits |
| `ki kI nIti` | `কি কী নীতি` | Short and long i forms |
| `tumi bhUmi kua` | `তুমি ভূমি কুয়া` | Contextual vowels |
| `ami ke kee` | `আমি কে কী` | Single and double e |
| `tumi kemon tOmake` | `তুমি কেমন তোমাকে` | Lowercase o and uppercase O |
| `OI kOI OU kOU nOUka` | `ঐ কৈ ঔ কৌ নৌকা` | Two-key vowels |
| `rri krri krriti rriN` | `ঋ কৃ কৃতি ঋণ` | Vocalic r |
| `t T th Th n N` | `ত ট থ ঠ ন ণ` | Case-sensitive consonants |
| `s sh S Sh` | `স শ শ ষ` | Distinct s spellings |
| `pani phOn fOn` | `পানি ফোন ফোন` | Alternate spellings for ফ |
| `baRi gaRi gaRh drriRh` | `বাড়ি গাড়ি গাঢ় দৃঢ়` | R and Rh forms |
| `kx kkh kSh` | `ক্ষ ক্ষ ক্ষ` | Conjunct spellings |

Common punctuation is also phonetic:

| Input | Output | Behavior |
| --- | --- | --- |
| `.` | `।` | Bangla sentence terminator |
| `` .` `` | `.` | Literal period |
| `...` | `...` | Three literal periods |
| `:` | `ঃ` | Bangla visarga |
| `` :` `` | `:` | Literal colon |
| `$` | `৳` | Taka sign |

Type the backtick after the symbol for the literal period/colon forms. A
standalone backtick separates phonetic matches and has no visible output; it
does not make the next Latin letter literal. Punctuation remains in the active
word until a commit boundary, so Backspace can edit these sequences.

These are selected examples. Exact Unicode sequences, overlapping matches and
per-rule limitations are recorded in the [behavior specification](v1.md#transliteration-api)
and [fixtures](../tests/fixtures). Unsupported characters, including Bangla and
emoji, pass through unchanged under the
[Unicode preservation policy](compatibility.md#unicode-case-preservation-policy).

## Editing in the desktop addon

The active word appears as editable Bangla, called *preedit*, before it is sent to
the application. There is no Bangla/Latin choice list in v1.

| Key or action | Result |
| --- | --- |
| Backspace | Remove the last raw phonetic keystroke and recompute Bangla |
| Ctrl+Backspace | Clear the active word without committing; otherwise let the application handle it |
| Space or Enter | Commit active Bangla, then forward the same key |
| Escape | Commit the active word and consume the press; otherwise forward |
| Navigation or application shortcut | Commit the active word before forwarding the key |
| Punctuation or phonetic escape | Keep it editable with the word until a boundary |

Punctuation has phonetic meanings and literal escape forms; consult the
[symbol table](compatibility/case-symbols-reph.md#punctuation-and-symbol-batch) and
[vowel-sign escapes](compatibility/case-symbols-reph.md#vowel-sign-escape-batch) for exact spellings.
Focus loss, switching and reset follow the
[adapter contract](adapter-contract.md#adapter-interaction-contract). Actual toolkit and desktop
coverage remains limited; see the [desktop checklist](fcitx5-validation.md#remaining-desktop-smoke-checklist).

## Switch to English

Use your configured Fcitx input-method switching action to select the keyboard
or English input method, and switch back to resume Bangla. Jong does not add a
global shortcut; the action depends on your Fcitx configuration. Switching while
a word is pending finalizes it when the frontend permits delivery, and returning
starts a fresh word. For literal Latin words or ASCII numbers, use that English
input method. The v1 preedit has no raw-Latin candidate or digit-mode toggle.

Report unexpected behavior in
[GitHub Issues](https://github.com/shaadahmmed/jong-bangla-keyboard/issues).
