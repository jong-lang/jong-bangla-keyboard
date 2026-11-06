// MIT. Synthetic C-ABI lifecycle stress; no frontend or desktop configuration.
#include "../../ffi/jong.h"
#include <cstdlib>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string_view>

namespace {
using Session = std::unique_ptr<JongSession, decltype(&jong_session_free)>;

JongResult action(JongSession *session, uint32_t kind, uint32_t scalar = 0) {
  auto result = jong_session_action(session, kind, scalar);
  if (result.status != 0) {
    throw std::runtime_error("synthetic action failed");
  }
  return result;
}

void type(JongSession *session) {
  for (const char32_t key : std::u32string_view(U"kShmri12`aকি🙂")) {
    action(session, JongInsert, key);
  }
}

// A lost Rust handle is the detector's positive control. Keep the pointer off
// the caller's stack so conservative stack scanning does not retain it.
[[gnu::noinline]] void leakControl() {
  auto *session = jong_session_new();
  if (!session) {
    throw std::runtime_error("allocate leak control");
  }
  type(session);
  action(session, JongCommit);
  type(session);
  // Intentionally omit jong_session_free, only with --leak-control.
}

void cycle(JongSession *session, unsigned index) {
  type(session);
  action(session, JongBackspace);
  action(session, JongInsert, U'i');
  constexpr uint32_t endings[] = {JongSpace,  JongEnter, JongCommit,
                                  JongCancel, JongReset, JongCtrlBackspace,
                                  JongEscape};
  auto result = action(session, endings[index % 7]);
  if (result.active || result.preedit_len) {
    throw std::runtime_error("lifecycle failed to clear active input");
  }
  // Invalid scalars/actions must not disturb or allocate new live state.
  if (jong_session_action(session, JongInsert, 0xd800).status != 1 ||
      jong_session_action(session, 99, 0).status != 1) {
    throw std::runtime_error("invalid arguments accepted");
  }
}
} // namespace

int main(int argc, char **argv) {
  try {
    if (argc == 2 && std::string_view(argv[1]) == "--leak-control") {
      leakControl();
      std::cout
          << "Intentional Rust session leak; detector must fail at exit\n";
      return 0;
    }
    if (argc != 1) {
      throw std::runtime_error("usage: jong-ffi-memory [--leak-control]");
    }
    {
      Session reused(jong_session_new(), jong_session_free);
      if (!reused) {
        throw std::runtime_error("allocate reused session");
      }
      for (unsigned i = 0; i < 10000; ++i) {
        cycle(reused.get(), i);
        Session fresh(jong_session_new(), jong_session_free);
        if (!fresh) {
          throw std::runtime_error("allocate fresh session");
        }
        cycle(fresh.get(), i);
        if (i % 2 == 0) {
          type(fresh.get()); // Destruction with pending preedit.
        }
      }
      // Exercise a larger live raw allocation before destruction as well.
      for (unsigned i = 0; i < 1024; ++i) {
        action(reused.get(), JongInsert, U'k');
      }
    }
    jong_session_free(nullptr);
    std::cout << "20000 lifecycle cycles; 10001 sessions freed\n";
    return 0;
  } catch (const std::exception &error) {
    std::cerr << "Memory workload failed: " << error.what() << '\n';
    return 1;
  }
}
