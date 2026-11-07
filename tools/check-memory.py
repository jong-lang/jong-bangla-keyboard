#!/usr/bin/env python3
"""Fail-closed synthetic native sanitizer or unsanitized Memcheck workloads."""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET


class CheckFailure(Exception):
    """A missing detector, failed control, or workload report."""


def run(command, env, logs, label, timeout=300):
    """Retain synthetic diagnostics, including partial output on timeout."""
    stdout = logs / f"{label}.stdout"
    stderr = logs / f"{label}.stderr"
    stdout.unlink(missing_ok=True)
    stderr.unlink(missing_ok=True)
    try:
        result = subprocess.run(command, env=env, capture_output=True, text=True,
                                timeout=timeout, check=False)
    except subprocess.TimeoutExpired as error:
        stdout.write_bytes(error.stdout or b"")
        stderr.write_bytes(error.stderr or b"")
        raise CheckFailure(f"{label}: timed out after {timeout} seconds") from error
    except OSError as error:
        raise CheckFailure(f"{label}: could not complete: {error}") from error
    stdout.write_text(result.stdout, encoding="utf-8")
    stderr.write_text(result.stderr, encoding="utf-8")
    return result


def require(result, code, diagnostic, label):
    if result.returncode != code or diagnostic not in result.stderr:
        raise CheckFailure(f"{label}: expected exit {code} and {diagnostic!r}; "
                           f"got exit {result.returncode}; inspect saved logs")
    print(f"PASS: {label} (exit {code})", flush=True)


def instrumentation(build, env, logs, enabled):
    objects = [
        "CMakeFiles/jong-bangla.dir/addon.cpp.o",
        "CMakeFiles/jong-fcitx5-harness.dir/tests/harness.cpp.o",
        "CMakeFiles/jong-ffi-memory.dir/tests/memory.cpp.o",
        "rust/release/libjong_bangla_fcitx5_ffi.a",
    ]
    for index, name in enumerate(objects):
        result = run(["llvm-nm", "--undefined-only", str(build / name)], env,
                     logs, f"instrumentation-{index}")
        expected = enabled and index < 3
        asan = bool(re.search(r"\b__asan_", result.stdout))
        ubsan = bool(re.search(r"\b__ubsan_", result.stdout))
        if result.returncode or asan != expected or ubsan != expected:
            raise CheckFailure(f"{name}: unexpected instrumentation "
                               f"(ASan={asan}, UBSan={ubsan}, expected={expected})")
    print("PASS: native/Rust instrumentation symbols match the selected recipe", flush=True)


def sanitizers(build, env, logs):
    env.update(
        ASAN_OPTIONS="detect_leaks=1:halt_on_error=1:abort_on_error=0:exitcode=23",
        LSAN_OPTIONS="exitcode=23",
        UBSAN_OPTIONS="halt_on_error=1:print_stacktrace=1:exitcode=23",
    )
    controls = [
        ("jong-memory-controls", "--address-control", 23,
         "ERROR: AddressSanitizer: heap-buffer-overflow", "native-address-control"),
        ("jong-memory-controls", "--undefined-control", 23,
         "runtime error: signed integer overflow", "native-undefined-control"),
        ("jong-ffi-memory", "--leak-control", 23,
         "ERROR: LeakSanitizer: detected memory leaks", "rust-allocation-leak-control"),
    ]
    for name, argument, code, diagnostic, label in controls:
        result = run([str(build / name), argument], env, logs, label)
        require(result, code, diagnostic, label)
    for name in ("jong-ffi-memory", "jong-fcitx5-harness"):
        result = run([str(build / name)], env, logs, name)
        if (result.returncode != 0 or "Sanitizer" in result.stderr or
                "runtime error:" in result.stderr):
            raise CheckFailure(f"{name}: exit {result.returncode} or sanitizer report")
        print(f"PASS: {name}; no sanitizer reports", flush=True)
    print("Coverage: native ASan/UBSan; LSan observes Rust allocator leaks. "
          "Rust instructions and system libraries are NOT instrumented.", flush=True)


def memcheck(command, env, logs, label, leak=False, suppression=None):
    report = logs / f"{label}.xml"
    # Do not accept a previous run's report if this invocation fails to write one.
    report.unlink(missing_ok=True)
    result = run([
        "valgrind", "--tool=memcheck", "--leak-check=full",
        "--show-leak-kinds=all", "--errors-for-leak-kinds=definite,indirect,possible",
        "--track-origins=yes", "--error-exitcode=23", "--xml=yes",
        f"--xml-file={report}",
        *([f"--suppressions={suppression}"] if suppression else []), *command,
    ], env, logs, label)
    try:
        root = ET.parse(report).getroot()
    except (OSError, ET.ParseError) as error:
        raise CheckFailure(f"{label}: missing/invalid Memcheck XML report "
                           f"(exit {result.returncode}); inspect saved logs") from error
    if (root.tag != "valgrindoutput" or root.findtext("tool") != "memcheck" or
            root.findtext("status[last()]/state") != "FINISHED"):
        raise CheckFailure(f"{label}: Memcheck did not finish")
    errors = root.findall("error")
    if leak:
        if (result.returncode != 23 or
                not any(e.findtext("kind") == "Leak_DefinitelyLost" for e in errors) or
                any(not e.findtext("kind", "").startswith("Leak_") for e in errors)):
            raise CheckFailure(f"{label}: detector missed intentional Rust allocation leak")
    elif result.returncode != 0 or any(
            e.findtext("kind") != "Leak_StillReachable" for e in errors):
        raise CheckFailure(f"{label}: exit {result.returncode} or Memcheck error")
    print(f"PASS: {label}" + ("; intentional leak detected" if leak else
                             "; no Memcheck errors (reachable blocks permitted)"), flush=True)
    if suppression:
        for pair in root.findall("suppcounts/pair"):
            print(f"  Suppression: {pair.findtext('name')} "
                  f"(count {pair.findtext('count')})", flush=True)
    return result


def valgrind(build, env, logs):
    memcheck([str(build / "jong-ffi-memory"), "--leak-control"], env, logs,
             "memcheck-rust-allocation-control", leak=True)
    for name in ("jong-ffi-memory", "jong-fcitx5-harness"):
        memcheck([str(build / name)], env, logs, f"memcheck-{name}")

    # Run existing private panic probes directly, avoiding the parent test which
    # intentionally aborts children. No fault injection enters the shipped ABI.
    root = Path(__file__).resolve().parents[1]
    result = run([
        "cargo", "test", "--offline", "--locked", "--release",
        "--manifest-path", str(root / "Cargo.toml"),
        "--target-dir", str(build / "rust-panic-tests"),
        "-p", "jong-bangla-fcitx5-ffi", "--lib", "--no-run", "--message-format=json",
    ], env, logs, "build-rust-panic-tests")
    if result.returncode != 0:
        raise CheckFailure("could not build Rust panic tests; inspect saved logs")
    binaries = []
    for line in result.stdout.splitlines():
        try:
            artifact = json.loads(line)
        except json.JSONDecodeError as error:
            raise CheckFailure("invalid Cargo artifact output") from error
        if (artifact.get("reason") == "compiler-artifact" and
                artifact.get("profile", {}).get("test") and artifact.get("executable")):
            binaries.append(artifact["executable"])
    if len(binaries) != 1:
        raise CheckFailure("could not identify exactly one Rust panic test binary")
    command = [binaries[0], "--exact", "panic_tests::panic_policy_child",
               "--ignored", "--nocapture", "--test-threads=1"]
    for mode, label, leak in [("0", "ordinary-panic-cleanup", False),
                              ("1", "replacement-payload-retention", True)]:
        result = memcheck(command, dict(env, JONG_TEST_PANIC_MODE=mode, RUST_BACKTRACE="0"),
                          logs, label, leak=leak,
                          suppression=root / "tools/valgrind-rust-tests.supp")
        if "1 passed; 0 failed" not in result.stdout:
            raise CheckFailure(f"{label}: Rust panic probe did not pass exactly one test")
    print("Coverage: executed Rust/native machine code under Memcheck; "
          "replacement panic payload retention is expected, not leak freedom.", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("build", type=Path)
    parser.add_argument("--mode", choices=("sanitizers", "valgrind"), default="sanitizers")
    args = parser.parse_args()
    build = args.build.resolve()
    logs = build / f"memory-logs-{args.mode}"
    try:
        metadata = dict(line.split("=", 1) for line in
                        (build / "memory-build.txt").read_text().splitlines())
        expected = "ON" if args.mode == "sanitizers" else "OFF"
        if metadata.get("sanitizers") != expected:
            raise CheckFailure(f"{args.mode} requires JONG_ENABLE_SANITIZERS={expected}")
        if args.mode == "valgrind" and metadata.get("build_type") != "Release":
            raise CheckFailure("Memcheck requires a separate unsanitized Release build")
        logs.mkdir(exist_ok=True)
        print(f"Synthetic logs: {logs}", flush=True)
        env = dict(os.environ, LC_ALL="C")
        # Override user detector settings: disabling checks must never pass.
        for name in ("ASAN_OPTIONS", "LSAN_OPTIONS", "UBSAN_OPTIONS", "VALGRIND_OPTS"):
            env.pop(name, None)
        instrumentation(build, env, logs, args.mode == "sanitizers")
        if args.mode == "sanitizers":
            sanitizers(build, env, logs)
        else:
            valgrind(build, env, logs)
    except (CheckFailure, OSError, ValueError) as error:
        sys.exit(f"FAIL: {error}")


if __name__ == "__main__":
    main()
