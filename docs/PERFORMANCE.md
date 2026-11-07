# Performance

Use full local collections to compare revisions on the Modern 15 A5M running
CachyOS KDE. The collector records clean source identity, environment, commands,
workload definitions, raw metrics, units and repetitions in `baseline.json`.
There are no agreed regression thresholds. CI only checks a bounded smoke run.

## Collect and compare

Run from a clean checkout on the reference machine with Rust, Fcitx5 development
files, GCC, CMake, Ninja, Python, binutils, heaptrack and heaptrack_print available.
Use a new output directory for each collection. Build products and logs stay
there, outside tracked source. Keep the same power source/profile, minimize other
activity, and record any known environmental changes when interpreting results.
Do not change desktop input settings. The probes isolate their Fcitx environment.

```sh
python3 tools/measure-baseline.py collect --output /tmp/jong-baseline-a --runs 3
python3 tools/measure-baseline.py collect --output /tmp/jong-baseline-b --runs 3
python3 tools/measure-baseline.py compare \
  /tmp/jong-baseline-a/baseline.json /tmp/jong-baseline-b/baseline.json \
  > /tmp/jong-baseline-comparison.json
```

Full collections refuse dirty source, reused output directories, inherited
instrumentation/profile overrides, and source identity changes during a run.
Each builds fresh unsanitized Release binaries. Core timing uses three fresh
processes; the adapter alternates baseline/Jong order across three paired runs,
with memory before timing. Each full timing workload calibrates to at least
5 ms (capped at 2^20 iterations), then collects 31 batch means. The minimum,
median and nearest-rank p95 are recorded in ns/action. One lifecycle action is
an entire create/type/clear/type/destroy cycle, reported as ns/cycle.

Short words, whole-string conversion, and editing prefilled 32/128/1024/8192
scalar buffers remain separate. Editing setup is untimed and each pair is
divided by two actions. Core and adapter mixed strings differ as recorded in
the JSON. These are synthetic batch costs, not individual-key or key-to-screen
tail latency. There is no frontend, event loop, or retained application document.

Process memory records total RSS, PSS, private resident memory and high-water
RSS in KiB, plus glibc heap used/reserved bytes. Compare matched Jong-minus-null
snapshots for incremental cost; do not call that difference the total process
footprint. Cleared buffers and repeated/destroyed contexts expose retention,
but neither snapshot growth nor retained capacity alone proves a leak.

Allocation profiling is separate from timing. Heaptrack observes three fresh
processes per mode, counting calls for 1000 fixed synthetic cycles: core
conversion/type/edit/commit, or adapter context lifecycle with matched null
baseline. Reports include process startup/teardown; paired adapter count
differences estimate incremental allocations across the whole process, not a
per-key allocator contract. Raw traces and textual reports remain in the output
directory; counts, report text and trace hashes are embedded in JSON. Profiler
timings and RSS are not used as unsanitized latency/footprint evidence. Exit
retention labels do not replace the [memory checks](TESTING.md#memory-checks).

The comparison reports each workload's median and range of per-process medians,
median percentage changes, environment differences, paired memory deltas and
allocation counts. Ranges are descriptive, not confidence intervals. Investigate
nonoverlap by repeating both revisions under matching conditions before calling
it a reproducible regression. Agree thresholds only after repeatability is
established; the comparison never applies a timing gate.

## CI smoke

```sh
python3 tools/measure-baseline.py smoke --output target/perf-smoke
python3 -m unittest discover -s tools/tests -p test_performance.py -v
```

Smoke builds the same probes and validates conversion, short typing, 32/128
scalar editing and context lifecycle in both adapter modes. It uses three
single-iteration samples, skips memory/profiling, accepts a dirty checkout, and
marks its JSON `smoke`. Comparisons reject smoke data. PR CI retains this JSON
as an observation artifact and fails on build, protocol or workload errors,
never on elapsed time. Shared-runner observations cannot establish parity.

## Current reference evidence

Collection results will be recorded here after measuring the committed collector
on clean source. The retained observations below remain historical evidence.

## Recorded environment

Date: 2026-10-30. Reference machine identified by the maintainer: Modern 15 A5M,
CachyOS KDE. The adapter metadata records a Ryzen 5 5500U, x86-64 Linux
7.3.0-4-cachyos, glibc 2.44, Rust 1.99.1, GCC 16.2.1, Fcitx5 5.1.23,
and CMake 4.4.5. This was an unsanitized Release build.

The recorded HEAD was `8970a9c3bda2c60f78fdc3f5b81cc90ba07e7475`, with
modified and untracked measurement sources. Metadata preserves source and binary
hashes. Current FFI and CMake source hashes differ. The core CSV has no separate
machine, compiler, or revision metadata, so the adapter metadata cannot establish
those details independently for the core run.

## Historical timing

Core values below are the range of recorded medians across two runs. Adapter
values are the median of three per-run medians. All values are nanoseconds per
action, derived from batch means; they are not individual key-to-screen latency.
Typing workloads include insertion and commit. Editing pairs divide their
combined time by two actions, rather than reporting the whole pair's duration.

| Probe | Workload | Recorded median ns/action |
| --- | --- | ---: |
| Core | Convert `bangla` | 1,071.5 to 1,090.4 |
| Core | Type and commit `bangla` | 597.6 to 600.1 |
| Core | Insert/Backspace at 1,024 raw scalars | 148,267.9 to 148,860.9 |
| Core | Insert/Backspace at 8,192 raw scalars | 1,188,653.0 to 1,189,761.6 |
| Fcitx5 with Jong | Type and commit `bangla` | 1,885.9 |
| Fcitx5 without Jong | Matching synthetic `bangla` workload | 813.5 |
| Fcitx5 with Jong | Insert/Backspace at 1,024 raw scalars | 183,096.4 |
| Fcitx5 with Jong | Insert/Backspace at 8,192 raw scalars | 1,459,306.0 |

Full data: [core CSV](measurements/2026-10-30-core.csv) and
[adapter timing CSV](measurements/2026-10-30-adapter-timing.csv).

## Historical memory

These are paired Jong-minus-baseline differences across three fresh-process
runs, not the total desktop input-method footprint. PSS apportions shared
resident memory. Heap bytes come from the probe's allocator accounting.

| Phase | PSS difference, KiB | Heap-used difference, bytes |
| --- | ---: | ---: |
| Idle | 349 to 393 | 7,424 |
| Short input pending | 457 to 482 | 8,704 |
| Long input pending | 669 to 694 | 94,016 |
| Long input cleared | 669 to 694 | 66,896 |
| Context destroyed | 600 to 656 | 2,272 |

Clearing input can retain reusable capacity. These snapshots cannot prove leak
freedom. Full data: [memory CSV](measurements/2026-10-30-adapter-memory.csv) and
[metadata](measurements/2026-10-30-adapter-metadata.json).

## Measurement commands

The original shell transcript was not retained. The following commands use the
current probes to reproduce the method; they are not a transcript of the recorded run.
Run on the reference machine with build dependencies installed:

```sh
cargo run --offline --locked --release --example measure > /tmp/jong-core.csv
cmake -S adapters/fcitx5 -B target/perf-fcitx5 -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr \
  -DFCITX_INSTALL_USE_FCITX_SYS_PATHS=ON -DJONG_BUILD_RESOURCE_PROBE=ON
cmake --build target/perf-fcitx5
python3 tools/measure-adapter.py target/perf-fcitx5 --output /tmp/jong-adapter
```

The adapter probe alternates baseline and Jong in fresh processes, measuring
memory before timing. It has no frontend, event loop, CPU pinning, or retained
application document. Batch-mean percentiles do not describe individual-key
tail latency. Long-buffer results reflect recomputing the active word.
