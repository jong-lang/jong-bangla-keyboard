// MIT. Native IBus events/UI only; Rust owns composition and transliteration.
#include "engine.h"
#include "../ffi/jong.h"

// IBus may reuse a global engine across fields. Every focus-in starts empty;
// matching focus-out clears it. No buffer is retained for a previous field.
typedef struct {
  IBusEngine parent;
  JongSession *session;
  gboolean focused;
  gboolean enabled;
  gchar *focus_id;
} JongIBusEngine;
typedef struct {
  IBusEngineClass parent;
} JongIBusEngineClass;

G_DEFINE_TYPE(JongIBusEngine, jong_ibus_engine, IBUS_TYPE_ENGINE)

static void clear_preedit(IBusEngine *engine) {
  ibus_engine_update_preedit_text_with_mode(
      engine, ibus_text_new_from_static_string(""), 0, FALSE,
      IBUS_ENGINE_PREEDIT_COMMIT);
}

static void discard(IBusEngine *engine) {
  JongIBusEngine *self = (JongIBusEngine *)engine;
  if (self->session)
    jong_session_action(self->session, JongReset, 0);
  clear_preedit(engine);
}

static gboolean restricted(IBusEngine *engine) {
  guint purpose = 0, hints = 0;
  ibus_engine_get_content_type(engine, &purpose, &hints);
  return purpose == IBUS_INPUT_PURPOSE_PASSWORD ||
         purpose == IBUS_INPUT_PURPOSE_PIN ||
         (hints & IBUS_INPUT_HINT_HIDDEN_TEXT) != 0;
}

static gboolean apply(IBusEngine *engine, enum JongAction action, guint scalar,
                      gboolean *consumed) {
  JongIBusEngine *self = (JongIBusEngine *)engine;
  JongResult result = jong_session_action(self->session, action, scalar);
  if (result.status != 0) {
    discard(engine);
    *consumed = TRUE; // Never replay a possibly applied mutation after failure.
    return FALSE;
  }
  *consumed = result.consumed != 0;
  // Copy BOTH borrowed spans before calling IBus; no pointer escapes Rust's
  // next-action lifetime. IBusText copies UTF-8 and consumes floating objects.
  gchar *preedit = result.preedit_len ? g_strndup((const gchar *)result.preedit,
                                                  result.preedit_len)
                                      : g_strdup("");
  gchar *committed =
      result.committed_len
          ? g_strndup((const gchar *)result.committed, result.committed_len)
          : g_strdup("");
  glong length = g_utf8_strlen(preedit, -1);
  if ((guint64)length > G_MAXUINT) {
    g_free(preedit);
    g_free(committed);
    discard(engine);
    *consumed = TRUE;
    return FALSE;
  }
  IBusText *text = ibus_text_new_from_string(preedit);
  if (length)
    ibus_text_append_attribute(text, IBUS_ATTR_TYPE_UNDERLINE,
                               IBUS_ATTR_UNDERLINE_SINGLE, 0, (guint)length);
  // IBus uses Unicode character positions, unlike Fcitx's byte offsets.
  // IBus/frontend owns focus-out and disable commits; callbacks only discard.
  ibus_engine_update_preedit_text_with_mode(
      engine, text, (guint)length, length != 0, IBUS_ENGINE_PREEDIT_COMMIT);
  if (*committed)
    ibus_engine_commit_text(engine, ibus_text_new_from_string(committed));
  g_free(preedit);
  g_free(committed);
  return TRUE;
}

static gboolean modifier_only(guint key) {
  return (key >= IBUS_KEY_Shift_L && key <= IBUS_KEY_Hyper_R) ||
         key == IBUS_KEY_Mode_switch || key == IBUS_KEY_Num_Lock ||
         key == IBUS_KEY_Scroll_Lock || key == IBUS_KEY_ISO_Lock ||
         key == IBUS_KEY_ISO_Level2_Latch ||
         (key >= IBUS_KEY_ISO_Level3_Shift &&
          key <= IBUS_KEY_ISO_Level3_Lock) ||
         (key >= IBUS_KEY_ISO_Level5_Shift &&
          key <= IBUS_KEY_ISO_Level5_Lock) ||
         (key >= IBUS_KEY_ISO_Group_Latch &&
          key <= IBUS_KEY_ISO_Last_Group_Lock);
}

static gboolean compose_prefix(guint key) {
  return key == IBUS_KEY_Multi_key ||
         (key >= IBUS_KEY_dead_grave && key <= IBUS_KEY_dead_currency) ||
         (key >= IBUS_KEY_dead_lowline &&
          key <= IBUS_KEY_dead_longsolidusoverlay) ||
         (key >= IBUS_KEY_dead_a && key <= IBUS_KEY_dead_greek);
}

static gboolean process_key(IBusEngine *engine, guint key, guint keycode,
                            guint state) {
  (void)keycode; // Use resolved keyvals; never reconstruct a keyboard layout.
  JongIBusEngine *self = (JongIBusEngine *)engine;
  if (!self->focused || !self->enabled || restricted(engine)) {
    discard(engine);
    return FALSE;
  }
  if ((state & (IBUS_RELEASE_MASK | IBUS_FORWARD_MASK)) || modifier_only(key) ||
      compose_prefix(key))
    return FALSE;

  // Mod2 is Num Lock. Mod5/AltGr remains ambiguous and is NOT erased into text.
  guint mods = state & ~(IBUS_LOCK_MASK | IBUS_MOD2_MASK | IBUS_HANDLED_MASK);
  enum JongAction action = JongCommit;
  if (mods == 0 && key == IBUS_KEY_BackSpace)
    action = JongBackspace;
  else if (mods == IBUS_CONTROL_MASK && key == IBUS_KEY_BackSpace)
    action = JongCtrlBackspace;
  else if (mods == 0 && key == IBUS_KEY_space)
    action = JongSpace;
  else if (mods == 0 && (key == IBUS_KEY_Return || key == IBUS_KEY_KP_Enter))
    action = JongEnter;
  else if (mods == 0 && key == IBUS_KEY_Escape)
    action = JongEscape;
  else if ((mods & ~IBUS_SHIFT_MASK) == 0 && key != IBUS_KEY_space &&
           key != IBUS_KEY_KP_Space) {
    gunichar scalar = ibus_keyval_to_unicode(key);
    if (key >= IBUS_KEY_KP_0 && key <= IBUS_KEY_KP_9)
      scalar = '0' + key - IBUS_KEY_KP_0;
    if (scalar && g_unichar_validate(scalar) && !g_unichar_iscntrl(scalar) &&
        !g_unichar_isspace(scalar)) {
      gboolean consumed = FALSE;
      if (!apply(engine, JongInsert, scalar, &consumed) || consumed)
        return consumed;
    }
  }
  gboolean consumed = FALSE;
  apply(engine, action, 0, &consumed);
  // FALSE lets IBus deliver the ORIGINAL key once, after preedit/commit
  // signals. Never call forward_key_event as well (including synchronous
  // clients).
  return consumed;
}

static void focus_in(IBusEngine *engine) {
  JongIBusEngine *self = (JongIBusEngine *)engine;
  discard(engine);
  g_clear_pointer(&self->focus_id, g_free);
  self->focused = TRUE;
}

static void focus_out(IBusEngine *engine) {
  JongIBusEngine *self = (JongIBusEngine *)engine;
  self->focused = FALSE;
  g_clear_pointer(&self->focus_id, g_free);
  discard(engine); // PREEDIT_COMMIT already delegated delivery to IBus/client.
}

static void focus_in_id(IBusEngine *engine, const gchar *path,
                        const gchar *client) {
  (void)client;
  focus_in(engine);
  ((JongIBusEngine *)engine)->focus_id = g_strdup(path);
}

static void focus_out_id(IBusEngine *engine, const gchar *path) {
  JongIBusEngine *self = (JongIBusEngine *)engine;
  // A stale callback must not discard a newly focused context's composition.
  if (g_strcmp0(self->focus_id, path) == 0)
    focus_out(engine);
}

static void enable(IBusEngine *engine) {
  ((JongIBusEngine *)engine)->enabled = TRUE;
  discard(engine);
}

static void disable(IBusEngine *engine) {
  ((JongIBusEngine *)engine)->enabled = FALSE;
  focus_out(engine);
}

static void content_type(IBusEngine *engine, guint purpose, guint hints) {
  if (purpose == IBUS_INPUT_PURPOSE_PASSWORD ||
      purpose == IBUS_INPUT_PURPOSE_PIN ||
      (hints & IBUS_INPUT_HINT_HIDDEN_TEXT))
    discard(engine);
}

static void destroy(IBusObject *object) {
  JongIBusEngine *self = (JongIBusEngine *)object;
  // Destruction discards without publication or a commit to another field.
  jong_session_free(self->session);
  self->session = NULL;
  g_clear_pointer(&self->focus_id, g_free);
  IBUS_OBJECT_CLASS(jong_ibus_engine_parent_class)->destroy(object);
}

static void jong_ibus_engine_init(JongIBusEngine *self) {
  self->session = jong_session_new();
  // Null allocation is contained by apply's status/error recovery, no raw echo.
}

static void jong_ibus_engine_class_init(JongIBusEngineClass *klass) {
  IBusEngineClass *engine = IBUS_ENGINE_CLASS(klass);
  engine->process_key_event = process_key;
  engine->focus_in = focus_in;
  engine->focus_out = focus_out;
  engine->focus_in_id = focus_in_id;
  engine->focus_out_id = focus_out_id;
  engine->enable = enable;
  engine->disable = disable;
  engine->reset = discard;
  engine->set_content_type = content_type;
  IBUS_OBJECT_CLASS(klass)->destroy = destroy;
}

static IBusEngine *create_engine(IBusFactory *factory, const gchar *name,
                                 gpointer data) {
  (void)data;
  static guint64 serial = 0;
  if (g_strcmp0(name, "jong-bangla") != 0 || serial == G_MAXUINT64)
    return NULL;
  gchar *path = g_strdup_printf(
      "/org/freedesktop/IBus/Engine/JongBangla/%" G_GUINT64_FORMAT, ++serial);
  IBusEngine *engine = g_object_new(
      JONG_TYPE_IBUS_ENGINE, "engine-name", name, "object-path", path,
      "connection", ibus_service_get_connection(IBUS_SERVICE(factory)),
      "has-focus-id", TRUE, NULL);
  g_free(path);
  if (!((JongIBusEngine *)engine)->session) {
    ibus_object_destroy(IBUS_OBJECT(engine));
    g_object_unref(engine);
    return NULL;
  }
  return engine;
}

IBusFactory *jong_ibus_factory_new(GDBusConnection *connection) {
  IBusFactory *factory = ibus_factory_new(connection);
  g_signal_connect(factory, "create-engine", G_CALLBACK(create_engine), NULL);
  return factory;
}
