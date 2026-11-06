#!/usr/bin/env python3
"""Verify the staged IBus payload and actual service without a desktop daemon."""

import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import tomllib
import xml.etree.ElementTree as ET


def require(condition, message):
    if not condition:
        sys.exit(f"FAIL: {message}")


def run(args, *, env=None, success=True):
    result = subprocess.run([str(arg) for arg in args], env=env, capture_output=True,
                            text=True, timeout=60, check=False)
    if (result.returncode == 0) != success:
        sys.stderr.write(result.stdout + result.stderr)
        sys.exit(f"FAIL: unexpected exit {result.returncode}: {args[0]}")
    return result


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: check-ibus-install.py BUILD_DIRECTORY")
    root = Path(__file__).resolve().parent.parent
    build = Path(sys.argv[1]).resolve()
    destinations = (build / "install-layout.txt").read_text().splitlines()
    require(len(destinations) == 2, "expected executable and registration destinations")
    require(all(Path(p).is_absolute() and ".." not in Path(p).parts for p in destinations),
            "installation destinations must be absolute without '..'")
    version = tomllib.loads((root / "Cargo.toml").read_text())["package"]["version"]
    with tempfile.TemporaryDirectory(prefix="jong-ibus-install-") as directory:
        stage = Path(directory)
        executable, metadata = [stage / Path(p).relative_to("/") for p in destinations]
        expected = {executable, metadata}
        run(["cmake", "--install", build], env=dict(os.environ, DESTDIR=str(stage)))
        require({p for p in stage.rglob("*") if p.is_file()} == expected,
                "expected exactly the executable and XML registration")
        component = ET.parse(metadata).getroot()
        require(component.findtext("name") == "org.freedesktop.IBus.JongBangla",
                "component service name")
        require(component.findtext("version") == version, "component version matches Cargo")
        require(component.findtext("engines/engine/name") == "jong-bangla", "engine identifier")
        require(component.findtext("engines/engine/language") == "bn", "Bangla language tag")
        require(shlex.split(component.findtext("exec")) == [destinations[0], "--ibus"],
                "XML command must address the installed executable with --ibus")
        require(str(build) not in metadata.read_text(), "no build path in metadata")
        require(run([executable, "--version"]).stdout.strip() == f"Jong Bangla IBus {version}",
                "staged executable version")
        require("must be launched by IBus" in run([executable], success=False).stderr,
                "bare execution must not connect to a user's session")
        print("PASS: two staged files; registration, command and version match", flush=True)
        harness = [sys.executable, root / "tools/run-ibus-tests.py",
                   build / "jong-ibus-harness", executable, metadata]
        run(harness)
        print("PASS: staged production service passes the private D-Bus suite", flush=True)
        hidden = executable.with_suffix(".hidden")
        executable.rename(hidden)
        try:
            require("IBus harness failed:" in run(harness, success=False).stderr,
                    "absent staged executable must fail without build/system fallback")
        finally:
            hidden.rename(executable)
        sentinel = executable.parent / "unrelated.keep"
        sentinel.write_text("retain unrelated files\n")
        for path in expected:
            path.unlink()
        require({p for p in stage.rglob("*") if p.is_file()} == {sentinel},
                "remove only Jong's payload")
        print("PASS: missing executable rejected; removal retains unrelated files", flush=True)


if __name__ == "__main__":
    main()
