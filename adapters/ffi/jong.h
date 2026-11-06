// MIT. Private C ABI for the experimental Linux adapters; not a stable public
// API.
#ifndef JONG_FFI_H
#define JONG_FFI_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct JongSession JongSession;
typedef struct JongResult {
  uint32_t status; // 0 success, 1 invalid argument, 2 caught Rust panic
  uint32_t consumed;
  uint32_t active; // raw input exists, even if preedit is empty
  const uint8_t *preedit;
  size_t preedit_len;
  const uint8_t *committed;
  size_t committed_len;
} JongResult;

enum JongAction {
  JongInsert = 0,
  JongBackspace = 1,
  JongCtrlBackspace = 2,
  JongSpace = 3,
  JongEnter = 4,
  JongCommit = 5,
  JongCancel = 6,
  JongReset = 7,
  JongEscape = 8, // Commit and consume only while raw input is active.
};

// Rust owns the allocation. Free exactly once; null is permitted. No concurrent
// or reentrant calls on a handle. Output spans are borrowed, UTF-8,
// byte-counted, not NUL-terminated; copy before the next action/free. Never
// dereference an empty span. Only use spans on success. Invalid action/scalar
// leaves state unchanged; caught panic clears state. Rust attempts payload
// cleanup once; if cleanup panics, its replacement payload is retained.
// OOM/abort/invalid pointers, panicking hooks and double panics during cleanup
// cannot recover.
JongSession *jong_session_new(void);
void jong_session_free(JongSession *session);
JongResult jong_session_action(JongSession *session, uint32_t action,
                               uint32_t scalar);

#ifdef __cplusplus
}
#endif
#endif
