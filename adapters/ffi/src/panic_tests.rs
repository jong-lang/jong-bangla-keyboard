//! Failure injection stays in the test binary; no public ABI injection action.

use super::*;
use std::os::unix::process::ExitStatusExt;
use std::panic::panic_any;
use std::process::Command;
use std::sync::Arc;
use std::sync::atomic::{AtomicUsize, Ordering};

struct DropPanic {
    _heap: Arc<Vec<u8>>,
    drops: Arc<AtomicUsize>,
    replacement: Option<Box<DropPanic>>,
}

impl Drop for DropPanic {
    fn drop(&mut self) {
        self.drops.fetch_add(1, Ordering::SeqCst);
        if let Some(replacement) = self.replacement.take() {
            panic_any(replacement);
        }
        panic!("synthetic payload destructor failure");
    }
}

fn assert_recovery(session: &mut JongSession, result: JongResult) {
    assert_eq!(result.status, PANIC);
    assert_eq!((result.consumed, result.active), (0, 0));
    assert!(result.preedit.is_null());
    assert!(result.committed.is_null());
    assert_eq!((result.preedit_len, result.committed_len), (0, 0));
    assert!(!session.word.is_active());
    assert!(session.word.preedit().is_empty());
    assert!(session.committed.is_empty());
    // SAFETY: this stack-owned session is live and exclusively borrowed.
    let result = unsafe { jong_session_action(session, 0, 'i' as u32) };
    assert_eq!(super::tests::strings(&result), ("ই".into(), "".into()));
}

fn heap_payload() {
    let heap = Arc::new(vec![0_u8; 4096]);
    let weak = Arc::downgrade(&heap);
    let mut session = JongSession {
        committed: "synthetic old commit".into(),
        ..JongSession::default()
    };
    let result = operate(&mut session, |session| {
        session.word.insert('k');
        session.committed = "synthetic partial commit".into();
        panic_any(heap);
    });
    assert!(weak.upgrade().is_none(), "ordinary payload was retained");
    assert_recovery(&mut session, result);
}

fn destructor_payload() {
    let primary = Arc::new(vec![0_u8; 4096]);
    let primary_weak = Arc::downgrade(&primary);
    let secondary = Arc::new(vec![0_u8; 8192]);
    let secondary_weak = Arc::downgrade(&secondary);
    let primary_drops = Arc::new(AtomicUsize::new(0));
    let secondary_drops = Arc::new(AtomicUsize::new(0));
    let payload = DropPanic {
        _heap: primary,
        drops: primary_drops.clone(),
        replacement: Some(Box::new(DropPanic {
            _heap: secondary,
            drops: secondary_drops.clone(),
            replacement: None,
        })),
    };
    let mut session = JongSession::default();
    let result = operate(&mut session, |session| {
        session.word.insert('k');
        session.committed = "synthetic partial commit".into();
        panic_any(payload);
    });
    assert_eq!(primary_drops.load(Ordering::SeqCst), 1);
    assert!(primary_weak.upgrade().is_none());
    // The replacement would panic again on drop. It must remain untouched;
    // process isolation keeps this deliberate leak out of the parent runner.
    assert_eq!(secondary_drops.load(Ordering::SeqCst), 0);
    assert!(secondary_weak.upgrade().is_some());
    assert_recovery(&mut session, result);
}

// Test the same operation wrapper behind an actual non-unwinding C ABI. If an
// unexpected panic escapes, the child aborts and the parent reports the failure.
extern "C" fn failure_probe(mode: u32) {
    match mode {
        0 => heap_payload(),
        1 => destructor_payload(),
        2 => {
            contain_panic(|| {
                let _during_unwind = DropPanic {
                    _heap: Arc::new(vec![0_u8; 4096]),
                    drops: Arc::default(),
                    replacement: None,
                };
                panic!("synthetic initial failure");
            });
        }
        3 => {
            struct DoubleDrop {
                _during_unwind: DropPanic,
            }
            impl Drop for DoubleDrop {
                fn drop(&mut self) {
                    panic!("synthetic outer destructor failure");
                }
            }
            contain_panic(|| {
                panic_any(DoubleDrop {
                    _during_unwind: DropPanic {
                        _heap: Arc::new(vec![0_u8; 4096]),
                        drops: Arc::default(),
                        replacement: None,
                    },
                });
            });
        }
        4 => {
            std::panic::set_hook(Box::new(|_| panic!("synthetic hook failure")));
            contain_panic(|| panic!("synthetic initial failure"));
        }
        _ => unreachable!(),
    }
}

#[test]
#[ignore = "run by panic_policy_subprocesses with a private environment selector"]
fn panic_policy_child() {
    let mode = std::env::var("JONG_TEST_PANIC_MODE")
        .expect("subprocess selector")
        .parse()
        .unwrap();
    failure_probe(mode);
}

#[test]
fn panic_policy_subprocesses() {
    for (mode, aborts, diagnostic) in [
        (0, false, ""),
        (1, false, ""),
        (2, true, "panic in a destructor during cleanup"),
        (3, true, "panic in a destructor during cleanup"),
        (4, true, "thread panicked while processing panic"),
    ] {
        // Disable core dumps in this child only. Arguments are passed verbatim,
        // not interpolated into shell code. No desktop daemon/settings touched.
        let output = Command::new("sh")
            .args(["-c", "ulimit -c 0; exec \"$@\"", "jong-panic-test"])
            .arg(std::env::current_exe().unwrap())
            .args([
                "--exact",
                "panic_tests::panic_policy_child",
                "--ignored",
                "--nocapture",
            ])
            .env("JONG_TEST_PANIC_MODE", mode.to_string())
            .env("RUST_BACKTRACE", "0")
            .output()
            .unwrap();
        let stderr = String::from_utf8_lossy(&output.stderr);
        if aborts {
            assert_eq!(output.status.signal(), Some(6), "mode {mode}: {stderr}");
            assert!(stderr.contains(diagnostic), "mode {mode}: {stderr}");
        } else {
            assert!(output.status.success(), "mode {mode}: {stderr}");
            assert!(String::from_utf8_lossy(&output.stdout).contains("1 passed"));
        }
    }
}
