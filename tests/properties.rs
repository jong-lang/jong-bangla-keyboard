//! Bounded property checks over authored fragments, independent of scanner rules.
use jong_bangla_core::{Composition, CompositionKey, transliterate};

fn corpus() -> Vec<String> {
    // Concatenation intentionally permits matches to cross fragment boundaries.
    let fragments = [
        "a", "i", "o", "O", "k", "h", "r", "rr", "ng", "Ng", "Sh", "N", "y", "Z", "1", ".", "`",
        "t``", "🙂", "ক", "İ", "\u{0301}", "\u{200D}",
    ];
    let mut inputs = vec![String::new()];
    for left in fragments {
        for middle in fragments {
            for right in ["", "a", "r", "`"] {
                inputs.push(format!("{left}{middle}{right}"));
            }
        }
    }
    inputs
}

fn insert(word: &mut Composition, raw: &str) {
    for ch in raw.chars() {
        assert!(word.insert(ch));
    }
}

#[test]
fn conversion_is_deterministic_and_independent_of_call_order() {
    let inputs = corpus();
    let expected: Vec<_> = inputs.iter().map(|raw| transliterate(raw)).collect();
    for (raw, expected) in inputs.iter().zip(&expected).rev() {
        // Force unrelated vowel, reph, escape and Unicode contexts between calls.
        let _ = transliterate("rrkShmrri`🙂oZ");
        assert_eq!(&transliterate(raw), expected, "input: {raw:?}");
    }
}

#[test]
fn editing_restores_every_raw_scalar_prefix() {
    for raw in corpus() {
        let mut word = Composition::new();
        let mut prefixes = vec![String::new()];
        let mut prefix = String::new();
        for ch in raw.chars() {
            prefix.push(ch);
            assert!(word.insert(ch));
            assert_eq!(word.preedit(), transliterate(&prefix), "input: {prefix:?}");
            prefixes.push(prefix.clone());
        }
        prefixes.pop();
        for prefix in prefixes.iter().rev() {
            assert!(word.backspace());
            assert_eq!(word.preedit(), transliterate(prefix), "input: {prefix:?}");
            assert_eq!(word.is_active(), !prefix.is_empty());
        }
        assert!(!word.backspace());
        assert_eq!(word.commit(), None);
    }
}

#[test]
fn finalization_removes_history_and_keeps_other_sessions_independent() {
    for raw in corpus() {
        for finish in 0..6 {
            let mut word = Composition::new();
            let mut other = Composition::new();
            insert(&mut word, &raw);
            insert(&mut other, "rrq");
            match finish {
                0 => word.reset(),
                1 => assert_eq!(word.cancel(), !raw.is_empty()),
                2 => assert_eq!(word.delete_word(), !raw.is_empty()),
                3 => assert_eq!(
                    word.commit(),
                    (!raw.is_empty()).then(|| transliterate(&raw))
                ),
                4 | 5 => {
                    let key = if finish == 4 {
                        CompositionKey::Space
                    } else {
                        CompositionKey::Enter
                    };
                    let effect = word.handle_key(key);
                    assert!(!effect.consumed);
                    assert_eq!(
                        effect.committed,
                        (!raw.is_empty()).then(|| transliterate(&raw))
                    );
                }
                _ => unreachable!(),
            }
            assert!(!word.is_active());
            assert_eq!(word.preedit(), "");
            // Reset is idempotent, and an invisible escape also starts afresh.
            word.reset();
            word.reset();
            for suffix in ["i", "rri", "`", "t``", "🙂"] {
                insert(&mut word, suffix);
                assert_eq!(word.preedit(), transliterate(suffix));
                word.reset();
            }
            assert_eq!(other.commit().as_deref(), Some("র্ক"));
        }
    }
}
