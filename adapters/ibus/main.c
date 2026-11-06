// MIT. IBus-launched service only: never starts a daemon or changes settings.
#include "engine.h"
#include <glib-unix.h>
#include <signal.h>

static void disconnected(IBusBus *bus, gpointer data) {
  (void)bus;
  (void)data;
  ibus_quit();
}

static gboolean stop(gpointer data) {
  (void)data;
  ibus_quit();
  return G_SOURCE_CONTINUE;
}

int main(int argc, char **argv) {
  gboolean launched = FALSE, version = FALSE;
  GOptionEntry entries[] = {
      {"ibus", 0, 0, G_OPTION_ARG_NONE, &launched, "Launched by IBus", NULL},
      {"version", 0, 0, G_OPTION_ARG_NONE, &version, "Print version", NULL},
      {NULL, 0, 0, 0, NULL, NULL, NULL}};
  GOptionContext *options = g_option_context_new("- Jong Bangla IBus engine");
  g_option_context_add_main_entries(options, entries, NULL);
  GError *error = NULL;
  if (!g_option_context_parse(options, &argc, &argv, &error)) {
    g_printerr("Invalid engine arguments: %s\n", error->message);
    g_clear_error(&error);
    g_option_context_free(options);
    return 1;
  }
  g_option_context_free(options);
  if (version) {
    g_print("Jong Bangla IBus %s\n", JONG_VERSION);
    return 0;
  }
  if (!launched || argc != 1) {
    g_printerr("This service must be launched by IBus with --ibus.\n");
    return 1;
  }
  ibus_init();
  IBusBus *bus = ibus_bus_new();
  if (!ibus_bus_is_connected(bus)) {
    g_printerr("No IBus connection; no daemon was started.\n");
    g_object_unref(bus);
    return 1;
  }
  g_signal_connect(bus, "disconnected", G_CALLBACK(disconnected), NULL);
  IBusFactory *factory = jong_ibus_factory_new(ibus_bus_get_connection(bus));
  // DO_NOT_QUEUE: a second instance must fail rather than wait invisibly.
  if (ibus_bus_request_name(bus, "org.freedesktop.IBus.JongBangla",
                            IBUS_BUS_NAME_FLAG_DO_NOT_QUEUE) !=
      IBUS_BUS_REQUEST_NAME_REPLY_PRIMARY_OWNER) {
    g_printerr("Cannot own the Jong Bangla IBus service name.\n");
    ibus_object_destroy(IBUS_OBJECT(factory));
    g_object_unref(factory);
    g_object_unref(bus);
    return 1;
  }
  guint sigint = g_unix_signal_add(SIGINT, stop, NULL);
  guint sigterm = g_unix_signal_add(SIGTERM, stop, NULL);
  ibus_main();
  g_source_remove(sigint);
  g_source_remove(sigterm);
  ibus_object_destroy(IBUS_OBJECT(factory));
  g_object_unref(factory);
  g_object_unref(bus);
  return 0;
}
