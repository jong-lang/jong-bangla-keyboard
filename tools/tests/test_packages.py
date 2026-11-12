"""Source isolation and fail-closed package evidence regressions."""

import importlib.util
import io
from pathlib import Path
import tarfile
import tempfile
import sys
import unittest
from unittest.mock import patch


TOOLS = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), TOOLS / f"{name}.py")
    result = importlib.util.module_from_spec(spec)
    with patch.object(sys, "path", [str(TOOLS), *sys.path]):
        spec.loader.exec_module(result)
    return result


builder = module("build-packages")
installer = module("check-package-install")


class SourceIsolation(unittest.TestCase):
    def test_unsafe_source_roots_and_links_fail_before_extraction(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for names, link in ((["../escape"], False), (["/absolute"], False),
                                (["one/file", "two/file"], False), (["one/link"], True)):
                archive = root / "source.tar.gz"
                with tarfile.open(archive, "w:gz") as tar:
                    for name in names:
                        entry = tarfile.TarInfo(name)
                        if link:
                            entry.type = tarfile.SYMTYPE
                            entry.linkname = "../../escape"
                            tar.addfile(entry)
                        else:
                            entry.size = 4
                            tar.addfile(entry, io.BytesIO(b"test"))
                destination = root / "unpack"
                destination.mkdir(exist_ok=True)
                with self.subTest(names=names), self.assertRaises(ValueError):
                    builder.source_root(archive, destination)
                self.assertEqual(list(destination.iterdir()), [])

    def test_release_source_extracts_without_git_or_host_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "source.tar.gz"
            with tarfile.open(archive, "w:gz") as tar:
                entry = tarfile.TarInfo("jong-bangla-0.1.0/Cargo.toml")
                entry.size = 4
                tar.addfile(entry, io.BytesIO(b"test"))
            source = builder.source_root(archive, root / "unpack")
            self.assertEqual((source / "Cargo.toml").read_bytes(), b"test")

    def test_lifecycle_tool_refuses_to_run_package_manager_on_host(self):
        with patch.dict("os.environ", {"JONG_PACKAGE_TEST": "0"}), patch.object(installer, "run") as run:
            with self.assertRaisesRegex(ValueError, "disposable Docker"):
                installer.check("deb", Path("first.deb"), Path("second.deb"))
            run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
