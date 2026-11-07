#!/usr/bin/env python3
"""Collect synthetic local baselines or run a bounded CI smoke (MIT)."""

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import platform
import re
import shutil
import statistics
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent
WORDS = ["ami", "bangla", "krrishTi", "shadhInota", "okkhor123", "k`a", "কি🙂"]
SPEC = importlib.util.spec_from_file_location("adapter", ROOT / "tools/measure-adapter.py")
ADAPTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ADAPTER)


def now():
    return datetime.now(timezone.utc).isoformat()


def read_optional(path):
    path = Path(path)
    return path.read_text().strip() if path.exists() else None


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_identity():
    status = ADAPTER.command(["git", "status", "--porcelain=v1", "--untracked-files=all"], ROOT)
    return {
        "commit": ADAPTER.command(["git", "rev-parse", "HEAD"], ROOT),
        "status": status, "dirty": bool(status),
    }


def timing_rows(content, expected):
    lines = [line for line in content.splitlines() if not line.startswith("#")]
    rows = list(csv.DictReader(lines))
    actual = [(row["workload"], int(row["raw_scalars"]),
               int(row["actions_per_iteration"])) for row in rows]
    if actual != expected:
        raise ValueError(f"unexpected workloads: {actual!r}")
    for row in rows:
        for key in ("raw_scalars", "actions_per_iteration", "iterations"):
            row[key] = int(row[key])
            if row[key] <= 0:
                raise ValueError(f"invalid {key}")
        for key in ("min_ns", "median_ns", "p95_ns"):
            row[key] = float(row[key])
            if not math.isfinite(row[key]):
                raise ValueError(f"nonfinite {key}")
        if not 0 < row["min_ns"] <= row["median_ns"] <= row["p95_ns"]:
            raise ValueError("invalid timing percentiles")
    return rows


def core_workloads(smoke):
    return [item for word in WORDS for item in
            [(f"convert:{word}", len(word), 1),
             (f"type_commit:{word}", len(word), len(word) + 1)]] + [
        item for length in ((32, 128) if smoke else (32, 128, 1024, 8192))
        for item in [("convert_mixed", length, 1), ("insert_backspace_pair", length, 2)]]


def allocation_calls(report):
    matches = re.findall(r"^calls to allocation functions: (\d+) \(", report, re.M)
    if len(matches) != 1 or int(matches[0]) <= 0:
        raise ValueError("missing/invalid heaptrack allocation count")
    return int(matches[0])


class Runner:
    def __init__(self, output):
        self.output = output
        self.commands = []

    def run(self, argv, timeout=300):
        argv = list(map(str, argv))
        print("Running: " + " ".join(argv), file=sys.stderr, flush=True)
        result = subprocess.run(argv, cwd=ROOT, text=True, capture_output=True,
                                timeout=timeout, check=False)
        index = len(self.commands)
        log = self.output / f"command-{index:02d}.log"
        log.write_text(result.stdout + "\n--- stderr ---\n" + result.stderr)
        self.commands.append({"argv": argv, "cwd": str(ROOT), "exit_code": result.returncode,
                              "log": log.name, "log_sha256": sha256(log)})
        if result.returncode:
            raise RuntimeError(f"command failed ({result.returncode}); see {log}")
        return result.stdout


def environment(runner):
    return {
        "product": read_optional("/sys/class/dmi/id/product_name"),
        "os_release": read_optional("/etc/os-release"),
        "platform": platform.platform(), "libc": platform.libc_ver(),
        "cpu_model": next(line.split(":", 1)[1].strip() for line in
                          Path("/proc/cpuinfo").read_text().splitlines()
                          if line.startswith("model name")),
        "logical_cpus": os.cpu_count(), "affinity": sorted(os.sched_getaffinity(0)),
        "governor": read_optional("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"),
        "boost": read_optional("/sys/devices/system/cpu/cpufreq/boost"),
        "ac_online": {p.parent.name: read_optional(p)
                      for p in Path("/sys/class/power_supply").glob("*/online")},
        "desktop": {key: os.environ.get(key) for key in
                    ("XDG_CURRENT_DESKTOP", "XDG_SESSION_TYPE", "KDE_SESSION_VERSION")},
        "tool_paths": {tool: shutil.which(tool) for tool in
                       ("rustc", "cargo", "c++", "cmake", "ninja", "heaptrack", "heaptrack_print")},
        "loadavg_start": os.getloadavg(),
        "python": sys.version,
        "rustc": runner.run(["rustc", "-vV"]),
        "cargo": runner.run(["cargo", "--version"]),
        "cxx": runner.run(["c++", "--version"]),
        "fcitx5": runner.run(["pkg-config", "--modversion", "Fcitx5Core"]).strip(),
        "cmake": runner.run(["cmake", "--version"]),
        "ninja": runner.run(["ninja", "--version"]).strip(),
        # Record only known measurement settings. Tool-prefix matches also
        # include credentials and arbitrary application-defined variables.
        "build_environment": {key: os.environ[key] for key in (
            "CC", "CXX", "RUSTC", "RUSTC_WRAPPER", "RUSTC_WORKSPACE_WRAPPER",
            "RUSTUP_TOOLCHAIN", "RUSTC_BOOTSTRAP", "CARGO_INCREMENTAL",
            "CARGO_BUILD_JOBS", "CARGO_BUILD_TARGET", "CARGO_BUILD_INCREMENTAL",
            "CARGO_BUILD_RUSTC", "CARGO_BUILD_RUSTC_WRAPPER", "CARGO_BUILD_RUSTC_WORKSPACE_WRAPPER",
            "LD_LIBRARY_PATH", "GLIBC_TUNABLES",
            "MALLOC_ARENA_MAX", "MALLOC_ARENA_TEST", "MALLOC_CHECK_",
            "MALLOC_MMAP_MAX_", "MALLOC_MMAP_THRESHOLD_", "MALLOC_PERTURB_",
            "MALLOC_TOP_PAD_", "MALLOC_TRIM_THRESHOLD_") if key in os.environ},
    }


def collect(args):
    smoke = args.mode == "smoke"
    identity = source_identity()
    if not smoke and identity["status"]:
        raise ValueError("full baselines require a clean tracked and untracked working tree")
    # Prevent inherited instrumentation/optimization overrides from creating a
    # misleading baseline. Record other build and allocator settings explicitly.
    forbidden = ("LD_PRELOAD", "LD_AUDIT", "RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS",
                 "CXXFLAGS", "CFLAGS", "LDFLAGS", "CARGO_BUILD_RUSTFLAGS")
    if any(os.environ.get(key) for key in forbidden) or any(
            key.startswith(("CARGO_PROFILE_", "CARGO_TARGET_")) for key in os.environ):
        raise ValueError("unset compiler/linker/profile/preload overrides before measurement")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    runner = Runner(output)
    data = {"schema_version": 1, "profile": args.mode, "started_utc": now(),
            "source": identity, "environment": environment(runner),
            "repetitions": 1 if smoke else args.runs,
            "method": {
                "timing": "31 sorted batch means, adaptive >=5ms calibration capped at 2^20 iterations; "
                          "nearest-rank p95 (index 29); allocations and output destruction included; "
                          "fresh process per run/mode; warm calibration; no CPU pinning",
                "smoke": "3 samples with one iteration; only 32/128 scalar editing; no memory/profiler; no timing gates",
                "units": {"latency": "ns/action, except context_lifecycle: ns/cycle",
                          "process_memory": "KiB", "allocator_memory": "bytes",
                          "allocations": "calls to allocation functions per complete profiled process"},
                "workloads": {
                    "core_short": WORDS,
                    "core_long": "kShmri12`a🙂 cycled to 32/128/1024/8192 Unicode scalars",
                    "adapter_short": "ami, bangla, shadhInota, kShmri12`aকি🙂",
                    "adapter_long": "kShmri12`aকি🙂 cycled to 32/128/1024/8192 Unicode scalars",
                    "typing": "insert each scalar then commit; actions = scalars + 1; core constructs a composition per iteration",
                    "editing": "insert i/backspace pair at a prefilled active buffer end; setup untimed; divide by 2",
                    "conversion": "whole raw string conversion and output destruction; one action",
                    "context_lifecycle": "create/focus context, type 13 scalars, Ctrl+Backspace, type again, destroy pending; one cycle",
                    "memory": "fresh paired baseline/Jong processes; idle, short pending/cleared, 8192 pending/cleared, "
                              "1000/2000 reused+fresh context sessions, context destroyed; see measure-adapter.py",
                    "core_allocations": "1000 convert + new composition/type 13 scalars/backspace/insert i/commit/destroy cycles",
                    "adapter_allocations": "1000 context_lifecycle cycles; paired baseline/Jong; event vector setup once",
                },
                "limits": ["Batch means are not individual key or key-to-screen tail latency.",
                           "No frontend, event loop, retained application document, or desktop acceptance.",
                           "RSS/PSS and heap snapshots include framework and allocator caching; paired differences estimate incremental cost.",
                           "Retained capacity and heaptrack exit-retention labels do not prove leaks or leak freedom.",
                           "Allocation profiles include process/framework startup and teardown; never use profiler timings/RSS as latency or footprint.",
                           "Uncontrolled scheduling, thermal state and background activity; no agreed thresholds."],
            }, "core_timing": [], "allocation_profiles": []}
    build = output / "build"
    core_target = output / "core"
    runner.run(["cargo", "build", "--offline", "--locked", "--release", "--example", "measure",
                "--target-dir", core_target])
    runner.run(["cmake", "-S", "adapters/fcitx5", "-B", build, "-G", "Ninja",
                "-DCMAKE_BUILD_TYPE=Release", "-DCMAKE_INSTALL_PREFIX=/usr",
                "-DFCITX_INSTALL_USE_FCITX_SYS_PATHS=ON", "-DJONG_BUILD_RESOURCE_PROBE=ON",
                "-DJONG_ENABLE_SANITIZERS=OFF"])
    runner.run(["cmake", "--build", build])
    core = core_target / "release/examples/measure"
    native = build / "jong-fcitx5-resources"
    data["artifact_sha256"] = {name: sha256(path) for name, path in {
        "core": core, "adapter_probe": native, "addon": build / "libjong-bangla.so",
        "cmake_cache": build / "CMakeCache.txt"}.items()}
    sources = ADAPTER.command(["git", "ls-files", "src", "examples", "adapters", "tools",
                               "Cargo.toml", "Cargo.lock"], ROOT).splitlines()
    data["source_sha256"] = {name: sha256(ROOT / name) for name in sources}
    for run in range(1, data["repetitions"] + 1):
        rows = timing_rows(runner.run([core] + (["--smoke"] if smoke else [])), core_workloads(smoke))
        data["core_timing"].extend(dict(row, run=run, mode="core") for row in rows)
    if smoke:
        data["adapter_timing"] = []
        expected = [item for item in ADAPTER.WORKLOADS if item[1] <= 128]
        for mode in ("baseline", "jong"):
            rows = timing_rows(runner.run([native, mode, "timing", "--smoke"]), expected)
            data["adapter_timing"].extend(dict(row, run=1, mode=mode) for row in rows)
    else:
        adapter_output = output / "adapter"
        runner.run(["python3", "tools/measure-adapter.py", build, "--output", adapter_output,
                    "--runs", str(args.runs)], timeout=900)
        data["adapter_metadata"] = json.loads((adapter_output / "metadata.json").read_text())
        if (data["adapter_metadata"]["git_head"] != identity["commit"] or
                data["adapter_metadata"]["git_status"] != identity["status"]):
            raise ValueError("adapter source identity differs from collection")
        content = (adapter_output / "timing.csv").read_text()
        rows = list(csv.DictReader(io.StringIO(content)))
        data["adapter_timing"] = []
        for run in range(1, args.runs + 1):
            for mode in ("baseline", "jong"):
                selected = [row for row in rows if int(row["run"]) == run and row["mode"] == mode]
                stream = io.StringIO()
                writer = csv.DictWriter(stream, fieldnames=ADAPTER.TIMING_FIELDS)
                writer.writeheader()
                writer.writerows(selected)
                validated = timing_rows(stream.getvalue(), ADAPTER.WORKLOADS)
                data["adapter_timing"].extend(dict(row, run=run, mode=mode) for row in validated)
        with (adapter_output / "memory.csv").open() as stream:
            data["adapter_memory"] = [dict(row, **{key: int(value) for key, value in row.items()
                                                   if key not in ("mode", "phase")})
                                      for row in csv.DictReader(stream)]
        data["environment"]["heaptrack"] = runner.run(["heaptrack", "--version"]).strip()
        data["environment"]["heaptrack_print"] = runner.run(["heaptrack_print", "--version"]).strip()
        for run in range(1, args.runs + 1):
            modes = ("core", "baseline", "jong") if run % 2 else ("jong", "baseline", "core")
            for mode in modes:
                prefix = output / f"allocations-{run}-{mode}"
                argv = [core, "--allocations"] if mode == "core" else [native, mode, "allocations"]
                runner.run(["heaptrack", "--record-only", "-o", prefix, *argv])
                traces = list(output.glob(prefix.name + ".*"))
                if len(traces) != 1:
                    raise ValueError("expected exactly one heaptrack trace")
                report = runner.run(["heaptrack_print", "-f", traces[0], "-p", "0", "-a", "0", "-T", "0",
                                     "--disable-builtin-suppressions", "--disable-embedded-suppressions"])
                data["allocation_profiles"].append({"run": run, "mode": mode,
                    "allocation_calls": allocation_calls(report), "report": report,
                    "trace": traces[0].name, "trace_sha256": sha256(traces[0])})
    if source_identity() != identity:
        raise ValueError("source identity changed during collection; results are not a baseline")
    data["finished_utc"] = now()
    data["environment"]["loadavg_finish"] = os.getloadavg()
    data["commands"] = runner.commands
    if not smoke:
        validate_full(data)
    (output / "baseline.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(output / "baseline.json")


def distribution(values):
    return {"min": min(values), "median": statistics.median(values), "max": max(values)}


def timing_summary(data):
    grouped = {}
    for row in data["core_timing"] + data["adapter_timing"]:
        key = f'{row["mode"]}/{row["workload"]}/{row["raw_scalars"]}'
        grouped.setdefault(key, []).append(row["median_ns"])
    return {key: distribution(values) for key, values in grouped.items()}


def validate_full(data):
    if data["schema_version"] != 1 or data["profile"] != "collect" or data["source"]["status"]:
        raise ValueError("compare requires clean full baselines of schema version 1")
    runs = data["repetitions"]
    if not isinstance(runs, int) or not 3 <= runs <= 10:
        raise ValueError("full baselines require 3 to 10 repetitions")
    for field, modes, expected in (("core_timing", ("core",), core_workloads(False)),
                                   ("adapter_timing", ("baseline", "jong"), ADAPTER.WORKLOADS)):
        rows = data[field]
        if len(rows) != runs * len(modes) * len(expected):
            raise ValueError("incomplete timing repetitions")
        for run in range(1, runs + 1):
            for mode in modes:
                selected = [row for row in rows if row["run"] == run and row["mode"] == mode]
                stream = io.StringIO()
                writer = csv.DictWriter(stream, fieldnames=ADAPTER.TIMING_FIELDS)
                writer.writeheader()
                writer.writerows(selected)
                timing_rows(stream.getvalue(), expected)
    expected_memory = {(run, mode, phase) for run in range(1, runs + 1)
                       for mode in ("baseline", "jong") for phase in ADAPTER.PHASES}
    rows = data["adapter_memory"]
    if len(rows) != len(expected_memory) or {
            (row["run"], row["mode"], row["phase"]) for row in rows} != expected_memory:
        raise ValueError("incomplete memory repetitions")
    for row in rows:
        if any(not isinstance(row[key], int) or row[key] < 0 for key in ADAPTER.MEMORY_FIELDS[3:]):
            raise ValueError("invalid memory metrics")
    profiles = data["allocation_profiles"]
    if len(profiles) != runs * 3 or {(row["run"], row["mode"]) for row in profiles} != {
            (run, mode) for run in range(1, runs + 1) for mode in ("core", "baseline", "jong")}:
        raise ValueError("incomplete allocation repetitions")
    if any(row["allocation_calls"] != allocation_calls(row["report"]) for row in profiles):
        raise ValueError("allocation count does not match report")


def memory_summary(data):
    result = {}
    rows = {(row["run"], row["mode"], row["phase"]): row for row in data["adapter_memory"]}
    for phase in ADAPTER.PHASES:
        result[phase] = {key: distribution([
            rows[run, "jong", phase][key] - rows[run, "baseline", phase][key]
            for run in range(1, data["repetitions"] + 1)]) for key in ADAPTER.MEMORY_FIELDS[3:]}
    return result


def compare(before, after):
    for data in (before, after):
        validate_full(data)
    left, right = timing_summary(before), timing_summary(after)
    if left.keys() != right.keys() or before["method"] != after["method"]:
        raise ValueError("workload/method mismatch")
    context = ("product", "os_release", "platform", "cpu_model", "libc", "rustc", "cargo", "cxx",
               "fcitx5", "cmake", "ninja", "governor", "boost", "affinity", "ac_online", "build_environment")
    return {
        "before_commit": before["source"]["commit"], "after_commit": after["source"]["commit"],
        "environment_differences": [key for key in context if before["environment"][key] != after["environment"][key]],
        "latency": {key: {"before_ns": left[key], "after_ns": right[key],
                          "median_change_percent": (right[key]["median"] / left[key]["median"] - 1) * 100,
                          "nonoverlapping_run_ranges": right[key]["min"] > left[key]["max"] or
                                                       right[key]["max"] < left[key]["min"]}
                    for key in left},
        "paired_memory_before": memory_summary(before), "paired_memory_after": memory_summary(after),
        "allocation_calls": {label: {mode: distribution([row["allocation_calls"] for row in
                             data["allocation_profiles"] if row["mode"] == mode])
                             for mode in ("core", "baseline", "jong")}
                             for label, data in (("before", before), ("after", after))},
        "interpretation": "Per-run median ranges describe repeatability, not confidence intervals. "
                          "Nonoverlap is descriptive, not a regression gate. Investigate environment changes and "
                          "repeat full local collections before claiming a reproducible regression; no thresholds agreed.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="mode", required=True)
    for mode in ("collect", "smoke"):
        command = commands.add_parser(mode)
        command.add_argument("--output", required=True, type=Path, help="new output directory")
        command.add_argument("--runs", type=int, choices=range(3, 11), default=3)
    command = commands.add_parser("compare")
    command.add_argument("before", type=Path)
    command.add_argument("after", type=Path)
    args = parser.parse_args()
    try:
        if args.mode == "compare":
            print(json.dumps(compare(json.loads(args.before.read_text()), json.loads(args.after.read_text())), indent=2))
        else:
            collect(args)
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError) as error:
        sys.exit(f"FAIL: {error}")


if __name__ == "__main__":
    main()
