"""Linux desktop-only transport for the issue #47 maintainer-run proof.

Uses system PyGObject/AT-SPI and the XDG RemoteDesktop portal; no imports from
the typing engine, DOM setters, clipboard operations, or persistent settings.
"""

from contextlib import contextmanager
import hashlib
import os
from pathlib import Path
import signal
import shutil
import subprocess
import tempfile
import time
from types import SimpleNamespace
import uuid

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi, Gio, GLib

from desktop_proof import ProofError, command, wait_for


PORTAL = "org.freedesktop.portal.Desktop"
REMOTE = "org.freedesktop.portal.RemoteDesktop"
PORTAL_PATH = "/org/freedesktop/portal/desktop"


class KeyboardPortal:
    def __init__(self):
        self.bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        self.session = None

    def call(self, path, interface, method, signature, values):
        return self.bus.call_sync(PORTAL, path, interface, method,
                                  GLib.Variant(signature, values), None,
                                  Gio.DBusCallFlags.NONE, 5000, None)

    def request(self, method, signature, values):
        token = "jong_" + uuid.uuid4().hex
        options = dict(values[-1], handle_token=GLib.Variant("s", token))
        sender = self.bus.get_unique_name()[1:].replace(".", "_")
        path = f"/org/freedesktop/portal/desktop/request/{sender}/{token}"
        response = []
        loop = GLib.MainLoop()

        def received(_bus, _sender, _path, _interface, _signal, parameters):
            response.append(parameters.unpack())
            loop.quit()

        subscription = self.bus.signal_subscribe(
            PORTAL, "org.freedesktop.portal.Request", "Response", path, None,
            Gio.DBusSignalFlags.NONE, received)
        def expired():
            loop.quit()
            return False
        timer = GLib.timeout_add_seconds(60, expired)
        try:
            returned = self.call(PORTAL_PATH, REMOTE, method, signature,
                                 (*values[:-1], options)).unpack()[0]
            if returned != path:
                raise ProofError("Portal returned an unexpected request handle")
            if not response:
                loop.run()
            if not response:
                self.call(path, "org.freedesktop.portal.Request", "Close", "()", ())
                raise ProofError(f"{method}: desktop control request timed out")
            code, data = response[0]
            if code != 0:
                raise ProofError(f"{method}: desktop control was cancelled or denied")
            return data
        finally:
            self.bus.signal_unsubscribe(subscription)
            # The source may already have fired on timeout.
            if GLib.MainContext.default().find_source_by_id(timer):
                GLib.source_remove(timer)

    def start(self):
        data = self.request("CreateSession", "(a{sv})", ({
            "session_handle_token": GLib.Variant("s", "jong_" + uuid.uuid4().hex)},))
        self.session = data["session_handle"]
        self.request("SelectDevices", "(oa{sv})", (self.session, {
            "types": GLib.Variant("u", 1)}))  # Keyboard only; no screen/clipboard.
        data = self.request("Start", "(osa{sv})", (self.session, "", {}))
        if data.get("devices", 0) != 1:
            raise ProofError("Portal did not grant keyboard-only access")

    def key(self, code):
        try:
            self.call(PORTAL_PATH, REMOTE, "NotifyKeyboardKeycode", "(oa{sv}iu)",
                      (self.session, {}, code, 1))
        finally:
            self.call(PORTAL_PATH, REMOTE, "NotifyKeyboardKeycode", "(oa{sv}iu)",
                      (self.session, {}, code, 0))
        time.sleep(0.15)

    def close(self):
        if self.session:
            self.call(self.session, "org.freedesktop.portal.Session", "Close", "()", ())
            self.session = None


def owned(process, accessible):
    """Only accept live processes in the runner-created application session."""
    if process.poll() is not None:
        return False
    try:
        return os.getsid(accessible.get_process_id()) == process.pid
    except (ProcessLookupError, PermissionError):
        return False


def descendants(node):
    """Bounded traversal, called only after validating application ownership."""
    pending = [node]
    count = 0
    while pending:
        item = pending.pop()
        yield item
        count += 1
        if count >= 2000:
            raise ProofError("Owned accessibility tree exceeded proof limit")
        for index in range(item.get_child_count()):
            child = item.get_child_at_index(index)
            if child is not None:
                pending.append(child)


def wayland_title(log, token):
    """Keep only the boolean evidence, never raw Wayland protocol logs."""
    log.flush()
    size = os.fstat(log.fileno()).st_size
    content = os.pread(log.fileno(), min(size, 2_000_000), 0).decode(errors="replace")
    return any("xdg_toplevel" in line and "set_title" in line and token in line
               for line in content.splitlines())


class LinuxDesktop:
    def __init__(self):
        self.portal = None

    @staticmethod
    def remote(*args):
        return command(["fcitx5-remote", "--check", *args])

    def snapshot_engine(self):
        engine, state = self.remote("-n"), self.remote()
        if not engine or state not in ("1", "2"):
            raise ProofError("Fcitx5 must already be running with an input method selected")
        return engine, state

    def restore_engine(self, previous):
        engine, state = previous
        self.remote("-s", engine)
        self.remote("-o" if state == "2" else "-c")

    def __enter__(self):
        Atspi.init()
        Atspi.set_timeout(1000, 1000)
        try:
            self.portal = KeyboardPortal()
            self.portal.start()
        except BaseException:
            try:
                if self.portal:
                    self.portal.close()
            finally:
                Atspi.exit()
            raise
        return self

    def __exit__(self, *_):
        try:
            if self.portal:
                self.portal.close()
        finally:
            Atspi.exit()

    @contextmanager
    def application(self, name):
        with tempfile.TemporaryDirectory(prefix="jong-desktop-") as folder, tempfile.TemporaryFile() as log:
            directory = Path(folder)
            token = "jong-proof-" + uuid.uuid4().hex
            env = dict(os.environ, WAYLAND_DEBUG="client")
            for variable, leaf in (("XDG_CONFIG_HOME", "config"), ("XDG_DATA_HOME", "data"),
                                   ("XDG_CACHE_HOME", "cache"), ("XDG_STATE_HOME", "state")):
                env[variable] = str(directory / leaf)
            env.pop("NO_AT_BRIDGE", None)
            if name == "kwrite":
                document = directory / f"{token}.txt"
                document.write_text("")
                # Keep recent-file/session/config writes outside the user's profile.
                env.update(QT_QPA_PLATFORM="wayland", QT_LINUX_ACCESSIBILITY_ALWAYS_ON="1")
                args = ["kwrite", str(document)]
            else:
                document = directory / "proof.html"
                document.write_text(f'<!doctype html><meta charset="utf-8"><title>{token}</title>'
                                    f'<label for="proof">{token}</label>'
                                    '<textarea id="proof" autofocus></textarea>')
                profile = directory / "profile"
                profile.mkdir()
                (profile / "user.js").write_text(
                    'user_pref("accessibility.force_disabled", -1);\n'
                    'user_pref("browser.shell.checkDefaultBrowser", false);\n'
                    'user_pref("browser.aboutwelcome.enabled", false);\n'
                    'user_pref("browser.startup.homepage_override.mstone", "ignore");\n'
                    'user_pref("datareporting.policy.dataSubmissionEnabled", false);\n'
                    'user_pref("toolkit.telemetry.enabled", false);\n')
                env.update(MOZ_ENABLE_WAYLAND="1", GDK_BACKEND="wayland")
                args = ["firefox", "--no-remote", "--new-instance", "--profile", str(profile),
                        "--offline", document.as_uri()]
            process = subprocess.Popen(args, env=env, stdin=subprocess.DEVNULL,
                                       stdout=subprocess.DEVNULL, stderr=log, start_new_session=True)
            app = SimpleNamespace(name=name, process=process, token=token, log=log,
                                  field=None, window=None)
            try:
                app.field = wait_for(lambda: self.find_field(app), f"{name} owned editable field")
                wait_for(lambda: wayland_title(log, token), f"{name} Wayland test-window title")
                yield app
            finally:
                # Never terminate another instance or send application-wide close commands.
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait(timeout=3)
                except ProcessLookupError:
                    process.wait(timeout=3)

    def find_field(self, app):
        desktop = Atspi.get_desktop(0)
        for index in range(desktop.get_child_count()):
            root = desktop.get_child_at_index(index)
            if root is None or not owned(app.process, root):
                continue
            for window in (root.get_child_at_index(i) for i in range(root.get_child_count())):
                if window is None or app.token not in (window.get_name() or ""):
                    continue
                candidates = []
                for node in descendants(window):
                    if not owned(app.process, node):
                        continue
                    states = node.get_state_set()
                    if (states.contains(Atspi.StateType.EDITABLE)
                            and states.contains(Atspi.StateType.FOCUSABLE)
                            and states.contains(Atspi.StateType.SHOWING)
                            and states.contains(Atspi.StateType.MULTI_LINE)
                            and node.get_text_iface() is not None
                            and (app.name != "firefox" or node.get_name() == app.token)):
                        candidates.append(node)
                if len(candidates) == 1:
                    app.window = window
                    return candidates[0]
                if len(candidates) > 1:
                    raise ProofError("Ambiguous owned editable field")
        return None

    def focus(self, app):
        if not owned(app.process, app.field):
            raise ProofError("Application ownership check failed")
        if not app.field.get_component_iface().grab_focus():
            raise ProofError("Could not focus the test field")
        def focused():
            app.field.clear_cache()
            app.window.clear_cache()
            return (app.field.get_state_set().contains(Atspi.StateType.FOCUSED)
                    and app.window.get_state_set().contains(Atspi.StateType.ACTIVE))
        wait_for(focused, "owned active window and field keyboard focus")

    def guard(self, app, engine=None):
        app.field.clear_cache()
        app.window.clear_cache()
        if not owned(app.process, app.field) or not owned(app.process, app.window):
            raise ProofError("Test application exited or ownership changed")
        if (app.token not in (app.window.get_name() or "")
                or not app.window.get_state_set().contains(Atspi.StateType.ACTIVE)
                or not app.field.get_state_set().contains(Atspi.StateType.FOCUSED)):
            raise ProofError("Test field lost focus; stopped before further input")
        if engine is not None and self.remote("-n") != engine:
            raise ProofError("Focused input method is not the required engine")

    def select_engine(self, app, engine):
        self.guard(app)
        self.remote("-s", engine)
        wait_for(lambda: self.remote("-n") == engine, "focused engine selection")
        self.guard(app, engine)

    def text(self, app):
        if not owned(app.process, app.field):
            raise ProofError("Refusing text observation outside the owned test application")
        app.field.clear_cache()
        interface = app.field.get_text_iface()
        count = interface.get_character_count()
        if count > 64:
            raise ProofError("Owned field exceeded the synthetic proof text limit")
        return interface.get_text(0, count)

    def key(self, code):
        self.portal.key(code)

    def application_identity(self, app):
        executable = Path(shutil.which(app.name)).resolve()
        return {"backend": "wayland", "evidence": "owned xdg_toplevel test-title request",
                "pid": app.process.pid,
                "executable": str(executable),
                "executable_sha256": hashlib.sha256(executable.read_bytes()).hexdigest(),
                "toolkit": app.field.get_toolkit_name(),
                "toolkit_version": app.field.get_toolkit_version(),
                "packages": command(["pacman", "-Q", app.name, "fcitx5", "kwin",
                                     "plasma-workspace"]) if os.path.exists("/usr/bin/pacman")
                else "unavailable: record distribution package versions separately"}
