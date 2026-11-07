"""Synthetic violations exercise the source scanner without real typed text."""

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "check-privacy.py"
spec = importlib.util.spec_from_file_location("privacy", SCRIPT)
privacy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(privacy)


class PrivacyScan(unittest.TestCase):
    def test_rust_network_paths_and_aliases(self):
        for source in (
            "use std::net::TcpStream as Transport;",
            "use std::{borrow::Cow, net::{TcpStream, UdpSocket}};",
            "use std /* synthetic */ :: net :: TcpStream;",
            "std::net::TcpStream::connect(address);",
            "reqwest::blocking::get(address);",
            "use socket2::Socket;",
        ):
            with self.subTest(source=source):
                self.assertTrue(privacy.violations(Path("src/lib.rs"), source))

    def test_native_network_headers_and_calls(self):
        for source in (
            "#include <sys/socket.h>", "#include <curl/curl.h>",
            "#include <winsock2.h>", "#include <QtNetwork/QTcpSocket>",
            "::socket(AF_INET, SOCK_STREAM, 0);", "connect(fd, address, len);",
            "send /* synthetic */ (fd, data, size, 0);",
            "WinHttpSendRequest(handle);", "curl_easy_perform(handle);",
        ):
            with self.subTest(source=source):
                self.assertTrue(privacy.violations(Path("adapters/future/bridge.cpp"), source))

    def test_diagnostics_persistence_telemetry_and_processes(self):
        for source in (
            'println!("synthetic");', 'dbg!("synthetic");',
            'log::info!("synthetic");', 'tracing::event!("synthetic");',
            'sentry::capture_message("synthetic");', "use std::fs::File;",
            "use std::{io::Write, fs::File};", 'fopen("synthetic", "w");',
            'fprintf(stderr, "synthetic");', 'std::ofstream file("synthetic");',
            'FCITX_INFO() << "synthetic";', 'qDebug("synthetic");',
            'std::cerr << "synthetic";', 'system("synthetic");',
        ):
            with self.subTest(source=source):
                self.assertTrue(privacy.violations(Path("adapters/future/bridge.rs"), source))

    def test_core_state_and_platform_tripwires(self):
        for source in (
            "static mut INPUT: String = String::new();", "thread_local! {}",
            "use std::sync::Mutex;", 'unsafe extern "C" { fn platform(); }',
            "libc::getpid();",
        ):
            with self.subTest(source=source):
                self.assertTrue(privacy.violations(Path("src/lib.rs"), source))
        self.assertFalse(privacy.violations(Path("adapters/future/bridge.rs"), "use std::sync::Mutex;"))

    def test_allows_composition_and_framework_commits(self):
        for path, source in (
            ("src/lib.rs", "use std::borrow::Cow; const RULE: &str = \"synthetic\";"),
            ("src/composition.rs", "std::mem::take(&mut self.preedit)"),
            ("adapters/fcitx5/addon.cpp", "inputContext->commitString(committed);"),
        ):
            self.assertEqual(privacy.violations(Path(path), source), [])

    def test_cli_discovers_future_adapters_and_never_echoes_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            bridge = root / "adapters/future/bridge.hpp"
            bridge.parent.mkdir(parents=True)
            bridge.write_text('inline void sendSynthetic() { socket(0, 0, 0); }')
            result = subprocess.run([sys.executable, str(SCRIPT)], cwd=root, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("adapters/future/bridge.hpp:1: network-call", result.stderr)
            self.assertNotIn("sendSynthetic", result.stderr)
            bridge.write_text("// synthetic bridge\n")
            tests = bridge.parent / "tests/harness.cpp"
            tests.parent.mkdir()
            tests.write_text('printf("synthetic");')
            result = subprocess.run([sys.executable, str(SCRIPT)], cwd=root, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_cli_rejects_wrong_root(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, str(SCRIPT)], cwd=directory, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing source directory", result.stderr)

    def test_comment_split_tokens_keep_line_numbers(self):
        findings = privacy.violations(Path("src/lib.rs"), "\nstd /* synthetic\ncomment */ :: net :: TcpStream;")
        self.assertIn((2, "rust-io"), findings)


if __name__ == "__main__":
    unittest.main()
