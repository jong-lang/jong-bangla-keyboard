//! Shared C ABI for the experimental Linux adapters. Pointer safety is confined here;
//! the reusable core still forbids unsafe code. See the crate’s `jong.h`.

use jong_bangla_core::{Composition, CompositionKey, KeyEffect};
use std::panic::{AssertUnwindSafe, catch_unwind};

#[cfg(all(test, target_os = "linux"))]
mod panic_tests;

const OK: u32 = 0;
const INVALID: u32 = 1;
const PANIC: u32 = 2;

/// Opaque, uniquely owned, single-threaded composition handle.
#[derive(Default)]
pub struct JongSession {
    word: Composition,
    committed: String,
}

/// Borrowed UTF-8 byte spans, valid until the next action or session destruction.
/// Empty spans must not be dereferenced; neither span is NUL-terminated.
#[repr(C)]
pub struct JongResult {
    pub status: u32,
    pub consumed: u32,
    pub active: u32,
    pub preedit: *const u8,
    pub preedit_len: usize,
    pub committed: *const u8,
    pub committed_len: usize,
}

impl JongResult {
    fn error(status: u32) -> Self {
        Self {
            status,
            consumed: 0,
            active: 0,
            preedit: std::ptr::null(),
            preedit_len: 0,
            committed: std::ptr::null(),
            committed_len: 0,
        }
    }
}

fn contain_panic<T>(f: impl FnOnce() -> T) -> Option<T> {
    match catch_unwind(AssertUnwindSafe(f)) {
        Ok(value) => Some(value),
        Err(payload) => {
            // Reclaim ordinary payloads, but contain a panic in their Drop too.
            // Do not recursively drop replacement payloads: arbitrary Drop code
            // can panic forever. This exceptional replacement remains leaked.
            if let Err(replacement) = catch_unwind(AssertUnwindSafe(|| drop(payload))) {
                std::mem::forget(replacement);
            }
            None
        }
    }
}

/// Allocates a handle, or returns null on a caught panic (OOM may abort).
#[unsafe(no_mangle)]
pub extern "C" fn jong_session_new() -> *mut JongSession {
    contain_panic(|| Box::into_raw(Box::<JongSession>::default())).unwrap_or(std::ptr::null_mut())
}

/// Frees the handle; null is a no-op. No callback or commit is performed.
///
/// # Safety
/// A non-null handle must come from `jong_session_new`, be exclusively owned,
/// and not have been freed. No borrowed output may be used after this call.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn jong_session_free(session: *mut JongSession) {
    if !session.is_null() {
        contain_panic(|| {
            // SAFETY: the caller transfers the unique allocation back to Rust.
            drop(unsafe { Box::from_raw(session) });
        });
    }
}

fn operate(session: &mut JongSession, f: impl FnOnce(&mut JongSession) -> bool) -> JongResult {
    session.committed.clear();
    let Some(consumed) = contain_panic(|| f(session)) else {
        // Never reuse partially mutated state after an internal failure.
        *session = JongSession::default();
        return JongResult::error(PANIC);
    };
    JongResult {
        status: OK,
        consumed: u32::from(consumed),
        active: u32::from(session.word.is_active()),
        preedit: session.word.preedit().as_ptr(),
        preedit_len: session.word.preedit().len(),
        committed: session.committed.as_ptr(),
        committed_len: session.committed.len(),
    }
}

/// Runs an action from `jong.h`; insertion takes one Unicode scalar value.
/// Invalid arguments return status 1 without mutating state. A caught panic
/// clears state and returns status 2. No input is logged by this crate.
///
/// # Safety
/// A non-null handle must be live and uniquely borrowed for this call. Calls on
/// one handle must not overlap or reenter. Copy output before the next action.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn jong_session_action(
    session: *mut JongSession,
    action: u32,
    scalar: u32,
) -> JongResult {
    if session.is_null() || action > 8 || (action == 0 && char::from_u32(scalar).is_none()) {
        return JongResult::error(INVALID);
    }
    // SAFETY: null is checked; validity and exclusive access are caller obligations.
    let session = unsafe { &mut *session };
    operate(session, |session| {
        let effect = match action {
            0 => return session.word.insert(char::from_u32(scalar).unwrap()),
            1 => session.word.handle_key(CompositionKey::Backspace),
            2 => session.word.handle_key(CompositionKey::CtrlBackspace),
            3 => session.word.handle_key(CompositionKey::Space),
            4 => session.word.handle_key(CompositionKey::Enter),
            5 => KeyEffect {
                consumed: false,
                committed: session.word.commit(),
            },
            6 => return session.word.cancel(),
            7 => {
                session.word.reset();
                return false;
            }
            8 => KeyEffect {
                consumed: session.word.is_active(),
                committed: session.word.commit(),
            },
            _ => unreachable!(),
        };
        session.committed = effect.committed.unwrap_or_default();
        effect.consumed
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    // Copy spans while the result's handle is still uniquely borrowed here.
    pub(super) fn strings(result: &JongResult) -> (String, String) {
        assert_eq!(result.status, OK);
        let copy = |ptr, len| {
            if len == 0 {
                return String::new();
            }
            // SAFETY: test callers keep the session alive without another action.
            String::from_utf8(unsafe { std::slice::from_raw_parts(ptr, len) }.to_vec()).unwrap()
        };
        (
            copy(result.preedit, result.preedit_len),
            copy(result.committed, result.committed_len),
        )
    }

    #[test]
    fn utf8_ownership_and_commit() {
        let session = jong_session_new();
        assert!(!session.is_null());
        // SAFETY: the handle is uniquely owned here until freed at the end.
        unsafe {
            jong_session_action(session, 0, 'k' as u32);
            let result = jong_session_action(session, 0, 'i' as u32);
            assert_eq!(strings(&result), ("কি".into(), "".into()));
            assert_eq!(result.preedit_len, 6);
            assert_eq!(result.active, 1);
            let result = jong_session_action(session, 3, 0);
            assert_eq!(strings(&result), ("".into(), "কি".into()));
            assert_eq!(result.consumed, 0);
            assert_eq!(result.active, 0);
            let result = jong_session_action(session, 5, 0);
            assert_eq!(strings(&result), ("".into(), "".into()));
            jong_session_free(session);
        }
    }

    #[test]
    fn invalid_arguments_preserve_state() {
        let session = jong_session_new();
        // SAFETY: null is supported; all non-null handles are live and unique.
        unsafe {
            assert_eq!(
                jong_session_action(std::ptr::null_mut(), 0, 0).status,
                INVALID
            );
            jong_session_free(std::ptr::null_mut());
            jong_session_action(session, 0, 'k' as u32);
            for (action, scalar) in [(0, 0xd800), (0, 0x110000), (9, 0)] {
                assert_eq!(jong_session_action(session, action, scalar).status, INVALID);
            }
            let result = jong_session_action(session, 5, 0);
            assert_eq!(strings(&result), ("".into(), "ক".into()));
            jong_session_free(session);
        }
    }

    #[test]
    fn internal_panic_discards_partial_state() {
        let mut session = JongSession::default();
        let result = operate(&mut session, |session| {
            session.word.insert('k');
            panic!("synthetic boundary failure");
        });
        assert_eq!(result.status, PANIC);
        assert!(!session.word.is_active());
        assert!(session.committed.is_empty());
        let result = operate(&mut session, |session| session.word.insert('i'));
        assert_eq!(strings(&result), ("ই".into(), "".into()));
    }
}
