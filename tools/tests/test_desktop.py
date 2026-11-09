"""Desktop proof rejection/cleanup regressions; never access a desktop session."""

from contextlib import contextmanager
import importlib.util
import json
from pathlib import Path
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

    def test_application_failure_cleans_only_owned_group_and_temporary_profile(self):
        for name in ("kwrite", "firefox"):
            with self.subTest(name=name):
                desktop = linux.LinuxDesktop()
                desktop.find_field = Mock(return_value=Mock())
                process = Mock(pid=1234)
                with patch.object(linux.subprocess, "Popen", return_value=process) as launch, \
                        patch.object(linux, "wait_for", side_effect=immediate), \
                        patch.object(linux, "wayland_title", return_value=True), \
                        patch.object(linux.os, "killpg") as terminate:
                    with self.assertRaisesRegex(proof.ProofError, "synthetic failure"):
                        with desktop.application(name):
                            raise proof.ProofError("synthetic failure")
                terminate.assert_called_once_with(1234, linux.signal.SIGTERM)
                self.assertTrue(launch.call_args.kwargs["start_new_session"])
                env = launch.call_args.kwargs["env"]
                for variable in ("XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_CACHE_HOME", "XDG_STATE_HOME"):
                    self.assertFalse(Path(env[variable]).parent.exists())
                if name == "firefox":
                    self.assertIn("--no-remote", launch.call_args.args[0])
                    self.assertIn("--offline", launch.call_args.args[0])

    def test_wrong_unicode_is_retained_as_failed_case_not_pass(self):
        report = {"applications": {}, "cases": []}
        with patch.object(proof, "wait_for", side_effect=immediate), patch.object(proof.time, "sleep"):
            with self.assertRaises(proof.ProofError):
                proof.prove(DesktopDouble("always-converts"), report)
        self.assertEqual(report["cases"][0]["status"], "failed")
        self.assertEqual(report["cases"][0]["actual"], "কি ")


if __name__ == "__main__":
    unittest.main()
