#!/usr/bin/env python3
"""Validate a release's local metadata and extract its reviewed changelog notes."""

import argparse
from datetime import date
from pathlib import Path
import re
import subprocess
import sys
import tomllib


REQUIRED_SECTIONS = (
    "Highlights", "Fixes", "Breaking changes", "Installation and upgrade",
    "Tested environments", "Known issues",
)
VERSION = r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)(?:-(?:alpha|beta|rc)\.[1-9][0-9]*)?"


def check_versions(root, version):
    for name in ("Cargo.toml", "adapters/fcitx5/ffi/Cargo.toml"):
        package = tomllib.loads((root / name).read_text(encoding="utf-8"))["package"]
        if package["version"] != version:
            raise ValueError(f"{name}: package version must equal {version}")
    lock = tomllib.loads((root / "Cargo.lock").read_text(encoding="utf-8"))
    for name in ("jong-bangla-core", "jong-bangla-fcitx5-ffi"):
        packages = [p for p in lock["package"] if p["name"] == name]
        if len(packages) != 1 or packages[0]["version"] != version:
            raise ValueError(f"Cargo.lock: {name} version must equal {version}")
    metadata = (root / "adapters/fcitx5/jong-bangla.conf.in").read_text(encoding="utf-8")
    if re.findall(r"^Version=(.*)$", metadata, re.M) != [version]:
        raise ValueError(f"addon metadata Version must equal {version}")


def release_notes(root, tag):
    if not re.fullmatch(rf"v{VERSION}", tag):
        raise ValueError("tag must be vX.Y.Z or vX.Y.Z-{alpha,beta,rc}.N (N >= 1)")
    version = tag[1:]
    check_versions(root, version)

    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    if not re.search(r"^## Unreleased\s*$", changelog, re.M):
        raise ValueError("CHANGELOG.md must retain an Unreleased section")
    headings = list(re.finditer(r"^## (.+)$", changelog, re.M))
    matches = [
        (index, heading) for index, heading in enumerate(headings)
        if re.fullmatch(rf"{re.escape(version)} - \d{{4}}-\d{{2}}-\d{{2}}", heading[1])
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one changelog heading: ## {version} - YYYY-MM-DD")
    index, heading = matches[0]
    date.fromisoformat(heading[1].rsplit(" - ", 1)[1])
    end = headings[index + 1].start() if index + 1 < len(headings) else len(changelog)
    notes = changelog[heading.end():end].strip()
    if "{{" in notes or "}}" in notes:
        raise ValueError("replace all release-template placeholders")
    for section in REQUIRED_SECTIONS:
        match = re.search(rf"^### {re.escape(section)}\s*\n(.*?)(?=^### |\Z)", notes, re.M | re.S)
        if not match or not match[1].strip():
            raise ValueError(f"release notes require a nonempty '{section}' section")
    return f"# Jong Bangla {tag}\n\n{notes}\n"


def preparation_notes(root, base_version, base_changelog):
    """Allow the initial unreleased baseline, but validate every prepared release."""
    version = tomllib.loads((root / "Cargo.toml").read_text(encoding="utf-8"))["package"]["version"]
    if not re.fullmatch(VERSION, version):
        raise ValueError("package version must be X.Y.Z or X.Y.Z-{alpha,beta,rc}.N (N >= 1)")
    check_versions(root, version)
    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    if not re.search(r"^## Unreleased\s*$", changelog, re.M):
        raise ValueError("CHANGELOG.md must retain an Unreleased section")
    # A version bump or any release heading in either revision requires notes.
    # Keeping the base changelog here also catches removal of all dated notes.
    headings = re.findall(r"^## (.+)$", changelog + "\n" + base_changelog, re.M)
    if version == base_version and headings and all(h.strip() == "Unreleased" for h in headings):
        return None
    return release_notes(root, "v" + version)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("tag", nargs="?")
    mode.add_argument("--base", help="check release preparation against this Git revision")
    parser.add_argument("--notes-file", type=Path)
    args = parser.parse_args()
    if args.base and args.notes_file:
        parser.error("--notes-file requires an explicit tag")
    try:
        if args.base:
            base_manifest, base_changelog = [
                subprocess.check_output(["git", "show", f"{args.base}:{name}"], text=True)
                for name in ("Cargo.toml", "CHANGELOG.md")
            ]
            base_version = tomllib.loads(base_manifest)["package"]["version"]
            notes = preparation_notes(Path.cwd(), base_version, base_changelog)
        else:
            notes = release_notes(Path.cwd(), args.tag)
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        sys.exit(f"FAIL: {error}")
    if notes is None:
        print("PASS: consistent initial unreleased baseline; no release prepared")
        return
    if args.notes_file:
        args.notes_file.write_text(notes, encoding="utf-8")
    print("PASS: release matches manifests, lockfile, addon metadata and complete dated notes")


if __name__ == "__main__":
    main()
