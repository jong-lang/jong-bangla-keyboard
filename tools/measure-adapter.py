#!/usr/bin/env python3
"""Run matched, sequential Linux/glibc Fcitx dispatcher resource probes (MIT)."""

import argparse
import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path
import platform
import select
import subprocess
import sys
import tempfile
from datetime import datetime, timezone


PHASES = ["idle", "short_pending", "short_cleared", "long_pending",
          "long_cleared", "sessions_1000", "sessions_2000", "context_destroyed"]
MEMORY_FIELDS = ["run", "mode", "phase", "rss_kib", "pss_kib", "private_kib",
                 "os_hwm_kib", "heap_used_bytes", "heap_reserved_bytes"]
TIMING_FIELDS = ["run", "mode", "workload", "raw_scalars", "actions_per_iteration",
                 "iterations", "min_ns", "median_ns", "p95_ns"]
WORKLOADS = [("type_commit:ami", 3, 4), ("type_commit:bangla", 6, 7),
             ("type_commit:shadhInota", 10, 11), ("type_commit:mixed", 13, 14),
             *[("insert_backspace_pair", n, 2) for n in (32, 128, 1024, 8192)],
             ("context_lifecycle", 13, 1)]


def command(args, cwd=None):
    return subprocess.check_output(args, cwd=cwd, text=True, stderr=subprocess.STDOUT,
                                   timeout=30).strip()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def proc_values(path):
    values = {}
    for line in path.read_text().splitlines():
        name, _, value = line.partition(":")
        if value.strip().endswith(" kB"):
            values[name] = int(value.split()[0])
    return values


def memory_probe(binary, mode, run):
    # stderr is a file so framework diagnostics cannot block a pipe. Each child
    # waits at named checkpoints while the parent reads its proc snapshots.
    with tempfile.TemporaryFile(mode="w+") as errors:
        child = subprocess.Popen([str(binary), mode, "memory"], stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, stderr=errors, text=True)
        rows = []
        try:
            for phase in PHASES:
                if not select.select([child.stdout], [], [], 180)[0]:
                    raise RuntimeError(f"{mode}/{phase}: checkpoint timed out")
                fields = child.stdout.readline().strip().split(",")
                if len(fields) != 3 or fields[0] != phase:
                    raise RuntimeError(f"{mode}/{phase}: invalid checkpoint {fields!r}")
                used, reserved = map(int, fields[1:])
                root = Path(f"/proc/{child.pid}")
                smaps = proc_values(root / "smaps_rollup")
                status = proc_values(root / "status")
                if not 0 < used <= reserved or smaps["Rss"] <= 0:
                    raise RuntimeError("invalid allocator or RSS sample")
                rows.append(dict(zip(MEMORY_FIELDS, [
                    run, mode, phase, smaps["Rss"], smaps["Pss"],
                    smaps["Private_Clean"] + smaps["Private_Dirty"],
                    status["VmHWM"], used, reserved,
                ])))
                child.stdin.write("\n")
                child.stdin.flush()
            remaining, _ = child.communicate(timeout=30)
            if child.returncode or remaining.strip():
                raise RuntimeError(f"{mode}: incomplete/failed memory probe")
        except BaseException:
            child.kill()
            child.wait()
            errors.seek(0)
            sys.stderr.write(errors.read())
            raise
    return rows


def timing_probe(binary, mode, run):
    result = subprocess.run([str(binary), mode, "timing"], capture_output=True,
                            text=True, timeout=180, check=False)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    rows = list(csv.DictReader(io.StringIO(result.stdout)))
    actual = [(row["workload"], int(row["raw_scalars"]),
               int(row["actions_per_iteration"])) for row in rows]
    if actual != WORKLOADS:
        raise RuntimeError(f"unexpected timing workloads: {actual!r}")
    for row in rows:
        if not all(math.isfinite(float(row[key])) for key in
                   ("min_ns", "median_ns", "p95_ns")) or not (
                0 < float(row["min_ns"]) <= float(row["median_ns"]) <=
                float(row["p95_ns"])) or int(row["iterations"]) < 1:
            raise RuntimeError("invalid timing sample")
        row.update(run=run, mode=mode)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("build", type=Path, help="unsanitized Release CMake directory")
    parser.add_argument("--output", type=Path, required=True, help="CSV/metadata directory")
    parser.add_argument("--runs", type=int, default=3, choices=range(1, 11))
    args = parser.parse_args()
    build = args.build.resolve()
    binary = build / "jong-fcitx5-resources"
    addon = build / "libjong-bangla.so"
    cache = (build / "CMakeCache.txt").read_text()
    if "CMAKE_BUILD_TYPE:STRING=Release\n" not in cache:
        sys.exit("use a matched -DCMAKE_BUILD_TYPE=Release build")
    if os.environ.get("LD_PRELOAD") or os.environ.get("LD_AUDIT"):
        sys.exit("remove LD_PRELOAD/LD_AUDIT for unsanitized measurements")
    for path in (binary, addon):
        symbols = command(["nm", "-D", str(path)])
        if any(name in symbols for name in ("__asan_", "__ubsan_", "__tsan_", "__lsan_")):
            sys.exit("sanitizer-instrumented builds are unsuitable for resource measurements")
    repo = Path(__file__).resolve().parent.parent
    tracked_sources = ["adapters/fcitx5/tests/resources.cpp", "adapters/fcitx5/CMakeLists.txt",
                       "tools/measure-adapter.py", "adapters/fcitx5/addon.cpp",
                       "adapters/fcitx5/ffi/src/lib.rs", "src/composition.rs"]
    metadata = {
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "runs": args.runs, "build": str(build), "platform": platform.platform(),
        "cpuinfo": Path("/proc/cpuinfo").read_text().split("\n\n")[0],
        "libc": platform.libc_ver(), "python": sys.version,
        "rustc": command(["rustc", "--version"]),
        "cxx": command(["c++", "--version"]).splitlines()[0],
        "fcitx5": command(["pkg-config", "--modversion", "Fcitx5Core"]),
        "cmake": command(["cmake", "--version"]).splitlines()[0],
        "git_head": command(["git", "rev-parse", "HEAD"], repo),
        "git_status": command(["git", "status", "--short"], repo),
        "sha256": {str(path.relative_to(repo)): digest(path)
                   for path in [repo / source for source in tracked_sources]},
        "binary_sha256": digest(binary), "addon_sha256": digest(addon),
        "cmake_cache_sha256": digest(build / "CMakeCache.txt"),
        "cmake_flags": [line for line in cache.splitlines() if line.startswith(
            ("CMAKE_BUILD_TYPE:", "CMAKE_CXX_COMPILER:", "CMAKE_CXX_FLAGS",
             "CMAKE_EXE_LINKER_FLAGS:", "CMAKE_SHARED_LINKER_FLAGS:"))],
        "allocator_environment": {key: os.environ[key] for key in (
            "GLIBC_TUNABLES", "MALLOC_ARENA_MAX", "MALLOC_ARENA_TEST", "MALLOC_CHECK_",
            "MALLOC_MMAP_MAX_", "MALLOC_MMAP_THRESHOLD_", "MALLOC_PERTURB_",
            "MALLOC_TOP_PAD_", "MALLOC_TRIM_THRESHOLD_") if key in os.environ},
        "rust_environment": {key: os.environ[key] for key in
                             ("RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS", "CARGO_PROFILE_RELEASE_OPT_LEVEL")
                             if key in os.environ},
        "method": "fresh processes; alternating baseline/Jong order; memory before timing; "
                  "31 batch means/workload; >=5ms adaptive calibration; key presses only; "
                  "no frontend, event loop, CPU pinning, malloc_trim or document retention",
    }
    memory_rows, timing_rows = [], []
    for run in range(1, args.runs + 1):
        modes = ("baseline", "jong") if run % 2 else ("jong", "baseline")
        for kind, probe, rows in (("memory", memory_probe, memory_rows),
                                  ("timing", timing_probe, timing_rows)):
            for mode in modes:
                rows.extend(probe(binary, mode, run))
                print(f"run {run}: {mode} {kind} complete", file=sys.stderr, flush=True)
    # Write only after all child exits, protocols and row counts were validated.
    args.output.mkdir(parents=True, exist_ok=True)
    for name, fields, rows in (("memory", MEMORY_FIELDS, memory_rows),
                                ("timing", TIMING_FIELDS, timing_rows)):
        with (args.output / f"{name}.csv").open("w", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    metadata["finished_utc"] = datetime.now(timezone.utc).isoformat()
    (args.output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"Saved {len(memory_rows)} memory / {len(timing_rows)} timing rows to {args.output}")


if __name__ == "__main__":
    main()
