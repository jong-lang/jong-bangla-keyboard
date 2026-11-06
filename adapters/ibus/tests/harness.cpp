// MIT. Synthetic protocol client: real IBusFactory/IBusEngine, private D-Bus.
#include "../engine.h"
#include <csignal>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
void require(bool condition, const std::string &message) {
  if (!condition)
    throw std::runtime_error(message);
}
struct Effect {
  std::string path, kind, text;
  guint cursor = 0, mode = 0;
  gboolean visible = FALSE;
};
struct Pending {
  bool done = false;
  GVariant *reply = nullptr;
  GError *error = nullptr;
};
void completed(GObject *object, GAsyncResult *result, gpointer data) {
  auto &pending = *static_cast<Pending *>(data);
  pending.reply = g_dbus_connection_call_finish(G_DBUS_CONNECTION(object),
                                                result, &pending.error);
  pending.done = true;
}
void signal(GDBusConnection *, const gchar *, const gchar *path, const gchar *,
            const gchar *name, GVariant *args, gpointer data) {
  auto &effects = *static_cast<std::vector<Effect> *>(data);
  Effect effect{path, name, ""};
  GVariant *variant = nullptr;
  if (effect.kind == "UpdatePreeditText") {
    g_variant_get(args, "(vubu)", &variant, &effect.cursor, &effect.visible,
                  &effect.mode);
  } else if (effect.kind == "CommitText") {
    g_variant_get(args, "(v)", &variant);
  }
  if (variant) {
    auto *text = IBUS_TEXT(ibus_serializable_deserialize(variant));
    effect.text = ibus_text_get_text(text);
    g_object_unref(text);
    g_variant_unref(variant);
  }
  effects.push_back(std::move(effect));
}

class Harness {
public:
  explicit Harness(const char *executable) {
    const auto *address = g_getenv("DBUS_SESSION_BUS_ADDRESS");
    require(address, "private session bus required");
    GError *error = nullptr;
    client = g_dbus_connection_new_for_address_sync(
        address,
        static_cast<GDBusConnectionFlags>(
            G_DBUS_CONNECTION_FLAGS_AUTHENTICATION_CLIENT |
            G_DBUS_CONNECTION_FLAGS_MESSAGE_BUS_CONNECTION),
        nullptr, nullptr, &error);
    require(client, error ? error->message : "connect private D-Bus");
    // Launch the actual production executable, pointed ONLY at the private
    // dbus-run-session bus. This is not an IBus daemon or a desktop frontend.
    auto *launcher = g_subprocess_launcher_new(G_SUBPROCESS_FLAGS_NONE);
    g_subprocess_launcher_setenv(launcher, "IBUS_ADDRESS", address, TRUE);
    g_subprocess_launcher_setenv(launcher, "IBUS_USE_PORTAL", "0", TRUE);
    process = g_subprocess_launcher_spawn(launcher, &error, executable,
                                          "--ibus", nullptr);
    g_object_unref(launcher);
    require(process, error ? error->message : "launch production service");
    const gint64 deadline = g_get_monotonic_time() + 5000000;
    bool ready = false;
    while (!ready && g_get_monotonic_time() < deadline) {
      auto *reply = g_dbus_connection_call_sync(
          client, "org.freedesktop.DBus", "/org/freedesktop/DBus",
          "org.freedesktop.DBus", "NameHasOwner",
          g_variant_new("(s)", "org.freedesktop.IBus.JongBangla"), nullptr,
          G_DBUS_CALL_FLAGS_NONE, 1000, nullptr, nullptr);
      require(reply, "service name readiness");
      gboolean owned = FALSE;
      g_variant_get(reply, "(b)", &owned);
      g_variant_unref(reply);
      ready = owned;
      if (!ready)
        g_usleep(10000);
    }
    require(ready, "production service did not acquire its bus name");
    // A second instance must fail instead of queueing for the same service.
    launcher = g_subprocess_launcher_new(G_SUBPROCESS_FLAGS_STDERR_PIPE);
    g_subprocess_launcher_setenv(launcher, "IBUS_ADDRESS", address, TRUE);
    g_subprocess_launcher_setenv(launcher, "IBUS_USE_PORTAL", "0", TRUE);
    auto *duplicate = g_subprocess_launcher_spawn(launcher, &error, executable,
                                                  "--ibus", nullptr);
    g_object_unref(launcher);
    require(duplicate, "launch duplicate-instance control");
    gchar *diagnostic = nullptr;
    require(g_subprocess_communicate_utf8(duplicate, nullptr, nullptr, nullptr,
                                          &diagnostic, &error),
            "collect duplicate-instance result");
    require(diagnostic && std::string(diagnostic) ==
                              "Cannot own the Jong Bangla IBus service name.\n",
            "duplicate-instance control must fail only for name ownership");
    g_free(diagnostic);
    require(g_subprocess_wait(duplicate, nullptr, nullptr) &&
                g_subprocess_get_if_exited(duplicate) &&
                g_subprocess_get_exit_status(duplicate) == 1,
            "duplicate service must exit with failure");
    g_object_unref(duplicate);

    subscription = g_dbus_connection_signal_subscribe(
        client, "org.freedesktop.IBus.JongBangla", IBUS_INTERFACE_ENGINE,
        nullptr, nullptr, nullptr, G_DBUS_SIGNAL_FLAGS_NONE, signal, &effects,
        nullptr);
    // Roundtrip to install the subscription before the first engine signal.
    auto *reply = g_dbus_connection_call_sync(
        client, "org.freedesktop.DBus", "/org/freedesktop/DBus",
        "org.freedesktop.DBus", "GetId", nullptr, nullptr,
        G_DBUS_CALL_FLAGS_NONE, 5000, nullptr, nullptr);
    require(reply, "subscription barrier");
    g_variant_unref(reply);
  }
  ~Harness() {
    g_dbus_connection_signal_unsubscribe(client, subscription);
    if (process) {
      g_subprocess_force_exit(process);
      g_subprocess_wait(process, nullptr, nullptr);
      g_object_unref(process);
    }
    g_dbus_connection_close_sync(client, nullptr, nullptr);
    g_object_unref(client);
  }
  void shutdown() {
    g_subprocess_send_signal(process, SIGTERM);
    require(g_subprocess_wait_check(process, nullptr, nullptr),
            "production service graceful shutdown");
    g_clear_object(&process);
  }
  GVariant *call(const std::string &path, const char *method,
                 GVariant *args = nullptr,
                 const char *interface = IBUS_INTERFACE_ENGINE) {
    Pending pending;
    g_dbus_connection_call(client, "org.freedesktop.IBus.JongBangla",
                           path.c_str(), interface, method, args, nullptr,
                           G_DBUS_CALL_FLAGS_NONE, 5000, nullptr, completed,
                           &pending);
    while (!pending.done)
      g_main_context_iteration(nullptr, TRUE);
    while (g_main_context_iteration(nullptr, FALSE)) {
    }
    if (pending.error) {
      std::string message = pending.error->message;
      g_error_free(pending.error);
      throw std::runtime_error(std::string(method) + ": " + message);
    }
    return pending.reply;
  }
  void event(const std::string &path, const char *method,
             GVariant *args = nullptr) {
    g_variant_unref(call(path, method, args));
  }
  std::string create() {
    auto *reply =
        call(IBUS_PATH_FACTORY, "CreateEngine",
             g_variant_new("(s)", "jong-bangla"), IBUS_INTERFACE_FACTORY);
    const char *path = nullptr;
    g_variant_get(reply, "(&o)", &path);
    std::string copy(path);
    g_variant_unref(reply);
    event(copy, "Enable");
    event(copy, "FocusInId", g_variant_new("(ss)", "/context/A", "synthetic"));
    effects.clear();
    return copy;
  }
  bool key(const std::string &path, guint key, guint state = 0,
           guint code = 38) {
    auto *reply =
        call(path, "ProcessKeyEvent", g_variant_new("(uuu)", key, code, state));
    gboolean handled = FALSE;
    g_variant_get(reply, "(b)", &handled);
    g_variant_unref(reply);
    // A FALSE reply is the framework's single original-key delivery route.
    // Explicit ForwardKeyEvent signals are always a defect for this adapter.
    for (const auto &effect : effects)
      require(effect.kind != "ForwardKeyEvent",
              "duplicate explicit forwarding");
    if (!handled)
      effects.push_back({path, "ApplicationKey",
                         std::to_string(key) + ":" + std::to_string(code) +
                             ":" + std::to_string(state)});
    return handled;
  }
  void word(const std::string &path) {
    require(key(path, IBUS_KEY_k) && key(path, IBUS_KEY_i), "insert ki");
    const auto &last = effects.back();
    require(last.text == "কি" && last.cursor == 2 && last.visible &&
                last.mode == IBUS_ENGINE_PREEDIT_COMMIT,
            "exact UTF-8 preedit, character cursor and commit owner");
    effects.clear();
  }
  void
  expect(std::initializer_list<std::pair<std::string, std::string>> expected) {
    require(effects.size() == expected.size(),
            "unexpected effect count: " + std::to_string(effects.size()) +
                " vs " + std::to_string(expected.size()));
    size_t i = 0;
    for (const auto &[kind, text] : expected) {
      require(effects[i].kind == kind && effects[i].text == text,
              "effect " + std::to_string(i) + " expected " + kind + ":" + text +
                  " got " + effects[i].kind + ":" + effects[i].text);
      ++i;
    }
    effects.clear();
  }
  void content(const std::string &path, guint purpose, guint hints = 0) {
    auto *reply =
        call(path, "Set",
             g_variant_new("(ssv)", IBUS_INTERFACE_ENGINE, "ContentType",
                           g_variant_new("(uu)", purpose, hints)),
             "org.freedesktop.DBus.Properties");
    g_variant_unref(reply);
    // ContentType also emits PropertiesChanged, outside the engine interface.
  }
  std::vector<Effect> effects;

private:
  GDBusConnection *client = nullptr;
  GSubprocess *process = nullptr;
  guint subscription = 0;
};

void run(const char *executable) {
  Harness h(executable);
  auto a = h.create();
  // Verify the factory advertises the ID-aware lifecycle protocol.
  auto *reply =
      h.call(a, "Get", g_variant_new("(ss)", IBUS_INTERFACE_ENGINE, "FocusId"),
             "org.freedesktop.DBus.Properties");
  GVariant *value = nullptr;
  g_variant_get(reply, "(v)", &value);
  require(g_variant_get_boolean(value), "FocusId advertised");
  g_variant_unref(value);
  g_variant_unref(reply);

  h.event(a, "SetCapabilities",
          g_variant_new("(u)", IBUS_CAP_PREEDIT_TEXT | IBUS_CAP_FOCUS |
                                   IBUS_CAP_SYNC_PROCESS_KEY));
  h.word(a);
  require(h.key(a, IBUS_KEY_BackSpace), "raw Backspace consumed");
  h.expect({{"UpdatePreeditText", "ক"}});
  require(h.key(a, IBUS_KEY_BackSpace), "last Backspace consumed");
  h.expect({{"UpdatePreeditText", ""}});
  require(!h.key(a, IBUS_KEY_BackSpace), "idle Backspace forwarded");
  h.expect({{"UpdatePreeditText", ""}, {"ApplicationKey", "65288:38:0"}});

  h.word(a);
  require(h.key(a, IBUS_KEY_BackSpace, IBUS_CONTROL_MASK), "Ctrl+Backspace");
  h.expect({{"UpdatePreeditText", ""}});
  require(!h.key(a, IBUS_KEY_BackSpace, IBUS_CONTROL_MASK),
          "idle Ctrl+Backspace");
  h.effects.clear();

  const std::vector<std::pair<guint, guint>> boundaries = {
      {IBUS_KEY_space, 0},
      {IBUS_KEY_Return, 0},
      {IBUS_KEY_KP_Enter, 0},
      {IBUS_KEY_Left, 0},
      {IBUS_KEY_Right, IBUS_SHIFT_MASK},
      {IBUS_KEY_Home, IBUS_CONTROL_MASK},
      {IBUS_KEY_End, 0},
      {IBUS_KEY_Page_Up, 0},
      {IBUS_KEY_Page_Down, 0},
      {IBUS_KEY_Insert, 0},
      {IBUS_KEY_Delete, 0},
      {IBUS_KEY_Tab, 0},
      {IBUS_KEY_ISO_Left_Tab, IBUS_SHIFT_MASK},
      {IBUS_KEY_c, IBUS_CONTROL_MASK},
      {IBUS_KEY_v, IBUS_CONTROL_MASK},
      {IBUS_KEY_x, IBUS_CONTROL_MASK},
      {IBUS_KEY_a, IBUS_CONTROL_MASK},
      {IBUS_KEY_z, IBUS_CONTROL_MASK},
      {IBUS_KEY_c, IBUS_MOD1_MASK},
      {IBUS_KEY_c, IBUS_SUPER_MASK},
      {IBUS_KEY_BackSpace, IBUS_CONTROL_MASK | IBUS_SHIFT_MASK},
      {IBUS_KEY_space, IBUS_SHIFT_MASK},
      {IBUS_KEY_Return, IBUS_SHIFT_MASK},
      {IBUS_KEY_BackSpace, IBUS_SHIFT_MASK},
      {IBUS_KEY_Escape, IBUS_SHIFT_MASK},
      {IBUS_KEY_EuroSign, IBUS_MOD5_MASK},
      {IBUS_KEY_e, IBUS_CONTROL_MASK | IBUS_MOD1_MASK},
      {0x010000a0, 0},
      {0x01000009, 0}};
  for (auto [key, state] : boundaries) {
    h.word(a);
    require(!h.key(a, key, state, 73), "boundary must forward");
    h.expect({{"UpdatePreeditText", ""},
              {"CommitText", "কি"},
              {"ApplicationKey",
               std::to_string(key) + ":73:" + std::to_string(state)}});
    require(!h.key(a, IBUS_KEY_BackSpace), "boundary clears raw state");
    h.effects.clear();
  }
  h.word(a);
  require(h.key(a, IBUS_KEY_Escape), "active Escape consumes");
  h.expect({{"UpdatePreeditText", ""}, {"CommitText", "কি"}});
  require(!h.key(a, IBUS_KEY_Escape), "repeat Escape forwards");
  h.effects.clear();

  h.word(a);
  for (guint key :
       {IBUS_KEY_Shift_L, IBUS_KEY_Control_L, IBUS_KEY_Alt_R, IBUS_KEY_Super_L,
        IBUS_KEY_Caps_Lock, IBUS_KEY_Num_Lock, IBUS_KEY_ISO_Level3_Shift,
        IBUS_KEY_dead_acute, IBUS_KEY_Multi_key}) {
    require(!h.key(a, key), "modifier/prefix passthrough");
    h.expect({{"ApplicationKey", std::to_string(key) + ":38:0"}});
  }
  for (guint key :
       {IBUS_KEY_k, IBUS_KEY_BackSpace, IBUS_KEY_Escape, IBUS_KEY_Return}) {
    require(!h.key(a, key, IBUS_RELEASE_MASK), "release passthrough");
    h.expect({{"ApplicationKey", std::to_string(key) + ":38:" +
                                     std::to_string(IBUS_RELEASE_MASK)}});
  }
  require(!h.key(a, IBUS_KEY_k, IBUS_FORWARD_MASK),
          "forwarded-event passthrough");
  h.effects.clear();
  require(h.key(a, IBUS_KEY_Escape),
          "word preserved across modifiers/releases");
  h.expect({{"UpdatePreeditText", ""}, {"CommitText", "কি"}});

  require(h.key(a, IBUS_KEY_k, IBUS_LOCK_MASK), "Caps resolved key");
  require(h.key(a, IBUS_KEY_I, IBUS_SHIFT_MASK | IBUS_LOCK_MASK),
          "Shift resolved I");
  require(h.effects.back().text == "কী", "phonetic case preserved");
  h.event(a, "Reset");
  h.effects.clear();
  for (guint key : {IBUS_KEY_1, IBUS_KEY_KP_2, IBUS_KEY_3})
    require(h.key(a, key, IBUS_MOD2_MASK), "digits consumed with NumLock");
  require(h.effects.back().text == "১২৩", "Bangla digits");
  h.event(a, "Reset");
  h.effects.clear();
  require(h.key(a, 0x0101f600), "Unicode scalar consumed");
  require(h.effects.back().text == "😀" && h.effects.back().cursor == 1,
          "non-BMP character cursor");
  h.event(a, "Reset");
  h.effects.clear();
  for (int i = 0; i < 3; ++i)
    require(h.key(a, IBUS_KEY_k), "repeat press");
  for (int i = 0; i < 3; ++i)
    require(h.key(a, IBUS_KEY_BackSpace), "repeat delete");
  require(!h.key(a, IBUS_KEY_BackSpace), "repeat reaches idle");
  h.effects.clear();

  for (guint boundary :
       {IBUS_KEY_space, IBUS_KEY_Return, IBUS_KEY_Left, IBUS_KEY_Escape}) {
    require(h.key(a, IBUS_KEY_o) && h.key(a, IBUS_KEY_grave),
            "invisible active input");
    require(h.effects.back().text.empty() && !h.effects.back().visible,
            "invisible preedit");
    h.effects.clear();
    require(h.key(a, boundary) == (boundary == IBUS_KEY_Escape),
            "invisible boundary ownership");
    if (boundary == IBUS_KEY_Escape)
      h.expect({{"UpdatePreeditText", ""}});
    else
      h.expect({{"UpdatePreeditText", ""},
                {"ApplicationKey", std::to_string(boundary) + ":38:0"}});
  }

  auto b = h.create();
  h.word(a);
  require(h.key(b, IBUS_KEY_i), "independent engine input");
  require(h.effects.back().text == "ই" && h.effects.back().path == b,
          "context isolation");
  h.effects.clear();
  h.event(a, "FocusOutId", g_variant_new("(s)", "/context/A"));
  h.expect({{"UpdatePreeditText", ""}}); // Framework owns the displayed commit.
  h.event(a, "Reset");
  h.event(a, "Disable");
  h.effects.clear();
  require(!h.key(a, IBUS_KEY_k), "unfocused disabled event forwards");
  h.effects.clear();
  h.event(a, "Enable");
  h.event(a, "FocusInId", g_variant_new("(ss)", "/context/B", "synthetic"));
  h.effects.clear();
  require(h.key(a, IBUS_KEY_i) && h.effects.back().text == "ই",
          "no restored raw word");
  h.event(a, "FocusOutId", g_variant_new("(s)", "/context/A"));
  require(h.effects.back().text == "ই", "stale focus-out did not clear B");
  h.effects.clear();
  require(h.key(a, IBUS_KEY_Escape), "finish new B");
  h.expect({{"UpdatePreeditText", ""}, {"CommitText", "ই"}});
  h.word(a);
  h.event(a, "Disable");
  h.expect({{"UpdatePreeditText", ""}});
  require(!h.key(a, IBUS_KEY_k), "disable blocks composition");
  h.effects.clear();
  h.event(a, "Enable");
  // Legacy lifecycle is also supported.
  h.event(a, "FocusOut");
  h.event(a, "FocusIn");
  h.effects.clear();

  for (auto [purpose, hints] : std::vector<std::pair<guint, guint>>{
           {IBUS_INPUT_PURPOSE_PASSWORD, 0},
           {IBUS_INPUT_PURPOSE_PIN, 0},
           {IBUS_INPUT_PURPOSE_FREE_FORM, IBUS_INPUT_HINT_HIDDEN_TEXT}}) {
    h.word(a);
    h.content(a, purpose, hints);
    h.expect({{"UpdatePreeditText", ""}});
    require(!h.key(a, IBUS_KEY_k), "restricted field passes key through");
    h.effects.clear();
    h.event(a, "FocusOut");
    h.event(a, "FocusIn");
    require(!h.key(a, IBUS_KEY_i), "restriction survives refocus");
    h.content(a, IBUS_INPUT_PURPOSE_FREE_FORM);
    h.effects.clear();
    require(h.key(a, IBUS_KEY_i) && h.effects.back().text == "ই",
            "no restricted raw text retained");
    h.event(a, "Reset");
    h.effects.clear();
  }
  h.content(a, IBUS_INPUT_PURPOSE_FREE_FORM, IBUS_INPUT_HINT_PRIVATE);
  h.word(a); // Private hint does not introduce a Latin mode or a logger.
  h.event(a, "Reset");
  h.expect({{"UpdatePreeditText", ""}});
  require(h.key(a, IBUS_KEY_i) && h.effects.back().text == "ই",
          "reset discards");
  h.event(a, "Reset");
  h.effects.clear();
  h.word(a);
  // Caret rectangle and surrounding text alone are not document relocation.
  h.event(a, "SetCursorLocation", g_variant_new("(iiii)", 20, 40, 2, 18));
  auto *text = ibus_text_new_from_static_string("synthetic");
  auto *serialized = ibus_serializable_serialize(IBUS_SERIALIZABLE(text));
  h.event(a, "SetSurroundingText", g_variant_new("(vuu)", serialized, 2, 2));
  g_object_unref(text);
  require(h.key(a, IBUS_KEY_Escape), "caret/surrounding text preserves word");
  h.expect({{"UpdatePreeditText", ""}, {"CommitText", "কি"}});
  h.word(a);
  g_variant_unref(
      h.call(a, "Destroy", nullptr, "org.freedesktop.IBus.Service"));
  h.expect({}); // No stale commit or publication on destruction.
  // B still owns its independently pending word.
  require(h.key(b, IBUS_KEY_Escape), "other context survives destruction");
  h.expect({{"UpdatePreeditText", ""}, {"CommitText", "ই"}});
  for (int i = 0; i < 200; ++i) {
    auto path = h.create();
    require(h.key(path, IBUS_KEY_k), "lifecycle allocation");
    h.effects.clear();
    g_variant_unref(
        h.call(path, "Destroy", nullptr, "org.freedesktop.IBus.Service"));
    h.expect({});
  }
  std::cout
      << "PASS: IBus factory and D-Bus editing, boundaries, "
         "modifiers/releases, "
         "Unicode, repeats, lifecycle, restrictions and context isolation\n";
}
} // namespace
int main(int argc, char **argv) {
  try {
    ibus_init();
    require(argc == 2 || argc == 3,
            "usage: harness ENGINE_EXECUTABLE [COMPONENT_XML]");
    if (argc == 3) {
      auto *component = ibus_component_new_from_file(argv[2]);
      require(component, "IBus parser accepts staged component");
      require(std::string(ibus_component_get_name(component)) ==
                  "org.freedesktop.IBus.JongBangla",
              "parsed service identifier");
      auto *engines = ibus_component_get_engines(component);
      require(g_list_length(engines) == 1 &&
                  std::string(ibus_engine_desc_get_name(
                      IBUS_ENGINE_DESC(engines->data))) == "jong-bangla",
              "parsed engine identifier");
      g_list_free(engines);
      g_object_unref(component);
    }
    run(argv[1]);
    return 0;
  } catch (const std::exception &error) {
    std::cerr << "IBus harness failed: " << error.what() << '\n';
    return 1;
  }
}
