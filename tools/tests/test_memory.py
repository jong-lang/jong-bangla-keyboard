"""Synthetic detector failures must never become successful memory checks."""

import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "check-memory.py"
spec = importlib.util.spec_from_file_location("memory", SCRIPT)
memory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(memory)


def result(code=0, stderr=""):
    return subprocess.CompletedProcess([], code, stdout="", stderr=stderr)


class MemoryChecks(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.build = Path(self.directory.name)

    def test_missing_build_and_wrong_build_modes_fail_clearly(self):
        for metadata, arguments, message in [
            (None, [], "memory-build.txt"),
            ("sanitizers=OFF\nbuild_type=Release\n", [], "requires JONG_ENABLE_SANITIZERS=ON"),
            ("sanitizers=ON\nbuild_type=Release\n", ["--mode", "valgrind"], "requires JONG_ENABLE_SANITIZERS=OFF"),
            ("sanitizers=OFF\nbuild_type=Debug\n", ["--mode", "valgrind"], "requires a separate unsanitized Release"),
        ]:
            with self.subTest(metadata=metadata, arguments=arguments):
                if metadata is not None:
                    (self.build / "memory-build.txt").write_text(metadata)
                completed = subprocess.run([sys.executable, str(SCRIPT), str(self.build), *arguments],
                                           capture_output=True, text=True)
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn("FAIL:", completed.stderr)
                self.assertIn(message, completed.stderr)
                self.assertNotIn("Traceback", completed.stderr)

    def test_instrumentation_rejects_missing_native_checks_and_instrumented_rust(self):
        native = subprocess.CompletedProcess([], 0, stdout="U __asan_init\nU __ubsan_handle_type_mismatch_v1", stderr="")
        ordinary = subprocess.CompletedProcess([], 0, stdout="U malloc", stderr="")
        for outputs in ([ordinary], [native, native, native, native]):
            with patch.object(memory, "run", side_effect=outputs):
                with self.assertRaisesRegex(memory.CheckFailure, "unexpected instrumentation"):
                    memory.instrumentation(self.build, {}, self.build, True)
        with patch.object(memory, "run", side_effect=[native, native, native, ordinary]):
            memory.instrumentation(self.build, {}, self.build, True)
        with patch.object(memory, "run", return_value=ordinary):
            memory.instrumentation(self.build, {}, self.build, False)

    def test_missing_executable_and_timeout_are_failures(self):
        for error in (FileNotFoundError("synthetic missing detector"),
                      subprocess.TimeoutExpired("synthetic detector", 1)):
            with self.subTest(error=error), patch.object(memory.subprocess, "run", side_effect=error):
                with self.assertRaises(memory.CheckFailure):
                    memory.run(["synthetic"], {}, self.build, "missing")

    def test_timeout_retains_partial_output_and_removes_stale_logs(self):
        (self.build / "timeout.stdout").write_text("stale")
        error = subprocess.TimeoutExpired("synthetic", 1, output=b"partial synthetic output")
        with patch.object(memory.subprocess, "run", side_effect=error):
            with self.assertRaisesRegex(memory.CheckFailure, "timed out"):
                memory.run(["synthetic"], {}, self.build, "timeout", timeout=1)
        self.assertEqual((self.build / "timeout.stdout").read_text(), "partial synthetic output")
        self.assertEqual((self.build / "timeout.stderr").read_text(), "")

    def test_sanitizer_controls_require_both_exit_and_specific_diagnostic(self):
        controls = [result(23, "ERROR: AddressSanitizer: heap-buffer-overflow"),
                    result(23, "runtime error: signed integer overflow"),
                    result(23, "ERROR: LeakSanitizer: detected memory leaks")]
        for index in range(3):
            for broken in (result(), result(23, "unavailable detector"),
                           result(0, controls[index].stderr)):
                with self.subTest(index=index, broken=broken):
                    outputs = controls[:index] + [broken]
                    with patch.object(memory, "run", side_effect=outputs):
                        with self.assertRaises(memory.CheckFailure):
                            memory.sanitizers(self.build, {}, self.build)

    def test_sanitizers_override_disabled_detector_environment(self):
        env = dict(ASAN_OPTIONS="detect_leaks=0", LSAN_OPTIONS="exitcode=0",
                   UBSAN_OPTIONS="halt_on_error=0")
        with patch.object(memory, "run", return_value=result()):
            with self.assertRaises(memory.CheckFailure):
                memory.sanitizers(self.build, env, self.build)
        self.assertIn("detect_leaks=1", env["ASAN_OPTIONS"])
        self.assertIn("exitcode=23", env["LSAN_OPTIONS"])
        self.assertIn("halt_on_error=1", env["UBSAN_OPTIONS"])

    def test_zero_exit_with_sanitizer_report_is_rejected(self):
        controls = [result(23, "ERROR: AddressSanitizer: heap-buffer-overflow"),
                    result(23, "runtime error: signed integer overflow"),
                    result(23, "ERROR: LeakSanitizer: detected memory leaks")]
        for diagnostic in ("AddressSanitizer: broken", "runtime error: synthetic"):
            with patch.object(memory, "run", side_effect=controls + [result(0, diagnostic)]):
                with self.assertRaisesRegex(memory.CheckFailure, "sanitizer report"):
                    memory.sanitizers(self.build, {}, self.build)

    def test_memcheck_rejects_missing_stale_incomplete_and_wrong_tool_reports(self):
        for xml in (None, "broken XML", "<valgrindoutput><tool>memcheck</tool></valgrindoutput>",
                    "<valgrindoutput><tool>other</tool><status><state>FINISHED</state></status></valgrindoutput>"):
            with self.subTest(xml=xml):
                # A stale successful report must not hide a detector startup failure.
                (self.build / "probe.xml").write_text('<valgrindoutput/>')
                def fake_run(*_):
                    self.assertFalse((self.build / "probe.xml").exists())
                    if xml is not None:
                        (self.build / "probe.xml").write_text(xml)
                    return result()
                with patch.object(memory, "run", side_effect=fake_run):
                    with self.assertRaises(memory.CheckFailure):
                        memory.memcheck(["synthetic"], {}, self.build, "probe")

    def test_memcheck_classifies_leaks_and_errors(self):
        for kinds, code, leak, accepted in [
            ([], 0, False, True),
            (["Leak_StillReachable"], 0, False, True),
            (["Leak_DefinitelyLost"], 23, False, False),
            (["Leak_PossiblyLost"], 23, False, False),
            (["InvalidRead"], 0, False, False),
            ([], 1, False, False),
            ([], 0, True, False),
            (["Leak_DefinitelyLost"], 0, True, False),
            (["Leak_DefinitelyLost", "Leak_IndirectlyLost"], 23, True, True),
            (["Leak_DefinitelyLost", "InvalidRead"], 23, True, False),
        ]:
            with self.subTest(kinds=kinds, code=code, leak=leak):
                def fake_run(*_):
                    errors = ''.join(f'<error><kind>{kind}</kind></error>' for kind in kinds)
                    (self.build / "probe.xml").write_text(
                        '<valgrindoutput><tool>memcheck</tool>' + errors +
                        '<status><state>FINISHED</state></status></valgrindoutput>')
                    return result(code)
                with patch.object(memory, "run", side_effect=fake_run):
                    if accepted:
                        memory.memcheck(["synthetic"], {}, self.build, "probe", leak=leak)
                    else:
                        with self.assertRaises(memory.CheckFailure):
                            memory.memcheck(["synthetic"], {}, self.build, "probe", leak=leak)

    @unittest.skipUnless(shutil.which("valgrind") and shutil.which("c++"),
                         "requires Valgrind and a C++ compiler")
    def test_memcheck_ignores_rc_file_disabling_mismatched_frees(self):
        source = self.build / "mismatch.cpp"
        binary = self.build / "mismatch"
        source.write_text("#include <cstdlib>\n"
                          "int main() { int *p = new int(7); std::free(p); }\n")
        subprocess.run(["c++", "-O0", "-g", str(source), "-o", str(binary)],
                       capture_output=True, text=True, check=True, timeout=30)
        self.addCleanup(os.chdir, Path.cwd())
        os.chdir(self.build)
        env = dict(os.environ, LC_ALL="C")
        env.pop("VALGRIND_OPTS", None)
        for rc_present in (False, True):
            with self.subTest(rc_present=rc_present):
                if rc_present:
                    (self.build / ".valgrindrc").write_text("--show-mismatched-frees=no\n")
                with self.assertRaisesRegex(memory.CheckFailure, "exit 23 or Memcheck error"):
                    memory.memcheck([str(binary)], env, self.build, "mismatch")
                report = memory.ET.parse(self.build / "mismatch.xml")
                self.assertIn("MismatchedFree", [e.findtext("kind")
                                                for e in report.findall("error")])


if __name__ == "__main__":
    unittest.main()
