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
        for name in ("Cargo.toml", "adapters/fcitx5/ffi/Cargo.toml"):
            self.write(name, f'[package]\nversion = "{self.version}"\n')
        self.write("Cargo.lock", "\n".join(
            f'[[package]]\nname = "{name}"\nversion = "{self.version}"\n'
            for name in ("jong-bangla-core", "jong-bangla-fcitx5-ffi")
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
        for name in ("Cargo.toml", "adapters/fcitx5/ffi/Cargo.toml", "Cargo.lock", "adapters/fcitx5/jong-bangla.conf.in"):
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
        for name in ("Cargo.toml", "adapters/fcitx5/ffi/Cargo.toml", "Cargo.lock",
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


class ChangelogGeneration(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Release test")
        self.git("config", "user.email", "test@example.invalid")
        self.commit("feat: initial feature")

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], text=True).strip()

    def commit(self, message):
        self.git("commit", "--allow-empty", "-qm", message)

    def candidates(self, **kwargs):
        return release.changelog_candidates(self.root, "0.2.0", "2026-11-07", **kwargs)

    def test_first_release_groups_types_and_preserves_unclassified_commits(self):
        for message in ("fix(core): correct Unicode", "perf: reduce work", "docs: explain setup",
                        "legacy title", "feat(api)!: replace interface",
                        "chore: remove option\n\nBREAKING-CHANGE: Use the new option.\nContinuation.\n\nRefs: #29"):
            self.commit(message)
        notes = self.candidates()
        self.assertIn("### Highlights\n\n- initial feature", notes)
        self.assertIn("### Fixes\n\n- core: correct Unicode", notes)
        self.assertIn("reduce work", notes)
        self.assertIn("### Breaking changes\n\n- api: replace interface", notes)
        self.assertIn("Use the new option. Continuation.", notes)
        self.assertNotIn("Refs: #29", notes)
        self.assertIn("### Other changes\n\n- explain setup", notes)
        self.assertIn("legacy title", notes)
        for section in ("Installation and upgrade", "Tested environments", "Known issues"):
            self.assertIn("### " + section, notes)
        self.assertIn("{{", notes)  # Candidates cannot pass the reviewed-notes gate.
        self.assertEqual(notes, self.candidates())

    def test_uses_nearest_reachable_semver_tag_and_explicit_range(self):
        initial = self.git("rev-parse", "HEAD")
        self.git("tag", "v0.1.0")
        self.commit("fix: earlier correction")
        self.git("tag", "v0.1.1")
        self.commit("feat: next feature")
        self.git("tag", "v999-invalid")
        notes = self.candidates()
        self.assertNotIn("earlier correction", notes)
        self.assertNotIn("initial feature", notes)
        self.assertIn("next feature", notes)
        self.assertIn("earlier correction", self.candidates(since="v0.1.0"))
        self.assertNotIn("next feature", self.candidates(since=initial, until="v0.1.1"))

    def test_first_parent_avoids_duplicate_pr_commits(self):
        self.git("switch", "-qc", "feature")
        self.commit("feat: internal duplicate")
        self.git("switch", "-q", "main")
        self.git("merge", "--no-ff", "-qm", "feat: reviewed PR summary", "feature")
        notes = self.candidates()
        self.assertIn("reviewed PR summary", notes)
        self.assertNotIn("internal duplicate", notes)

    def test_case_insensitive_type_and_both_breaking_markers(self):
        self.commit("FIX(api)!: adjust API\n\nBREAKING CHANGE: Migrate callers.")
        notes = self.candidates()
        self.assertIn("### Fixes\n\n- api: adjust API", notes)
        self.assertEqual(notes.count("Migrate callers."), 1)
        breaking = notes.split("### Breaking changes\n\n")[1].split("### ")[0]
        self.assertNotIn("adjust API", breaking)

    def test_rejects_invalid_or_nonancestor_ranges_dates_and_versions(self):
        with self.assertRaises(subprocess.CalledProcessError):
            self.candidates(since="missing-tag")
        self.git("checkout", "--orphan", "unrelated")
        self.commit("chore: unrelated history")
        with self.assertRaises(subprocess.CalledProcessError):
            self.candidates(since="main")
        for version, day in (("01.0.0", "2026-11-07"), ("0.1.0", "2026-02-30"),
                             ("0.1.0", "20261107")):
            with self.subTest(version=version, day=day), self.assertRaises(ValueError):
                release.changelog_candidates(self.root, version, day)

    def test_cli_outputs_candidate_and_requires_date(self):
        command = [sys.executable, str(Path(release.__file__).resolve()), "--generate", "0.2.0"]
        result = subprocess.run(command + ["--date", "2026-11-07"], cwd=self.root,
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, self.candidates())
        result = subprocess.run(command, cwd=self.root, text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires --date", result.stderr)


if __name__ == "__main__":
    unittest.main()
