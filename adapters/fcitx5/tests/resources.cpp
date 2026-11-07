// MIT. Linux/glibc synthetic resource probe; no desktop frontend or user input.
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <filesystem>
#include <iostream>
#include <malloc.h>
#include <memory>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

#include <fcitx-config/rawconfig.h>
#include <fcitx-utils/capabilityflags.h>
#include <fcitx-utils/key.h>
#include <fcitx/addonfactory.h>
#include <fcitx/addonmanager.h>
#include <fcitx/event.h>
#include <fcitx/globalconfig.h>
#include <fcitx/inputcontext.h>
#include <fcitx/inputcontextmanager.h>
#include <fcitx/inputmethodengine.h>
#include <fcitx/inputmethodentry.h>
#include <fcitx/inputmethodgroup.h>
#include <fcitx/inputmethodmanager.h>
#include <fcitx/inputpanel.h>
#include <fcitx/instance.h>
#include <fcitx/text.h>

using namespace fcitx;

namespace {
void require(bool condition, const char *message) {
  if (!condition) {
    throw std::runtime_error(message);
  }
}

// Deliberately independent of the correctness harness: no stored effects,
// committed document, desktop services or UI. Both modes use this same binary.
class Sandbox {
public:
  Sandbox() {
    char pattern[] = "/tmp/jong-fcitx5-resources-XXXXXX";
    const auto path = mkdtemp(pattern);
    require(path != nullptr, "create resource sandbox");
    root_ = path;
    for (const auto *name : {"config", "cache", "runtime"}) {
      std::filesystem::create_directory(root_ / name);
    }
    std::filesystem::permissions(root_ / "runtime",
                                 std::filesystem::perms::owner_all);
    env("XDG_CONFIG_HOME", (root_ / "config").string());
    env("XDG_CACHE_HOME", (root_ / "cache").string());
    env("XDG_RUNTIME_DIR", (root_ / "runtime").string());
    env("XDG_DATA_HOME", JONG_HARNESS_DATA);
    env("SKIP_FCITX_PATH", "1");
    env("SKIP_FCITX_SYSTEM_PATH", "1");
    env("SKIP_FCITX_USER_PATH", "0");
    env("FCITX_NO_PREEDIT_APPS", "");
  }
  ~Sandbox() {
    std::error_code error;
    std::filesystem::remove_all(root_, error);
  }

private:
  static void env(const char *name, const std::string &value) {
    require(setenv(name, value.c_str(), 1) == 0, "set isolated environment");
  }
  std::filesystem::path root_;
};

class NullEngine final : public InputMethodEngine {
public:
  void keyEvent(const InputMethodEntry &, KeyEvent &) override {}
};
class NullFactory final : public AddonFactory {
public:
  AddonInstance *create(AddonManager *) override { return new NullEngine; }
};

class Context final : public InputContext {
public:
  Context(Instance &instance, bool jong)
      : InputContext(instance.inputContextManager(), "jong-resource"),
        jong_(jong) {
    try {
      setCapabilityFlags(CapabilityFlags(CapabilityFlag::Preedit) |
                         CapabilityFlag::FormattedPreedit);
      created();
      focusIn();
      instance.setCurrentInputMethod(this, jong ? "jong-bangla" : "keyboard-us",
                                     true);
      require(instance.inputMethod(this) ==
                  (jong ? "jong-bangla" : "keyboard-us"),
              "activate requested engine");
    } catch (...) {
      destroy();
      throw;
    }
  }
  ~Context() override { destroy(); }
  const char *frontend() const override { return "jong-resource"; }

  void send(Key key, bool expectedConsumed) {
    KeyEvent event(this, key, false, 73);
    require(keyEvent(event) == (jong_ && expectedConsumed),
            "unexpected key disposition");
  }
  void type(const std::vector<Key> &keys) {
    for (const auto &key : keys) {
      send(key, true);
    }
  }
  void clear() {
    const bool active = !inputPanel().clientPreedit().empty();
    send(Key(FcitxKey_BackSpace, KeyState::Ctrl), active);
    require(inputPanel().clientPreedit().empty(), "clear preedit");
  }
  void pending() {
    require(inputPanel().clientPreedit().empty() != jong_,
            "expected pending preedit only in Jong mode");
  }

private:
  void commitStringImpl(const std::string &text) override {
    require(!text.empty(), "nonempty synthetic commit");
    ++commits_;
  }
  void deleteSurroundingTextImpl(int, unsigned int) override {
    throw std::runtime_error("unexpected surrounding text deletion");
  }
  void forwardKeyImpl(const ForwardKeyEvent &) override {
    throw std::runtime_error("unexpected explicit key forwarding");
  }
  void updatePreeditImpl() override { ++preedits_; }
  // Fixed-size counters, not a document or per-event allocation in the sink.
  size_t commits_ = 0;
  size_t preedits_ = 0;
  bool jong_;
};

std::vector<Key> keys(std::u32string_view text, size_t length = 0) {
  std::vector<Key> result;
  if (!length) {
    length = text.size();
  }
  result.reserve(length);
  for (size_t i = 0; i < length; ++i) {
    result.emplace_back(Key::keySymFromUnicode(text[i % text.size()]));
  }
  return result;
}

constexpr auto mixed = U"kShmri12`aকি🙂";

// Parent reads /proc while this process waits. No in-process /proc parsing or
// heap walk pollutes the measured RSS. No malloc_trim: allocator caching is
// real.
void checkpoint(const char *phase) {
  const auto heap = mallinfo2();
  std::printf("%s,%zu,%zu\n", phase, heap.uordblks + heap.hblkhd,
              heap.arena + heap.hblkhd);
  std::fflush(stdout);
  require(std::getchar() == '\n', "checkpoint acknowledgement missing");
}

void memory(Instance &instance, bool jong) {
  // Construct the identical event storage before any snapshot in both modes.
  const auto shortKeys = keys(mixed);
  const auto longKeys = keys(mixed, 8192);
  auto context = std::make_unique<Context>(instance, jong);
  checkpoint("idle");
  context->type(shortKeys);
  context->pending();
  checkpoint("short_pending");
  context->clear();
  checkpoint("short_cleared");
  context->type(longKeys);
  context->pending();
  checkpoint("long_pending");
  context->clear();
  checkpoint("long_cleared");
  for (unsigned batch = 0; batch < 2; ++batch) {
    for (unsigned i = 0; i < 1000; ++i) {
      context->focusIn();
      context->type(shortKeys);
      context->send(Key(FcitxKey_space), false);
      Context fresh(instance, jong);
      fresh.type(shortKeys);
      fresh.clear();
    }
    context->focusIn();
    checkpoint(batch == 0 ? "sessions_1000" : "sessions_2000");
  }
  context.reset();
  checkpoint("context_destroyed");
}

template <typename Work>
void measure(const char *name, size_t scalars, size_t actions, bool smoke,
             Work work) {
  using Clock = std::chrono::steady_clock;
  size_t iterations = 1;
  for (;;) {
    const auto start = Clock::now();
    for (size_t i = 0; i < iterations; ++i) {
      work();
    }
    if (smoke || Clock::now() - start >= std::chrono::milliseconds(5) ||
        iterations >= (1U << 20)) {
      break;
    }
    iterations *= 2;
  }
  std::array<double, 31> samples{};
  const size_t count = smoke ? 3 : samples.size();
  for (size_t index = 0; index < count; ++index) {
    const auto start = Clock::now();
    for (size_t i = 0; i < iterations; ++i) {
      work();
    }
    samples[index] =
        std::chrono::duration<double, std::nano>(Clock::now() - start).count() /
        static_cast<double>(iterations) / static_cast<double>(actions);
  }
  std::sort(samples.begin(), samples.begin() + count);
  std::printf("%s,%zu,%zu,%zu,%.1f,%.1f,%.1f\n", name, scalars, actions,
              iterations, samples[0], samples[count / 2],
              samples[(count * 95 + 99) / 100 - 1]);
}

void lifecycle(Instance &instance, bool jong, const std::vector<Key> &events) {
  Context context(instance, jong);
  context.type(events);
  context.clear();
  context.type(events); // Destroy with pending input.
}

void timing(Instance &instance, bool jong, bool smoke) {
  Context context(instance, jong);
  std::puts(
      "workload,raw_scalars,actions_per_iteration,iterations,min_ns,median_ns,"
      "p95_ns");
  for (const auto &[name, word] :
       std::array<std::pair<const char *, std::u32string_view>, 4>{
           {{"type_commit:ami", U"ami"},
            {"type_commit:bangla", U"bangla"},
            {"type_commit:shadhInota", U"shadhInota"},
            {"type_commit:mixed", mixed}}}) {
    const auto events = keys(word);
    measure(name, events.size(), events.size() + 1, smoke, [&] {
      context.type(events);
      context.send(Key(FcitxKey_space), false);
    });
    require(context.inputPanel().clientPreedit().empty(),
            "commit cleared word");
  }
  for (const size_t length : {32, 128, 1024, 8192}) {
    if (smoke && length > 128) {
      continue;
    }
    context.type(keys(mixed, length)); // Setup deliberately outside timer.
    context.pending();
    measure("insert_backspace_pair", length, 2, smoke, [&] {
      context.send(Key(FcitxKey_i), true);
      context.send(Key(FcitxKey_BackSpace), true);
    });
    context.clear();
  }
  const auto events = keys(mixed);
  // One action is a whole create/type/clear/type/destroy cycle, not a key.
  measure("context_lifecycle", events.size(), 1, smoke,
          [&] { lifecycle(instance, jong, events); });
}
} // namespace

int main(int argc, char **argv) {
  try {
    require(JONG_RESOURCE_RELEASE, "configure with -DCMAKE_BUILD_TYPE=Release");
    require((argc == 3 ||
             (argc == 4 && std::string_view(argv[3]) == "--smoke" &&
              std::string_view(argv[2]) == "timing")) &&
                (std::string_view(argv[1]) == "baseline" ||
                 std::string_view(argv[1]) == "jong") &&
                (std::string_view(argv[2]) == "memory" ||
                 std::string_view(argv[2]) == "timing" ||
                 std::string_view(argv[2]) == "allocations"),
            "usage: jong-fcitx5-resources baseline|jong memory|timing|allocations [--smoke]");
    const bool jong = std::string_view(argv[1]) == "jong";
    // Prime stdio before the first heap sample. No buffered phase history.
    require(std::setvbuf(stdout, nullptr, _IONBF, 0) == 0, "unbuffer stdout");
    require(std::setvbuf(stdin, nullptr, _IONBF, 0) == 0, "unbuffer stdin");
    Sandbox sandbox;
    char program[] = "jong-fcitx5-resources";
    char disable[] = "--disable=all";
    char enableJong[] = "--enable=jong-bangla,jong-harness-null";
    char enableNull[] = "--enable=jong-harness-null";
    char quiet[] = "--verbose=*=0";
    char *args[] = {program, disable, jong ? enableJong : enableNull, quiet};
    NullFactory factory;
    StaticAddonRegistry registry{{"jong-harness-null", &factory}};
    Instance instance(4, args);
    require(instance.initialized(), "construct dispatcher");
    instance.addonManager().registerDefaultLoader(&registry);
    instance.initialize();
    RawConfig config;
    for (const auto *name :
         {"TriggerKeys", "AltTriggerKeys", "ActivateKeys", "DeactivateKeys",
          "EnumerateForwardKeys", "EnumerateBackwardKeys",
          "EnumerateGroupForwardKeys", "EnumerateGroupBackwardKeys",
          "TogglePreedit"}) {
      config[std::string("Hotkey/") + name].setValue("");
    }
    instance.globalConfig().load(config, true);
    InputMethodGroup group("Jong resource");
    group.setDefaultLayout("us");
    group.inputMethodList().emplace_back("keyboard-us");
    if (jong) {
      group.inputMethodList().emplace_back("jong-bangla");
    }
    group.setDefaultInputMethod(jong ? "jong-bangla" : "keyboard-us");
    instance.inputMethodManager().addEmptyGroup(group.name());
    instance.inputMethodManager().setGroup(group);
    instance.inputMethodManager().setCurrentGroup(group.name());
    if (std::string_view(argv[2]) == "memory") {
      memory(instance, jong);
    } else if (std::string_view(argv[2]) == "timing") {
      timing(instance, jong, argc == 4);
    } else {
      const auto events = keys(mixed);
      for (unsigned i = 0; i < 1000; ++i) {
        lifecycle(instance, jong, events);
      }
    }
    bool sawJong = false;
    bool sawNull = false;
    for (const auto &name : instance.addonManager().loadedAddonNames()) {
      require(name == "jong-harness-null" || (jong && name == "jong-bangla"),
              "unexpected desktop addon");
      sawJong |= name == "jong-bangla";
      sawNull |= name == "jong-harness-null";
    }
    require(sawJong == jong && sawNull, "verify loaded baseline/Jong addons");
    return 0;
  } catch (const std::exception &error) {
    std::cerr << "Resource probe failed: " << error.what() << '\n';
    return 1;
  }
}
