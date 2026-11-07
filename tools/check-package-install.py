#!/usr/bin/env python3
"""Exercise package-manager lifecycle in a disposable container, never the host."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


LAYOUT = {
    "deb": ("/usr/lib/x86_64-linux-gnu/fcitx5", "/usr/share/doc/jong-bangla/LICENSE"),
    "rpm": ("/usr/lib64/fcitx5", "/usr/share/licenses/jong-bangla/LICENSE"),
    "arch": ("/usr/lib/fcitx5", "/usr/share/licenses/jong-bangla/LICENSE"),
}


def run(args, success=True):
    result = subprocess.run([str(a) for a in args], text=True, capture_output=True)
    print(result.stdout, end="", flush=True)
    print(result.stderr, end="", file=sys.stderr, flush=True)
    if (result.returncode == 0) != success:
        raise ValueError(f"unexpected exit {result.returncode}: {args[0]}")
    return result.stdout + result.stderr


def check(kind, first, second):
    if not Path("/.dockerenv").exists() or os.environ.get("JONG_PACKAGE_TEST") != "1":
        raise ValueError("package lifecycle tests require the disposable Docker runner")
    addon, license_file = LAYOUT[kind]
    library = Path(addon) / "libjong-bangla.so"
    data = Path("/usr/share/fcitx5")
    required = {library, data / "addon/jong-bangla.conf", data / "inputmethod/jong-bangla.conf",
                Path(license_file), Path("/usr/share/doc/jong-bangla/PACKAGING.md")}
    notices = Path(license_file).with_name("THIRD_PARTY_NOTICES")
    if kind == "deb":
        notices = Path("/usr/share/doc/jong-bangla/THIRD_PARTY_NOTICES")
    required.add(notices)
    stdlib = Path(license_file).parent / "rust-stdlib"
    required.update({stdlib / "COPYRIGHT-library.html", stdlib / "rustc-version.txt",
                     *(stdlib / "licenses" / name for name in (
                         "MIT.txt", "Apache-2.0.txt", "BSD-2-Clause.txt", "Unicode-3.0.txt"))})
    # Preserve both an unrelated addon and a synthetic user's existing profile.
    sentinel = Path(addon) / "jong-unrelated.keep"
    profile = Path.home() / ".config/fcitx5/profile"
    for path in (sentinel, profile):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("synthetic unrelated data\n")
    harness = ["/opt/jong-package-test/harness", "--installed", data, addon]
    install = {"deb": ["apt-get", "install", "-y"], "rpm": ["dnf", "install", "-y"],
               "arch": ["pacman", "-U", "--noconfirm"]}[kind]
    query = {"deb": ["dpkg-query", "-L", "jong-bangla"], "rpm": ["rpm", "-ql", "jong-bangla"],
             "arch": ["pacman", "-Qlq", "jong-bangla"]}[kind]
    installed_versions = []
    for package in (first, second):
        run([*install, package])
        listing = set(run(query).splitlines())
        missing = [str(path) for path in required if not path.is_file() or str(path) not in listing]
        if missing:
            raise ValueError(f"package must own every required runtime, license and instruction file: {sorted(missing)}")
        if "Library=libjong-bangla\n" not in (data / "addon/jong-bangla.conf").read_text():
            raise ValueError("addon registration must be relocatable")
        if "Addon=jong-bangla\n" not in (data / "inputmethod/jong-bangla.conf").read_text():
            raise ValueError("input method must reference the Jong addon")
        linking = run(["ldd", "-r", library])
        if "not found" in linking or "undefined symbol" in linking:
            raise ValueError("installed addon has unresolved runtime dependencies")
        run(harness)
        version_query = {"deb": ["dpkg-query", "-W", "-f=${Version}", "jong-bangla"],
                         "rpm": ["rpm", "-q", "--qf", "%{VERSION}-%{RELEASE}", "jong-bangla"],
                         "arch": ["pacman", "-Q", "jong-bangla"]}[kind]
        installed_versions.append(run(version_query).strip())
        if any(p.read_text() != "synthetic unrelated data\n" for p in (sentinel, profile)):
            raise ValueError("installation/upgrade changed unrelated files or the user profile")
    if installed_versions[0] == installed_versions[1]:
        raise ValueError("upgrade control must install a distinct newer package revision")
    hidden = library.with_suffix(".hidden")
    library.rename(hidden)
    try:
        missing = run(harness, success=False)
        if "load Jong addon from configured library path" not in missing:
            raise ValueError("missing-library control failed for an unrelated reason")
    finally:
        hidden.rename(library)
    remove = {"deb": ["apt-get", "purge", "-y", "jong-bangla"],
              "rpm": ["dnf", "remove", "-y", "--setopt=clean_requirements_on_remove=False", "jong-bangla"],
              "arch": ["pacman", "-R", "--noconfirm", "jong-bangla"]}[kind]
    run(remove)
    if any(p.exists() for p in required):
        raise ValueError("removal left package-owned runtime files")
    if any(p.read_text() != "synthetic unrelated data\n" for p in (sentinel, profile)):
        raise ValueError("removal changed unrelated files or the user profile")
    run(harness, success=False)
    manager = {"deb": ["dpkg-query", "-W"], "rpm": ["rpm", "-qa"], "arch": ["pacman", "-Q"]}[kind]
    return {"format": kind, "install_upgrade_remove": True, "installed_versions": installed_versions,
            "missing_library_rejected": True, "unrelated_files_preserved": True,
            "os_release": Path("/etc/os-release").read_text(), "runtime_packages": run(manager).splitlines(),
            "artifacts": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (first, second)}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("format", choices=LAYOUT)
    parser.add_argument("first", type=Path)
    parser.add_argument("second", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        report = check(args.format, args.first, args.second)
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    except (OSError, ValueError) as error:
        sys.exit(f"FAIL: {error}")


if __name__ == "__main__":
    main()
