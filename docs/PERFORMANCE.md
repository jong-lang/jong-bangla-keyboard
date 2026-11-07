# Performance

Use the retained measurements as historical observations, not current release
guarantees. These are recorded observations, not results for the current
revision. No clean-revision JSON baseline or agreed regression thresholds exist yet.

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

## Baseline plan

Planned in [#28](https://github.com/shaadahmmed/jong-bangla-keyboard/issues/28):
commit baseline JSON with revision, date, machine, environment, commands,
workloads, and latency/memory metrics. Compare full local runs on the reference
machine, establish repeatability, then agree regression thresholds. CI gets a
smoke benchmark without timing gates. Use synthetic text and keep measured
numbers here rather than copying them into other guides.
