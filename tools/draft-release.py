#!/usr/bin/env python3
"""Validate a complete release bundle and create a new, unpublished GitHub draft."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile


def capture(args):
    return subprocess.check_output([str(arg) for arg in args], text=True).strip()


def verify_bundle(directory, version, commit):
    expected = {f"jong-bangla-{version}.tar.gz",
                f"jong-bangla-{version}-fcitx5-x86_64-linux-gnu.tar.gz", "build-info.json"}
    actual = {path.name for path in directory.iterdir()}
    if actual != expected | {"SHA256SUMS"}:
        raise ValueError("release bundle has missing or unexpected artifacts")
    if any(not path.is_file() or path.is_symlink() or path.stat().st_size == 0
           for path in directory.iterdir()):
        raise ValueError("release assets must be nonempty regular files")
    checksums = {}
    for line in (directory / "SHA256SUMS").read_text().splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9._-]+)", line)
        if not match or match[2] in checksums:
            raise ValueError("malformed or duplicate checksum entry")
        checksums[match[2]] = match[1]
    if checksums.keys() != expected:
        raise ValueError("SHA256SUMS must cover every payload exactly once (excluding itself)")
    for name, digest in checksums.items():
        if hashlib.sha256((directory / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"checksum mismatch: {name}")
    info = json.loads((directory / "build-info.json").read_text())
    if (info["commit"] != commit or info["version"] != version
            or info["target"] != "x86_64-linux-gnu" or info["independent_builds_identical"] is not True):
        raise ValueError("build info must match the tagged commit, version and reproducibility check")
    return sorted(directory.iterdir())


def draft(root, tag, directory, repository):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("repository must be OWNER/NAME")
    with tempfile.TemporaryDirectory(prefix="jong-draft-") as temporary:
        work = Path(temporary)
        notes = work / "notes.md"
        subprocess.run([sys.executable, str(root / "tools/check-release.py"), tag,
                        "--notes-file", str(notes)], cwd=root, check=True)
        commit = capture(["git", "-C", root, "rev-parse", "--verify", "--end-of-options", tag + "^{commit}"])
        if commit != capture(["git", "-C", root, "rev-parse", "HEAD^{commit}"]):
            raise ValueError("release tag must point to the checked-out commit")
        assets = verify_bundle(directory, tag[1:], commit)
        # Listing must succeed. An authentication/network error is never absence.
        tags = capture(["gh", "api", "--paginate", f"repos/{repository}/releases", "--jq", ".[].tag_name"])
        if tag in tags.splitlines():
            raise ValueError("release already exists; inspect it without overwriting or retrying uploads")
        command = ["gh", "release", "create", tag, "--repo", repository, "--draft", "--verify-tag",
                   "--latest=false", "--notes-file", str(notes), "--title", f"Jong Bangla {tag}"]
        if "-" in tag:
            command.append("--prerelease")
        # A failed upload leaves the release a draft. Never publish, edit or delete it.
        subprocess.run([*command, *(str(path) for path in assets)], check=True)
        state = json.loads(capture(["gh", "release", "view", tag, "--repo", repository,
                                    "--json", "isDraft,tagName,assets"]))
        if (state["isDraft"] is not True or state["tagName"] != tag
                or {asset["name"] for asset in state["assets"]} != {path.name for path in assets}):
            raise ValueError("remote draft state or asset set differs; maintainer inspection required")
        downloaded = work / "downloaded"
        subprocess.run(["gh", "release", "download", tag, "--repo", repository,
                        "--dir", str(downloaded)], check=True)
        for path in assets:
            if (downloaded / path.name).read_bytes() != path.read_bytes():
                raise ValueError(f"uploaded asset differs: {path.name}; leave draft unpublished")
    print("PASS: complete draft and downloaded assets verified; maintainer publication required")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag")
    parser.add_argument("--artifacts", required=True, type=Path)
    parser.add_argument("--repo", required=True)
    args = parser.parse_args()
    try:
        draft(Path.cwd(), args.tag, args.artifacts.resolve(), args.repo)
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        sys.exit(f"FAIL: {error}")


if __name__ == "__main__":
    main()
