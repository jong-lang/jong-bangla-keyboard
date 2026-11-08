"""Offline failure-path checks for the pinned policy-tool installer."""

import hashlib
import importlib.util
import io
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location("policy_tools", Path(__file__).parents[1] / "install-policy-tools.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class PolicyTools(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.output = self.root / "bin"
        self.payloads = {}
        self.tools = []
        for name in ("cargo-deny", "cargo-audit"):
            payload = self.archive(f"package/{name}", name.encode())
            self.payloads[name + ".tgz"] = payload
            self.tools.append((name, "example/tools", "1.0.0", name + ".tgz", 123,
                               hashlib.sha256(payload).hexdigest(), f"package/{name}"))
        context = patch.object(installer, "TOOLS", self.tools)
        context.start()
        self.addCleanup(context.stop)

    def archive(self, name, content, kind=tarfile.REGTYPE, duplicate=False):
        stream = io.BytesIO()
        with tarfile.open(fileobj=stream, mode="w:gz") as archive:
            for _ in range(2 if duplicate else 1):
                member = tarfile.TarInfo(name)
                member.type = kind
                member.linkname = "../../outside"
                member.size = len(content) if kind == tarfile.REGTYPE else 0
                archive.addfile(member, io.BytesIO(content))
            extra = tarfile.TarInfo("../../outside")
            extra.size = 1
            archive.addfile(extra, io.BytesIO(b"x"))
        return stream.getvalue()

    def curl(self, args, **kwargs):
        destination = Path(args[args.index("--output") + 1])
        destination.write_bytes(self.payloads[destination.name])
        return subprocess.CompletedProcess(args, 0)

    def assert_installed(self):
        self.assertEqual({path.name for path in self.output.iterdir()}, {"cargo-deny", "cargo-audit"})
        for path in self.output.iterdir():
            self.assertEqual(path.read_bytes(), path.name.encode())
            self.assertEqual(path.stat().st_mode & 0o777, 0o755)
        self.assertFalse((self.root / "outside").exists())

    def test_success_installs_only_verified_selected_binaries(self):
        with patch.object(installer.subprocess, "run", side_effect=self.curl) as run:
            installer.install(self.output)
        self.assert_installed()
        self.assertEqual(run.call_count, 2)

    def test_transport_failure_uses_official_api_and_discards_partial_response(self):
        def transport(args, **kwargs):
            destination = Path(args[args.index("--output") + 1])
            if args[-1].startswith("https://github.com/"):
                destination.write_bytes(b"partial HTTP response")
                raise subprocess.CalledProcessError(22, args)
            self.assertFalse(destination.exists())
            self.assertIn("Accept: application/octet-stream", args)
            self.assertTrue(args[-1].startswith("https://api.github.com/repos/example/tools/releases/assets/"))
            self.assertEqual(args[args.index("--proto-redir") + 1], "=https")
            return self.curl(args, **kwargs)

        with patch.object(installer.subprocess, "run", side_effect=transport) as run:
            installer.install(self.output)
        self.assert_installed()
        self.assertEqual(run.call_count, 4)

    def test_both_download_paths_failing_never_install(self):
        with patch.object(installer.subprocess, "run", side_effect=subprocess.CalledProcessError(22, "curl")) as run:
            with self.assertRaises(subprocess.CalledProcessError):
                installer.install(self.output)
        self.assertEqual(run.call_count, 2)
        self.assertFalse(self.output.exists())

    def test_checksum_mismatch_never_falls_back_or_installs_partial_toolset(self):
        self.payloads["cargo-audit.tgz"] = b"corrupted archive"
        with patch.object(installer.subprocess, "run", side_effect=self.curl) as run:
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                installer.install(self.output)
        self.assertEqual(run.call_count, 2)
        self.assertFalse(self.output.exists())

    def test_api_success_with_wrong_bytes_still_fails_checksum(self):
        self.payloads["cargo-deny.tgz"] = b'{"message": "not binary content"}'

        def transport(args, **kwargs):
            if args[-1].startswith("https://github.com/"):
                raise subprocess.CalledProcessError(22, args)
            return self.curl(args, **kwargs)

        with patch.object(installer.subprocess, "run", side_effect=transport):
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                installer.install(self.output)
        self.assertFalse(self.output.exists())

    def test_missing_duplicate_linked_and_empty_binary_fail_closed(self):
        for name, content, kind, duplicate in (
            ("wrong/member", b"x", tarfile.REGTYPE, False),
            ("package/cargo-deny", b"x", tarfile.REGTYPE, True),
            ("package/cargo-deny", b"", tarfile.SYMTYPE, False),
            ("package/cargo-deny", b"", tarfile.LNKTYPE, False),
            ("package/cargo-deny", b"", tarfile.REGTYPE, False),
        ):
            payload = self.archive(name, content, kind, duplicate)
            self.payloads["cargo-deny.tgz"] = payload
            self.tools[0] = (*self.tools[0][:5], hashlib.sha256(payload).hexdigest(), "package/cargo-deny")
            with self.subTest(name=name, kind=kind, duplicate=duplicate):
                with patch.object(installer.subprocess, "run", side_effect=self.curl):
                    with self.assertRaises(ValueError):
                        installer.install(self.output)
                self.assertFalse(self.output.exists())

    def test_existing_directory_or_symlink_is_never_overwritten(self):
        self.output.mkdir()
        sentinel = self.output / "sentinel"
        sentinel.write_bytes(b"keep")
        with patch.object(installer.subprocess, "run") as run:
            with self.assertRaises(ValueError):
                installer.install(self.output)
            self.assertEqual(sentinel.read_bytes(), b"keep")
            link = self.root / "link"
            link.symlink_to(self.root / "missing")
            with self.assertRaises(ValueError):
                installer.install(link)
            run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
