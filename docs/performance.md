# Performance measurements

Run these commands from the repository root after the
[development checks](development.md) finish. Recorded results are observations
from specific environments, not release performance guarantees.

## Measure core latency

```sh
cargo run --offline --release --example measure > target/core-latency.csv
```

The dependency-free runner measures seven short inputs and mixed buffers of
32, 128, 1,024 and 8,192 Unicode scalars. It includes one-shot conversion,
short-word typing/commit and insert/Backspace pairs at long buffers' ends.
It prints nanoseconds per action: minimum, median and 95th percentile of 31
batch means after adaptive calibration. Those percentiles describe batches,
not individual keystroke tail latency. Allocations/output destruction are timed;
long-buffer setup is excluded. The runner rejects debug builds. Run it without
concurrent builds/tests and record hardware, toolchain and load conditions.
The [local measurements](#local-resource-measurement-and-leak-check)
record two core release runs. Separate
[adapter measurements](#synthetic-adapter-resource-measurements)
compare dispatch time and memory with an explicit Fcitx baseline.

## Measure synthetic adapter resources

Use Linux/glibc, Python 3, `nm` from binutils and a Git checkout. This runner
records `git_head` and `git_status` and cannot currently collect that provenance
from an extracted source archive:

```sh
cmake -S adapters/fcitx5 -B target/fcitx5-release -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DJONG_BUILD_RESOURCE_PROBE=ON
cmake --build target/fcitx5-release
ctest --test-dir target/fcitx5-release --output-on-failure
python3 tools/measure-adapter.py target/fcitx5-release --output target/adapter-resources
```

Run measurements after builds/checks finish. The optional probe uses the real
dispatcher and addon, isolated temporary XDG paths and no desktop frontend.
Three sequential rounds alternate baseline/Jong order. Each mode/workload class
starts in a fresh process. The baseline loads only a static passthrough engine;
Jong adds its shared addon and input-method entry. Both receive identical keys
through identical synthetic contexts, with no retained document or effect log.
The runner rejects non-Release and sanitizer-instrumented builds, and
`LD_PRELOAD`/`LD_AUDIT`; the probe is disabled in normal builds.

`timing.csv` records nanoseconds per key press for four typing/Space cycles and
insert/Backspace pairs at 32/128/1,024/8,192-scalar buffer ends. It uses 31 batch
means with adaptive >=5 ms calibration; setup is excluded. The Jong-minus-baseline
difference includes conversion, the C ABI, adapter and synchronous preedit work;
it does not isolate bridge cost or individual-event tail latency.

`memory.csv` records eight checkpoints: idle, short word, short cleared, long
word, long cleared, 1,000/2,000 repeated sessions and context destruction. The
parent reads `/proc/PID/smaps_rollup` while the probe waits, capturing RSS, PSS and
private pages. `os_hwm_kib` preserves the kernel's approximate `VmHWM` counter;
the maximum snapshot RSS is only an observed peak, not an exact transient peak.
glibc `mallinfo2` records allocator-accounted used/reserved bytes, including
allocator caches rather than exact Rust capacities. No allocator trimming is
forced. `metadata.json` records build/source hashes, versions and method.
These results measure an isolated dispatcher, not a running desktop daemon or
frontend. See the [recorded results and limits](#synthetic-adapter-resource-measurements).

## Compatibility and performance evidence

Before claiming Avro compatibility, validate against the pinned reference and
document expected behavior independently. Build a fixture set covering vowels,
context-dependent forms, consonants, conjuncts, case sensitivity, punctuation,
escapes, digits, and backspace sequences. Record the origin and license of any
imported fixtures or data; do not assume a public rule table is MIT licensed.

Measure conversion latency across realistic word lengths and long pasted/input
buffers. Measure adapter overhead and added memory separately from Fcitx5's own
baseline. Record hardware, build mode, workload, and measurement method before
setting release budgets. On 2026-10-30 the user also requested memory-leak checks.
The bounded core timings and synthetic heap-ownership checks below provide local
evidence. The subsequent [synthetic adapter measurements](#synthetic-adapter-resource-measurements)
add a dispatcher baseline; added desktop memory and release budgets remain open.

## Local resource measurement and leak check

**2026-10-30 — bounded measurement increment.** Added a dependency-free release
[measurement runner](../examples/measure.rs), a
[C-ABI lifecycle workload](../adapters/fcitx5/tests/memory.cpp), and a
[leak-check command](../tools/check-memory.py). No transliteration, composition,
adapter behavior, dependencies, installation or input-method settings changed.

**Environment:** CachyOS rolling, Linux 7.3.0-4-cachyos, x86_64, AMD Ryzen 5 5500U
(6 cores/12 logical CPUs, boost enabled). Rust/Cargo 1.99.1, LLVM 23.1.3;
default Cargo release profile, no custom RUSTFLAGS, CPU pinning or fixed CPU
frequency. Two sequential runs used the same release executable after checks
finished, with no concurrent project builds/tests. Background desktop load was
not controlled. C++ memory checks used GCC 16.2.1, CMake 4.4.5, Fcitx5 5.1.23;
Debug C++ with ASan/UBSan and the same release Rust archive used by the addon.

**Timing method:** `cargo build --offline --release --example measure`, then
`target/release/examples/measure` twice. `std::time::Instant` times 31 batches per
workload after doubling iterations until a calibration batch takes at least
5 ms (cap 1,048,576 iterations). Values are batch duration / iterations / actions.
The median and p95 describe batch means, not individual event latency. `black_box`
keeps results observable. Loop/assert/clock overhead is included without baseline
subtraction, along with allocation and output destruction. Input creation and
long composition setup are untimed. Short composition workloads include a fresh
session, every insertion and a commit; results divide by insertions plus commit.
Long editing repeats insertion of `i` followed by Backspace on an existing buffer
and divides each pair by two. This averages insertion/deletion; neither is timed
individually. Whole long-word typing, adapter/framework delivery and cold startup
are unmeasured. Lengths count Unicode scalars rather than bytes or graphemes.

The seven short inputs are `ami`, `bangla`, `krrishTi`, `shadhInota`, `okkhor123`,
`` k`a `` and `কি🙂`. Across both runs their conversion medians range from
0.594–2.032 microseconds; short typing/commit medians range from
0.305–0.932 microseconds per action (amortized over each word and its commit).
Long input repeats `` kShmri12`a🙂 `` to the stated scalar count:

| Raw scalars | Conversion median A / B (µs) | Insert/Backspace mean-action median A / B (µs) |
| --- | --- | --- |
| 32 | 4.575 / 4.544 | 4.727 / 4.698 |
| 128 | 18.593 / 18.475 | 18.393 / 18.300 |
| 1,024 | 148.105 / 147.989 | 148.268 / 148.861 |
| 8,192 | 1,186.406 / 1,180.069 | 1,188.653 / 1,189.762 |

[All 44 CSV rows](measurements/2026-10-30-core.csv) preserve batch counts, minima,
medians and p95 values in nanoseconds for runs A/B. An exploratory run concurrent
with build/check preparation is excluded. These are local observations, not
release budgets, desktop responsiveness guarantees or a general speed claim.
Composition currently recomputes the whole raw buffer on each edit; repeated
typing of a growing long buffer may cost much more than a single final conversion.

**Leak method and result:** configured/built the sanitized tree using the
[development commands](development.md#build-and-check-the-fcitx5-experiment), then ran
`python3 tools/check-memory.py target/fcitx5-sanitized` outside ptrace tracing.
The initial sandbox run failed with LeakSanitizer's explicit ptrace error; the
checker rejected it. The run outside tracing completed successfully. No
disabled-detector run is counted as leak evidence.
The command enables `detect_leaks=1`, stops on ASan/UBSan errors and sets LSan's
leak exit code to 23. It first requires both that exit code and an actual leak
report for a deliberately lost Rust-owned session. This control passed, proving
that the linked runtime sees allocations from the Rust system allocator.
See [LeakSanitizer's documented method](https://clang.llvm.org/docs/LeakSanitizer.html).

The normal C-ABI workload then passed with **20,000 lifecycle cycles and 10,001
freed sessions**, exercising reuse, fresh sessions, Unicode, Backspace, all seven
finish/discard actions, invalid arguments, pending text on destruction, a
1,024-scalar buffer and null destruction. The real-addon dispatcher also passed
all ten synthetic suites with leak detection enabled. Neither normal workload
reported ASan, UBSan or LSan errors; no suppressions were used. Normal CTest now
includes this lifecycle workload; an unsanitized pass alone is not leak evidence.

**Memory limits:** leak detection does not measure resident memory, peak live
allocations or Jong's incremental memory over Fcitx's baseline. Rust/system
libraries are not compiled with ASan/UBSan instrumentation; the leak control
establishes heap-allocation visibility, not Rust access instrumentation. No
long-running desktop/frontend process was tested. Cleared `String` buffers can
retain capacity until reuse/destruction; reachable retained allocations are not
reported as leaks. At the time of this measurement, C-ABI containment forgot all
caught panic payloads to prevent a payload destructor from unwinding across C.
That path can leak heap-owning payloads and is not induced by these workloads;
the result does not claim leak freedom on caught-panic paths. The separate
[failure-policy review](adapter-contract.md#c-abi-caught-panic-policy-review) subsequently
narrows that exception; it does not rerun this leak measurement.

**Other validation:** Rust format/Clippy/workspace tests and release builds passed
(20 composition, 352 conversion, three FFI tests, two doctests). All 522,933 pinned
reference fixtures passed with the three existing Unicode case differences
unchanged. C++ formatting, both normal CTest cases and the leak-enabled
ASan/UBSan workloads passed. No frontend routes or older generated audits were
rerun. At the end of that increment, the next resource step was the synthetic
adapter comparison below. These core/leak results remain separate prior evidence.

## Synthetic adapter resource measurements

**2026-10-30 — matched release dispatcher comparison.** Added the optional
Linux/glibc `jong-fcitx5-resources` probe and `tools/measure-adapter.py`. No engine,
adapter behavior, dependency, installation or input-method setting changed.
The probe is disabled in normal builds. Commands are in the
[performance guide](#measure-synthetic-adapter-resources).

**Baseline and environment:** the same executable constructs an isolated Fcitx
instance, a static passthrough engine and a synthetic context. Baseline mode never
loads Jong. Jong mode adds the shared addon and its input-method entry, with the
same context capabilities, keys, disabled hotkeys and fixed-size sink counters.
No desktop frontend, bus, display, event loop, document storage or per-event
effect log runs. Temporary XDG paths isolate configuration. The probe verifies
active input methods, consumed/unhandled events, pending/cleared preedit and the
loaded addon allowlist. Framework UI scheduling can coalesce without a running
event loop; actual frontend/UI delivery costs are outside this measurement.

Ryzen 5 5500U, x86_64, CachyOS kernel 7.3.0-4-cachyos, glibc 2.44, Fcitx5 5.1.23,
GCC 16.2.1, CMake 4.4.5, Rust 1.99.1 and Python 3.14.8. C++ Release uses `-O3
-DNDEBUG`; Rust uses the default release profile. No sanitizers, CPU pinning,
frequency control, allocator tuning or forced trimming. Background desktop load
was uncontrolled; no concurrent project builds/checks ran during collection.
Three sequential rounds alternate baseline/Jong order; each memory/timing mode
gets a fresh process. A one-round tooling trial is excluded from the results.

**Timing:** `python3 tools/measure-adapter.py target/fcitx5-release --output
target/adapter-resources-recorded --runs 3`. Each workload has 31 timed batch
means after adaptive >=5 ms calibration, with key storage and long-buffer setup
outside the timer. Short cycles type the word and press Space; long cycles insert
`i` and Backspace at the stated buffer's end. All are key presses, without release
events. The mixed raw sequence is `kShmri12` followed by a backtick, `a`, `কি`,
and `🙂` (13 scalars), repeated/truncated for long buffers. Both modes receive
identical sequences; calibrated batch iteration counts can differ.

| Workload | Baseline median µs/action | Jong median µs/action | Paired added median µs/action |
| --- | ---: | ---: | ---: |
| Type/Space `ami` | 0.785–0.817 | 1.651–1.678 | 0.834–0.886 |
| Type/Space `bangla` | 0.779–0.816 | 1.864–1.903 | 1.048–1.107 |
| Type/Space `shadhInota` | 0.781–0.814 | 2.221–2.255 | 1.408–1.474 |
| Type/Space mixed | 0.776–0.818 | 2.217–2.232 | 1.400–1.456 |
| Edit at 32 scalars | 0.768–0.819 | 6.572–6.603 | 5.753–5.815 |
| Edit at 128 scalars | 0.783–0.825 | 24.092–24.192 | 23.309–23.368 |
| Edit at 1,024 scalars | 0.765–0.823 | 182.927–183.133 | 182.162–182.316 |
| Edit at 8,192 scalars | 0.767–0.822 | 1,459.128–1,460.183 | 1,458.362–1,459.397 |

Ranges span the three runs, not confidence intervals. Added time is each run's
Jong median minus its baseline median, including conversion, C ABI, adapter,
Fcitx dispatch and synchronous preedit work. It does not isolate C++ bridge cost.
Batch percentiles are not individual-event tail percentiles. The different
workload/sink prevents subtracting earlier core timings to infer bridge overhead.

**Memory:** at eight checkpoints the child reports `mallinfo2` counters and waits
while its parent reads `/proc/PID/smaps_rollup` and `/proc/PID/status`. Event storage
for both short and long words exists before the idle sample in both modes.
Each repeated-session batch commits 1,000 short words in the reused context and
creates/types/clears/destroys 1,000 fresh contexts. The second batch reaches 2,000
of each, followed by destruction of the reused context; Fcitx and addons stay live.

| Checkpoint | Added RSS KiB, paired range | Added allocator-used bytes, all runs |
| --- | ---: | ---: |
| Idle active context | 276–364 | 7,424 |
| Short pending | 400–492 | 8,704 |
| Short cleared | 400–492 | 8,704 |
| 8,192-scalar pending | 612–704 | 94,016 |
| Long cleared | 612–704 | 66,896 |
| After 1,000 sessions | 608–764 | 20,512 |
| After 2,000 sessions | 608–764 | 20,512 |
| Reused context destroyed | 544–700 | 2,272 |

Maximum snapshot RSS was 7,784/7,812/7,756 KiB baseline versus
8,400/8,420/8,520 KiB Jong: paired additions 616/608/764 KiB. These are observed
peaks among checkpoints, lower bounds on transient peak RSS. The raw kernel
`VmHWM` maxima were 7,784/7,836/7,836 versus 8,400/8,420/8,520 KiB. Kernel RSS
accounting is approximate (the excluded trial even reported a decreasing HWM
after context destruction); do not interpret that counter as exact heap peak.
[Kernel proc documentation](https://www.kernel.org/doc/html/latest/filesystems/proc.html)
describes RSS accounting and the more precise smaps snapshots.

Allocator-used is `uordblks + hblkhd`; reserved is `arena + hblkhd`, per
[glibc's allocator statistics](https://sourceware.org/glibc/manual/latest/html_node/Statistics-of-Malloc.html).
These process-wide counters include allocator bookkeeping/caches, not exact
reachable Rust capacities or an object-level heap profiler. After clearing the
long word, Jong's used counter fell by 27,120 bytes but RSS/reserved stayed level.
After later short sessions it fell further, then by 20,016 bytes on context
destruction. Reserved memory remained 28,672 bytes above baseline after destruction;
loaded code and allocator-held pages also remain. Both modes' used/reserved and
RSS snapshots were unchanged between 1,000 and 2,000 sessions in all three runs.
This is bounded reuse evidence, not proof that every retained allocation is
reachable or that a long-running desktop process cannot grow.

All **48 memory rows**, including PSS/private pages and raw HWM, are in
[memory.csv](measurements/2026-10-30-adapter-memory.csv); all **48 timing rows**, including
batch counts/minimum/p95, are in [timing.csv](measurements/2026-10-30-adapter-timing.csv).
[Metadata](measurements/2026-10-30-adapter-metadata.json) preserves versions, build
flags and hashes from the measured, uncommitted increment based on `8970a9c`.
Exact transient heap peaks, daemon/frontend overhead, real desktop event latency,
multi-machine evidence and release budgets remain open. Prior leak results and
the caught-panic payload exception above are unchanged; no leak detector or
desktop smoke test was rerun in this increment.
