// MIT. Internal IBus engine type, no transliteration rules here.
#ifndef JONG_IBUS_ENGINE_H
#define JONG_IBUS_ENGINE_H
#include <ibus.h>
G_BEGIN_DECLS
GType jong_ibus_engine_get_type(void);
IBusFactory *jong_ibus_factory_new(GDBusConnection *connection);
#define JONG_TYPE_IBUS_ENGINE (jong_ibus_engine_get_type())
G_END_DECLS
#endif
