//! Deterministic Bangla phonetic transliteration with no external dependencies.
//!
//! Converts supported phonetic sequences and ASCII digits, preserving unmatched
//! Unicode characters. A platform-independent composition controller supports
//! editable preedit and normalized editing keys. Compatibility with Avro is
//! partial. Experimental Fcitx5 event translation lives in a separate adapter;
//! desktop integration has limited manual smoke evidence and remains experimental.
//!
//! See the repository's [coverage overview] and [behavior notes] for supported
//! rules, compatibility evidence, and limitations.
//!
//! [coverage overview]: https://github.com/jong-lang/jong-bangla-keyboard#current-status
//! [behavior notes]: https://github.com/jong-lang/jong-bangla-keyboard/blob/main/docs/FEATURES.md#typing-behavior
//!
//! ```
//! use jong_bangla_core::transliterate;
//!
//! assert_eq!(transliterate("kh12T"), "খ১২ট");
//! assert_eq!(transliterate("ami khani kia"), "আমি খানি কিয়া");
//! assert_eq!(transliterate("s sh S Sh"), "স শ শ ষ");
//! ```

mod composition;
mod transliteration;

pub use composition::{Composition, CompositionKey, KeyEffect};
pub use transliteration::transliterate;
