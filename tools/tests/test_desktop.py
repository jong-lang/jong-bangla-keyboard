"""Desktop proof rejection/cleanup regressions; never access a desktop session."""

from contextlib import contextmanager
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch


TOOLS = Path(__file__).resolve().parents[1]
with patch.object(sys, "path", [str(TOOLS), *sys.path]):
    import desktop_proof as proof

# Backend tests use API doubles so ordinary tool tests need no GUI packages/bus.
gi = SimpleNamespace(require_version=Mock())
atspi = SimpleNamespace(StateType=SimpleNamespace(FOCUSED=1, ACTIVE=2))
with patch.dict(sys.modules, {"gi": gi, "gi.repository": SimpleNamespace(
        Atspi=atspi, Gio=SimpleNamespace(), GLib=SimpleNamespace(Variant=Mock()))}):
    spec = importlib.util.spec_from_file_location("desktop_linux_test", TOOLS / "desktop_linux.py")
    linux = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(linux)


def immediate(probe, description, timeout=15):
    value = probe()
    if not value:
        raise proof.ProofError(f"Timed out: {description}")
    return value


class DesktopDouble:
    def __init__(self, broken=None):
        self.broken = broken
        self.events = []
        self.closed = []
        self.restored = None
        self.focused = True

    def snapshot_engine(self):
        return ("original", "1")

    def restore_engine(self, previous):
        self.restored = previous
        if self.broken == "restore":
            raise proof.ProofError("restore failed")

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.closed.append("portal")

    @contextmanager
    def application(self, name):
        self.app = SimpleNamespace(name=name, text="")
        try:
            yield self.app
        finally:
            self.closed.append(name)

    def application_identity(self, app):
        return {"backend": "wayland"}

    def focus(self, app):
        pass

    def select_engine(self, app, engine):
        self.engine = engine

    def guard(self, app, engine):
        if not self.focused:
            raise proof.ProofError("wrong focus")

    def key(self, code):
        self.events.append((self.app.name, self.engine, code))
        if self.broken == "focus":
            self.focused = False
        if code == 57:
            bangla = self.engine == "jong-bangla"
            if self.broken == "always-converts":
                bangla = True
            if self.broken == "never-converts":
                bangla = False
            self.app.text += "কি " if bangla else "ki "

    def text(self, app):
        return app.text


class OrchestrationTests(unittest.TestCase):
    def setUp(self):
        self.wait_patch = patch.object(proof, "wait_for", side_effect=immediate)
        self.wait_patch.start()
        self.addCleanup(self.wait_patch.stop)
        self.sleep_patch = patch.object(proof.time, "sleep")
        self.sleep_patch.start()
        self.addCleanup(self.sleep_patch.stop)

    def run_proof(self, desktop):
        report = {"applications": {}, "cases": []}
        proof.prove(desktop, report)
        return report

    def test_both_apps_require_latin_control_and_jong_output(self):
        desktop = DesktopDouble()
        report = self.run_proof(desktop)
        self.assertEqual(report["proof_status"], "pass")
        self.assertEqual(len(report["cases"]), 4)
        self.assertEqual(desktop.closed, ["kwrite", "firefox", "portal"])
        self.assertEqual(desktop.restored, ("original", "1"))
        self.assertEqual([case["actual"] for case in report["cases"]],
                         ["ki ", "ki কি ", "ki ", "ki কি "])

    def test_inactive_control_and_active_conversion_fail_independently(self):
        for broken in ("always-converts", "never-converts"):
            with self.subTest(broken=broken):
                desktop = DesktopDouble(broken)
                with self.assertRaisesRegex(proof.ProofError, "exact committed text"):
                    self.run_proof(desktop)
                self.assertEqual(desktop.restored, ("original", "1"))
                self.assertEqual(desktop.closed, ["kwrite", "portal"])

    def test_focus_loss_stops_before_next_key(self):
        desktop = DesktopDouble("focus")
        with self.assertRaisesRegex(proof.ProofError, "wrong focus"):
            self.run_proof(desktop)
        self.assertEqual(len(desktop.events), 1)
        self.assertEqual(desktop.restored, ("original", "1"))

    def test_failed_restore_cannot_leave_passed_report(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(proof, "identity", return_value={}):
            output = Path(folder) / "report"
            self.assertEqual(proof.run(output, lambda: DesktopDouble("restore"), TOOLS.parent), 1)
            report = json.loads((output / "report.json").read_text())
            self.assertEqual(report["proof_status"], "failed")
            self.assertEqual(report["acceptance_status"], "incomplete")

    def test_failed_application_cleanup_invalidates_completed_cases(self):
        class CleanupFailure(DesktopDouble):
            @contextmanager
            def application(self, name):
                with super().application(name) as app:
                    yield app
                if name == "firefox":
                    raise proof.ProofError("owned application session kill timed out")

        desktop = CleanupFailure()
        with tempfile.TemporaryDirectory() as folder, patch.object(proof, "identity", return_value={}):
            output = Path(folder) / "report"
            self.assertEqual(proof.run(output, lambda: desktop, TOOLS.parent), 1)
            report = json.loads((output / "report.json").read_text())
            self.assertEqual(len(report["cases"]), 4)
            self.assertTrue(all(case["status"] == "pass" for case in report["cases"]))
            self.assertEqual(report["proof_status"], "failed")
            self.assertIn("session kill timed out", report["error"])
            self.assertEqual(desktop.restored, ("original", "1"))

    def test_passed_proof_is_not_full_acceptance(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(proof, "identity", return_value={}):
            output = Path(folder) / "report"
            self.assertEqual(proof.run(output, DesktopDouble, TOOLS.parent), 0)
            report = json.loads((output / "report.json").read_text())
            self.assertEqual(report["proof_status"], "pass")
            self.assertEqual(report["acceptance_status"], "incomplete")
            with self.assertRaisesRegex(proof.ProofError, "existing reports were left untouched"):
                proof.run(output, DesktopDouble, TOOLS.parent)
            self.assertEqual(json.loads((output / "report.json").read_text()), report)

    def test_initialization_failure_retains_incomplete_report(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(proof, "identity", return_value={}):
            output = Path(folder) / "report"
            with patch.object(proof, "prove", side_effect=RuntimeError("portal unavailable")):
                self.assertEqual(proof.run(output, DesktopDouble, TOOLS.parent), 1)
            report = json.loads((output / "report.json").read_text())
            self.assertEqual(report["cases"], [])
            self.assertEqual(report["proof_status"], "failed")

    def test_original_portal_failure_survives_cleanup_failure(self):
        def broken_proof(*_):
            try:
                raise proof.ProofError("Start: desktop control was denied")
            finally:
                raise proof.ProofError("Session.Close: object no longer exists")
        with tempfile.TemporaryDirectory() as folder, \
                patch.object(proof, "identity", return_value={}), \
                patch.object(proof, "prove", side_effect=broken_proof):
            output = Path(folder) / "report"
            self.assertEqual(proof.run(output, DesktopDouble, TOOLS.parent), 1)
            report = json.loads((output / "report.json").read_text())
            self.assertEqual(report["error_chain"], ["Start: desktop control was denied",
                                                    "Session.Close: object no longer exists"])
            self.assertIn("Start: desktop control was denied", (output / "summary.txt").read_text())
            self.assertEqual(report["cases"], [])

    def test_explicit_cause_and_cyclic_context_are_bounded(self):
        primary = proof.ProofError("primary")
        wrapper = proof.ProofError("wrapper")
        wrapper.__cause__ = primary
        primary.__context__ = wrapper
        self.assertEqual(proof.failure_chain(wrapper), ["primary", "wrapper"])

    def test_cli_requires_explicit_run_and_output(self):
        result = subprocess.run([sys.executable, TOOLS / "check-desktop.py", "--run"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("--run requires --output", result.stderr)

    def test_cli_prerequisite_failure_does_not_access_desktop(self):
        with patch.dict("os.environ", {"XDG_SESSION_TYPE": "x11"}):
            with self.assertRaisesRegex(proof.ProofError, "Wayland"):
                proof.prerequisites()

    def test_wait_is_bounded(self):
        self.wait_patch.stop()
        with patch.object(proof.time, "monotonic", side_effect=[0, 1]):
            with self.assertRaisesRegex(proof.ProofError, "Timed out"):
                proof.wait_for(lambda: False, "test", timeout=1)


class BackendTests(unittest.TestCase):
    def engine_backend(self, state="1", selected="another-im"):
        desktop = linux.LinuxDesktop()
        controller = SimpleNamespace(state=state, selected=selected, group="test-group",
                                     reject_selection=False, reject_state=False)

        def remote(*args):
            if args == ("-n",):
                return controller.selected if controller.state == "2" else "keyboard-us"
            if not args:
                return controller.state
            if args[0] == "-s" and not controller.reject_selection:
                if args[1] == "keyboard-us":
                    controller.state = "1"
                else:
                    controller.selected = args[1]
                    controller.state = "2"
            elif args[0] in ("-o", "-c") and not controller.reject_state:
                controller.state = "2" if args[0] == "-o" else "1"
            return ""

        desktop.remote = Mock(side_effect=remote)
        desktop.group_selection = Mock(side_effect=lambda: (
            controller.group, controller.selected, "keyboard-us"))
        return desktop, controller

    def test_restore_preserves_third_method_for_inactive_and_active_starts(self):
        for state in ("1", "2"):
            with self.subTest(state=state):
                desktop, controller = self.engine_backend(state)
                previous = desktop.snapshot_engine()
                desktop.remote("-s", "keyboard-us")
                desktop.remote("-s", "jong-bangla")
                desktop.restore_engine(previous)
                self.assertEqual(controller.selected, "another-im")
                self.assertEqual(controller.state, state)
                self.assertEqual(desktop.snapshot_engine(), previous)
                desktop.remote("-o")
                self.assertEqual(desktop.remote("-n"), "another-im")

    def test_unobserved_default_or_state_restoration_fails(self):
        for rejected in ("reject_selection", "reject_state"):
            with self.subTest(rejected=rejected):
                desktop, controller = self.engine_backend()
                previous = desktop.snapshot_engine()
                desktop.remote("-s", "jong-bangla")
                setattr(controller, rejected, True)
                with patch.object(linux, "wait_for", side_effect=immediate):
                    with self.assertRaisesRegex(proof.ProofError, "restoration"):
                        desktop.restore_engine(previous)

    def test_restore_does_not_modify_a_different_group(self):
        desktop, controller = self.engine_backend()
        previous = desktop.snapshot_engine()
        controller.group = "other-group"
        desktop.remote.reset_mock()
        with self.assertRaisesRegex(proof.ProofError, "group changed"):
            desktop.restore_engine(previous)
        desktop.remote.assert_not_called()

    def test_unrestorable_effective_selection_is_rejected_before_mutation(self):
        desktop, _controller = self.engine_backend("2")
        desktop.group_selection.side_effect = lambda: ("test-group", "different-default", "keyboard-us")
        with self.assertRaisesRegex(proof.ProofError, "restorable"):
            desktop.snapshot_engine()
        self.assertEqual(desktop.remote.call_args_list, [unittest.mock.call("-n"),
                                                        unittest.mock.call()])

    def test_group_selection_reads_default_from_controller_without_activation(self):
        bus = Mock()
        bus.call_sync.return_value.unpack.return_value = (
            "test-group", "another-im", "us", {},
            [("keyboard-us",), ("jong-bangla",), ("another-im",)])
        gio = SimpleNamespace(bus_get_sync=Mock(return_value=bus),
                              BusType=SimpleNamespace(SESSION=1),
                              DBusCallFlags=SimpleNamespace(NONE=0))
        with patch.object(linux, "Gio", gio):
            self.assertEqual(linux.LinuxDesktop.group_selection(),
                             ("test-group", "another-im", "keyboard-us"))
        self.assertEqual(bus.call_sync.call_args.args[:4], (
            "org.fcitx.Fcitx5", "/controller", "org.fcitx.Fcitx.Controller1",
            "FullInputMethodGroupInfo"))

    def focus_app(self, focused=False, active=True):
        field, window = Mock(), Mock()
        field.get_state_set.return_value.contains.return_value = focused
        window.get_state_set.return_value.contains.return_value = active
        window.get_name.return_value = "owned"
        field.get_component_iface.return_value.grab_focus.return_value = False
        field.get_action_iface.return_value = None
        field.get_parent.return_value = window
        window.get_action_iface.return_value = None
        return SimpleNamespace(name="kwrite", process=Mock(), field=field, window=window,
                               token="owned", focus_attempts=[])

    def test_already_focused_owned_field_needs_no_grab_focus(self):
        desktop = linux.LinuxDesktop()
        app = self.focus_app(focused=True)
        with patch.object(linux, "owned", return_value=True):
            desktop.focus(app)
        app.field.get_component_iface.assert_not_called()
        self.assertEqual(app.focus_attempts, [{"method": "initial_state", "field_focused": True,
                                               "window_active": True}])

    def test_false_focus_request_can_succeed_only_with_observed_focus(self):
        desktop = linux.LinuxDesktop()
        app = self.focus_app()
        def focused_despite_false():
            app.field.get_state_set.return_value.contains.return_value = True
            return False
        app.field.get_component_iface.return_value.grab_focus.side_effect = focused_despite_false
        with patch.object(linux, "owned", return_value=True):
            desktop.focus(app)
        self.assertEqual(app.focus_attempts[-1]["accepted"], False)
        self.assertEqual(app.focus_attempts[-1]["field_focused"], True)

    def test_successful_focus_request_without_focus_still_fails(self):
        desktop = linux.LinuxDesktop()
        app = self.focus_app()
        app.field.get_component_iface.return_value.grab_focus.return_value = True
        with patch.object(linux, "owned", return_value=True), \
                patch.object(linux, "wait_for", side_effect=immediate):
            with self.assertRaisesRegex(proof.ProofError, "keyboard focus"):
                desktop.focus(app)
        self.assertEqual(app.focus_attempts[-1]["field_focused"], False)

    def test_parent_focus_action_must_focus_the_actual_field_and_window(self):
        desktop = linux.LinuxDesktop()
        app = self.focus_app(active=False)
        action = app.window.get_action_iface.return_value = Mock()
        action.get_n_actions.return_value = 2
        action.get_action_name.side_effect = ["press", "SetFocus"]
        def focus_target(index):
            self.assertEqual(index, 1)
            app.field.get_state_set.return_value.contains.return_value = True
            app.window.get_state_set.return_value.contains.return_value = True
            return True
        action.do_action.side_effect = focus_target
        with patch.object(linux, "owned", return_value=True):
            desktop.focus(app)
        action.do_action.assert_called_once_with(1)
        self.assertEqual(app.focus_attempts[-1]["method"], "SetFocus")

    def test_focused_field_in_inactive_window_is_not_accepted(self):
        desktop = linux.LinuxDesktop()
        app = self.focus_app(focused=True, active=False)
        with patch.object(linux, "owned", return_value=True), \
                patch.object(linux, "wait_for", side_effect=immediate):
            with self.assertRaisesRegex(proof.ProofError, "keyboard focus"):
                desktop.focus(app)
        self.assertFalse(app.focus_attempts[-1]["window_active"])

    def test_focus_actions_cannot_escape_owned_test_window_ancestry(self):
        desktop = linux.LinuxDesktop()
        app = self.focus_app()
        unrelated_parent = Mock()
        unrelated_parent.get_parent.return_value = None
        app.field.get_parent.return_value = unrelated_parent
        with patch.object(linux, "owned", return_value=True), \
                patch.object(linux, "wait_for", side_effect=immediate):
            with self.assertRaises(proof.ProofError):
                desktop.focus(app)
        unrelated_parent.get_action_iface.assert_not_called()

    def test_wayland_evidence_requires_the_owned_surface_title(self):
        for line, expected in [
            (' -> xdg_toplevel#7.set_title("jong-proof-owned")', True),
            (' -> xdg_toplevel#7.set_title("other-window")', False),
            ('jong-proof-owned: using Wayland', False),
        ]:
            with self.subTest(line=line), tempfile.TemporaryFile() as log:
                log.write(line.encode())
                self.assertEqual(linux.wayland_title(log, "jong-proof-owned"), expected)

    def test_ownership_requires_live_runner_created_session(self):
        process = Mock(pid=123)
        process.poll.return_value = None
        accessible = Mock()
        accessible.get_process_id.return_value = 456
        with patch.object(linux.os, "getsid", return_value=123):
            self.assertTrue(linux.owned(process, accessible))
        with patch.object(linux.os, "getsid", return_value=999):
            self.assertFalse(linux.owned(process, accessible))
        process.poll.return_value = 0
        self.assertFalse(linux.owned(process, accessible))

    def test_portal_releases_key_even_when_press_fails(self):
        portal = object.__new__(linux.KeyboardPortal)
        portal.session = "/synthetic/session"
        portal.call = Mock(side_effect=[proof.ProofError("press failed"), None])
        with self.assertRaises(proof.ProofError):
            portal.key(37)
        self.assertEqual(portal.call.call_args_list[0].args[-1][-1], 1)
        self.assertEqual(portal.call.call_args_list[1].args[-1][-1], 0)

    def test_portal_requires_keyboard_grant(self):
        portal = object.__new__(linux.KeyboardPortal)
        portal.request = Mock(side_effect=[{"session_handle": "/test"}, {}, {"devices": 0}])
        with self.assertRaisesRegex(proof.ProofError, "keyboard-only"):
            portal.start()

    def test_wrong_focus_blocks_engine_changes_and_input(self):
        desktop = linux.LinuxDesktop()
        desktop.remote = Mock()
        app = SimpleNamespace(process=Mock(), field=Mock(), window=Mock(), token="owned")
        app.window.get_name.return_value = "owned"
        app.window.get_state_set.return_value.contains.return_value = True
        app.field.get_state_set.return_value.contains.return_value = False
        with patch.object(linux, "owned", return_value=True):
            with self.assertRaisesRegex(proof.ProofError, "lost focus"):
                desktop.select_engine(app, "jong-bangla")
        desktop.remote.assert_not_called()

    def test_unowned_field_is_not_read(self):
        desktop = linux.LinuxDesktop()
        app = SimpleNamespace(process=Mock(), field=Mock())
        with patch.object(linux, "owned", return_value=False):
            with self.assertRaisesRegex(proof.ProofError, "Refusing"):
                desktop.text(app)
        app.field.get_text_iface.assert_not_called()

    def test_text_read_uses_interface_despite_accessible_method_collision(self):
        class AccessibleText:
            def __init__(self, text):
                self.text = text

            def clear_cache(self):
                pass

            def get_text_iface(self):
                return self

            def get_character_count(self):
                return len(self.text)

            def get_text(self):
                # Same zero-argument accessor as the real Accessible binding.
                raise AssertionError("Deprecated Accessible accessor must not be used")

        class TextInterface:
            @staticmethod
            def get_character_count(interface):
                return len(interface.text)

            @staticmethod
            def get_text(interface, start, end):
                return interface.text[start:end]

        desktop = linux.LinuxDesktop()
        for text in ("", "ki ", "ki কি "):
            app = SimpleNamespace(process=Mock(), field=AccessibleText(text))
            with self.subTest(text=text), patch.object(linux, "owned", return_value=True), \
                    patch.object(linux.Atspi, "Text", TextInterface, create=True):
                self.assertEqual(desktop.text(app), text)

    def test_text_read_rejects_missing_interface_and_invalid_lengths(self):
        desktop = linux.LinuxDesktop()
        app = SimpleNamespace(process=Mock(), field=Mock())
        with patch.object(linux, "owned", return_value=True):
            app.field.get_text_iface.return_value = None
            with self.assertRaisesRegex(proof.ProofError, "no longer exposes"):
                desktop.text(app)
            app.field.get_text_iface.return_value = app.field
            for count in (-1, 65):
                interface = SimpleNamespace(get_character_count=Mock(return_value=count), get_text=Mock())
                with self.subTest(count=count), \
                        patch.object(linux.Atspi, "Text", interface, create=True):
                    with self.assertRaisesRegex(proof.ProofError, "text limit"):
                        desktop.text(app)
                    interface.get_text.assert_not_called()

    def test_text_read_rejects_null_response(self):
        desktop = linux.LinuxDesktop()
        app = SimpleNamespace(process=Mock(), field=Mock())
        interface = SimpleNamespace(get_character_count=Mock(return_value=0),
                                    get_text=Mock(return_value=None))
        with patch.object(linux, "owned", return_value=True), \
                patch.object(linux.Atspi, "Text", interface, create=True):
            with self.assertRaisesRegex(proof.ProofError, "readable text"):
                desktop.text(app)

    def test_application_failure_cleans_only_owned_group_and_temporary_profile(self):
        for name in ("kwrite", "firefox"):
            with self.subTest(name=name):
                desktop = linux.LinuxDesktop()
                desktop.find_field = Mock(return_value=Mock())
                process = Mock(pid=1234)
                with patch.object(linux.subprocess, "Popen", return_value=process) as launch, \
                        patch.object(linux, "wait_for", side_effect=immediate), \
                        patch.object(linux, "wayland_title", return_value=True), \
                        patch.object(linux, "stop_application") as terminate:
                    with self.assertRaisesRegex(proof.ProofError, "synthetic failure"):
                        with desktop.application(name):
                            raise proof.ProofError("synthetic failure")
                terminate.assert_called_once_with(process)
                self.assertTrue(launch.call_args.kwargs["start_new_session"])
                env = launch.call_args.kwargs["env"]
                for variable in ("XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_CACHE_HOME", "XDG_STATE_HOME"):
                    self.assertFalse(Path(env[variable]).parent.exists())
                if name == "firefox":
                    self.assertIn("--no-remote", launch.call_args.args[0])
                    self.assertIn("--offline", launch.call_args.args[0])

    def test_application_waits_for_stubborn_child_after_leader_exit(self):
        launch_process = subprocess.Popen
        stop = linux.stop_application
        for separate_group in (False, True):
            for fail in (False, True):
                with self.subTest(separate_group=separate_group, fail=fail), \
                        tempfile.TemporaryDirectory() as folder:
                    ready = Path(folder) / "ready.json"
                    child_code = (
                        "import json, os, signal, sys\n"
                        "from pathlib import Path\n"
                        "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
                        + ("os.setpgrp()\n" if separate_group else "")
                        + "Path(sys.argv[1]).write_text(json.dumps(os.getpid()))\n"
                        "signal.pause()\n")
                    parent_code = (
                        "import signal, subprocess, sys\n"
                        "subprocess.Popen([sys.executable, '-c', sys.argv[1], sys.argv[2]])\n"
                        "signal.pause()\n")
                    processes = []
                    profiles = []
                    child_pid = None

                    def launch(*_args, **kwargs):
                        process = launch_process([sys.executable, "-c", parent_code,
                                                  child_code, str(ready)], **kwargs)
                        processes.append(process)
                        profiles.append(Path(kwargs["env"]["XDG_CONFIG_HOME"]).parent)
                        proof.wait_for(ready.exists, "synthetic child readiness", timeout=3)
                        return process

                    desktop = linux.LinuxDesktop()
                    desktop.find_field = Mock(return_value=Mock())
                    try:
                        with patch.object(linux.subprocess, "Popen", side_effect=launch), \
                                patch.object(linux, "wayland_title", return_value=True), \
                                patch.object(linux, "stop_application",
                                             side_effect=lambda process: stop(process, timeout=0.2)):
                            try:
                                with desktop.application("firefox") as app:
                                    child_pid = json.loads(ready.read_text())
                                    if fail:
                                        raise proof.ProofError("synthetic application failure")
                            except proof.ProofError as error:
                                if not fail or str(error) != "synthetic application failure":
                                    raise
                        self.assertEqual(processes[0].returncode, -signal.SIGTERM)
                        self.assertEqual(linux.live_session_processes(processes[0].pid), [])
                        self.assertFalse(profiles[0].exists())
                        stat = Path(f"/proc/{child_pid}/stat")
                        if stat.exists():
                            self.assertIn(stat.read_text().rsplit(")", 1)[1].split()[0], ("Z", "X"))
                    finally:
                        if ready.exists():
                            child_pid = json.loads(ready.read_text())
                        for pid in ([child_pid] if child_pid else []) + [p.pid for p in processes]:
                            try:
                                os.kill(pid, signal.SIGKILL)
                            except ProcessLookupError:
                                pass
                        for process in processes:
                            process.wait(timeout=3)

    def test_unterminated_session_fails_cleanup_after_bounded_escalation(self):
        process = Mock(pid=1234)
        with patch.object(linux, "live_session_processes", return_value=[1235]), \
                patch.object(linux.os, "pidfd_open", return_value=99), \
                patch.object(linux.os, "getsid", return_value=1234), \
                patch.object(linux.os, "close"), \
                patch.object(linux.signal, "pidfd_send_signal") as send, \
                patch.object(linux, "wait_for", side_effect=immediate):
            with self.assertRaisesRegex(proof.ProofError, "session kill"):
                linux.stop_application(process)
        self.assertEqual([call.args[1] for call in send.call_args_list],
                         [signal.SIGTERM, signal.SIGKILL])
        process.wait.assert_not_called()

    def test_cleanup_does_not_signal_a_pid_that_changed_sessions(self):
        process = Mock(pid=1234)
        with patch.object(linux, "live_session_processes", side_effect=[[1235], []]), \
                patch.object(linux.os, "pidfd_open", return_value=99), \
                patch.object(linux.os, "getsid", return_value=9876), \
                patch.object(linux.os, "close") as close, \
                patch.object(linux.signal, "pidfd_send_signal") as send:
            linux.stop_application(process)
        send.assert_not_called()
        close.assert_called_once_with(99)
        process.wait.assert_called_once()

    def test_wrong_unicode_is_retained_as_failed_case_not_pass(self):
        report = {"applications": {}, "cases": []}
        with patch.object(proof, "wait_for", side_effect=immediate), patch.object(proof.time, "sleep"):
            with self.assertRaises(proof.ProofError):
                proof.prove(DesktopDouble("always-converts"), report)
        self.assertEqual(report["cases"][0]["status"], "failed")
        self.assertEqual(report["cases"][0]["actual"], "কি ")


if __name__ == "__main__":
    unittest.main()
