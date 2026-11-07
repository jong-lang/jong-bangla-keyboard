#!/usr/bin/env python3
"""Generate review candidates, validate release metadata, or extract reviewed notes."""

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


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def changelog_candidates(root, version, release_date, since=None, until="HEAD"):
    """Use first-parent commits so merged PR commits are not counted twice."""
    if not re.fullmatch(VERSION, version):
        raise ValueError("candidate version must be a supported semantic version")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", release_date):
        raise ValueError("candidate date must be YYYY-MM-DD")
    date.fromisoformat(release_date)
    head = git(root, "rev-parse", "--verify", "--end-of-options", until + "^{commit}")
    if since is None:
        tags = [tag for tag in git(root, "tag", "--merged", head).splitlines()
                if re.fullmatch(rf"v{VERSION}", tag)]
        if tags:
            since = git(root, "describe", "--tags", "--abbrev=0",
                        *("--match=" + tag for tag in tags), head)
    base = None
    if since is not None:
        base = git(root, "rev-parse", "--verify", "--end-of-options", since + "^{commit}")
        subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", base, head], check=True)
    revision = f"{base}..{head}" if base else head
    records = git(root, "log", "--first-parent", "--reverse", "--format=%H%x00%B%x00", revision).split("\0")
    groups = {name: [] for name in (*REQUIRED_SECTIONS, "Other changes")}
    for index in range(0, len(records) - 1, 2):
        commit, message = records[index].strip(), records[index + 1].strip()
        subject, _, body = message.partition("\n")
        header = re.fullmatch(r"([A-Za-z]+)(?:\(([^()]+)\))?(!)?: (.+)", subject)
        footer = re.search(r"^BREAKING(?: CHANGE|-CHANGE):[ \t]*(.+)", body, re.M)
        group = "Other changes"
        summary = subject
        if header:
            kind, scope, breaking, description = header.groups()
            kind = kind.lower()
            summary = f"{scope}: {description}" if scope else description
            if kind in ("feat", "perf"):
                group = "Highlights"
            elif kind in ("fix", "revert"):
                group = "Fixes"
            if breaking and not footer:
                groups["Breaking changes"].append(f"- {summary} ({commit[:12]})")
        if footer:
            # Retain continuation text, stopping at the next conventional footer.
            detail = body[footer.start(1):]
            detail = re.split(r"\n[A-Za-z-]+(?:: | #)", detail, maxsplit=1)[0]
            groups["Breaking changes"].append(f"- {' '.join(detail.split())} ({commit[:12]})")
        groups[group].append(f"- {summary} ({commit[:12]})")
    for section in ("Installation and upgrade", "Tested environments", "Known issues"):
        groups[section] = [f"- {{{{Record reviewed {section.lower()} notes; do not infer support from builds.}}}}"]
    sections = [f"## {version} - {release_date}",
                f"<!-- Candidates from {revision}; curate user-visible changes before review. -->"]
    for name, entries in groups.items():
        sections.append(f"### {name}\n\n" + ("\n".join(entries) if entries else "None."))
    return "\n\n".join(sections) + "\n"


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
    mode.add_argument("--generate", metavar="VERSION", help="print candidate changelog entry for review")
    parser.add_argument("--date", help="explicit release date (YYYY-MM-DD), required with --generate")
    parser.add_argument("--since", help="exclude this ancestor; default: nearest reachable semantic version tag")
    parser.add_argument("--until", default="HEAD", help="candidate commit range endpoint (default: HEAD)")
    parser.add_argument("--notes-file", type=Path)
    args = parser.parse_args()
    if (args.base or args.generate) and args.notes_file:
        parser.error("--notes-file requires an explicit tag")
    if args.generate and not args.date:
        parser.error("--generate requires --date")
    if not args.generate and (args.date or args.since or args.until != "HEAD"):
        parser.error("--date, --since and --until require --generate")
    try:
        if args.generate:
            print(changelog_candidates(Path.cwd(), args.generate, args.date, args.since, args.until), end="")
            return
        elif args.base:
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
