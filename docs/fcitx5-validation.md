# Fcitx5 validation and installation evidence

These are dated implementation, environment and validation records. They do not
establish unrecorded desktop support. Current behavior belongs in the
[adapter contract](adapter-contract.md); actual installation instructions are in
[installation.md](installation.md). Use the checklist below for new candidate
results and GitHub Issues for product failures.

## Fcitx5 local feasibility result

**Implemented and checked on 2026-10-29:** a build-local C++ shared-library addon
and a separate Rust static-library C ABI. This settles the thin C++ bridge as the
practical boundary for this experiment; it does not make C++ a requirement for
future platforms. The core's rules and composition implementation are unchanged.
[Build/check commands](development.md#build-and-check-the-fcitx5-experiment) and the
[private C header](../adapters/fcitx5/jong.h) make the experiment reproducible.

The addon handles framework key classification, per-context ownership and Fcitx5
preedit/UI/commit calls. The boundary crate only wraps existing Rust controller
actions. Each input-context property uniquely owns one opaque Rust handle;
properties never copy raw composition between fields. Destruction frees it
without committing. No installed addon, desktop process or settings were changed.

The current [interoperability contract](adapter-contract.md#fcitx5-interoperability-boundary)
specifies ownership, encoding, lifetimes and failure containment.

**Key and lifecycle evidence:** the actual shared addon is loaded through Fcitx5
5.1.23's addon loader into an isolated `Instance`. Its real event dispatcher routes
synthetic input-context calls to the addon. Ten suites cover the 15 acceptance
groups' synthetic portions: clear-preedit → commit → one application-key delivery;
editing/Escape commit/repeats/releases; resolved case/keypad text; ambiguous AltGr as a
boundary; pending dead/compose prefixes; invisible input; input-method switching;
focus/reset/repeated callbacks; restricted fields; destruction; independent
contexts; fallback preedit without choices; and explicit preedit clicks.

On ordinary focus-out, the framework owns delivery: Fcitx5 commits client preedit
in its `ReservedFirst` handler unless `ClientUnfocusCommit` delegates that to the
frontend. The engine's later `deactivate` only discards local state. The harness
checks the server path and simulates an advertised frontend commit, proving no
extra addon commit. Missing frontend delivery is never retried in another field.
Ordinary input-method switching while focused instead takes the Rust commit once.
Capability-driven switching discards; framework password/disable policy wins.
Fcitx5's configured shortcuts run first: a configured Ctrl+Space switches without
an extra forwarded key, and its modifier-only Shift toggle commits on release.
Keys that reach the addon retain the specified modifier-only policy.

Inspected matching installed headers and upstream tagged sources:
[Fcitx5 5.1.23 dispatcher](https://github.com/fcitx/fcitx5/blob/5.1.23/src/lib/fcitx/instance.cpp),
[input-context delivery](https://github.com/fcitx/fcitx5/blob/5.1.23/src/lib/fcitx/inputcontext.cpp),
[shared-addon loader](https://github.com/fcitx/fcitx5/blob/5.1.23/src/lib/fcitx/sharedlibraryloader.cpp),
and [default shortcuts](https://github.com/fcitx/fcitx5/blob/5.1.23/src/lib/fcitx/globalconfig.cpp).
These informed API use; no upstream implementation or rule tables were copied.
Project sources remain MIT; installed Fcitx5 Core/Config/Utils are linked dynamically
and their upstream headers identify LGPL-2.1-or-later licensing. Distribution and
packaging remain a separate step.

**Recorded environment, not desktop support:** CachyOS rolling, x86_64,
`XDG_SESSION_TYPE=wayland`, `XDG_CURRENT_DESKTOP=KDE`; installed package versions:

| Item | Observed version |
| --- | --- |
| Plasma workspace | 6.8.2-1.1 |
| Fcitx5 / Core/Utils headers | package 5.1.23-1.1; executable/pkg-config 5.1.23 |
| Rust / Cargo | 1.99.1; rustc 58cf8f9c3; Cargo 5f94df478 |
| GCC C++ | 16.2.1; package 16.2.1+r23+gd564253eb6c8-3 |
| CMake / Ninja | 4.4.5 / 1.13.2 |
| clang-format | 23.1.4 |
| Qt6 base / GTK3 / GTK4 | 6.12.0-3.1 / 1:3.24.52-2.1 / 1:4.24.1-1.1 |
| Fcitx5 Qt / GTK integrations | 5.1.16-2.1 / 5.1.7-1.1 |

No new tools or dependencies were installed. CMake requires 3.25+, C++20 and
Fcitx5 development headers 5.1.23+; these are build constraints, not a tested
version range. Installed toolkit versions do not establish that any app used them.

**Bounded desktop observations:** GTK3, Firefox, KWrite and Kate have limited
user-reported typing/focus observations. The user also confirmed the updated
Escape-commits behavior. These do not establish a complete per-application
acceptance run, installed-route support or a supported version range.

The harness frontend is synthetic, neither Wayland nor XWayland. It does not
complete a real AltGr/dead-key/Compose pipeline, application cursor relocation,
frontend-owned commit or fallback UI rendering. Use the installed-application
checklist below for current validation. Product bugs and their disposition are
tracked in GitHub Issues, rather than duplicated in this evidence record.

**Automated follow-up (2026-10-30):** Rust format, workspace Clippy, workspace
tests and release build passed again: 20 composition tests, 352 conversion tests,
three FFI tests and two doctests. The pinned external reference comparison passed
all 522,933 authored fixture rows; the three documented Unicode case differences
remain. C++ formatting, the normal dispatcher harness and C++ ASan/UBSan harness
passed. Each harness run covers ten synthetic suites. Leak detection was disabled
with `ASAN_OPTIONS=detect_leaks=0`; Rust and system libraries were not instrumented.
The generated mixed-context audit was not rerun. Actual commands were recorded in
the validation handoff at commit `5ed5bdc`; current reproduction commands are in
the [development guide](development.md).

**Installed inventory refreshed on 2026-10-30:** CachyOS rolling, Linux
7.3.0-4-cachyos, x86_64; inherited session variables report Wayland and KDE.
Plasma workspace/KWin are 6.8.2-1.1, Fcitx5 is 5.1.23-1.1, Fcitx Qt is
5.1.16-2.1 and Fcitx GTK is 5.1.7-1.1. Qt6 base is 6.12.0-3.1, GTK3 is
1:3.24.52-2.1 and GTK4 is 1:4.24.1-1.1. Firefox is 159.0-1.1; Kate/KWrite
are provided by package `kate` 26.08.2-1.1; XWayland is 24.1.14-1.1.
The system Python GTK3 binding reports runtime 3.24.52. Tool versions remain
Rust/Cargo 1.99.1, GCC 16.2.1, CMake 4.4.5 and Ninja 1.13.2. No tools were
installed or upgraded. An offscreen KWrite `--help` probe stalled and was
interrupted; it supplied no application runtime evidence. The sandbox could not
inspect the active desktop applications, so this is an installed inventory,
not proof of their loaded toolkit or protocol versions.

**Historical private-session follow-up (2026-10-30):** GTK3, Firefox and KWrite
have overall user-reported passes. Detailed per-case observations were not
supplied. The temporary helper and launcher were not committed and are not
reproducible repository tooling. Their captured runtime fields below remain
prior evidence; new validation uses normally installed apps and the documented
installation procedure. Any future isolated helper must be versioned with its
launch instructions before becoming a required test dependency.

**Runtime evidence supplied on 2026-10-30:** the user provided Firefox's
`about:support` JSON and the private test shell's GTK/Qt/browser console output.
The table extracts the relevant fields; these are observations from the user's
test session rather than new agent-run GUI tests.

| Test app | Runtime evidence | Display path and limits |
| --- | --- | --- |
| Firefox | `application.name=Firefox`, `version=159.0`, `buildID=20261027211755`, `distributionID=archlinux`; OS reports Linux 7.3.0-4-cachyos | `graphics.windowProtocol=wayland`; native Wayland is directly reported. No GTK runtime version is present in the supplied library-version fields. |
| GTK3 helper | Console prints `GTK runtime: 3 24 52 display backend: GdkWaylandDisplay` | GTK 3.24.52 and native Wayland directly reported after the import fix. |
| KWrite | Console identifies `kwrite` opening the disposable `qt-test.txt`; no application/Qt runtime versions printed | Launcher sets `QT_QPA_PLATFORM=wayland` and `QT_IM_MODULE=fcitx`; this is the requested route, without an independent runtime backend report. Prior package inventory is `kate` 26.08.2-1.1 / `qt6-base` 6.12.0-3.1, not a runtime-version observation. |

Firefox's supplied environment also reports `MOZ_ENABLE_WAYLAND=1` and
`GDK_BACKEND=wayland`, consistent with its runtime protocol field. The private
launcher's explicit IM modules use its separate Fcitx D-Bus session; native
Wayland windows alone do not validate KWin text-input protocol integration.

**Bounded smoke result:** direct GTK/Firefox Wayland evidence and limited Qt
runtime evidence are recorded above. AltGr/dead-key/Compose, Electron, XWayland,
KWin text-input protocols and exact frontend commit ownership remain untested or
unrecorded. The private-session route does not establish ordinary installed-addon
delivery. Existing observations must not be relabelled as new checks. Track
product failures, workarounds and release decisions in
[GitHub Issues](https://github.com/shaadahmmed/jong-bangla-keyboard/issues).

## Installed-route basic smoke result

**2026-11-06 — User-reported result:** in response to the four-case request for
normally launched applications with the installed Jong Bangla addon selected,
the user confirmed that the checks work in **KWrite 26.08.2 (Wayland)** and
**Firefox 159.0.1 (Wayland)**.

| Check | Expected result | KWrite 26.08.2 | Firefox 159.0.1 |
| --- | --- | --- | --- |
| Commit boundary | `ki`, Space produces `কি ` | User-reported pass | User-reported pass |
| Raw Backspace | `ki`, Backspace, `i` produces `কি` | User-reported pass | User-reported pass |
| Clear active word | `ki`, Ctrl+Backspace, `i` produces fresh `ই` | User-reported pass | User-reported pass |
| Escape boundary | `ki`, Escape, `i` commits `কি`, then starts fresh pending `ই` | User-reported pass | User-reported pass |

These statuses record the user's combined confirmation of the requested cases;
the agent did not observe or capture the application output. Application versions
and Wayland routes are user-reported. The loaded addon revision, exact frontend
transport, current distro/Plasma versions and Fcitx5/toolkit runtime versions were
not supplied with this result; earlier environment records remain prior evidence.
This establishes a basic installed-route result for these two named apps.
Follow-up KWrite, Firefox and Kate results are recorded below. Remaining app/case
combinations and the wider matrix still need separate results. These observations
do not establish a broader support range.

### KWrite lifecycle follow-up

**2026-11-06 — User-reported follow-up:** the user confirmed all three requested
checks pass in the previously reported **KWrite 26.08.2 (Wayland)** environment.
Each case was requested in a fresh disposable document.

| Check | Requested sequence and expected result | Result |
| --- | --- | --- |
| Enter boundary | `ki`, Enter commits `কি` and inserts one newline | User-reported pass |
| Select-all shortcut | `ki`, Ctrl+A, `i` replaces the selection with fresh `ই` | User-reported pass |
| Window focus and return | With `ki` pending, switch to Firefox and return, then type `i`: the original `কি` appears once and `i` starts fresh | User-reported pass |

The combined confirmation reported no failure for these cases; the agent did
not observe or capture the output. The window-focus result covers KWrite as
the composing application and Firefox as the other window. It does not establish
Firefox field-focus behavior or the corresponding Firefox composition cases.
Candidate/runtime details remain limited as described above.

### Firefox field handoff and input-method switching

**2026-11-06 — User-reported follow-up:** the user reported the Firefox
two-field handoff working, describing `ki` in A, Tab, then `i` in B. They also
confirmed the requested English/Bangla switching case works as expected without
issues, reporting **Meta+X** as the shortcut used to switch to English. App/route
context remains the previously reported Firefox 159.0.1 and KWrite 26.08.2 on Wayland.

| Check | App context | Requested behavior | Reported result |
| --- | --- | --- | --- |
| Field A to B | Firefox | Pending `ki` in A, Tab to B, `i`: one `কি` in A and fresh `ই` in B | User-reported working A-to-B flow |
| Input-method switch | Firefox and KWrite | Pending `ki`, switch to English, type literal `x`, return to Jong and type `i`: committed `কি`, literal `x`, fresh `ই` | User-reported pass, no issues |

The initial field response describes A-to-B typing; return-to-A stale-buffer
behavior is covered by the follow-up below. The switching response is a combined
confirmation for the two requested apps; it does not
provide separate output captures. Meta+X was specified for switching to English;
the return-to-Jong action was not separately specified. These are user reports,
not agent-observed checks, and add no new candidate/runtime details.

### Firefox field return and context closure

**2026-11-06 — User-reported follow-up:** the user replied `pass` to all three
requested checks in the previously reported **Firefox 159.0.1 (Wayland)** context.
Disposable fields and dummy text were requested, including for the password field.

| Check | Requested behavior | Reported result |
| --- | --- | --- |
| Return to field A | After the Tab test, return to A and type `i`: fresh composition without restoring the old `ki` buffer | User-reported pass |
| Dummy password-field transition | With `ki` pending, move to a dummy password field and back: no unexpected Bangla composition or stale text | User-reported pass |
| Window closure and fresh composition | Close a test window with `ki` pending, open a new one, type `i`: fresh `ই` | User-reported pass |

This combined confirmation closes the previously unconfirmed return-to-A case.
It reports no unexpected composition/stale text for the dummy password-field
transition; whether the original pending word committed or was discarded was
not separately described. The agent did not observe or capture these results.
No new candidate/runtime details or direct callback/commit-ownership evidence
were supplied; those limits and remaining app/case combinations still apply.

### Further Firefox cases and environment report

**2026-11-06 — User-reported follow-up:** the user confirmed all three requested
Firefox cases below pass, in the previously reported Firefox 159.0.1 Wayland
context. They also supplied current environment details and one AltGr result.

| Check | Requested behavior | Reported result |
| --- | --- | --- |
| Enter boundary | `ki`, Enter produces `কি` and one newline | User-reported pass |
| Select-all shortcut | `ki`, Ctrl+A, `i` replaces the selection with `ই` | User-reported pass |
| Window focus and return | Pending `ki`, switch to KWrite and return, then type `i`: the original word appears once and the new composition starts fresh | User-reported pass |
| AltGr character | English UK layout, AltGr+E while Jong is selected produces `€` | User-reported working; app and pending-word state not specified |

| Environment field | Evidence |
| --- | --- |
| Distro / architecture | User reports CachyOS, x86_64 |
| Desktop / kernel | User reports KDE Plasma 6.8.2 and Linux 7.3.1-1-cachyos |
| KWrite toolkit | User reports Qt 6.12.0; KWrite 26.08.2/Wayland is the earlier app context |
| Installed package inventory | Agent read `pacman -Q fcitx5 plasma-workspace qt6-base`: 5.1.23-1.1, 6.8.2-1.1 and 6.12.0-3.1 respectively |

Package inventory does not independently identify running processes or the loaded
addon revision. The AltGr report does not establish both apps, pending-word
interaction, the raw modifier route, or dead-key/Compose completion. The remaining
modifier/case/repeat and pointer/cursor checks were not reported as passes.
The Shift-switching report, investigation, configuration choice and desktop
retest status are tracked in [Issue #12](https://github.com/shaadahmmed/jong-bangla-keyboard/issues/12).
After the reversible manual-setting instructions, the user confirmed the unwanted
switching was fixed and working normally in response to the Meta+Space,
standalone-Shift/pending-word and `kI` retest request. The retest app was not named;
this confirmation must not be assigned independently to both apps.

The expanded synthetic framework-shortcuts suite separately reproduces the
Meta+Space/temporary-Shift activation cycle and checks an empty temporary-toggle
list as a control. Both profiles preserve resolved Shift+I case; the empty-list
profile also preserves a pending word under standalone Shift. These dispatcher
results are separate from the user-reported retest. No production adapter policy
was changed.

### Kate modifiers, case, repeats and cursor relocation

**2026-11-06 — User-reported follow-up:** the user tested the requested three
groups in **Kate 26.08.3**, then clarified the old word's location after clicking
and confirmed both case spellings.

| Check | Reported result |
| --- | --- |
| Modifier-only keys | Pressing Ctrl or Shift separately leaves the word pending without committing it |
| Case-sensitive spelling | Fresh `ki` → `কি` and `kI` → `কী` both pass |
| Held letter and Backspace | No freezing, lag or stuck-key issue reported |
| Pointer motion | Moving the pointer preserves the pending state |
| Click to a new location | The old word stays at its original location; the next word starts at the clicked location |

These are user-reported observations, not agent-observed output or latency
measurements. The held-key report does not separately confirm duplication on key
release. The click result covers relocation by clicking, without a separate
selection test or exact next-character output. Kate is a distinct application
from the earlier KWrite reports; these results do not establish the corresponding
Firefox or KWrite checks. No new loaded-addon revision, Kate toolkit/runtime or
frontend/Wayland route evidence was supplied.

## Remaining desktop smoke checklist

Use the [installed addon](installation.md) in normally launched GTK3, Firefox
and KWrite applications. Use disposable local fields/documents and record how
each app was launched; no untracked helper is required. Start with basic typing
and Escape for the candidate being tested. First check `ki` then Space
produces `কি ` to confirm that each new test window reaches Jong. Start each case
in an empty field/document or a separate disposable line. Here, *pending* means
the underlined word still being edited before Space or Enter commits it.
The observations above cover only their named cases and apps; use the checklist
for the remaining combinations rather than treating one app's pass as another's.

| Case | Procedure and observation to report |
| --- | --- |
| Raw editing | Type `ki`, Backspace: ক; type `i`: কি. Ctrl+Backspace clears the pending word; a fresh `i` produces ই. |
| Field focus and return | In GTK3/Firefox, type pending `ki` in A, Tab to B and type `i`. A should contain কি once, B ই. Return to A and check that its old pending buffer does not resume. |
| Window focus | With pending `ki`, switch to another window and return. Report whether কি stays once in the original field and whether the next `i` starts fresh; no old text should appear in the other window. |
| Input-method switch | With pending `ki`, use your configured Fcitx switching action to select English, type `x`, then switch back and type `i`. Record that action. Expect one committed কি, literal `x`, then fresh ই; no duplicate or restored raw buffer. |
| Modifiers, case and repeats | With pending `ki`, press/release Shift and Ctrl alone, then continue typing. Report preservation or a focus/shortcut action. On fresh input compare `ki` (কি) with `kI` (কী); hold a letter and Backspace briefly, checking for stuck keys, duplication on release or freezing. |
| Enter and application shortcuts | In a multiline field, `ki` then Enter should insert কি and one newline. With pending `ki`, Ctrl+A should commit before selecting; typing `i` should replace the selection with ই. Report extra or missing actions. |
| Pointer and cursor relocation | Move the pointer over pending `ki`, then continue: motion alone should preserve it. Separately click elsewhere in the document or select text while input is pending. Report where কি ends up and whether the next `i` begins fresh. A reset may discard pending text; stale text must not be inserted at the new cursor. |
| Restricted field / context closure | In GTK3/Firefox, move from pending `ki` to the dummy password field, then back. Report any original-field commit/discard, password-field composition or stale buffer. Close a test window with pending input and open a new one; its first `i` should be fresh ই. Never use a real password. |
| AltGr / dead key / Compose | Use only an already configured layout/Compose key. Report the exact sequence, expected character, actual result and whether a word was pending. Otherwise mark unavailable; do not change system settings for this test. |

Record existing framework bindings before interpreting modifier-only results.
A configured temporary Shift toggle is owned by Fcitx; the adapter's preservation
rule applies to events reaching it. The [typing guide](typing.md#standalone-shift-switching)
explains how users can choose and reverse that binding without an addon change.

For each application, record its version, toolkit version where exposed and
Wayland/XWayland path, distinguishing an observed runtime value from a forced
launch setting or installed package version. Use the installed GTK application's
About/system information where available. Firefox's `about:support` exposes its
version and Window Protocol; report only those fields. KWrite's Help/About dialogs
expose application and Qt versions where available. Record unavailable fields
explicitly; do not infer a runtime from installed packages or launch flags.

Report `pass`, `fail` or `unavailable` per case and app. For a failure include
the field, exact keys, expected and actual text, whether the word was pending,
and whether it repeats on a second attempt. A screenshot or short recording is
optional when cursor/underline behavior is hard to describe. Include Escape
(`ki`, Escape, then `i` gives committed কি followed by fresh ই), and document
editing after commit. Record failures in GitHub Issues. Direct
reset/destruction callbacks, unavailable commit targets and frontend commit
ownership still have synthetic evidence only where no desktop observation is
available; do not infer them from a passing visible interaction.

## Experimental local installation plan

**Reviewed and implemented on 2026-10-30.** The user
will perform the actual installation and desktop configuration. Development may
prepare install rules and verify a staged copy under a temporary directory;
it must not install into system/user addon paths or restart the desktop daemon.

**Local layout decision:** target the installed Fcitx5 prefix explicitly, `/usr`
on the recorded CachyOS x86_64 machine. Use Fcitx5's CMake directory variables
with `FCITX_INSTALL_USE_FCITX_SYS_PATHS=ON`; the current build defaults to
`/usr/local`, whose addon discovery has not been validated. Do not infer that
arbitrary prefixes or a per-user install work without testing discovery there.
This is an experimental source installation, not a public package/support policy.

| Installed artifact | Destination on the recorded machine |
| --- | --- |
| Shared addon | `/usr/lib/fcitx5/libjong-bangla.so` (`FCITX_INSTALL_ADDONDIR`) |
| Addon metadata | `/usr/share/fcitx5/addon/jong-bangla.conf` (`FCITX_INSTALL_PKGDATADIR/addon`) |
| Input-method metadata | `/usr/share/fcitx5/inputmethod/jong-bangla.conf` (`FCITX_INSTALL_PKGDATADIR/inputmethod`) |

Keep the stable internal identifier `jong-bangla` in both metadata filenames and
the input method's `Addon` field. Retain the provisional names `Jong Bangla
feasibility addon` / `Jong Bangla`, label `জং`, language `bn`, version `0.1.0`,
on-demand loading and `Configurable=False`. Confirm the public display name
before public packaging; the local experiment does not settle that choice.

Generate separate metadata for installation with `Library=libjong-bangla`,
without a suffix or absolute build path. Keep the existing harness metadata's
absolute path so ordinary tests continue to load the build-local binary.
Fcitx5's tagged [shared-library loader](https://github.com/fcitx/fcitx5/blob/5.1.23/src/lib/fcitx/sharedlibraryloader.cpp)
appends the platform suffix and searches its addon directories. Its official
[addon tutorial](https://fcitx-im.org/wiki/Develop_an_simple_input_method) describes
the three-file layout and matching metadata identifiers. Installed
`/usr/lib/cmake/Fcitx5Utils/Fcitx5UtilsConfig.cmake` supplies the paths above.
No upstream implementation is copied into the project.

**Dependencies:** building needs Rust/Cargo satisfying the manifest's Rust
1.99.1 baseline, a C++20 compiler, CMake 3.25+, Ninja and Fcitx5 Core/Utils
development headers 5.1.23+. Cargo runs offline with the lockfile. At runtime
the Rust implementation is linked into the addon; Cargo/Rust and the test
executables are not installed. Inspection of the existing local ELF with
`readelf -d target/fcitx5/libjong-bangla.so` found Fcitx5 Core `.so.7`, Config
`.so.6`, Utils `.so.2`, plus the system C/C++/math/unwind libraries and ELF
loader. This is an observed ABI dependency list, not a portable minimum-version
claim. Desktop use also needs an already configured Fcitx5/frontend route and
application integration; do not silently set environment variables or install
toolkit modules. Existing [desktop evidence and limits](#remaining-desktop-smoke-checklist)
continue to apply.

**Implementation and verification contract:**

1. Add install rules for exactly these three files using the Fcitx5 variables.
   Do not install test engines, harness/resource/memory binaries, the Rust
   archive, private headers or build-local metadata.
2. Configure a separate Release build with prefix `/usr` and the Fcitx system
   path option enabled; build it and run the existing dispatcher/lifecycle tests.
3. Use CMake's [DESTDIR staging](https://cmake.org/cmake/help/latest/envvar/DESTDIR.html)
   to install under a fresh temporary root without privileges. Verify the exact
   file list and installed metadata, then exercise the staged addon through the
   isolated dispatcher. Include a missing-library control so a build-local or
   system addon cannot hide a broken installation layout.
4. Verify removal of the three staged files, retaining an unrelated sentinel.
   Check a non-system prefix separately if the install rules allow one; record
   that staged discovery does not establish normal desktop discovery there.
5. Publish reproducible build, install, activation and removal instructions only
   after those checks pass. Never execute real installation/activation on the
   user's behalf in this task.

**Removal contract for the `/usr` layout:** the user first switches away from
Jong Bangla and removes its entry in Fcitx5's configuration tool, then removes
only the three absolute paths in the table and restarts their normal Fcitx5
session (a loaded process retains its old addon until restarted). Do not remove
shared directories, the Fcitx5 profile, toolkit integration or other engines.
Before installation, identify any existing files at those paths and back them
up or use the owning package's workflow; removal of an upgrade must restore
those prior files when appropriate. Avoid a generic recursive uninstall command.

**Current distribution direction (2026-11-05):** the [roadmap](roadmap.md)
confirms Flatpak/deb/rpm/pacman and maintained AUR delivery in stages. Recipes,
Flatpak deployment, public distribution/license manifests, supported version
ranges and desktop routes remain implementation/validation work. The public
display name remains provisional. Local source installation is the only
currently documented installation path.

**Staging evidence (2026-10-30):** install rules now generate separate installed
metadata and install exactly the three artifacts above. The Release build in
`target/fcitx5-install`, configured with `/usr` and
`FCITX_INSTALL_USE_FCITX_SYS_PATHS=ON`, passed both CTest tests (ten dispatcher
suites plus the C-ABI lifecycle workload). `python3 tools/check-install.py
target/fcitx5-install` verified the file list, metadata, all ten suites loaded from
the staged copy, missing-library rejection and removal retaining an unrelated
file. An initial negative-control assertion looked for a suppressed Fcitx log;
the harness now explicitly checks addon loading and the control checks that
failure directly. The final checker passed. No production key handling changed.

The same staged checker passed for `target/fcitx5-prefix-check`, configured with
`CMAKE_INSTALL_PREFIX=/opt/jong-prefix-check` and
`FCITX_INSTALL_USE_FCITX_SYS_PATHS=OFF`. Explicit test-only data/addon paths select
that temporary copy; this does not prove ordinary desktop discovery at `/opt`.
The checker inherits no system addon fallback. Python 3 is a check dependency,
not an addon runtime dependency. No install target for test tooling was added.

`readelf -d target/fcitx5-install/libjong-bangla.so` confirmed the same runtime
dependencies recorded above and no RPATH/RUNPATH. The three real `/usr` target
files were absent when inspected; no actual installation was performed. C++
format checks, Rust formatting/Clippy/workspace tests/release build/API docs and
local Markdown links/diff whitespace passed. Reference comparison, sanitizers,
leak/resource measurement and desktop smoke tests were not rerun. Actual
installation, activation and restart are reserved for the user; see the
[tested preparation and manual instructions](installation.md#install-the-experimental-addon).
