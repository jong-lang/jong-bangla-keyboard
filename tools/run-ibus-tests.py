#!/usr/bin/env python3
"""Run the IBus protocol client on a private bus and temporary XDG directories."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile


def main():
    if len(sys.argv) not in (3, 4):
        sys.exit("usage: run-ibus-tests.py HARNESS ENGINE_EXECUTABLE [COMPONENT_XML]")
    with tempfile.TemporaryDirectory(prefix="jong-ibus-test-") as directory:
        env = dict(os.environ)
        for key, suffix in (("XDG_CONFIG_HOME", "config"),
                            ("XDG_CACHE_HOME", "cache"),
                            ("XDG_DATA_HOME", "data"),
                            ("XDG_RUNTIME_DIR", "runtime")):
            path = Path(directory) / suffix
            path.mkdir(mode=0o700)
            env[key] = str(path)
        for key in ("DISPLAY", "WAYLAND_DISPLAY", "IBUS_ADDRESS", "DBUS_SESSION_BUS_ADDRESS"):
            env.pop(key, None)
        env["G_DEBUG"] = "fatal-warnings"
        # Desktop GVfs can mount below XDG_RUNTIME_DIR and outlive the private bus.
        # These protocol tests need only local files and must not activate it.
        env["GIO_USE_VFS"] = "local"
        result = subprocess.run(
            ["dbus-run-session", "--", *sys.argv[1:]], env=env, check=False,
            timeout=45,
        )
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
