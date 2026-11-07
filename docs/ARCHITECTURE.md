# Architecture

The reusable Rust core owns transliteration and composition. Platform adapters
translate native events into core operations and apply the resulting actions.
Engineering rules and enforcement status are in
[CONTRIBUTING.md](../CONTRIBUTING.md#engineering-standards).

## Code map

| Location | Responsibility |
| --- | --- |
| [src/transliteration/](../src/transliteration/) | Phonetic conversion, including context, case, symbols, and following-r rules |
| [src/composition.rs](../src/composition.rs) | Editable raw input, preedit, commit, cancellation, and normalized editing keys |
| [adapters/fcitx5/ffi/](../adapters/fcitx5/ffi/) | Rust C ABI and session ownership around the core |
| [adapters/fcitx5/addon.cpp](../adapters/fcitx5/addon.cpp) | Fcitx5 keys, input contexts, preedit UI, and application commits |

## Data flow

A native key event reaches the Fcitx5 C++ addon. The addon translates it into an
action, calls the Rust FFI, and receives preedit, optional committed text, and
whether to consume the key. It copies the returned text before framework calls,
publishes preedit, and commits text through Fcitx5. Unconsumed keys remain for
the framework and application to handle.

Each Fcitx5 input context owns a separate session. Within it, `Composition`
stores only the active raw input and converted preedit. Insertion and Backspace
recompute conversion from raw input; deletion removes a Unicode scalar rather
than a byte of Bangla output. Composition does not own platform events or UI.

`transliterate(&str)` provides conversion without a composition session.
`CompositionKey` and `KeyEffect` express shared editing behavior without Fcitx5
types. Keep Bangla output fixes in the core, not in native glue.

## FFI boundary

The Rust FFI builds as a static library for the C++ addon. Its C ABI is private
to this adapter, not a promised cross-platform or stable public interface.
[jong.h](../adapters/fcitx5/jong.h) defines actions, statuses, and the contract:

- Rust allocates each opaque session; C++ owns its handle and frees it exactly
  once through the Rust destructor. A null handle may be freed safely.
- Calls on a session must not overlap or reenter. A non-null pointer must be
  valid and uniquely owned or borrowed for the operation.
- Results borrow UTF-8 byte spans, with explicit lengths and no NUL terminator.
  Copy successful results before the next action or destruction. Do not
  dereference empty spans or retain their pointers.
- Invalid arguments return an error without changing composition. A caught
  Rust panic clears composition and returns an error. The addon resets state
  and UI on failure rather than allowing C++ exceptions to escape callbacks.

Panic containment does not recover from aborts or invalid pointers. Exceptional
panic-payload cleanup can retain a replacement allocation, as described in the
header. It is not a general guarantee of leak freedom or crash recovery.

## Boundaries and decisions

The core has no platform dependencies and forbids unsafe code. Its required
contract is deterministic processing without I/O or global state. Necessary
unsafe operations belong to the FFI layer, with explicit safety explanations.

Keep per-keystroke work local and allocation-light. Do not add services,
dictionaries, prediction, or autocorrection to deterministic transliteration.
Reuse composition behavior for future adapters. Choose native bindings when
each platform is implemented; do not generalize a platform framework early.
