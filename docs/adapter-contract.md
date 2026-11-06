# Adapter interaction and interoperability contract

This document owns native event/lifecycle behavior and the implemented Fcitx5
interop boundary. Shared product requirements are in [v1.md](v1.md); platform
implementation stages are in the [roadmap](roadmap.md). The Fcitx5-specific C ABI
below does not impose a binding choice on other adapters.

## Adapter interaction contract

**Updated by the user on 2026-10-29:** Escape commits active Bangla, clears the
raw buffer and consumes that press; it must preserve the typed word. This
supersedes the earlier Escape-cancels decision. Navigation, Tab, Delete and
application shortcuts commit first, then forward. Modifier-only presses that
reach the adapter preserve composition; configured framework switching shortcuts
take precedence. Focus loss and input-method switching commit to the original field when the framework still permits it, then
clear state. Explicit resets and destroyed contexts discard pending input.
These decisions settle the earlier interaction proposals. They preserve typed
text before application editing; Escape finishes a word without inserting a
space or newline. Explicit reset/destruction and the separate `cancel()` API
retain their discard semantics.

The experimental adapter implements this specification with synthetic validation
and limited user-reported desktop smoke evidence; the full frontend matrix
remains unverified. It uses the existing Rust controller's
actions; no new `CompositionKey` variants are required.
Raw framework events and modifier classification stay outside the Rust core.

| Event reaching the adapter | Active raw input | No active input |
| --- | --- | --- |
| Text key | `insert(char)` and consume accepted text | Same; start composition |
| Plain Backspace | `handle_key(Backspace)` | Forward |
| Exact Ctrl+Backspace | `handle_key(CtrlBackspace)` | Forward |
| Plain Space or Enter | `handle_key(Space/Enter)`; commit, then forward | Forward |
| Plain Escape | `commit()`; clear preedit, commit nonempty Bangla and consume | Forward |
| Navigation, Tab, Delete, application shortcut or other non-text action | `commit()`; clear preedit, commit nonempty output, then forward | Forward |
| Modifier-only press or key release | No composition action; pass through | Same |

Activity always follows raw input, including invisible escapes. After active
Escape commits once, a second Escape reaches the app; after a navigation boundary, subsequent
Backspace belongs to the app. There is no cursor or selection inside raw input
in v1: arrows, Home/End, Page Up/Down, Insert and their selection/word-navigation
variants finalize the whole word before application editing. Tab and Shift+Tab
likewise finalize before completion or moving to another field. Ctrl+C, Ctrl+V,
Ctrl+X, Ctrl+A, Ctrl+Z and other application actions finalize first; the app then
decides what the unchanged shortcut does, including selection and undo behavior.

### Event normalization and ordering

The following engineering rules make the confirmed behavior precise. They avoid
treating shortcut keys as typed text or replaying an event twice.

1. Let Fcitx5 handle its configured activation/switching shortcuts. The adapter
   adds no global language shortcut. If a switch causes deactivation, apply the
   lifecycle contract below, rather than forwarding a second switching key.
2. Classify releases and modifier-only presses before text or boundaries. They
   never insert, delete, commit or cancel. A release may pass through without
   replaying its press; release handling needs actual frontend validation.
3. Match editing keys using the effective symbol and semantic modifiers.
   Ignore lock/repeat bookkeeping when deciding an exact modifier combination;
   preserve the original event for forwarding. Exact Ctrl+Backspace means Ctrl
   without Shift, Alt, Super or other semantic modifiers. Plain Backspace,
   Space, Enter and Escape have none. Keypad Enter follows plain Enter.
4. Shift and Caps Lock affect resolved text, preserving phonetic case. Plain
   digits, keypad digits resolved as text, punctuation and backticks are text.
   Shift+Space/Enter/Backspace/Escape and Ctrl+Shift+Backspace are other actions:
   commit first and forward with their modifiers intact. Shift+Tab is navigation.
5. Ctrl/Alt/Super shortcuts cannot become raw input. Accept a layout-resolved
   AltGr character only when Fcitx5 identifies it as text, with no remaining
   shortcut modifiers. Do not globally erase Ctrl+Alt to make text; ambiguous
   events follow the non-text boundary route until the frontend is verified.
   Dead/compose prefixes with no completed character keep composition unchanged
   and remain available to the framework; resolved text follows the text route.
6. Each delivered repeat press runs the same policy once. Repeated text inserts
   repeatedly; held Backspace consumes only while raw input exists. Repeated
   Escape or Ctrl+Backspace can reach the app after the first press clears input.
   Do not synthesize a second repeat, space or newline.
7. For a handled edit, publish the resulting preedit first, send any nonempty
   commit next, and only then allow the original boundary/action to reach the
   app once. Forwarding means one delivery path: let the framework deliver the
   event or explicitly forward it, never both. Empty-output composition still
   finalizes, without a framework empty commit. Rejected whitespace/control text
   uses the non-text boundary route; rejection alone must not leave stale state.

### Context lifecycle and commit ownership

Keep one controller per input context; never transfer a buffer to another field
or restore it on refocus. On ordinary focus loss or input-method deactivation,
finalize to the original context when its frontend still permits delivery.
If the framework/frontend has already committed the displayed preedit, clear
the Rust buffer without committing again. Otherwise take `commit()` once,
clear displayed preedit, and deliver nonempty output only to that original
context while delivery remains valid. If delivery is unavailable, discard state;
do not retry against a newly focused field. Duplicate callbacks see empty state.

An explicit client reset or context destruction discards state without a commit.
Activation/focus-in begins empty. Framework restrictions on input-method use,
including password-field restrictions, take precedence over key processing;
disabling the input method clears pending state without sending it into the
restricted field. A sensitive-input hint alone is not permission to log text,
persist it, or introduce a new Latin/Bangla mode. No such mode is added here.

Mouse pointer motion alone does not end composition. For an actual preedit click
or a notified cursor/selection relocation, finalize before relocation only when
the original insertion position is still valid. A reset or notification received
after relocation clears state without inserting the old word at the new position.
Do not infer document movement from a candidate-window/caret rectangle change or
ordinary surrounding-text updates. Generic mouse/selection notifications may be
unavailable; the feasibility step must establish what each frontend reports.

Fcitx5's upstream [engine callbacks](https://github.com/fcitx/fcitx5/blob/master/src/lib/fcitx/inputmethodengine.h)
distinguish deactivation from reset. Its [event definitions](https://github.com/fcitx/fcitx5/blob/master/src/lib/fcitx/event.h)
warn that focus-out may follow an already completed preedit commit and expose
key-release and preedit-click events. The [input-context API](https://github.com/fcitx/fcitx5/blob/master/src/lib/fcitx/inputcontext.h)
also distinguishes a context from a guaranteed individual text field. Consulted
on 2026-10-29; these are API investigation evidence, not a validated version or
a guarantee about toolkit event ordering. No upstream source was imported.

### Adapter acceptance cases

These 15 groups define the adapter acceptance scope. The local dispatcher harness
now exercises their synthetic routes, with the limits recorded in the
[feasibility result](fcitx5-validation.md#fcitx5-local-feasibility-result). Real frontend/desktop
acceptance is incomplete; limited user observations are recorded in the
[Fcitx5 validation guide](fcitx5-validation.md). Core tests also cover raw editing, cancel/reset,
independent contexts and the four normalized keys. The harness records ordered
preedit/commit/application-key effects using only synthetic text such as
`ki` → কি or `o` plus a backtick → empty output, comparing exact strings and counts.

| Case | Required observation |
| --- | --- |
| Escape with `ki`, invisible input, then idle Escape | Commit কি and consume once; invisible input skips an empty commit; idle press forwards |
| Arrow/Home/End/Page/Delete/Insert, including Shift/Ctrl variants | Clear preedit, commit কি once, forward unchanged action once |
| Tab, Shift+Tab and Ctrl+C/V/X/A/Z | Commit before the app action; next text starts fresh |
| Ctrl+Backspace versus Ctrl+Shift+Backspace | Exact Ctrl deletes pending input; extra Shift commits and forwards |
| Space/Enter, keypad Enter and modified variants | One commit then one unchanged key; no added space/newline |
| Shift/Ctrl/Alt/Super press and release without another key | Preserve pending word; no commit or inserted modifier |
| Text and editing-key releases, with active and idle buffers | No second insertion, edit, commit or boundary action |
| Held text/Backspace/Ctrl+Backspace/Escape/Enter | One action per delivered press; empty-state behavior re-evaluated |
| Case-sensitive text, Caps/Num Lock, AltGr, dead/compose sequences | Correct resolved text; no shortcut modifier stripped into text |
| Invisible pending input plus any commit boundary | Clear state, skip empty framework commit, forward once |
| Focus loss or switch with addon-owned commit | Commit once to original context if valid; all local state empty |
| Focus loss with frontend-owned commit, followed by reset/deactivate | No duplicate commit; all local state empty |
| Reset, destruction, unavailable commit target or restricted-field transition | Discard; no stale commit into another field |
| Focus A → B → A and duplicate lifecycle callbacks | No cross-context text or restored raw buffer; next `i` is ই |
| Pointer motion, preedit click, relocation before/after reset | Motion preserves; valid pre-relocation commit or post-relocation discard |

## Fcitx5 interoperability boundary

**Interoperability contract:**

- Rust allocates/frees the handle; C++ never constructs or deletes its contents.
  Calls use exclusive, non-reentrant access on Fcitx's event thread. Null handles
  are accepted only as an error/no-op; fabricated or freed pointers are invalid.
- Insertion passes a Unicode scalar (`uint32_t`), rejecting surrogates/out-of-range
  values. Rust returns UTF-8 pointer/byte-length spans, without a NUL terminator.
  They are borrowed until the next action/free; C++ copies both spans before
  calling back into Fcitx. Empty spans are never dereferenced. Preedit cursor
  offsets use UTF-8 bytes, including six bytes for synthetic `কি`.
- Status 0 means success; 1 means invalid argument without mutation; 2 means a
  caught Rust panic with state discarded. The separate crate contains the unsafe
  pointer operations; `jong-bangla-core` continues to forbid unsafe code. Rust
  unwinding is caught; payload cleanup is attempted once inside another unwind
  guard. If that destructor panics, its replacement payload is forgotten, avoiding
  recursive cleanup. OOM/abort, invalid pointers, double panics during unwinding
  and a panic in the runtime hook cannot be recovered. The
  [failure-policy review](#c-abi-caught-panic-policy-review) records the evidence
  and tradeoff. Do not build this boundary with `panic=abort` if unwinding
  containment is required. The normal Cargo profiles use unwinding.
- C++ catches exceptions in engine callbacks, discards state and clears preedit
  where possible. An internal key-processing failure consumes that event rather
  than replaying a possibly applied edit. The factory returns null on failure.
  Neither boundary nor addon logs or persists typed text. Standard runtime panic
  diagnostics are not replaced with a process-global panic hook.

## C-ABI caught-panic policy review

**Changed and checked on 2026-10-30:** the private Rust boundary now attempts to
drop each caught panic payload once, inside a second `catch_unwind`. Ordinary
heap-owning payloads are released. If their destructor panics, the replacement
payload is deliberately forgotten without another cleanup attempt. The operation
then discards partial session state and returns status 2 with empty/null output;
the next insertion starts a fresh word. Allocation failure still returns null
only when it unwinds; process-aborting allocation failures cannot be caught.
No public failure-injection action, dependency or core behavior was added.

**Decision and tradeoff:** replace the unconditional payload leak with one guarded
cleanup attempt. The current session owns ordinary Rust strings, and the boundary
accepts no foreign panic payload/callback. Running arbitrary custom destructors
can nevertheless do more than unwind once: nested cleanup panics can abort, and
a destructor can retain memory, block or explicitly terminate the process. The
new policy favors ordinary cleanup while preserving the non-unwinding C ABI;
it does not promise universal failure recovery. Repeatedly dropping replacement
payloads would allow unbounded cleanup chains. Retaining the replacement bounds
our cleanup attempts, not its allocation size or the destructor's execution time.
Production code leaves the process-global panic hook untouched. Rust documents
[payload-drop panics and unwind-only catching](https://doc.rust-lang.org/stable/std/panic/fn.catch_unwind.html)
and the [global hook's execution before unwinding](https://doc.rust-lang.org/stable/std/panic/fn.set_hook.html).

**Focused evidence:** Linux-only
[`panic_tests.rs`](../adapters/fcitx5/ffi/src/panic_tests.rs) runs five scenarios in
separate copies of the Rust test executable, behind a test-only `extern "C"`
function using the production containment/operation helpers. Core dumps are
disabled only in each child; aborts and the test hook do not affect the parent,
Fcitx or the desktop. There is no injection entry point in the shipped ABI.

| Injected failure | Observed result |
| --- | --- |
| Ordinary payload owning a 4,096-byte vector through `Arc` | Its weak reference can no longer be upgraded after recovery. Partial preedit/commit cleared; status 2, zero flags/lengths and null spans; next public insertion yields ই. |
| Primary destructor panics with a second destructor-panicking payload | Primary destructor runs exactly once and its 4,096-byte vector is released. Secondary destructor never runs and its 8,192-byte vector stays reachable through the deliberately forgotten payload. Same state/output recovery and fresh insertion pass. |
| Operation unwinds through another panicking destructor | Child terminates with SIGABRT and Rust's cleanup-panic diagnostic. |
| Caught payload's destructor and its field destructor both panic | Child terminates with SIGABRT and Rust's cleanup-panic diagnostic. This is an additional termination exposure of attempting arbitrary payload cleanup. |
| Process-global panic hook panics | Child terminates with SIGABRT and Rust's hook-panic diagnostic. |

The ordinary-ownership test first failed against the old policy because its
payload remained retained; all five scenarios pass after the change. The child
helper is marked ignored to prevent unselected standalone execution; the parent
test invokes it explicitly and checks successful child completion or the exact
abort signal plus the corresponding runtime diagnostic. These are ownership and
termination assertions, not new LeakSanitizer/RSS measurements. Actual Rust
accesses are not sanitizer-instrumented; OOM, invalid pointers, `panic=abort`,
every possible destructor and failures during session allocation/free are not
injected. The documented C ABI continues to prevent Rust unwinding into C, with
process termination on nonrecoverable paths. Older normal-path leak/resource
observations in the [measurement guide](performance.md) remain prior evidence
from their recorded source versions.
