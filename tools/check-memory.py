#!/usr/bin/env python3
"""Check synthetic heap ownership; reject an unavailable/broken leak detector."""

import os
from pathlib import Path
import subprocess
import sys


def main():
    if len(sys.argv) not in (2, 3):
        sys.exit("usage: python3 tools/check-memory.py FCITX5_SANITIZED_BUILD [IBUS_SANITIZED_BUILD]")
    build = Path(sys.argv[1]).resolve()
    env = dict(os.environ)
    env.update(
        ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",
        LSAN_OPTIONS="exitcode=23",
        UBSAN_OPTIONS="halt_on_error=1:print_stacktrace=1",
    )
    control = subprocess.run(
        [str(build / "jong-ffi-memory"), "--leak-control"],
        env=env, capture_output=True, text=True, timeout=120, check=False,
    )
    if (control.returncode != 23 or
            "ERROR: LeakSanitizer: detected memory leaks" not in control.stderr):
        sys.stderr.write(control.stdout + control.stderr)
        sys.exit("FAIL: detector did not identify the intentional Rust session leak")
    print("PASS: detector identified intentional Rust session leak (exit 23)", flush=True)
    for name in ["jong-ffi-memory", "jong-fcitx5-harness"]:
        result = subprocess.run(
            [str(build / name)], env=env, capture_output=True, text=True,
            timeout=120, check=False,
        )
        if result.returncode != 0 or "Sanitizer" in result.stderr:
            sys.stderr.write(result.stdout + result.stderr)
            sys.exit(f"FAIL: {name} (exit {result.returncode})")
        print(f"PASS: {name}; ASan/UBSan/LSan enabled; no reports", flush=True)
        print(result.stdout.strip(), flush=True)

    if len(sys.argv) == 3:
        ibus_build = Path(sys.argv[2]).resolve()
        for name in ("jong-ibus-harness", "ibus-engine-jong-bangla"):
            symbols = subprocess.check_output(["nm", "-D", str(ibus_build / name)], text=True)
            if "__asan_init" not in symbols or "__ubsan_handle_" not in symbols:
                sys.exit(f"FAIL: {name} must have address/undefined-behavior instrumentation")
        result = subprocess.run(
            [sys.executable, str(Path(__file__).with_name("run-ibus-tests.py")),
             str(ibus_build / "jong-ibus-harness"),
             str(ibus_build / "ibus-engine-jong-bangla")],
            env=env, capture_output=True, text=True, timeout=60, check=False,
        )
        if result.returncode != 0 or "Sanitizer" in result.stderr:
            sys.stderr.write(result.stdout + result.stderr)
            sys.exit(f"FAIL: IBus service memory check (exit {result.returncode})")
        print("PASS: IBus production service; ASan/UBSan/LSan enabled; no reports", flush=True)


if __name__ == "__main__":
    main()
