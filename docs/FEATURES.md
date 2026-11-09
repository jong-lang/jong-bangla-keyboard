# Features and platform status

Jong Bangla converts phonetic input into Bangla with Avro-compatible behavior
as its target. Conversion works in the maintainer's typing tests, including
Bangla letters. The pinned jsAvroPhonetic v1.1.4 audit covers every reference
spelling and reachable contextual rule in a finite fixture corpus. An expanded
bounded context audit found no unexpected differences; unsupported Unicode
case preservation remains a deliberate difference. See the
[coverage and limits](TESTING.md#reference-coverage-audit). This evidence does
not establish parity for every possible input.

## Typing behavior

The active word appears as editable Bangla preedit: text displayed before it
is committed to the application. Conversion is deterministic, with contextual
vowels, conjuncts, case-sensitive sequences, punctuation, and phonetic escapes.

| Input | Behavior |
| --- | --- |
| Phonetic text | Update the active raw input and recompute Bangla preedit |
| Digits | Convert to Bangla digits by default |
| Backspace | Remove one raw input character and recompute |
| Ctrl+Backspace | Clear the active word without committing |
| Space or Enter | Commit active Bangla, then let the application handle the same key |
| Escape in Fcitx5 | Commit and consume the key while input is active; otherwise pass it through |

With no active input, Backspace and Ctrl+Backspace pass to the application.
Punctuation and phonetic escapes remain editable until a boundary. There is no
Bangla/Latin choice list, raw Latin selection, dictionary, prediction, or
autocorrection in the first-release scope.

## Platform matrix

| Platform | Status |
| --- | --- |
| CachyOS, KDE Plasma, Wayland, Fcitx5 | Working; native v0.1.0 published |
| Debian testing (forky), KDE Plasma, Wayland, Fcitx5 | Maintainer reports desktop tests and package installation, revision upgrade and removal passed; evidence limits below |
| Fedora 45, KDE Plasma, Wayland, Fcitx5 | Maintainer reports desktop tests and RPM installation, revision upgrade and removal passed; evidence limits below |
| Other Linux distributions and desktops with Fcitx5 | Untested; no support claim |
| Windows TSF | Next adapter after Fcitx5 |
| Linux with IBus | Planned after Windows TSF |
| macOS on Apple silicon or Intel | Out of scope; reconsider only if a viable free path exists |

The published Fcitx5 release targets x86-64 native packages. ARM64 is outside that
initial scope. Flatpak packaging is out of scope for now;
see the [release plan](../CONTRIBUTING.md#release-policy-and-checklist).

The reference desktop is a Modern 15 A5M running CachyOS KDE Plasma.
The maintainer reports successful typing in Kate, Firefox, and KWrite on
Wayland, plus Python GTK and Qt test environments. These reports do not
establish XWayland or other application coverage.

The Debian testing and Fedora 45 reports cover the supplied packaging-task
artifacts in Kate, KWrite and Firefox (Firefox ESR on Debian). They do not
establish desktop acceptance of subsequently rebuilt packages, Python GTK/Qt
environments, XWayland, or individual application backends. The Fedora 45 report
used Fedora 44-built RPMs. Fedora 45 is the native RPM packaging target.

No user-visible bugs are currently known to the maintainer. Track new bugs
in [GitHub Issues](https://github.com/shaadahmmed/jong-bangla-keyboard/issues).
Engineering follow-ups are separate from user-visible bug reports.

The [testing policy](TESTING.md#maintainer-run-desktop-acceptance) uses CachyOS
KDE Wayland as the desktop reference and Debian/Fedora KDE VMs for packaging.
Compatibility with comparable KDE setups is an engineering assumption, not a
claim that every distribution or application was tested. The agreed application
targets and future Windows 11 AMD64 matrix are acceptance goals, not new passes.
