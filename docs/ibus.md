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
into a temporary directory because IBus was not installed. No IBus daemon,
GNOME session, installed client or input-method setting was started or changed.
Only synthetic protocol/service and staged-installation evidence is available.
The current Fcitx5 installation was left intact.

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
or `ibus-devel`. A running IBus daemon is unnecessary for these checks.

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
rejection and graceful shutdown. It does not simulate a real IBus daemon's
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

## Next desktop acceptance

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
