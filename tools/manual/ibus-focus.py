#!/usr/bin/env python3
"""Interactive synthetic-input probe; never inject keys or save typed text."""

import argparse
import os
import time

import gi


def describe(text):
    points = " ".join(f"U+{ord(char):04X}" for char in text) or "(empty)"
    return f"{text!r}\n{points}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gtk", choices=("3", "4"), required=True)
    parser.add_argument("--action", choices=("focus", "reset"), default="focus")
    args = parser.parse_args()
    if args.action == "reset" and args.gtk != "3":
        parser.error("the reset-only probe uses GTK3's public Entry.reset_im_context")

    gi.require_version("Gtk", f"{args.gtk}.0")
    from gi.repository import Gdk, GLib, GObject, Gtk

    app = Gtk.Application(application_id="org.jongbangla.ManualFocusProbe")

    def activate(application):
        window = Gtk.ApplicationWindow(application=application)
        window.set_title(f"Jong Bangla manual probe: GTK{args.gtk} / {args.action}")
        window.set_default_size(600, 420)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        for side in ("top", "bottom", "start", "end"):
            getattr(box, f"set_margin_{side}")(8)
        if args.gtk == "4":
            window.set_child(box)
            append = box.append
        else:
            window.add(box)

            def append(child):
                box.pack_start(child, False, False, 0)

        def label(text):
            item = Gtk.Label(label=text, xalign=0)
            if args.gtk == "4":
                item.set_wrap(True)
            else:
                item.set_line_wrap(True)
            append(item)
            return item

        display = Gdk.Display.get_default()
        version = ".".join(str(getattr(Gtk, f"get_{part}_version")())
                           for part in ("major", "minor", "micro"))
        module = os.environ.get("GTK_IM_MODULE", "(unset)")
        label(f"GTK {version}; {GObject.type_name(display)}; GTK_IM_MODULE={module}")
        label("Synthetic text only; values exclude preedit. Relaunch for each case.")
        entries = {}
        for name in ("A", "B"):
            entries[name] = Gtk.Entry()
            entries[name].set_placeholder_text(f"Field {name}")
            append(entries[name])

        prefix = "ki" if args.action == "focus" else "k"
        label(f"Select Jong Bangla. Arm; type {prefix} in A without Space. "
              "After the action, wait 2 seconds; type i and Space.")
        arm = Gtk.Button(label=f"Arm {args.action} in 8 seconds")
        append(arm)
        status = label("Not armed")
        values = label("")
        deadline = None
        action_id = None

        def refresh():
            values.set_text("A: " + describe(entries["A"].get_text()) + "\nB: "
                            + describe(entries["B"].get_text()))
            return True

        def tick():
            nonlocal action_id
            remaining = deadline - time.monotonic()
            if remaining > 0:
                status.set_text(f"Armed: {remaining:.1f} seconds remaining")
                return True
            # This callback moves focus or invokes the widget's public reset API.
            # It never calls IBus, inserts text, or synthesizes a keyboard event.
            if args.action == "focus":
                entries["B"].grab_focus()
                status.set_text("B.grab_focus() called. Wait 2s; type i and Space in B.")
            else:
                entries["A"].reset_im_context()
                status.set_text("A.reset_im_context() called. Stay in A. "
                                "Wait 2s; type i and Space.")
            refresh()
            action_id = None
            return False

        def start(_button):
            nonlocal deadline, action_id
            arm.set_sensitive(False)
            entries["A"].grab_focus()
            deadline = time.monotonic() + 8
            action_id = GLib.timeout_add(100, tick)

        arm.connect("clicked", start)
        # Polling observes committed widget values only; it does not change focus
        # or ask the framework to finalize composition to obtain a snapshot.
        refresh_id = GLib.timeout_add(100, refresh)

        def close(*_args):
            GLib.source_remove(refresh_id)
            if action_id is not None:
                GLib.source_remove(action_id)
            application.quit()
            return False

        window.connect("close-request" if args.gtk == "4" else "delete-event", close)
        if args.gtk == "3":
            window.show_all()
        window.present()

    app.connect("activate", activate)
    app.run([])


if __name__ == "__main__":
    main()
