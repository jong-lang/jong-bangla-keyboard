"""Run the real cargo-deny against tiny offline path-dependency graphs.

No third-party source is copied or built. These fixtures test name/license
policy, not behavior of the actual crates with these names. CI's dependency
job installs cargo-deny before running this module, so skips are local-only.
"""

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


CONFIG = Path(__file__).resolve().parents[2] / "deny.toml"


@unittest.skipUnless(shutil.which("cargo-deny"), "cargo-deny not installed; required in dependency CI job")
class DependencyPolicy(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def crate(self, name, license="MIT", dependency=None, kind="dependencies"):
        directory = self.root / name
        (directory / "src").mkdir(parents=True, exist_ok=True)
        manifest = f'[package]\nname = "{name}"\nversion = "0.1.0"\nedition = "2024"\npublish = false\n'
        if license is not None:
            manifest += f'license = "{license}"\n'
        if dependency:
            # A rename must not hide the actual banned package name.
            manifest += f'[{kind}]\nrenamed = {{ package = "{dependency}", path = "../{dependency}" }}\n'
        (directory / "Cargo.toml").write_text(manifest)
        (directory / "src/lib.rs").write_text("// independently authored synthetic fixture\n")
        return directory

    def check(self, root, *checks):
        subprocess.run(["cargo", "generate-lockfile", "--offline"], cwd=root, check=True, capture_output=True)
        return subprocess.run([
            "cargo", "deny", "--manifest-path", str(root / "Cargo.toml"),
            "--workspace", "--all-features", "--locked", "--offline",
            "--config", str(CONFIG), "check", *checks,
        ], cwd=root, text=True, capture_output=True)

    def test_permissive_private_transitive_graph_passes(self):
        self.crate("leaf", "MIT OR Apache-2.0")
        self.crate("middle", "BSD-3-Clause", "leaf")
        root = self.crate("fixture", dependency="middle")
        result = self.check(root, "bans", "licenses", "sources")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_banned_direct_transitive_and_dev_dependencies_fail(self):
        self.crate("reqwest")
        self.crate("middle", dependency="reqwest")
        for kind, dependency in (
            ("dependencies", "reqwest"), ("dependencies", "middle"),
            ("dev-dependencies", "reqwest"), ("build-dependencies", "reqwest"),
            ('target.\'cfg(windows)\'.dependencies', "reqwest"),
        ):
            with self.subTest(kind=kind, dependency=dependency):
                root = self.crate("fixture", dependency=dependency, kind=kind)
                result = self.check(root, "bans")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("banned", result.stderr)
                self.assertIn("reqwest", result.stderr)
                shutil.rmtree(root)

    def test_unapproved_and_missing_transitive_licenses_fail(self):
        for license in ("GPL-3.0-only", None):
            with self.subTest(license=license):
                self.crate("leaf", license)
                self.crate("middle", dependency="leaf")
                root = self.crate("fixture", dependency="middle")
                result = self.check(root, "licenses")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("leaf", result.stderr)
                self.assertRegex(result.stderr, "unlicensed|license-not-encountered|rejected")
                for directory in self.root.iterdir():
                    shutil.rmtree(directory)

    def test_dev_and_build_dependency_licenses_are_checked(self):
        self.crate("leaf", "GPL-3.0-only")
        for kind in ("dev-dependencies", "build-dependencies"):
            with self.subTest(kind=kind):
                root = self.crate("fixture", dependency="leaf", kind=kind)
                result = self.check(root, "licenses")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("rejected", result.stderr)
                shutil.rmtree(root)


if __name__ == "__main__":
    unittest.main()
