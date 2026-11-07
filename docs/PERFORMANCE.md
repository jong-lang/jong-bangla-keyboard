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

Measured 2026-11-07, 16:27 to 16:31 Asia/Dhaka, on the Modern 15 A5M,
CachyOS KDE 6 Wayland, Ryzen 5 5500U, Linux 7.3.1-1-cachyos, glibc 2.44,
Rust 1.99.1, GCC 16.2.1, Fcitx5 5.1.23, CMake 4.4.5, Ninja 1.13.2,
Python 3.14.9 and heaptrack 1.5.0. Both collections tested clean commit
`b72917e3805325f1789bf91f4b8a4dc6fcb308c1`. Later evidence and CI integration
commits do not change the measured probes; the tested identity remains explicit.
The machine was on battery, governor `powersave`, boost enabled, with affinity
to all 12 logical CPUs. Scheduling, thermals and background activity were not
controlled. These observations are a reference for this recorded environment,
not a release guarantee or a tuned/pinned benchmark.

Full evidence: [collection A](measurements/2026-11-07-baseline-a.json),
[collection B](measurements/2026-11-07-baseline-b.json), and
[comparison](measurements/2026-11-07-comparison.json). Each collection contains
three core timing processes, three matched adapter memory/timing pairs, and
three allocation profiles per mode. Core and adapter CSV rows are embedded in
JSON, along with profile reports, source/binary hashes and exact command arrays.
Full build/profiler logs and compressed traces remain under the local output
directories; the committed JSON records their hashes, not the binary traces.

Exact collection commands used the already extracted profiling tools on `PATH`:

```sh
PATH=/tmp/jong-memory-tools/usr/bin:$PATH python3 tools/measure-baseline.py collect --output /tmp/jong-28-baseline-a --runs 3
PATH=/tmp/jong-memory-tools/usr/bin:$PATH python3 tools/measure-baseline.py collect --output /tmp/jong-28-baseline-b --runs 3
python3 tools/measure-baseline.py compare \
  /tmp/jong-28-baseline-a/baseline.json /tmp/jong-28-baseline-b/baseline.json \
  > /tmp/jong-28-comparison.json
```

The commands above require checking out the tested commit cleanly; collection
will otherwise record a different revision. To inspect the committed evidence:

```sh
python3 tools/measure-baseline.py compare \
  docs/measurements/2026-11-07-baseline-a.json \
  docs/measurements/2026-11-07-baseline-b.json > /tmp/jong-recorded-comparison.json
```

Values below are the median of three per-process medians in each collection,
in ns/action except the lifecycle row, which is ns/cycle. The full JSON retains
every per-process minimum, median and batch-mean p95.

| Probe/workload | Collection A | Collection B |
| --- | ---: | ---: |
| Core convert `bangla` | 1,201.6 | 1,193.8 |
| Core type/commit `bangla` | 632.3 | 640.1 |
| Core edit pair, 1,024 scalars | 172,599.8 | 174,961.8 |
| Core edit pair, 8,192 scalars | 1,350,463.0 | 1,387,719.2 |
| Jong type/commit `bangla` | 1,910.1 | 1,896.1 |
| Null dispatcher matching `bangla` | 800.4 | 800.1 |
| Jong edit pair, 1,024 scalars | 187,792.3 | 185,516.1 |
| Jong edit pair, 8,192 scalars | 1,476,566.5 | 1,476,208.2 |
| Jong context lifecycle | 70,171.1 | 69,881.3 |

Across all 40 mode/workload/size combinations, B-minus-A median changes range
from -2.99% to +6.38%; nine per-run median ranges do not overlap even though
both collections test identical source. Core convert `bangla` has a wider
individual-run median range of 1,144.5 to 1,921.0 ns across the six runs.
These observations show why neither range nonoverlap nor a small percentage
change alone establishes a source regression. No regression thresholds are
proposed. A changed revision still needs repeated, matched local comparisons.

Memory ranges span all six paired runs. Totals are the Jong probe process;
deltas are paired Jong-minus-null snapshots, not the complete desktop daemon.

| Phase | Total Jong RSS, KiB | Total Jong PSS, KiB | PSS delta, KiB | Heap-used delta, bytes |
| --- | ---: | ---: | ---: | ---: |
| Idle | 8,052 to 8,208 | 2,649 to 2,699 | 281 to 439 | 7,760 |
| Short pending | 8,176 to 8,332 | 2,773 to 2,823 | 405 to 563 | 8,544 |
| Long pending | 8,432 to 8,588 | 3,029 to 3,079 | 661 to 819 | 98,448 |
| Long cleared | 8,432 to 8,588 | 3,029 to 3,079 | 661 to 819 | 71,328 |
| After 1,000 session cycles | 8,448 to 8,540 | 2,981 to 3,031 | 609 to 735 | 24,800 |
| After 2,000 session cycles | 8,448 to 8,540 | 2,981 to 3,031 | 609 to 735 | 24,784 |
| Context destroyed | 8,392 to 8,484 | 2,925 to 2,975 | 553 to 679 | 6,720 |

The stable/decreasing heap snapshots over the sampled session batches are
bounded retention evidence, not proof of leak freedom. Memory snapshots cover
adapter processes; core-only live memory is not sampled separately.

Allocation calls were identical in all six profiles per mode: core 47,014,
null dispatcher 358,629, Jong dispatcher 663,689. Each matched adapter profile
therefore had 305,060 additional allocation calls over its full 1,000-cycle
process. Startup and teardown are included; the core profile has a different
workload and is not a subtraction baseline for the adapter. Heaptrack's reported
exit retention includes framework/runtime allocations and is not diagnosed as
a production leak. Use the independent memory recipes for such investigations.

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
