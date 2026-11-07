"""Release archive reproducibility and draft failure gates without GitHub access."""

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest


TOOLS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build_release", TOOLS / "build-release.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)

    def test_archive_ignores_input_order_mtime_and_host_modes(self):
        first, second = self.root / "first", self.root / "second"
        first.write_bytes(b"synthetic ELF")
        second.write_bytes(b"registration")
        one, two = self.root / "one.tar.gz", self.root / "two.tar.gz"
        builder.archive(one, {"lib/addon.so": first, "data.conf": second}, "payload", 1234567890)
        first.chmod(0o600)
        os.utime(first, (1, 1))
        builder.archive(two, {"data.conf": second, "lib/addon.so": first}, "payload", 1234567890)
        self.assertEqual(one.read_bytes(), two.read_bytes())
        with tarfile.open(one) as archive:
            self.assertEqual(archive.getnames(), ["payload/data.conf", "payload/lib/addon.so"])
            for entry in archive:
                self.assertEqual((entry.uid, entry.gid, entry.mtime), (0, 0, 1234567890))
                self.assertEqual(entry.mode, 0o755 if entry.name.endswith(".so") else 0o644)

    def test_archive_rejects_symlinks_and_cannot_overwrite(self):
        source = self.root / "source"
        source.write_bytes(b"payload")
        link = self.root / "link"
        link.symlink_to(source)
        destination = self.root / "payload.tar.gz"
        with self.assertRaisesRegex(ValueError, "regular files"):
            builder.archive(destination, {"link": link}, "payload", 1)
        with self.assertRaises(FileExistsError):
            builder.archive(destination, {"source": source}, "payload", 1)

    def test_differing_build_outputs_and_invalid_stages_fail(self):
        first, second = self.root / "first", self.root / "second"
        first.write_bytes(b"first")
        second.write_bytes(b"second")
        builder.compare({"addon": first}, {"addon": first})
        for payload in ({"addon": second}, {"other": first}):
            with self.assertRaisesRegex(ValueError, "builds differ"):
                builder.compare({"addon": first}, payload)
        with self.assertRaisesRegex(ValueError, "exactly the three"):
            builder.staged_files(self.root)

    def test_staged_payload_requires_exact_paths_and_rejects_extra_files_and_links(self):
        stage = self.root / "stage"
        for name in ("usr/lib/fcitx5/libjong-bangla.so", "usr/share/fcitx5/addon/jong-bangla.conf",
                     "usr/share/fcitx5/inputmethod/jong-bangla.conf"):
            path = stage / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"synthetic payload")
        self.assertEqual(len(builder.staged_files(stage)), 3)
        extra = stage / "unexpected"
        extra.write_bytes(b"extra")
        with self.assertRaises(ValueError):
            builder.staged_files(stage)
        extra.unlink()
        library = stage / "usr/lib/fcitx5/libjong-bangla.so"
        library.unlink()
        library.symlink_to(stage / "usr/share/fcitx5/addon/jong-bangla.conf")
        with self.assertRaises(ValueError):
            builder.staged_files(stage)


# This executable emulates only the external GitHub operations. Real git, notes
# validation, bundle checks, CLI flags and downloaded-byte verification still run.
FAKE_GH = r'''#!/usr/bin/env python3
import json, os, pathlib, shutil, sys
args = sys.argv[1:]
root = pathlib.Path(os.environ["FAKE_REMOTE"])
mode = os.environ.get("FAKE_MODE", "success")
with (root / "calls").open("a") as log:
    log.write(json.dumps(args) + "\n")
if args[0] == "api":
    if mode == "list-error":
        sys.exit(7)
    if mode == "existing":
        print(os.environ["FAKE_TAG"])
elif args[:2] == ["release", "create"]:
    assert "--draft" in args and "--verify-tag" in args and "--latest=false" in args
    assert "--generate-notes" not in args and "--clobber" not in args
    (root / "is-draft").write_text("true")
    if mode == "upload-error":
        sys.exit(8)
    for arg in args:
        path = pathlib.Path(arg)
        if path.parent == pathlib.Path(os.environ["FAKE_BUNDLE"]):
            shutil.copyfile(path, root / path.name)
elif args[:2] == ["release", "view"]:
    names = [p.name for p in root.iterdir() if p.name not in ("calls", "is-draft")]
    if mode == "missing-remote":
        names.pop()
    print(json.dumps({"isDraft": mode != "published", "tagName": os.environ["FAKE_TAG"],
                      "assets": [{"name": name} for name in names]}))
elif args[:2] == ["release", "download"]:
    dest = pathlib.Path(args[args.index("--dir") + 1])
    dest.mkdir()
    for path in root.iterdir():
        if path.name not in ("calls", "is-draft"):
            shutil.copyfile(path, dest / path.name)
    if mode == "corrupt-download":
        (dest / "build-info.json").write_text("corrupted")
else:
    raise AssertionError(args)
'''


class DraftTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.version = "0.1.0-alpha.1"
        self.tag = "v" + self.version
        for name in ("Cargo.toml", "adapters/fcitx5/ffi/Cargo.toml"):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f'[package]\nversion = "{self.version}"\n')
        (self.root / "Cargo.lock").write_text("\n".join(
            f'[[package]]\nname = "{name}"\nversion = "{self.version}"\n'
            for name in ("jong-bangla-core", "jong-bangla-fcitx5-ffi")))
        (self.root / "adapters/fcitx5/jong-bangla.conf.in").write_text(f"Version={self.version}\n")
        sections = ("Highlights", "Fixes", "Breaking changes", "Installation and upgrade",
                    "Tested environments", "Known issues")
        self.notes = "\n\n".join(f"### {section}\n\nReviewed note." for section in sections)
        (self.root / "CHANGELOG.md").write_text(
            f"# Changelog\n\n## Unreleased\n\n## {self.version} - 2026-11-07\n\n{self.notes}\n")
        (self.root / "tools").mkdir()
        shutil.copyfile(TOOLS / "check-release.py", self.root / "tools/check-release.py")
        for args in (("init", "-q"), ("add", "."),
                     ("-c", "user.name=Release test", "-c", "user.email=test@example.invalid",
                      "commit", "-qm", "feat: release fixture"), ("tag", self.tag)):
            subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True)
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.root, text=True).strip()
        self.bundle = self.root / "bundle"
        self.bundle.mkdir()
        for name in (f"jong-bangla-{self.version}.tar.gz",
                     f"jong-bangla-{self.version}-fcitx5-x86_64-linux-gnu.tar.gz"):
            (self.bundle / name).write_bytes(b"synthetic archive")
        self.info = {"commit": commit, "version": self.version, "target": "x86_64-linux-gnu",
                     "independent_builds_identical": True}
        self.write_info()
        self.remote = self.root / "remote"
        self.remote.mkdir()
        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        gh = bin_dir / "gh"
        gh.write_text(FAKE_GH)
        gh.chmod(0o755)
        self.env = dict(os.environ, PATH=str(bin_dir) + os.pathsep + os.environ["PATH"],
                        FAKE_REMOTE=str(self.remote), FAKE_BUNDLE=str(self.bundle), FAKE_TAG=self.tag)

    def write_info(self):
        (self.bundle / "build-info.json").write_text(json.dumps(self.info))
        (self.bundle / "SHA256SUMS").unlink(missing_ok=True)
        builder.checksum_manifest(self.bundle)

    def draft(self, mode="success"):
        return subprocess.run([sys.executable, str(TOOLS / "draft-release.py"), self.tag,
                               "--artifacts", str(self.bundle), "--repo", "example/jong"],
                              cwd=self.root, env=dict(self.env, FAKE_MODE=mode),
                              capture_output=True, text=True)

    def calls(self):
        path = self.remote / "calls"
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []

    def test_complete_draft_downloads_and_verifies_all_assets(self):
        result = self.draft()
        self.assertEqual(result.returncode, 0, result.stderr)
        commands = self.calls()
        self.assertEqual([call[:2] for call in commands[1:]],
                         [["release", "create"], ["release", "view"], ["release", "download"]])
        self.assertIn("--prerelease", commands[1])
        self.assertEqual((self.remote / "is-draft").read_text(), "true")

    def test_stable_draft_is_not_marked_prerelease(self):
        for name in ("Cargo.toml", "adapters/fcitx5/ffi/Cargo.toml", "Cargo.lock",
                     "adapters/fcitx5/jong-bangla.conf.in", "CHANGELOG.md"):
            path = self.root / name
            path.write_text(path.read_text().replace(self.version, "0.1.0"))
        for path in self.bundle.glob("*.tar.gz"):
            path.rename(path.with_name(path.name.replace(self.version, "0.1.0")))
        self.version, self.tag = "0.1.0", "v0.1.0"
        for args in (("add", "."), ("-c", "user.name=Release test", "-c", "user.email=test@example.invalid",
                                  "commit", "-qm", "chore: prepare stable fixture"), ("tag", self.tag)):
            subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True)
        self.info["version"] = self.version
        self.info["commit"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.root, text=True).strip()
        self.write_info()
        self.env["FAKE_TAG"] = self.tag
        result = self.draft()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("--prerelease", self.calls()[1])

    def test_existing_release_or_api_failure_never_attempts_creation(self):
        for mode in ("existing", "list-error"):
            with self.subTest(mode=mode):
                result = self.draft(mode)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((self.remote / "is-draft").exists())
        self.assertTrue(all(call[0] == "api" for call in self.calls()))

    def test_upload_or_postflight_failure_never_publishes_or_retries(self):
        for mode in ("upload-error", "missing-remote", "corrupt-download", "published"):
            with self.subTest(mode=mode):
                for path in self.remote.iterdir():
                    path.unlink()
                result = self.draft(mode)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual((self.remote / "is-draft").read_text(), "true")
                self.assertEqual(sum(call[:2] == ["release", "create"] for call in self.calls()), 1)
                self.assertFalse(any(call[1] in ("edit", "delete", "upload") for call in self.calls()))

    def test_corrupt_missing_extra_duplicate_checksums_and_symlinks_fail_before_api(self):
        original = (self.bundle / "SHA256SUMS").read_text()
        for content in (original.replace(original[:64], "0" * 64),
                        original.splitlines()[0] + "\n", original + original,
                        original + "0" * 64 + "  unexpected.tar.gz\n"):
            (self.bundle / "SHA256SUMS").write_text(content)
            self.assertNotEqual(self.draft().returncode, 0)
        (self.bundle / "SHA256SUMS").write_text(original)
        extra = self.bundle / "stale.tar.gz"
        extra.write_bytes(b"stale")
        self.assertNotEqual(self.draft().returncode, 0)
        extra.unlink()
        source = self.bundle / f"jong-bangla-{self.version}.tar.gz"
        content = source.read_bytes()
        source.unlink()
        self.assertNotEqual(self.draft().returncode, 0)
        source.write_bytes(content)
        info = self.bundle / "build-info.json"
        info.unlink()
        info.symlink_to(self.root / "Cargo.toml")
        self.assertNotEqual(self.draft().returncode, 0)
        self.assertEqual(self.calls(), [])

    def test_wrong_commit_version_target_or_failed_reproducibility_fails_before_api(self):
        for key, value in (("commit", "0" * 40), ("version", "0.2.0"),
                           ("target", "aarch64-linux-gnu"), ("independent_builds_identical", False)):
            original = self.info[key]
            self.info[key] = value
            self.write_info()
            with self.subTest(key=key):
                self.assertNotEqual(self.draft().returncode, 0)
            self.info[key] = original
        self.assertEqual(self.calls(), [])

    def test_unreviewed_notes_fail_before_api(self):
        path = self.root / "CHANGELOG.md"
        path.write_text(path.read_text().replace("Reviewed note.", "{{Pending review}}"))
        self.assertNotEqual(self.draft().returncode, 0)
        self.assertEqual(self.calls(), [])


if __name__ == "__main__":
    unittest.main()
