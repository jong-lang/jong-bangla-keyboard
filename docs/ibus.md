# Experimental IBus adapter

## Scope and evidence

The IBus adapter is an implemented source-build experiment, with a native C11
IBus service around the shared Rust composition controller. It has no copied
upstream engine source, new Rust dependencies, dictionary or input logger.
It dynamically links the separately supplied LGPL IBus/GLib libraries; original
project code remains MIT licensed. Binary packages and desktop support are not
declared. Follow the [roadmap](roadmap.md#2-add-ibus) for release acceptance.

On 2026-11-06, local builds used CachyOS x86_64, GCC 16.2.1, CMake 4.4.5,
Rust/Cargo 1.99.1, GLib 2.90.1 and Arch's `libibus` 1.5.34-2 package. Its
pkg-config metadata reports `1.5.34-rc2`. The library and headers were extracted
into a temporary directory because IBus was not installed on the host. Those
original checks did not start a desktop daemon or change input-method settings.
The [GNOME VM smoke result](#gnome-vm-smoke-result) now adds installed desktop
evidence and an open pre-merge finding. The host Fcitx5 installation/session
remains intact; no beta/stable support is declared.

## Native boundary and lifecycle

[`engine.c`](../adapters/ibus/engine.c) subclasses `IBusEngine` directly.
[`main.c`](../adapters/ibus/main.c) connects to the existing IBus bus, exports the
factory and requests `org.freedesktop.IBus.JongBangla` without queueing. It exits
on bus disconnection, SIGINT or SIGTERM. Bare execution refuses to connect;
IBus launches it with `--ibus`. A second instance fails. No daemon is spawned,
framework selected or client configuration written by this service.

**Implementation decision, 2026-11-06:** use IBus's C/GLib API and reuse the
existing private Rust C ABI, now located under [adapters/ffi](../adapters/ffi/Cargo.toml).
This avoids a second unsafe boundary or registry dependency. The Fcitx5 bridge
still uses C++; neither native adapter contains phonetic rules. This is concrete
Linux reuse, not a requirement for future Windows/macOS bindings.

- One Rust handle belongs to each engine instance and is freed at IBus object
  destruction. All calls run exclusively on the GLib main thread. IBus can reuse
  a global engine across fields: every focus-in starts empty, and focus-out,
  disable and reset discard raw state. Focus-ID callbacks distinguish a stale
  focus-out from the currently focused field; legacy callbacks are also handled.
- Rust spans are borrowed UTF-8 bytes. The bridge copies both preedit and commit
  before publishing. IBus text objects copy those strings and consume their
  floating references. Preedit cursor and underline ranges use Unicode character
  counts: `কি` has cursor 2, unlike Fcitx5's six-byte offset. Empty commits are
  skipped, including active raw input with invisible output.
- Preedit uses `IBUS_ENGINE_PREEDIT_COMMIT`. IBus or its client owns committing
  displayed text on focus loss and engine switching. The engine's callbacks
  clear raw state without committing again. Upstream IBus clears/commits preedit
  before notifying the engine of focus-out/disable; actual frontend ownership
  and ordering still need desktop validation. Explicit reset and destruction
  discard; the adapter never retries a commit into a newly focused field.
- Backspace, exact Ctrl+Backspace and Escape follow the shared
  [interaction contract](adapter-contract.md#adapter-interaction-contract).
  Space/Enter and shortcuts publish cleared preedit, then commit, then return
  false so IBus delivers the original key. The service never also emits a
  `ForwardKeyEvent`, including for synchronous clients.
- Releases, modifier-only keys and forwarded events do not mutate composition.
  Shift/Caps affect the supplied resolved keyval; Num Lock is bookkeeping.
  Keypad digits are text. Ctrl/Alt/Super/ambiguous Mod5 events finalize and pass
  through rather than being reinterpreted as plain text. Dead/Compose prefixes
  pass through without altering the buffer. The service does not implement a
  Compose table; completed layout text, AltGr, dead/Compose combinations and
  their pending-word interactions require real frontend investigation.
- Password/PIN purposes and the hidden-text hint clear composition and bypass
  conversion. The private-input hint alone does not introduce a Latin mode.
  Neither surrounding text nor caret rectangle updates are treated as proof of
  document relocation. Generic preedit-click/document-relocation notification
  is unavailable in this direct engine interface; client reset and actual
  mouse/selection behavior require desktop tests.
- Nonzero C-ABI status discards state, clears preedit and consumes the potentially
  mutated key. Factory allocation failure refuses an engine. The shared
  [panic/ownership policy](adapter-contract.md#shared-rust-c-abi) applies, including
  unrecoverable allocation aborts and the exceptional panic-payload retention
  limit. There are no C++ exceptions in the C service and no input-text logging.

The ownership decision follows the official
[IBus engine API](https://ibus.github.io/docs/ibus-1.5/IBusEngine.html) and the
pinned upstream [1.5.34 input-context implementation](https://github.com/ibus/ibus/blob/1.5.34/bus/inputcontext.c)
(`bus_input_context_clear_preedit_text`, focus-out and disable). Factory cleanup
was checked against the [1.5.34 factory implementation](https://github.com/ibus/ibus/blob/1.5.34/src/ibusfactory.c).
These sources were inspected, not copied; API/source reasoning is distinct from
installed desktop observations.

## Build and synthetic checks

In addition to the [Rust prerequisites](development.md#build-and-check-the-rust-workspace),
use IBus development headers/library **1.5.33 or newer**, pkg-config, a C11/C++20
compiler, CMake 3.25+, Ninja, Python 3.11+ and `dbus-run-session`. The minimum is a
build prerequisite; only the environment above has been checked. Arch splits
the library/headers into `libibus`; other distributions may use `libibus-1.0-dev`
or `ibus-devel`. A running IBus daemon is unnecessary for these checks. Minimal test containers
need their own initialized D-Bus machine identity; CI provisions that inside its
disposable container, without changing the developer host.

```sh
cmake -S adapters/ibus -B target/ibus -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr
cmake --build target/ibus
ctest --test-dir target/ibus --output-on-failure
python3 tools/check-ibus-install.py target/ibus
```

With development files in a custom prefix, set `PKG_CONFIG_PATH` to its pkg-config
directory. A staged executable needs its runtime library discoverable, for example
through `LD_LIBRARY_PATH` pointing to that temporary prefix's library directory.
This is local validation setup, not an installed deployment recipe.

The CTest harness launches the actual `ibus-engine-jong-bangla` executable against
a private D-Bus message bus, with temporary XDG directories and no display.
It calls the real factory and engine protocol and checks exact preedit, cursor,
commit signals, return values and ordering. It exercises raw edits, boundaries,
shortcuts, Escape, releases, modifiers, repeats, digits, non-BMP Unicode,
invisible input, focus-ID and legacy lifecycle, restrictions, independent engine
instances and 200 create/type/destroy cycles. It also checks duplicate-service
rejection and graceful shutdown. The runner selects GIO's local filesystem
backend only for its private child processes, preventing desktop GVfs activation
and temporary-directory cleanup failures tracked in
[#21](https://github.com/shaadahmmed/jong-bangla-keyboard/issues/21).
Production filesystem/backend selection is unchanged.
The suite does not simulate a real IBus daemon's
frontend routing; an application-key observation means an unhandled protocol
reply, not proof that a desktop application received it.

The stage checker installs exactly the executable and XML registration into a
temporary `DESTDIR`, validates identifiers/version/command, parses the registration
with IBus, and repeats the protocol suite against the staged executable. Hiding
that executable must fail even when a build copy exists. Removal preserves an
unrelated sentinel. No system installation or framework activation occurs.

For native diagnostics:

```sh
cmake -S adapters/ibus -B target/ibus-sanitized -G Ninja \
  -DCMAKE_BUILD_TYPE=Debug -DCMAKE_INSTALL_PREFIX=/usr \
  -DCMAKE_C_FLAGS='-fsanitize=address,undefined -fno-omit-frame-pointer' \
  -DCMAKE_CXX_FLAGS='-fsanitize=address,undefined -fno-omit-frame-pointer' \
  -DCMAKE_EXE_LINKER_FLAGS='-fsanitize=address,undefined'
cmake --build target/ibus-sanitized
ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 UBSAN_OPTIONS=halt_on_error=1 \
  ctest --test-dir target/ibus-sanitized --output-on-failure
```

The 2026-11-06 run passed with address/undefined-behavior/leak detection enabled.
These instrument the native service/client, not Rust memory accesses or system
libraries. The protocol suite covers ordinary lifecycle cleanup, not every failure
path or desktop behavior. For a positive leak-detector control and shared Rust
lifecycle stress, use the [memory checker](development.md#build-and-check-the-fcitx5-experiment)
with its optional IBus build argument. A ptrace sandbox may prevent leak detection;
a failed detector is not a passing leak check. No performance budget is claimed.

## Explicit installation and removal

Perform installed testing in a separate, explicitly selected GNOME/IBus Wayland
environment. Do not activate IBus alongside the current Fcitx5 session. The
build/stage checks above are the appropriate checks on the current desktop.

For a system whose active input framework is already IBus, after reviewing the
staged payload, the explicit source-install command is:

```sh
sudo cmake --install target/ibus
```

Use the same prefix configured at build time; reconfigure and rebuild to change
it. `DESTDIR` staging is supported; install-time `--prefix` relocation is not,
because IBus's XML command records the configured absolute executable path.
No post-install daemon restart or settings change is automated. Restart/login
and selecting “Jong Bangla” in the desktop input-source settings are separate
maintainer actions for the chosen IBus environment. Discovery, activation and
real typing have not yet been accepted.

The build's `install-layout.txt` records the exact executable and XML destinations.
With the documented `/usr` prefix on the tested x86_64 layout, they are
`/usr/libexec/ibus-engine-jong-bangla` and
`/usr/share/ibus/component/jong-bangla.xml`. Confirm your generated paths before
removal. Deselect the engine in the IBus environment first, remove only these two
recorded files, then follow that environment's restart/login procedure. No other
IBus components, user settings or Fcitx5 files belong to this payload.

## GNOME VM smoke result

**2026-11-07, Asia/Dhaka:** a disposable x86_64 Fedora 45 Cloud image was
customized with GNOME Shell 51.1 and source-installed Jong Bangla. QEMU 11.1.3/KVM
used four virtual CPUs, 6 GiB RAM and a 24 GiB sparse disk. The official image's
signed SHA-256 and the locally extracted QEMU packages' signatures/checksums
were verified. No host packages, input-method settings or Fcitx5 files changed.
This is a customized VM, not an unmodified Workstation installation.

Native source revision: `a1f5ae687fffd2c6baf4aa439132616269a590a3`.
The test-runner-only correction for #21 does not change the executable.
Guest versions: GLib 2.90.1, IBus **1.5.35-rc1**, GTK 3.24.52/4.24.1,
Qt 6.11.2, Firefox 159.0.1, GNOME Text Editor 51.0, GCC 16.2.1,
Rust/Cargo 1.99.1 and Python 3.15.0. Fedora's IBus build is a release candidate;
these desktop results do not establish the same routes on stable IBus 1.5.34.

The guest built the source archive, passed CTest and the staged-install checker,
installed the two recorded files and discovered/activated `jong-bangla` in an
actual GNOME Wayland session. Private tests initially exposed #21; the corrected
runner passes on both the guest and original host without a caller override.

QEMU keyboard events exercised the compositor and real IBus/frontend route.
Small native GTK4/Qt clients and a local Firefox test page used only synthetic
text, with snapshots on explicit requests. Browser inspection read/reset fields
and invoked ordinary DOM focus changes; it did not inject typing into the page.
The 12-case suite covered raw Backspace, Ctrl+Backspace, Space, Escape, mouse/Tab
focus changes, password transitions/bypass, multiline Enter, digits, consecutive
words and invisible-buffer clearing.

| Client route | 12-case suite | Programmatic A → B focus |
| --- | --- | --- |
| GTK4, native Wayland, `GTK_IM_MODULE` unset | 12 passed | Failed at all three settling delays; [#22](https://github.com/shaadahmmed/jong-bangla-keyboard/issues/22) |
| GTK4, Wayland, explicit `GTK_IM_MODULE=ibus` control | Not rerun | All three delays passed |
| GTK3, native Wayland, `GTK_IM_MODULE` unset, maintainer manual probe | Not run | Three reported visual transfers: A empty, `কি` appears in B at the timed focus change; final `i`/Space phase not reported |
| Qt, Wayland, session `QT_IM_MODULE=ibus` | 12 passed | All three delays passed |
| Firefox, forced Wayland, `GTK_IM_MODULE` unset | 12 passed | Initial two passes/one failure; three additional two-second-delay repeats failed; #22 |
| Firefox, explicit `GTK_IM_MODULE=ibus` | Not rerun | Maintainer-reported manual A → B pass on 2026-11-07; exact expected field contents confirmed |

The Firefox direct-IBus result is a maintainer's manual report, not an
agent-executed suite or a fresh environment/binary identity check. To use that
workaround for one Firefox process, close Firefox completely and launch
`env GTK_IM_MODULE=ibus firefox` inside the GNOME/IBus session. This does not
validate the default Wayland route or establish broader application support.
Keep diagnosis, reproduction and correction work in #22. At the maintainer's
request, further testing is manual; agents should supply focused test steps
instead of running tests themselves.

Firefox used a disposable remote-inspection/kiosk profile. XWayland was not
tested. GNOME Text Editor also passed native Wayland typing and Ctrl+S forwarding:
the saved synthetic Bangla sample matched exactly. A US-layout control confirmed
the editor's own implicit trailing newline when interpreting saved files.
These bounded checks used software rendering. They do not establish performance,
full frontend acceptance, restart/
update/removal behavior or universal focus correctness. Test artifacts and VM
start/stop instructions remain local under ignored `target/ibus-vm/`.

## Manual focus investigation

The maintainer owns further testing. The interactive
[GTK probe](../tools/manual/ibus-focus.py) and
[Firefox page](../tools/manual/ibus-focus.html) are manual tools for
[#22](https://github.com/shaadahmmed/jong-bangla-keyboard/issues/22), not a
production correction or acceptance evidence. They inject no keys, call no
engine methods and do not save or transmit typed text. Use synthetic text only.
The GTK probe requires Python GObject introspection and the chosen GTK version;
these were available in the saved VM. No application build is needed.
The probe explicitly selects matching Gtk and Gdk versions before importing
either namespace. A maintainer GTK3 launch exposed automatic Gdk4 selection;
the corrected launcher now has maintainer-reported GTK3 reset/focus observations
in #22. These are visual observations; the final committed-value/Unicode
readouts and post-focus `i`/Space phase remain pending. No agent rerun is claimed.

If the saved VM is stopped, start it from the **host checkout root** and keep
that terminal open until shutdown:

```sh
python3 target/ibus-vm/run-vm.py
```

Wait for the GNOME desktop. Use a second host terminal for the copy below;
SSH port 22719 is available only while the VM is running and SSH has started.

Copy the probes into the running disposable VM from the **host checkout root**:

```sh
tar -cf - tools/manual/ibus-focus.py tools/manual/ibus-focus.html |
  target/ibus-vm/guest-ssh 'mkdir -p ~/acceptance/focus22-manual && tar -xf - -C ~/acceptance/focus22-manual'
```

Then use a terminal **inside the VM's GNOME Wayland desktop**, with Jong Bangla
selected. Do not launch clients from an SSH shell with a guessed session bus.
Record `gnome-shell --version`, `ibus version`,
`rpm -q gtk3 gtk4 mutter firefox`, `echo "$XDG_SESSION_TYPE"` and the addon
revision used. These are environment observations, not test passes.

### Default-route field change

Run one GTK client at a time, closing it before the next case:

```sh
cd ~/acceptance/focus22-manual
env -u GTK_IM_MODULE GDK_BACKEND=wayland python3 tools/manual/ibus-focus.py --gtk 3
env -u GTK_IM_MODULE GDK_BACKEND=wayland python3 tools/manual/ibus-focus.py --gtk 4
```

For Firefox, open the same page in a separate disposable process/profile:

```sh
focus_profile=$(mktemp -d /tmp/jong-focus22-firefox.XXXXXX)
env -u GTK_IM_MODULE GDK_BACKEND=wayland MOZ_ENABLE_WAYLAND=1 firefox --no-remote --profile "$focus_profile" "file://$PWD/tools/manual/ibus-focus.html"
```

Check Firefox's `about:support` reports **Window Protocol: wayland**, then
return to the probe before starting. If needed, use F11 before arming to fit
the browser probe in the saved VM's small display. In GTK, the header must show
`GdkWaylandDisplay` and `GTK_IM_MODULE=(unset)`. An unset variable alone does not
prove the selected IM module; record any independent module identification
separately. Do not run this baseline with `GTK_IM_MODULE=ibus`.

1. Click **Arm**. It focuses A and schedules a programmatic change in eight
   seconds. Type `ki` promptly, without Space or Enter; observe editable `কি`.
2. Stop typing and do not click, press Tab or switch windows. Wait for the
   status to say `B.grab_focus()` or `B.focus()` was called, then wait two more
   seconds. Type `i` followed by exactly one Space.
3. Read the passive values display without moving focus. Required result:
   A = `কি`, U+0995 U+09BF; B = `ই `, U+0987 U+0020. A must retain the old
   word once, and B must contain only the new word and one trailing space.
4. Record both exact values/code points, the frontend/version and any open
   composition indicator. Close/relaunch GTK or reload the Firefox page before
   another attempt. Repeat three times for each frontend; record every result.

GTK's display excludes live preedit; DOM values can include live composition.
Judge final contents after Space, not the interim display. A missing old word
is a failure even if B starts fresh; duplicated/moved old text is also a failure.
After a candidate correction, also repeat with 0.4 and 1.0 seconds of settling
instead of two, and run mouse/Tab handoff controls in fresh cases. In those
controls click A, type `ki`, move to B by the chosen action, then type `i` and
Space; the same final A/B contents are required. Neither control replaces the
programmatic case.

### GTK3 reset-only discriminator

This case isolates the public widget reset API without moving between fields:

```sh
env -u GTK_IM_MODULE GDK_BACKEND=wayland python3 tools/manual/ibus-focus.py --gtk 3 --action reset
```

Click **Arm**, type only `k` in A without a boundary, and stop typing. When the
status says `A.reset_im_context()` was called, wait two seconds, then type `i`
and one Space. Keep focus in A throughout. Record exact A/B values in three
fresh runs. B must stay empty. With discard semantics A is `ই `, U+0987 U+0020;
`কি `, U+0995 U+09BF U+0020, shows the old `k` survived into the next vowel.
Record `কই `, U+0995 U+0987 U+0020, separately: it indicates the old displayed
text was committed rather than discarded, without proving raw carryover.
The status confirms the widget API was invoked; it does not prove GTK forwarded
a protocol reset. In GTK 3.24.52 the widget delegates to its IM context only
when its internal `need_im_reset` flag is set. Composition surviving the widget
call therefore does not establish that an IM-context/engine reset was delivered
and ignored. This probe does not determine Firefox's exact callback path.

### Pending committed-text observation

The maintainer reports three GTK3 runs where `k`, the timed widget-reset call,
then `i` leaves visible `কি`, and three focus runs where visible `কি` transfers
to B as soon as focus changes, leaving A empty. Full details belong in #22.
Do not infer a trailing Space, exact code points or engine callback delivery
from those reports.

For the next GTK3 focus run, use the existing `--gtk 3` command and type `ki`
after Arm. Immediately after the timer moves focus to B, read the **bottom
values display**, without typing or clicking. Record A and B exactly. That
display excludes live preedit: B containing `কি` there means committed text;
an empty B there with visible `কি` in the entry means live preedit. Then wait
two seconds, type `i` and one Space in B, and record the bottom values/code
points again. This completes the previously unreported phase without assuming
whether GTK3 shares GTK4's traced cached-commit failure or another path.

Only after recording the default-route cases, optionally repeat a fresh case
with `GTK_IM_MODULE=ibus` to compare the existing workaround. Label that result
**explicit IBus-module control**, including which client/action was used.
Do not make it the default launcher, change session settings or count it as a
default Wayland fix. Report results on #22; its frontend investigation owns
the source evidence and any proposed upstream correction.

## Next desktop acceptance

Desktop testing is pre-merge work for PR #19. Investigate and resolve
[#22](https://github.com/shaadahmmed/jong-bangla-keyboard/issues/22) before merging;
the passing alternate GTK module is a control, not acceptance of the failing
default route. Preserve the default-route evidence when comparing frontends.
Fix findings, rerun affected checks and obtain the required separate-chat review
of the final revision before merge.

Record source SHA, distro/architecture, GNOME, IBus, library, toolkit and app
versions and actual Wayland/XWayland route. Test GTK, Qt and browser fields for
all relevant [adapter acceptance groups](adapter-contract.md#adapter-acceptance-cases),
including framework-owned focus/switch commits exactly once, return to the
original field, restrictions, modifier releases/repeats, layouts/AltGr/Compose,
mouse/selection relocation, reset/destruction and client preedit fallback.
Verify registration discovery, activation, restart/update and removal. Track
reproduced bugs and deferral decisions in
[GitHub Issues](https://github.com/shaadahmmed/jong-bangla-keyboard/issues).
No such desktop result is supplied by the synthetic suite or sanitizer run.
