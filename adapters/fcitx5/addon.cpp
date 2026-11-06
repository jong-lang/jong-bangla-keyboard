// MIT. Fcitx5 events/UI only; all composition and transliteration live in Rust.
#include "../ffi/jong.h"

#include <cstdint>
#include <limits>
#include <memory>
#include <stdexcept>
#include <string>

#include <fcitx-utils/capabilityflags.h>
#include <fcitx-utils/key.h>
#include <fcitx-utils/textformatflags.h>
#include <fcitx/addonfactory.h>
#include <fcitx/addonmanager.h>
#include <fcitx/event.h>
#include <fcitx/globalconfig.h>
#include <fcitx/inputcontext.h>
#include <fcitx/inputcontextmanager.h>
#include <fcitx/inputcontextproperty.h>
#include <fcitx/inputmethodengine.h>
#include <fcitx/inputpanel.h>
#include <fcitx/instance.h>
#include <fcitx/text.h>
#include <fcitx/userinterface.h>

namespace {

class State final : public fcitx::InputContextProperty {
public:
  State() : session(jong_session_new(), jong_session_free) {
    if (!session) {
      throw std::runtime_error("Jong composition allocation failed");
    }
  }

  // The base property's default needCopy=false prevents cross-field sharing.
  std::unique_ptr<JongSession, decltype(&jong_session_free)> session;
};

// Resolved text comes from rawKey: normalized keys may strip Shift/case.
// Keep Mod5 ambiguous until actual AltGr frontend behavior is verified.
uint32_t semanticStates(const fcitx::Key &key) {
  constexpr uint32_t bookkeeping =
      static_cast<uint32_t>(fcitx::KeyState::CapsLock) |
      static_cast<uint32_t>(fcitx::KeyState::NumLock) |
      static_cast<uint32_t>(fcitx::KeyState::Repeat) |
      static_cast<uint32_t>(fcitx::KeyState::HandledMask) |
      static_cast<uint32_t>(fcitx::KeyState::IgnoredMask);
  return key.states().toInteger() & ~bookkeeping;
}

bool composePrefix(fcitx::KeySym sym) {
  // XKB's dead symbols have two contiguous ranges and a separate vowel range.
  return sym == FcitxKey_Multi_key ||
         (sym >= FcitxKey_dead_grave && sym <= FcitxKey_dead_currency) ||
         (sym >= FcitxKey_dead_lowline &&
          sym <= FcitxKey_dead_longsolidusoverlay) ||
         (sym >= FcitxKey_dead_a && sym <= FcitxKey_dead_greek);
}

bool modifierOnly(const fcitx::Key &key) {
  // Key::isModifier excludes lock keys and XKB's level/group selectors.
  const auto sym = key.sym();
  return key.isModifier() || sym == FcitxKey_Caps_Lock ||
         sym == FcitxKey_Shift_Lock || sym == FcitxKey_Num_Lock ||
         sym == FcitxKey_Scroll_Lock || sym == FcitxKey_Mode_switch ||
         sym == FcitxKey_ISO_Lock || sym == FcitxKey_ISO_Level2_Latch ||
         (sym >= FcitxKey_ISO_Level3_Shift &&
          sym <= FcitxKey_ISO_Level3_Lock) ||
         (sym >= FcitxKey_ISO_Level5_Shift &&
          sym <= FcitxKey_ISO_Level5_Lock) ||
         (sym >= FcitxKey_ISO_Group_Latch &&
          sym <= FcitxKey_ISO_Last_Group_Lock);
}

std::string copySpan(const uint8_t *data, size_t size) {
  return size ? std::string(reinterpret_cast<const char *>(data), size)
              : std::string();
}

class Engine final : public fcitx::InputMethodEngineV3 {
public:
  explicit Engine(fcitx::Instance &instance) : instance_(instance) {
    if (!instance_.inputContextManager().registerProperty("jong-bangla-state",
                                                          &factory_)) {
      throw std::runtime_error("Jong context property registration failed");
    }
  }

  void keyEvent(const fcitx::InputMethodEntry &,
                fcitx::KeyEvent &event) override {
    auto &ic = *event.inputContext();
    try {
      if (!permitted(ic)) {
        apply(ic, JongReset);
        return;
      }
      const auto key = event.rawKey();
      if (event.isRelease() || modifierOnly(key) || composePrefix(key.sym())) {
        return;
      }
      const auto mods = semanticStates(key);
      JongAction action = JongCommit;
      if (mods == 0 && key.sym() == FcitxKey_BackSpace) {
        action = JongBackspace;
      } else if (mods == static_cast<uint32_t>(fcitx::KeyState::Ctrl) &&
                 key.sym() == FcitxKey_BackSpace) {
        action = JongCtrlBackspace;
      } else if (mods == 0 && key.sym() == FcitxKey_space) {
        action = JongSpace;
      } else if (mods == 0 && (key.sym() == FcitxKey_Return ||
                               key.sym() == FcitxKey_KP_Enter)) {
        action = JongEnter;
      } else if (mods == 0 && key.sym() == FcitxKey_Escape) {
        action = JongEscape;
      } else if ((mods & ~static_cast<uint32_t>(fcitx::KeyState::Shift)) == 0) {
        const auto scalar = fcitx::Key::keySymToUnicode(key.sym());
        if (scalar != 0 && key.sym() != FcitxKey_space &&
            key.sym() != FcitxKey_KP_Space) {
          auto result = run(ic, JongInsert, scalar);
          if (result.consumed) {
            publish(ic, result);
            event.filterAndAccept();
            return;
          }
          // Whitespace/control text rejected by Rust is a boundary.
        }
      }
      if (apply(ic, action)) {
        event.filterAndAccept();
      }
      // Unhandled events use Fcitx's delivery path. Never forwardKey here.
    } catch (...) {
      recover(ic);
      // Do not replay an event whose composition mutation may have run.
      event.filterAndAccept();
    }
  }

  void activate(const fcitx::InputMethodEntry &,
                fcitx::InputContextEvent &event) override {
    discard(*event.inputContext());
  }

  void reset(const fcitx::InputMethodEntry &,
             fcitx::InputContextEvent &event) override {
    discard(*event.inputContext());
  }

  void deactivate(const fcitx::InputMethodEntry &,
                  fcitx::InputContextEvent &event) override {
    auto &ic = *event.inputContext();
    try {
      bool capabilitySwitch = false;
      if (event.type() == fcitx::EventType::InputContextSwitchInputMethod) {
        capabilitySwitch =
            static_cast<fcitx::InputContextSwitchInputMethodEvent &>(event)
                .reason() ==
            fcitx::InputMethodSwitchedReason::CapabilityChanged;
      }
      // Fcitx's ReservedFirst focus-out handler has already committed the
      // client preedit, or delegated that responsibility to the frontend.
      const bool mayCommit =
          event.type() != fcitx::EventType::InputContextFocusOut &&
          ic.hasFocus() && permitted(ic) && !capabilitySwitch;
      apply(ic, mayCommit ? JongCommit : JongReset);
    } catch (...) {
      recover(ic);
    }
  }

  void invokeActionImpl(const fcitx::InputMethodEntry &,
                        fcitx::InvokeActionEvent &event) override {
    auto &ic = *event.inputContext();
    try {
      apply(ic, ic.hasFocus() && permitted(ic) ? JongCommit : JongReset);
      event.filter();
    } catch (...) {
      recover(ic);
      event.filter();
    }
  }

private:
  bool permitted(const fcitx::InputContext &ic) const {
    const auto flags = ic.capabilityFlags();
    return !flags.test(fcitx::CapabilityFlag::Disable) &&
           (!flags.test(fcitx::CapabilityFlag::Password) ||
            instance_.globalConfig().allowInputMethodForPassword());
  }

  JongResult run(fcitx::InputContext &ic, JongAction action,
                 uint32_t scalar = 0) {
    auto *state = ic.propertyFor(&factory_);
    if (!state) {
      throw std::runtime_error("Jong context state unavailable");
    }
    const auto result =
        jong_session_action(state->session.get(), action, scalar);
    if (result.status != 0) {
      throw std::runtime_error("Jong composition action failed");
    }
    return result;
  }

  void publish(fcitx::InputContext &ic, const JongResult &result) {
    // Copy both borrowed spans before any framework call can reenter us.
    const auto preedit = copySpan(result.preedit, result.preedit_len);
    const auto committed = copySpan(result.committed, result.committed_len);
    ic.inputPanel().reset();
    fcitx::Text text(preedit, fcitx::TextFormatFlag::Underline);
    if (preedit.size() > static_cast<size_t>(std::numeric_limits<int>::max())) {
      throw std::length_error("Jong preedit exceeds Fcitx cursor range");
    }
    text.setCursor(static_cast<int>(preedit.size())); // UTF-8 byte offset
    ic.inputPanel().setClientPreedit(text);
    if (!ic.capabilityFlags().test(fcitx::CapabilityFlag::Preedit)) {
      ic.inputPanel().setPreedit(text);
    }
    ic.updatePreedit();
    ic.updateUserInterface(fcitx::UserInterfaceComponent::InputPanel);
    if (!committed.empty()) {
      ic.commitString(committed);
    }
  }

  bool apply(fcitx::InputContext &ic, JongAction action) {
    const auto result = run(ic, action);
    const bool consumed = result.consumed;
    publish(ic, result);
    return consumed;
  }

  void recover(fcitx::InputContext &ic) noexcept {
    // No text or exception contents are logged. Reset before clearing UI.
    try {
      if (auto *state = ic.propertyFor(&factory_)) {
        jong_session_action(state->session.get(), JongReset, 0);
      }
      ic.inputPanel().reset();
      ic.updatePreedit();
      ic.updateUserInterface(fcitx::UserInterfaceComponent::InputPanel);
    } catch (...) {
      // C++ exceptions must not leave addon callbacks.
    }
  }

  void discard(fcitx::InputContext &ic) noexcept {
    try {
      apply(ic, JongReset);
    } catch (...) {
      recover(ic);
    }
  }

  fcitx::Instance &instance_;
  fcitx::SimpleInputContextPropertyFactory<State> factory_;
};

class Factory final : public fcitx::AddonFactory {
public:
  fcitx::AddonInstance *create(fcitx::AddonManager *manager) override {
    try {
      return new Engine(*manager->instance());
    } catch (...) {
      return nullptr;
    }
  }
};

} // namespace

FCITX_ADDON_FACTORY(Factory)
