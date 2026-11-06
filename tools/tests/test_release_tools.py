"""Regression checks for release publication gates; no GitHub access required."""

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


spec = importlib.util.spec_from_file_location("check_release", Path(__file__).parents[1] / "check-release.py")
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class ReleaseFixture:
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.version = "0.1.0-alpha.1"
        for name in ("Cargo.toml", "adapters/ffi/Cargo.toml"):
            self.write(name, f'[package]\nversion = "{self.version}"\n')
        self.write("Cargo.lock", "\n".join(
            f'[[package]]\nname = "{name}"\nversion = "{self.version}"\n'
            for name in ("jong-bangla-core", "jong-bangla-ffi")
        ))
        self.write("adapters/fcitx5/jong-bangla.conf.in", f"[Addon]\nVersion={self.version}\n")
        self.notes = "\n\n".join(f"### {section}\n\nRecorded result." for section in release.REQUIRED_SECTIONS)
        self.changelog = f"# Changelog\n\n## Unreleased\n\nFuture work.\n\n## {self.version} - 2026-10-31\n\n{self.notes}\n\n## 0.0.1 - 2026-10-01\n\nOlder notes.\n"
        self.write("CHANGELOG.md", self.changelog)

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


class ReleaseValidation(ReleaseFixture, unittest.TestCase):
    def test_extracts_only_selected_release(self):
        notes = release.release_notes(self.root, "v" + self.version)
        self.assertIn("# Jong Bangla v0.1.0-alpha.1", notes)
        self.assertIn("### Known issues", notes)
        self.assertNotIn("Future work", notes)
        self.assertNotIn("Older notes", notes)

    def test_accepts_stable_release(self):
        for version in ("0.1.0", "0.1.0-beta.2", "0.1.0-rc.1"):
            for path in self.root.rglob("*"):
                if path.is_file():
                    path.write_text(path.read_text().replace(self.version, version))
            self.version = version
            with self.subTest(version=version):
                self.assertIn("v" + version, release.release_notes(self.root, "v" + version))

    def test_cli_writes_reviewed_notes(self):
        destination = self.root / "notes.md"
        result = subprocess.run(
            [sys.executable, str(Path(release.__file__).resolve()), "v" + self.version,
             "--notes-file", str(destination)],
            cwd=self.root, text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(destination.read_text(), release.release_notes(self.root, "v" + self.version))

    def test_rejects_malformed_tags(self):
        for tag in ("0.1.0", "v01.1.0", "v0.1.0-alpha.0", "v0.1.0-alpha.01", "v0.1.0-nightly", "v0.1.0;echo bad"):
            with self.subTest(tag=tag), self.assertRaisesRegex(ValueError, "tag must"):
                release.release_notes(self.root, tag)

    def test_rejects_each_version_mismatch(self):
        for name in ("Cargo.toml", "adapters/ffi/Cargo.toml", "Cargo.lock", "adapters/fcitx5/jong-bangla.conf.in"):
            original = (self.root / name).read_text()
            self.write(name, original.replace(self.version, "0.1.0"))
            with self.subTest(name=name), self.assertRaises(ValueError):
                release.release_notes(self.root, "v" + self.version)
            self.write(name, original)

    def test_rejects_missing_or_duplicate_release(self):
        for content in (self.changelog.replace(self.version, "0.2.0"), self.changelog + self.changelog):
            self.write("CHANGELOG.md", content)
            with self.assertRaisesRegex(ValueError, "expected one changelog"):
                release.release_notes(self.root, "v" + self.version)

    def test_requires_unreleased_and_valid_date(self):
        for content in (self.changelog.replace("## Unreleased", "## Pending"), self.changelog.replace("2026-10-31", "2026-02-30")):
            self.write("CHANGELOG.md", content)
            with self.assertRaises(ValueError):
                release.release_notes(self.root, "v" + self.version)

    def test_rejects_missing_section_or_placeholder(self):
        for content in (self.changelog.replace("### Known issues", "### Other"), self.changelog.replace("Recorded result.", "{{Complete this.}}")):
            self.write("CHANGELOG.md", content)
            with self.assertRaises(ValueError):
                release.release_notes(self.root, "v" + self.version)

    def test_rejects_empty_required_section(self):
        for section in release.REQUIRED_SECTIONS:
            self.write("CHANGELOG.md", self.changelog.replace(
                f"### {section}\n\nRecorded result.", f"### {section}\n\n",
            ))
            with self.subTest(section=section), self.assertRaisesRegex(ValueError, "nonempty"):
                release.release_notes(self.root, "v" + self.version)


class ReleasePreparation(ReleaseFixture, unittest.TestCase):
    def test_allows_only_consistent_initial_baseline(self):
        baseline = "# Changelog\n\n## Unreleased\n\nInitial development.\n"
        self.write("CHANGELOG.md", baseline)
        self.assertIsNone(release.preparation_notes(self.root, self.version, baseline))
        for name in ("Cargo.toml", "adapters/ffi/Cargo.toml", "Cargo.lock",
                     "adapters/fcitx5/jong-bangla.conf.in"):
            original = (self.root / name).read_text()
            self.write(name, original.replace(self.version, "0.2.0"))
            with self.subTest(name=name), self.assertRaises(ValueError):
                release.preparation_notes(self.root, self.version, baseline)
            self.write(name, original)

    def test_version_bump_requires_dated_notes(self):
        baseline = "# Changelog\n\n## Unreleased\n\nInitial development.\n"
        self.write("CHANGELOG.md", baseline)
        with self.assertRaisesRegex(ValueError, "expected one changelog"):
            release.preparation_notes(self.root, "0.0.1", baseline)

    def test_initial_baseline_still_requires_unreleased_section_and_valid_version(self):
        baseline = "# Changelog\n\n## Unreleased\n"
        self.write("CHANGELOG.md", "# Changelog\n\nInitial development.\n")
        with self.assertRaisesRegex(ValueError, "Unreleased section"):
            release.preparation_notes(self.root, self.version, baseline)
        self.write("CHANGELOG.md", baseline)
        self.write("Cargo.toml", '[package]\nversion = "0.1.0-nightly"\n')
        with self.assertRaisesRegex(ValueError, "package version must"):
            release.preparation_notes(self.root, self.version, baseline)

    def test_first_release_without_version_bump_requires_complete_notes(self):
        baseline = "# Changelog\n\n## Unreleased\n"
        self.assertIn("### Known issues", release.preparation_notes(self.root, self.version, baseline))
        self.write("CHANGELOG.md", self.changelog.replace("Recorded result.", "{{Pending}}"))
        with self.assertRaisesRegex(ValueError, "placeholders"):
            release.preparation_notes(self.root, self.version, baseline)

    def test_removing_all_release_notes_cannot_restore_baseline(self):
        self.write("CHANGELOG.md", "# Changelog\n\n## Unreleased\n")
        with self.assertRaisesRegex(ValueError, "expected one changelog"):
            release.preparation_notes(self.root, self.version, self.changelog)

    def test_ordinary_change_after_release_still_validates_notes(self):
        self.assertIsNotNone(release.preparation_notes(self.root, self.version, self.changelog))
        self.write("CHANGELOG.md", self.changelog.replace("### Known issues", "### Other"))
        with self.assertRaisesRegex(ValueError, "Known issues"):
            release.preparation_notes(self.root, self.version, self.changelog)

    def test_cli_checks_base_revision_and_fails_for_unknown_base(self):
        for args in (["init", "-q"], ["add", "."],
                     ["-c", "user.name=Release test", "-c", "user.email=test@example.invalid",
                      "commit", "-qm", "baseline"]):
            subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True)
        command = [sys.executable, str(Path(release.__file__).resolve()), "--base"]
        result = subprocess.run(command + ["HEAD"], cwd=self.root, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.write("adapters/fcitx5/jong-bangla.conf.in", "[Addon]\nVersion=0.2.0\n")
        result = subprocess.run(command + ["HEAD"], cwd=self.root, text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("addon metadata", result.stderr)
        result = subprocess.run(command + ["missing-revision"], cwd=self.root, text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
