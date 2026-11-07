#!/usr/bin/env python3
"""Combine the native bundle and verified packages into a complete release bundle."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

from package_bundle import package_assets, verify_packages


def assemble(native, packages, destination):
    destination.mkdir(parents=True, exist_ok=False)
    info = json.loads((native / "build-info.json").read_text())
    version = info["version"]
    expected = package_assets(version)
    # Native draft checksums must already cover the source archive being used.
    original = {line.split("  ")[1]: line.split("  ")[0]
                for line in (native / "SHA256SUMS").read_text().splitlines()}
    base_names = {f"jong-bangla-{version}.tar.gz", f"jong-bangla-{version}-fcitx5-x86_64-linux-gnu.tar.gz", "build-info.json"}
    if original.keys() != base_names or {p.name for p in native.iterdir()} != base_names | {"SHA256SUMS"}:
        raise ValueError("native bundle asset set differs")
    for name, digest in original.items():
        path = native / name
        if not path.is_file() or path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f"native bundle checksum mismatch: {name}")
        shutil.copyfile(path, destination / name)
    for name in expected:
        matches = list(packages.glob(f"*/{name}"))
        if len(matches) != 1 or not matches[0].is_file() or matches[0].is_symlink():
            raise ValueError(f"expected exactly one package asset: {name}")
        shutil.copyfile(matches[0], destination / name)
    verify_packages(destination, version)
    paths = sorted(destination.iterdir())
    with (destination / "SHA256SUMS").open("x") as output:
        for path in paths:
            output.write(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n")
    print(f"PASS: complete native/package bundle in {destination}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native", required=True, type=Path)
    parser.add_argument("--packages", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        assemble(args.native, args.packages, args.output)
    except (OSError, ValueError, KeyError, TypeError) as error:
        sys.exit(f"FAIL: {error}")


if __name__ == "__main__":
    main()
