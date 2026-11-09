"""Bounded desktop proof orchestration; no desktop access at import time."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time


class ProofError(Exception):
    """A required observation or operation could not be completed."""


def wait_for(probe, description, timeout=15):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = probe()
        if value:
            return value
        time.sleep(0.1)
    raise ProofError(f"Timed out: {description}")


def command(args):
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=5,
                                check=False)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ProofError(f"Could not run {args[0]}") from error
    if result.returncode:
        raise ProofError(f"{args[0]} exited {result.returncode}")
    return result.stdout.strip()


def prerequisites():
    if os.environ.get("XDG_SESSION_TYPE") != "wayland":
        raise ProofError("Run from a terminal in the KDE Plasma Wayland session")
    if "KDE" not in os.environ.get("XDG_CURRENT_DESKTOP", "").split(":"):
        raise ProofError("This proof currently targets KDE Plasma only")
    for name in ("WAYLAND_DISPLAY", "DBUS_SESSION_BUS_ADDRESS"):
        if not os.environ.get(name):
            raise ProofError(f"Missing session variable: {name}")
    for name in ("kwrite", "firefox", "fcitx5-remote"):
        if not shutil.which(name):
            raise ProofError(f"Missing executable: {name}")
    try:
        import gi
        gi.require_version("Atspi", "2.0")
        from gi.repository import Atspi, Gio, GLib  # noqa: F401
    except (ImportError, ValueError) as error:
        raise ProofError("Install PyGObject and the AT-SPI 2 introspection typelib") from error


def identity(root):
    """Record source/tool identity without exporting arbitrary environment data."""
    library = Path("/usr/lib/fcitx5/libjong-bangla.so")
    if not library.is_file():
        raise ProofError("Install Jong at /usr/lib/fcitx5/libjong-bangla.so before this Arch proof")
    return {
        "source_commit": command(["git", "-C", str(root), "rev-parse", "HEAD"]),
        "source_dirty": bool(command(["git", "-C", str(root), "status", "--porcelain"])),
        "tool_sha256": {name: hashlib.sha256((root / "tools" / name).read_bytes()).hexdigest()
                        for name in ("check-desktop.py", "desktop_proof.py", "desktop_linux.py")},
        "os_release": Path("/etc/os-release").read_text(),
        "kernel": os.uname().release,
        "installed_library_sha256": hashlib.sha256(library.read_bytes()).hexdigest(),
        "installed_library": str(library),
        "loaded_library_identity": "unverified; restart Fcitx5 after installation",
    }


def exercise(desktop, app, engine, expected, results):
    case = {"application": app.name, "engine": engine, "status": "failed",
            "expected": expected}
    try:
        desktop.focus(app)
        desktop.select_engine(app, engine)
        # Empty control first, then append Jong output to the same owned field.
        for code in (37, 23, 57):  # Linux evdev KEY_K, KEY_I, KEY_SPACE; no text injection.
            desktop.guard(app, engine)
            desktop.key(code)
        desktop.guard(app, engine)
        def matches():
            desktop.guard(app, engine)
            case["actual"] = desktop.text(app)
            return case["actual"] == expected
        wait_for(matches, "exact committed text")
        # Read again after a quiet interval to catch late/duplicate commits.
        time.sleep(0.3)
        if not matches():
            raise ProofError("Committed Unicode changed after settling")
        case["status"] = "pass"
    finally:
        if "actual" in case:
            case["codepoints"] = [f"U+{ord(ch):04X}" for ch in case["actual"]]
        results.append(case)


def prove(desktop, report):
    """Always restore runtime engine selection and close owned resources."""
    previous = desktop.snapshot_engine()
    try:
        with desktop:
            for name in ("kwrite", "firefox"):
                with desktop.application(name) as app:
                    report["applications"][name] = desktop.application_identity(app)
                    desktop.focus(app)
                    if desktop.text(app) != "":
                        raise ProofError("Test field was not empty")
                    exercise(desktop, app, "keyboard-us", "ki ", report["cases"])
                    exercise(desktop, app, "jong-bangla", "ki কি ", report["cases"])
        report["proof_status"] = "pass"
    finally:
        # A failed restore also invalidates the run, even after passing cases.
        desktop.restore_engine(previous)


def failure_chain(error):
    """Retain the original failure if a later cleanup operation also raises."""
    messages = []
    seen = set()
    while error is not None and id(error) not in seen:
        seen.add(id(error))
        messages.append(str(error) or type(error).__name__)
        error = error.__cause__ if error.__cause__ is not None else error.__context__
    return list(reversed(messages))


def run(output, desktop_factory, root):
    try:
        output.mkdir(parents=True, exist_ok=False)
    except FileExistsError as error:
        raise ProofError(f"Output already exists: {output}. Use a new --output directory; "
                         "existing reports were left untouched.") from error
    report = {"schema": 1, "proof_status": "incomplete", "acceptance_status": "incomplete",
              "cases": [], "applications": {},
              "unverified": ["preedit content/rendering", "editing and shortcuts",
                             "focus transitions", "password restrictions",
                             "package install/upgrade/removal"],
              "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    error_message = None
    try:
        report["identity"] = identity(root)
        prove(desktop_factory(), report)
    except (Exception, KeyboardInterrupt) as error:
        report["proof_status"] = "failed"
        report["error_chain"] = failure_chain(error)
        error_message = " -> ".join(report["error_chain"])
        report["error"] = error_message
    finally:
        (output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        summary = [f"Desktop proof: {report['proof_status']}",
                   "Full desktop acceptance: incomplete (proof only)"]
        summary.extend(f"{case['status'].upper()}: {case['application']} / {case['engine']}"
                       for case in report["cases"])
        if error_message:
            summary.append(f"FAIL: {error_message}")
        summary.append("Unverified: " + ", ".join(report["unverified"]))
        (output / "summary.txt").write_text("\n".join(summary) + "\n")
        print("\n".join(summary))
    return 0 if report["proof_status"] == "pass" else 1
