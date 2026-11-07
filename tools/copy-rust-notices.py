#!/usr/bin/env python3
"""Copy the actual build toolchain's standard-library notices into a package."""

from pathlib import Path
import shutil
import subprocess
import sys


def copy(destination):
    sysroot = Path(subprocess.check_output(["rustc", "--print", "sysroot"], text=True).strip())
    documents = [sysroot / "share/doc/rust", sysroot / "share/doc/rustc"]
    notices = [path / "COPYRIGHT-library.html" for path in documents]
    notices.append(sysroot / "share/licenses/rust/COPYRIGHT-library.html.rustc")
    notice = next((path for path in notices if path.is_file()), None)
    licenses = next((path / "licenses" for path in documents if (path / "licenses").is_dir()), None)
    if notice is None or licenses is None or not all((licenses / name).is_file() for name in (
            "MIT.txt", "Apache-2.0.txt", "BSD-2-Clause.txt", "Unicode-3.0.txt")):
        raise ValueError("build toolchain must supply Rust standard-library copyright and license texts")
    destination.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(notice, destination / "COPYRIGHT-library.html")
    shutil.copytree(licenses, destination / "licenses")
    (destination / "rustc-version.txt").write_text(subprocess.check_output(["rustc", "-vV"], text=True))


if __name__ == "__main__":
    try:
        if len(sys.argv) != 2:
            raise ValueError("usage: python3 tools/copy-rust-notices.py NEW_DESTINATION")
        copy(Path(sys.argv[1]))
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        sys.exit(f"FAIL: {error}")
