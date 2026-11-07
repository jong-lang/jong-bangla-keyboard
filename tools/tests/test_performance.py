"""Synthetic protocol, provenance and comparison regressions; no timing assertions."""

import argparse
import copy
import csv
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch


PATH = Path(__file__).resolve().parents[1] / "measure-baseline.py"
SPEC = importlib.util.spec_from_file_location("performance", PATH)
PERF = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PERF)


def timings(expected, median=10):
    return [dict(workload=name, raw_scalars=scalars, actions_per_iteration=actions,
                 iterations=8, min_ns=1, median_ns=median, p95_ns=30)
            for name, scalars, actions in expected]


def baseline():
    data = {"schema_version": 1, "profile": "collect", "repetitions": 3,
            "source": {"commit": "synthetic", "status": ""}, "method": {"synthetic": True},
            "environment": dict.fromkeys(("product", "os_release", "platform", "cpu_model", "libc",
                                          "rustc", "cargo", "cxx", "fcitx5", "cmake", "ninja",
                                          "governor", "boost", "affinity", "ac_online", "build_environment"), "synthetic"),
            "core_timing": [], "adapter_timing": [], "adapter_memory": [], "allocation_profiles": []}
    for run in range(1, 4):
        data["core_timing"].extend(dict(row, run=run, mode="core")
                                   for row in timings(PERF.core_workloads(False), 8 + run))
        for mode in ("baseline", "jong"):
            data["adapter_timing"].extend(dict(row, run=run, mode=mode)
                                          for row in timings(PERF.ADAPTER.WORKLOADS))
            for phase in PERF.ADAPTER.PHASES:
                data["adapter_memory"].append(dict(run=run, mode=mode, phase=phase,
                    **dict.fromkeys(PERF.ADAPTER.MEMORY_FIELDS[3:], 100 + (5 if mode == "jong" else 0))))
        for mode in ("core", "baseline", "jong"):
            data["allocation_profiles"].append(dict(run=run, mode=mode, allocation_calls=100,
                                                    report="calls to allocation functions: 100 (10/s)\n"))
    return data


class PerformanceTests(unittest.TestCase):
    def test_environment_records_only_explicit_measurement_settings(self):
        settings = {"CC": "synthetic-cc", "CXX": "synthetic-cxx",
                    "RUSTUP_TOOLCHAIN": "synthetic-toolchain", "CARGO_BUILD_JOBS": "2",
                    "CARGO_INCREMENTAL": "0",
                    "MALLOC_ARENA_MAX": "2", "GLIBC_TUNABLES": "glibc.malloc.trim_threshold=1024"}
        excluded = {key: "synthetic-private-value" for key in (
            "CARGO_REGISTRY_TOKEN", "CARGO_REGISTRIES_SYNTHETIC_TOKEN",
            "CARGO_REGISTRY_CREDENTIAL_PROVIDER", "CARGO_FUTURE_SETTING",
            "RUST_PRIVATE_SETTING", "CXX_PRIVATE_SETTING", "CC_PRIVATE_SETTING",
            "MALLOC_PRIVATE_SETTING", "UNRELATED_PRIVATE_SETTING")}
        with patch.dict(os.environ, settings | excluded, clear=True):
            metadata = PERF.environment(Mock(run=Mock(return_value="synthetic-tool")))
        self.assertEqual(metadata["build_environment"], settings)
        serialized = json.dumps(metadata)
        self.assertNotIn("synthetic-private-value", serialized)
        for key in excluded:
            self.assertNotIn(key, serialized)

    def test_adapter_metadata_omits_unknown_allocator_variables(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "CMakeCache.txt").write_text("CMAKE_BUILD_TYPE:STRING=Release\n")
            for name in ("jong-fcitx5-resources", "libjong-bangla.so"):
                (root / name).write_text("synthetic")
            output = root / "output"
            with patch.dict(os.environ, {"MALLOC_ARENA_MAX": "2",
                                         "MALLOC_PRIVATE_SETTING": "synthetic-private-value"}, clear=True), \
                    patch.object(sys, "argv", ["measure-adapter.py", str(root), "--output", str(output)]), \
                    patch.object(PERF.ADAPTER, "command", return_value="synthetic"), \
                    patch.object(PERF.ADAPTER, "memory_probe", return_value=[]), \
                    patch.object(PERF.ADAPTER, "timing_probe", return_value=[]):
                PERF.ADAPTER.main()
            serialized = (output / "metadata.json").read_text()
            self.assertEqual(json.loads(serialized)["allocator_environment"], {"MALLOC_ARENA_MAX": "2"})
            self.assertNotIn("MALLOC_PRIVATE_SETTING", serialized)
            self.assertNotIn("synthetic-private-value", serialized)

    def test_protocol_rejects_missing_reordered_duplicate_or_extra_workloads(self):
        expected = PERF.core_workloads(False)
        rows = timings(expected)
        for changed in (rows[:-1], list(reversed(rows)), rows + [rows[0]]):
            with self.subTest(length=len(changed)), self.assertRaises(ValueError):
                self.parse(changed, expected)
        self.assertEqual(self.parse(rows, expected), rows)

    def parse(self, rows, expected):
        stream = io.StringIO()
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
        return PERF.timing_rows("# synthetic\n" + stream.getvalue(), expected)

    def test_protocol_rejects_invalid_metrics(self):
        for key, value in (("min_ns", 0), ("median_ns", float("nan")),
                           ("p95_ns", float("inf")), ("p95_ns", 2), ("iterations", 0)):
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                rows = timings(PERF.core_workloads(False))
                rows[0][key] = value
                self.parse(rows, PERF.core_workloads(False))

    def test_comparison_uses_replicate_ranges_and_paired_memory(self):
        before = baseline()
        after = copy.deepcopy(before)
        after["environment"]["rustc"] = "changed"
        for row in after["core_timing"]:
            row["median_ns"] *= 2
        result = PERF.compare(before, after)
        item = result["latency"]["core/convert:bangla/6"]
        self.assertEqual(item["before_ns"], {"min": 9, "median": 10, "max": 11})
        self.assertEqual(item["median_change_percent"], 100)
        self.assertTrue(item["nonoverlapping_run_ranges"])
        self.assertEqual(result["environment_differences"], ["rustc"])
        self.assertEqual(result["paired_memory_before"]["idle"]["pss_kib"]["median"], 5)

    def test_comparison_rejects_smoke_dirty_incomplete_and_changed_methods(self):
        for mutation in (lambda data: data.update(profile="smoke"),
                         lambda data: data["source"].update(status=" M synthetic"),
                         lambda data: data["core_timing"].pop(),
                         lambda data: data["adapter_memory"].pop(),
                         lambda data: data["allocation_profiles"].pop(),
                         lambda data: data["method"].update(synthetic=False),
                         lambda data: data.update(repetitions=1)):
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                after = baseline()
                mutation(after)
                PERF.compare(baseline(), after)

    def test_full_collection_refuses_dirty_source_before_building(self):
        with patch.object(PERF, "source_identity", return_value={"commit": "synthetic", "status": "?? synthetic"}), \
                patch.object(PERF, "Runner") as runner, self.assertRaisesRegex(ValueError, "clean"):
            PERF.collect(argparse.Namespace(mode="collect"))
        runner.assert_not_called()

    def test_failed_command_retains_log_and_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            runner = PERF.Runner(Path(temporary))
            with self.assertRaisesRegex(RuntimeError, "command failed"):
                runner.run([sys.executable, "-c", "print('synthetic'); raise SystemExit(7)"])
            self.assertEqual(runner.commands[0]["exit_code"], 7)
            self.assertIn("synthetic", (Path(temporary) / "command-00.log").read_text())

    def test_allocation_reports_require_exactly_one_valid_count(self):
        for text in ("", "calls to allocation functions: 0 (0/s)",
                     "calls to allocation functions: 5 (1/s)\ncalls to allocation functions: 6 (1/s)"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                PERF.allocation_calls(text)
        self.assertEqual(PERF.allocation_calls("calls to allocation functions: 53 (10/s)\n"), 53)

    def test_cli_failure_is_nonzero_without_creating_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "invalid.json"
            source.write_text(json.dumps({"schema_version": 1, "profile": "smoke"}))
            result = subprocess.run([sys.executable, str(PATH), "compare", str(source), str(source)],
                                    text=True, capture_output=True, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("FAIL:", result.stderr)
            self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
