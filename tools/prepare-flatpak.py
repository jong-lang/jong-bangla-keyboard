#!/usr/bin/env python3
"""Export committed source and the local-only x86-64 Flatpak prototype inputs."""

import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args])


def prepare(root, output):
    if git(root, "status", "--porcelain", "--untracked-files=normal").strip():
        raise ValueError("commit or preserve outstanding work first; a clean checkout is required")
    commit = git(root, "rev-parse", "HEAD").decode().strip()
    archive = git(root, "archive", "--format=tar", commit)
    manifest_name = "org.fcitx.Fcitx5.Addon.Jong.json"
    # Read the recipe from that same commit, never from an uncommitted file.
    manifest = git(root, "show", f"{commit}:packaging/flatpak/{manifest_name}")
    output.mkdir(parents=True, exist_ok=False)
    (output / "source").mkdir()
    with tarfile.open(fileobj=io.BytesIO(archive)) as source:
        source.extractall(output / "source", filter="data")
    (output / manifest_name).write_bytes(manifest)
    (output / "source-info.json").write_text(json.dumps({
        "commit": commit,
        "git_archive_sha256": hashlib.sha256(archive).hexdigest(),
        "target": "x86_64",
        "status": "local prototype; desktop acceptance pending",
    }, indent=2, sort_keys=True) + "\n")
    print(f"Prepared {commit} in {output}; no build, installation or desktop changes")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="new input directory")
    args = parser.parse_args()
    try:
        prepare(Path(__file__).resolve().parent.parent, args.output.resolve())
    except (OSError, ValueError, subprocess.CalledProcessError, tarfile.TarError) as error:
        sys.exit(f"FAIL: {error}")


if __name__ == "__main__":
    main()
