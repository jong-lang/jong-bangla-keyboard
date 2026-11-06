// MIT. Synthetic strings only; loads the real addon into an isolated
// dispatcher.
#include <cstdlib>
#include <filesystem>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include <fcitx-config/rawconfig.h>
#include <fcitx-utils/capabilityflags.h>
#include <fcitx-utils/key.h>
#include <fcitx-utils/standardpaths.h>
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

void require(bool condition, const std::string &message) {
  if (!condition) {
    throw std::runtime_error(message);
  }
}

// Set paths before Fcitx's global StandardPaths is initialized. No desktop
// frontend, bus, display, daemon or real input-method configuration is loaded.
class Sandbox {
public:
  Sandbox(int argc, char **argv) {
    require(argc == 1 || (argc == 4 && std::string(argv[1]) == "--installed"),
            "usage: jong-fcitx5-harness [--installed PKG_DATA_DIR ADDON_DIR]");
    char pattern[] = "/tmp/jong-fcitx5-harness-XXXXXX";
    const auto path = mkdtemp(pattern);
    require(path != nullptr, "create harness sandbox");
    root_ = path;
    for (const auto &name : {"config", "cache", "runtime"}) {
      std::filesystem::create_directory(root_ / name);
    }
    std::filesystem::permissions(root_ / "runtime",
                                 std::filesystem::perms::owner_all);
    env("XDG_CONFIG_HOME", (root_ / "config").string());
    env("XDG_CACHE_HOME", (root_ / "cache").string());
    env("XDG_RUNTIME_DIR", (root_ / "runtime").string());
    env("XDG_DATA_HOME", JONG_HARNESS_DATA);
    env("FCITX_CONFIG_HOME", (root_ / "config" / "fcitx5").string());
    env("FCITX_CONFIG_DIRS", (root_ / "empty").string());
    env("FCITX_DATA_HOME",
        (std::filesystem::path(JONG_HARNESS_DATA) / "fcitx5").string());
    env("SKIP_FCITX_PATH", "1");
    env("SKIP_FCITX_SYSTEM_PATH", "1");
    env("SKIP_FCITX_USER_PATH", "0");
    env("FCITX_NO_PREEDIT_APPS", "");
    if (argc == 4) {
      // Supply only the two test registrations locally; Jong's metadata and
      // binary must both be discovered in the staged installation.
      const auto data = root_ / "data" / "fcitx5";
      std::filesystem::create_directories(data / "addon");
      std::filesystem::create_directories(data / "inputmethod");
      std::filesystem::copy_file(std::filesystem::path(JONG_HARNESS_DATA) /
                                     "fcitx5/addon/jong-harness-null.conf",
                                 data / "addon/jong-harness-null.conf");
      std::filesystem::copy_file(std::filesystem::path(JONG_HARNESS_DATA) /
                                     "fcitx5/inputmethod/keyboard-us.conf",
                                 data / "inputmethod/keyboard-us.conf");
      env("XDG_DATA_HOME", (root_ / "data").string());
      env("FCITX_DATA_HOME", data.string());
      env("XDG_DATA_DIRS", (root_ / "empty").string());
      env("FCITX_DATA_DIRS", argv[2]);
      env("FCITX_ADDON_DIRS", argv[3]);
      env("SKIP_FCITX_SYSTEM_PATH", "0");
      const auto dirs =
          StandardPaths::global().directories(StandardPathsType::Addon);
      require(dirs.size() == 1 && dirs.front() == argv[3],
              "search only the staged addon directory");
    }
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

void disableHotkeys(Instance &instance) {
  RawConfig config;
  for (const auto &name : {"TriggerKeys", "AltTriggerKeys", "ActivateKeys",
                           "DeactivateKeys", "EnumerateForwardKeys",
                           "EnumerateBackwardKeys", "EnumerateGroupForwardKeys",
                           "EnumerateGroupBackwardKeys", "TogglePreedit"}) {
    config[std::string("Hotkey/") + name].setValue("");
  }
  instance.globalConfig().load(config, true);
  require(instance.globalConfig().altTriggerKeys().empty() &&
              instance.globalConfig().triggerKeys().empty(),
          "disable harness global shortcuts");
}

struct Delivery {
  Key key;
  bool release;
  int time;
};

class Context final : public InputContext {
public:
  explicit Context(Instance &instance,
                   CapabilityFlags extra = CapabilityFlags())
      : InputContext(instance.inputContextManager(), "jong-synthetic"),
        instance_(instance) {
    try {
      setCapabilityFlags(CapabilityFlags(CapabilityFlag::Preedit) |
                         CapabilityFlag::FormattedPreedit | extra);
      created();
      focusIn();
      instance_.setCurrentInputMethod(this, "jong-bangla", true);
      require(instance_.inputMethod(this) == "jong-bangla",
              "activate local addon: " + instance_.inputMethod(this));
      clear();
    } catch (...) {
      destroy();
      throw;
    }
  }

  ~Context() override { close(); }
  const char *frontend() const override { return "jong-synthetic"; }

  void close() {
    if (!closed_) {
      destroy();
      closed_ = true;
    }
  }

  bool send(Key key, bool release = false, int time = 73) {
    KeyEvent event(this, key, release, time);
    const bool handled = keyEvent(event);
    if (!handled) {
      // The synthetic application receives an unhandled event once. An
      // explicit forward from the addon would be an additional delivery.
      deliver(key, release, time);
    }
    return handled;
  }

  void type(const std::string &ascii) {
    for (unsigned char ch : ascii) {
      require(send(Key(static_cast<KeySym>(ch))), "synthetic text consumed");
    }
  }

  void clear() {
    effects.clear();
    deliveries.clear();
  }

  void expect(std::vector<std::string> wanted) const {
    if (effects != wanted) {
      std::ostringstream message;
      message << "ordered effects differ; actual:";
      for (const auto &effect : effects) {
        message << " [" << effect << ']';
      }
      message << "; expected:";
      for (const auto &effect : wanted) {
        message << " [" << effect << ']';
      }
      throw std::runtime_error(message.str());
    }
  }

  void unchanged(Key key, bool release = false, int time = 73) const {
    require(deliveries.size() == 1, "one application key delivery");
    require(deliveries[0].key == key && deliveries[0].release == release &&
                deliveries[0].time == time,
            "original symbol/modifiers/release/time preserved");
  }

  std::vector<std::string> effects;
  std::vector<Delivery> deliveries;

private:
  void deliver(Key key, bool release, int time) {
    effects.push_back("key");
    deliveries.push_back({key, release, time});
  }
  void commitStringImpl(const std::string &text) override {
    effects.push_back("commit:" + text);
  }
  void deleteSurroundingTextImpl(int, unsigned int) override {
    throw std::runtime_error("addon must not delete application text");
  }
  void forwardKeyImpl(const ForwardKeyEvent &event) override {
    deliver(event.rawKey(), event.isRelease(), event.time());
  }
  void updatePreeditImpl() override {
    effects.push_back("preedit:" + inputPanel().clientPreedit().toString());
  }
  Instance &instance_;
  bool closed_ = false;
};

void boundary(Instance &instance, Key key) {
  Context ic(instance);
  ic.type("ki");
  require(ic.inputPanel().clientPreedit().cursor() == 6,
          "preedit cursor uses UTF-8 byte length");
  ic.clear();
  require(!ic.send(key), "boundary remains unhandled");
  ic.expect({"preedit:", "commit:কি", "key"});
  ic.unchanged(key);
  ic.clear();
  require(!ic.send(key), "idle boundary remains unhandled");
  ic.expect({"key"});
  ic.unchanged(key);
  ic.clear();
  require(!ic.send(Key(FcitxKey_BackSpace)), "idle Backspace belongs to app");
  ic.expect({"key"});
}

void test_boundaries(Instance &instance) {
  for (const auto sym :
       {FcitxKey_space, FcitxKey_Return, FcitxKey_KP_Enter, FcitxKey_Left,
        FcitxKey_Right, FcitxKey_Up, FcitxKey_Down, FcitxKey_Home, FcitxKey_End,
        FcitxKey_Page_Up, FcitxKey_Page_Down, FcitxKey_Delete, FcitxKey_Insert,
        FcitxKey_Tab, FcitxKey_F5}) {
    boundary(instance, Key(sym));
  }
  for (const auto sym : {FcitxKey_space, FcitxKey_Return, FcitxKey_BackSpace,
                         FcitxKey_Escape, FcitxKey_Tab, FcitxKey_Left}) {
    boundary(instance, Key(sym, KeyState::Shift));
  }
  for (const auto sym : {FcitxKey_c, FcitxKey_v, FcitxKey_x, FcitxKey_a,
                         FcitxKey_z, FcitxKey_Left, FcitxKey_Right}) {
    boundary(instance, Key(sym, KeyState::Ctrl));
  }
  boundary(instance, Key(FcitxKey_BackSpace, KeyState::Ctrl_Shift));
  boundary(instance, Key(FcitxKey_F4, KeyState::Alt));
  boundary(instance, Key(FcitxKey_c, KeyState::Super));
}

void test_editing(Instance &instance) {
  Context ic(instance);
  ic.type("ki");
  ic.clear();
  require(ic.send(Key(FcitxKey_BackSpace)), "active Backspace consumed");
  ic.expect({"preedit:ক"});
  ic.clear();
  const Key controlDelete(FcitxKey_BackSpace, KeyStates(KeyState::Ctrl) |
                                                  KeyState::CapsLock |
                                                  KeyState::Repeat);
  require(ic.send(controlDelete), "exact Ctrl+Backspace ignores bookkeeping");
  ic.expect({"preedit:"});
  ic.clear();
  require(!ic.send(controlDelete), "idle repeated Ctrl+Backspace forwarded");
  ic.expect({"key"});
  ic.unchanged(controlDelete);
  ic.type("ki");
  ic.clear();
  require(ic.send(Key(FcitxKey_Escape)), "active Escape consumed");
  ic.expect({"preedit:", "commit:কি"});
  ic.clear();
  require(!ic.send(Key(FcitxKey_Escape)), "idle Escape forwarded");
  ic.expect({"key"});
  ic.type("i");
  require(ic.inputPanel().clientPreedit().toString() == "ই",
          "fresh word after Escape commit");
}

void test_invisible(Instance &instance) {
  for (const auto sym :
       {FcitxKey_space, FcitxKey_Return, FcitxKey_Left, FcitxKey_Escape}) {
    Context ic(instance);
    ic.type("o`");
    require(ic.inputPanel().clientPreedit().empty(), "invisible raw buffer");
    ic.clear();
    const bool handled = ic.send(Key(sym));
    require(handled == (sym == FcitxKey_Escape), "invisible activity routing");
    ic.expect(sym == FcitxKey_Escape ? std::vector<std::string>{}
                                     : std::vector<std::string>{"key"});
    ic.type("i");
    require(ic.inputPanel().clientPreedit().toString() == "ই",
            "invisible buffer finalized");
  }
}

void test_releases_modifiers(Instance &instance) {
  Context ic(instance);
  ic.type("ki");
  for (const auto sym :
       {FcitxKey_Shift_L, FcitxKey_Control_L, FcitxKey_Alt_L, FcitxKey_Super_L,
        FcitxKey_Caps_Lock, FcitxKey_Num_Lock, FcitxKey_ISO_Lock,
        FcitxKey_ISO_Level3_Shift, FcitxKey_ISO_Level5_Shift,
        FcitxKey_Mode_switch, FcitxKey_ISO_Group_Latch}) {
    for (const bool release : {false, true}) {
      ic.clear();
      const Key key(sym);
      require(!ic.send(key, release), "modifier passes through");
      try {
        ic.expect({"key"});
      } catch (const std::exception &error) {
        throw std::runtime_error(key.toString() +
                                 (release ? " release: " : " press: ") +
                                 error.what());
      }
      ic.unchanged(key, release);
    }
  }
  for (const auto sym : {FcitxKey_i, FcitxKey_BackSpace, FcitxKey_space,
                         FcitxKey_Return, FcitxKey_Escape}) {
    ic.clear();
    const Key key(sym);
    require(!ic.send(key, true), "release passes through");
    try {
      ic.expect({"key"});
    } catch (const std::exception &error) {
      throw std::runtime_error(key.toString() + " release: " + error.what());
    }
    ic.unchanged(key, true);
  }
  require(ic.inputPanel().clientPreedit().toString() == "কি",
          "modifiers/releases preserve word");
  ic.reset();
  for (const auto sym :
       {FcitxKey_i, FcitxKey_BackSpace, FcitxKey_Escape, FcitxKey_Return}) {
    ic.clear();
    require(!ic.send(Key(sym), true), "idle release passes through");
    ic.expect({"key"});
  }
}

void test_resolved_text(Instance &instance) {
  for (const auto mods :
       {KeyStates(KeyState::Shift), KeyStates(KeyState::CapsLock)}) {
    Context ic(instance);
    ic.type("k");
    require(ic.send(Key(FcitxKey_I, mods)), "resolved uppercase text");
    require(ic.inputPanel().clientPreedit().toString() == "কী",
            "raw uppercase I preserved");
  }
  {
    Context ic(instance);
    require(ic.send(Key(FcitxKey_KP_1, KeyState::NumLock)),
            "resolved keypad digit");
    require(ic.inputPanel().clientPreedit().toString() == "১",
            "Bangla keypad digit");
  }
  {
    Context ic(instance);
    ic.type("ki");
    for (const auto sym :
         {FcitxKey_dead_acute, FcitxKey_dead_a, FcitxKey_Multi_key}) {
      ic.clear();
      require(!ic.send(Key(sym)), "compose prefix available to framework");
      ic.expect({"key"});
      require(ic.inputPanel().clientPreedit().toString() == "কি",
              "prefix preserves word");
    }
    // Resolved Unicode with no shortcut modifier can enter the controller.
    require(ic.send(Key(Key::keySymFromUnicode(0x00e9))),
            "resolved Unicode text");
    require(ic.inputPanel().clientPreedit().toString() == "কিé",
            "unmatched Unicode preserved");
  }
  boundary(instance, Key(FcitxKey_e, KeyState::Ctrl_Alt));
  boundary(instance, Key(FcitxKey_e, KeyState::Mod5));
  boundary(instance,
           Key(Key::keySymFromUnicode(0x00a0))); // rejected whitespace
}

void test_repeats(Instance &instance) {
  Context ic(instance);
  ic.type("k");
  require(ic.send(Key(FcitxKey_i, KeyState::Repeat)), "text repeat accepted");
  require(ic.send(Key(FcitxKey_i, KeyState::Repeat)),
          "second text repeat accepted");
  ic.clear();
  for (int i = 0; i < 3; ++i) {
    require(ic.send(Key(FcitxKey_BackSpace, KeyState::Repeat)),
            "repeat deletes one raw key");
  }
  require(!ic.send(Key(FcitxKey_BackSpace, KeyState::Repeat)),
          "idle repeat forwarded");
  ic.expect({"preedit:কি", "preedit:ক", "preedit:", "key"});
  ic.type("ki");
  ic.clear();
  require(!ic.send(Key(FcitxKey_Return, KeyState::Repeat)),
          "Enter repeat forwards");
  require(!ic.send(Key(FcitxKey_Return, KeyState::Repeat)),
          "idle Enter repeat forwards");
  ic.expect({"preedit:", "commit:কি", "key", "key"});
  ic.type("ki");
  ic.clear();
  require(ic.send(Key(FcitxKey_Escape, KeyState::Repeat)),
          "active Escape repeat consumes");
  require(!ic.send(Key(FcitxKey_Escape, KeyState::Repeat)),
          "idle Escape repeat forwards");
  ic.expect({"preedit:", "commit:কি", "key"});
}

void test_temporary_trigger(Instance &instance) {
  for (const bool shiftToggle : {true, false}) {
    RawConfig config;
    config["Hotkey/TriggerKeys/0"].setValue("Super+space");
    config["Hotkey/AltTriggerKeys"].setValue("");
    if (shiftToggle) {
      config["Hotkey/AltTriggerKeys/0"].setValue("Shift_L");
    }
    config["Hotkey/EnumerateGroupForwardKeys"].setValue("");
    config["Hotkey/EnumerateGroupBackwardKeys"].setValue("");
    instance.globalConfig().load(config, true);
    require(instance.globalConfig().altTriggerKeys().empty() == !shiftToggle,
            "load temporary toggle configuration");
    Context ic(instance);
    const auto shift = [&ic]() {
      ic.send(Key(FcitxKey_Shift_L));
      ic.send(Key(FcitxKey_Shift_L), true);
    };
    const auto toggle = [&ic]() {
      ic.send(Key(FcitxKey_Super_L));
      require(ic.send(Key(FcitxKey_space, KeyState::Super)),
              "Meta+Space trigger consumed");
      ic.send(Key(FcitxKey_space, KeyState::Super), true);
      ic.send(Key(FcitxKey_Super_L), true);
    };
    instance.setCurrentInputMethod(&ic, "keyboard-us", true);
    shift();
    require(instance.inputMethod(&ic) == "keyboard-us",
            "temporary Shift does not activate from ordinary English");
    toggle();
    require(instance.inputMethod(&ic) == "jong-bangla",
            "Meta+Space activates Jong");

    // Using Shift for a character must not trigger a modifier-only shortcut.
    ic.type("k");
    ic.send(Key(FcitxKey_Shift_L));
    require(ic.send(Key(FcitxKey_I, KeyState::Shift)), "uppercase I consumed");
    ic.send(Key(FcitxKey_I, KeyState::Shift), true);
    ic.send(Key(FcitxKey_Shift_L), true);
    require(instance.inputMethod(&ic) == "jong-bangla" &&
                ic.inputPanel().clientPreedit().toString() == "কী",
            "Shift+I preserves Jong and phonetic case");
    ic.reset();
    ic.type("ki");
    ic.clear();
    shift();
    if (shiftToggle) {
      require(instance.inputMethod(&ic) == "keyboard-us",
              "configured temporary Shift deactivates Jong");
      ic.expect({"key", "preedit:", "commit:কি", "key"});
      shift();
      require(instance.inputMethod(&ic) == "jong-bangla",
              "temporary Shift returns to Jong");
      ic.type("i");
      require(ic.inputPanel().clientPreedit().toString() == "ই",
              "temporary return starts fresh composition");
      shift();
      require(instance.inputMethod(&ic) == "keyboard-us",
              "temporary Shift can toggle repeatedly");
      shift();
      require(instance.inputMethod(&ic) == "jong-bangla",
              "repeated temporary Shift returns to Jong");
    } else {
      shift();
      require(instance.inputMethod(&ic) == "jong-bangla" &&
                  ic.inputPanel().clientPreedit().toString() == "কি",
              "without temporary toggle, standalone Shift preserves the word");
      ic.expect({"key", "key", "key", "key"});
    }
    toggle();
    require(instance.inputMethod(&ic) == "keyboard-us",
            "Meta+Space returns to ordinary English");
    ic.clear();
    shift();
    shift();
    require(instance.inputMethod(&ic) == "keyboard-us",
            "temporary Shift stays inactive after the primary toggle exits");
    ic.expect({"key", "key", "key", "key"});
  }
}

void test_framework_shortcuts(Instance &instance) {
  RawConfig config;
  config["Hotkey/TriggerKeys/0"].setValue("Control+space");
  config["Hotkey/AltTriggerKeys/0"].setValue("Shift_L");
  instance.globalConfig().load(config, true);
  {
    Context ic(instance);
    ic.type("ki");
    ic.clear();
    require(ic.send(Key(FcitxKey_space, KeyState::Ctrl)),
            "framework switching key consumed");
    ic.expect({"preedit:", "commit:কি"});
    require(instance.inputMethod(&ic) == "keyboard-us",
            "framework performed switch");
  }
  {
    Context ic(instance);
    ic.type("ki");
    ic.clear();
    require(!ic.send(Key(FcitxKey_Shift_L)),
            "framework modifier shortcut press passes");
    ic.expect({"key"});
    ic.clear();
    require(!ic.send(Key(FcitxKey_Shift_L), true),
            "framework modifier shortcut release passes");
    ic.expect({"preedit:", "commit:কি", "key"});
    require(instance.inputMethod(&ic) == "keyboard-us",
            "framework modifier shortcut switched");
  }
  test_temporary_trigger(instance);
  disableHotkeys(instance);
}

void test_lifecycle(Instance &instance) {
  {
    Context ic(instance);
    ic.type("ki");
    ic.clear();
    instance.setCurrentInputMethod(&ic, "keyboard-us", true);
    ic.expect({"preedit:", "commit:কি"});
    instance.setCurrentInputMethod(&ic, "jong-bangla", true);
    ic.type("i");
    require(ic.inputPanel().clientPreedit().toString() == "ই",
            "switch starts fresh");
  }
  for (const bool frontendOwns : {false, true}) {
    Context ic(instance, frontendOwns ? CapabilityFlags(
                                            CapabilityFlag::ClientUnfocusCommit)
                                      : CapabilityFlags());
    ic.type("ki");
    ic.clear();
    if (frontendOwns) {
      // Synthetic frontend fulfills its advertised responsibility before
      // notifying Fcitx. A real toolkit is still a separate smoke test.
      ic.effects.push_back("frontend-commit:কি");
    }
    ic.focusOut();
    ic.expect({frontendOwns ? "frontend-commit:কি" : "commit:কি", "preedit:"});
    ic.clear();
    ic.focusOut(); // no event if already unfocused
    ic.reset();    // framework ignores reset when unfocused
    ic.expect({});
    ic.focusIn();
    ic.type("i");
    require(ic.inputPanel().clientPreedit().toString() == "ই",
            "focus starts fresh");
  }
  {
    Context ic(instance);
    ic.type("ki");
    ic.clear();
    ic.reset();
    ic.reset();
    ic.expect({"preedit:"});
    ic.type("i");
    require(ic.inputPanel().clientPreedit().toString() == "ই",
            "reset discards");
  }
  {
    Context ic(instance);
    ic.type("ki");
    ic.clear();
    auto *engine = instance.inputMethodEngine(&ic);
    const auto *entry = instance.inputMethodEntry(&ic);
    FocusOutEvent event(&ic);
    ic.focusOut();
    ic.clear();
    engine->deactivate(*entry, event);
    engine->deactivate(*entry, event);
    engine->reset(*entry, event);
    ic.expect({});
  }
  {
    Context a(instance);
    a.type("ki");
    a.focusOut();
    Context b(instance);
    b.type("i");
    require(b.inputPanel().clientPreedit().toString() == "ই",
            "no buffer transferred to B");
    b.focusOut();
    a.focusIn();
    a.type("i");
    require(a.inputPanel().clientPreedit().toString() == "ই",
            "A does not restore old buffer");
  }
  for (const auto restriction :
       {CapabilityFlag::Disable, CapabilityFlag::Password}) {
    Context ic(instance);
    ic.type("ki");
    ic.clear();
    ic.setCapabilityFlags(ic.capabilityFlags() | restriction);
    ic.expect({"preedit:"});
    ic.clear();
    require(!ic.send(Key(FcitxKey_i)), "restricted field passes through");
    ic.expect({"key"});
    ic.setCapabilityFlags(CapabilityFlags(CapabilityFlag::Preedit) |
                          CapabilityFlag::FormattedPreedit);
    ic.type("i");
    require(ic.inputPanel().clientPreedit().toString() == "ই",
            "restricted transition discards");
  }
}

void test_context_isolation(Instance &instance) {
  {
    Context a(instance);
    a.type("ki");
    Context b(instance);
    b.type("kI");
    instance.inputContextManager().setPropertyPropagatePolicy(
        PropertyPropagatePolicy::All);
    a.updateProperty("jong-bangla-state");
    require(a.inputPanel().clientPreedit().toString() == "কি",
            "A keeps independent word");
    require(b.inputPanel().clientPreedit().toString() == "কী",
            "B keeps independent word");
    a.reset();
    require(b.inputPanel().clientPreedit().toString() == "কী",
            "A reset leaves B intact");
    instance.inputContextManager().setPropertyPropagatePolicy(
        PropertyPropagatePolicy::No);
  }
  {
    Context ic(instance);
    ic.type("ki");
    ic.clear();
    ic.close();
    ic.expect({}); // destruction must never commit
  }
  {
    Context ic(instance, CapabilityFlag::ClientUnfocusCommit);
    ic.type("ki");
    ic.clear();
    // If frontend-owned delivery is unavailable, the addon must still not
    // retry the text in a newly focused field.
    ic.focusOut();
    ic.expect({"preedit:"});
    Context next(instance);
    next.type("i");
    require(next.inputPanel().clientPreedit().toString() == "ই",
            "no retry at new target");
  }
  {
    Context ic(instance);
    ic.setEnablePreedit(false);
    ic.type("ki");
    require(ic.inputPanel().preedit().toString() == "কি",
            "converted fallback UI text");
    require(!ic.inputPanel().candidateList(), "no choice list");
    ic.clear();
    require(!ic.send(Key(FcitxKey_space)), "fallback boundary passes through");
    ic.expect({"commit:কি", "key"});
  }
}

void test_preedit_click(Instance &instance) {
  Context ic(instance);
  ic.type("ki");
  ic.clear();
  // Cursor-rectangle and surrounding-text notifications do not establish a
  // document relocation. Only the explicit preedit action finalizes here.
  ic.setCursorRect(Rect(10, 10, 1, 20));
  ic.updateSurroundingText();
  ic.expect({});
  InvokeActionEvent event(InvokeActionEvent::Action::LeftClick, 0, &ic);
  ic.invokeAction(event);
  require(event.accepted(), "preedit click handled");
  ic.expect({"preedit:", "commit:কি"});
  ic.clear();
  ic.reset();
  ic.invokeAction(event);
  ic.expect({});
}

} // namespace

int main(int argc, char **argv) {
  try {
    Sandbox sandbox(argc, argv);
    char program[] = "jong-fcitx5-harness";
    char disable[] = "--disable=all";
    char enable[] = "--enable=jong-bangla,jong-harness-null";
    char quiet[] = "--verbose=*=0";
    char *args[] = {program, disable, enable, quiet};
    NullFactory nullFactory;
    StaticAddonRegistry registry{{"jong-harness-null", &nullFactory}};
    Instance instance(4, args);
    require(instance.initialized(), "construct isolated dispatcher");
    instance.addonManager().registerDefaultLoader(&registry);
    instance.initialize();
    disableHotkeys(instance);
    require(instance.inputMethodManager().entry("jong-bangla") != nullptr,
            "discover local metadata");
    require(instance.addonManager().addon("jong-bangla", true) != nullptr,
            "load Jong addon from configured library path");
    InputMethodGroup group("Jong synthetic");
    group.setDefaultLayout("us");
    group.inputMethodList().emplace_back("keyboard-us");
    group.inputMethodList().emplace_back("jong-bangla");
    group.setDefaultInputMethod("jong-bangla");
    instance.inputMethodManager().addEmptyGroup(group.name());
    instance.inputMethodManager().setGroup(group);
    instance.inputMethodManager().setCurrentGroup(group.name());
    require(
        instance.inputMethodManager().currentGroup().inputMethodList().size() ==
            2,
        "configure two harness input methods");
    const std::vector<std::pair<const char *, void (*)(Instance &)>> suites = {
        {"boundaries", test_boundaries},
        {"editing", test_editing},
        {"invisible input", test_invisible},
        {"releases and modifiers", test_releases_modifiers},
        {"resolved text", test_resolved_text},
        {"repeats", test_repeats},
        {"framework shortcuts", test_framework_shortcuts},
        {"lifecycle", test_lifecycle},
        {"context isolation", test_context_isolation},
        {"preedit click", test_preedit_click},
    };
    for (const auto &[name, run] : suites) {
      try {
        run(instance);
      } catch (const std::exception &error) {
        throw std::runtime_error(std::string(name) + ": " + error.what());
      }
    }
    for (const auto &name : instance.addonManager().loadedAddonNames()) {
      require(name == "jong-bangla" || name == "jong-harness-null",
              "no desktop addons loaded");
    }
    std::cout << suites.size()
              << " synthetic Fcitx5 suites passed; no desktop frontends used\n";
    return 0;
  } catch (const std::exception &error) {
    std::cerr << "Fcitx5 harness failed: " << error.what() << '\n';
    return 1;
  }
}
