"""Exercise the real Git export boundary without Flatpak or network access."""

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


spec = importlib.util.spec_from_file_location(
    "prepare_flatpak", Path(__file__).resolve().parents[1] / "prepare-flatpak.py")
prepare_flatpak = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare_flatpak)


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "repo"
        self.root.mkdir()
        self.output = Path(self.temporary.name) / "input"
        self.git("init", "-q")
        self.git("config", "user.name", "Synthetic test")
        self.git("config", "user.email", "test@example.invalid")
        self.recipe = self.root / "packaging/flatpak/org.fcitx.Fcitx5.Addon.Jong.json"
        self.recipe.parent.mkdir(parents=True)
        self.recipe.write_text('{"app-id": "synthetic"}\n')
        (self.root / ".gitignore").write_text("target/\n")
        (self.root / "engine.txt").write_text("synthetic source\n")
        self.git("add", ".")
        self.git("commit", "-qm", "chore: synthetic fixture")

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args])

    def test_export_has_exact_commit_identity_and_excludes_ignored_data(self):
        (self.root / "target").mkdir()
        (self.root / "target/private.keep").write_text("must not be exported")
        prepare_flatpak.prepare(self.root, self.output)
        info = json.loads((self.output / "source-info.json").read_text())
        self.assertEqual(info["commit"], self.git("rev-parse", "HEAD").decode().strip())
        self.assertEqual(info["git_archive_sha256"], hashlib.sha256(
            self.git("archive", "--format=tar", "HEAD")).hexdigest())
        self.assertEqual((self.output / "source/engine.txt").read_text(), "synthetic source\n")
        self.assertFalse((self.output / "source/target").exists())
        self.assertFalse((self.output / "source/.git").exists())
        self.assertEqual((self.output / self.recipe.name).read_bytes(), self.recipe.read_bytes())

    def test_dirty_or_untracked_source_is_rejected_before_output(self):
        for path in (self.root / "engine.txt", self.root / "untracked.txt"):
            with self.subTest(path=path.name):
                old = path.read_bytes() if path.exists() else None
                path.write_text("uncommitted work\n")
                with self.assertRaisesRegex(ValueError, "clean checkout"):
                    prepare_flatpak.prepare(self.root, self.output)
                self.assertFalse(self.output.exists())
                if old is None:
                    path.unlink()
                else:
                    path.write_bytes(old)

    def test_existing_output_is_preserved(self):
        self.output.mkdir()
        sentinel = self.output / "keep"
        sentinel.write_text("preserve\n")
        with self.assertRaises(FileExistsError):
            prepare_flatpak.prepare(self.root, self.output)
        self.assertEqual(sentinel.read_text(), "preserve\n")


if __name__ == "__main__":
    unittest.main()
