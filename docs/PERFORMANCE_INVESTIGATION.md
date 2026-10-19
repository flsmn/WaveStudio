# Performance findings and remaining work

Performance observations are specific to the recorded version, hardware, power state, layout and measurement loop. Current open work is MAC-02 in [ROADMAP.md](ROADMAP.md); preserved resource criteria are in [BALANCED_MAC_PLAN.md](../validation/plans/BALANCED_MAC_PLAN.md).

## Confirmed corrections

The rate meter excludes allocation/startup time, resets its interval on Resume, ignores duplicate-step snapshots and keeps paused rates at zero. It waits for a full advancing interval before reporting a rate. This fixes reporting, not the solver's numerical throughput.

On macOS, scoped NSProcessInfo activity and High worker service level apply only while work is requested and are released/restored on Pause, Reset, failure and shutdown. No global power setting is changed. `--without-run-activity` provides an A/B diagnostic; API activation alone does not prove a speedup.

## Selected observations

The dev8 matched package intervals used the same Balanced lens grid (3780 × 2268), MPS, two views, Performance mode, Qt accessibility, active application state and Low Power Mode on. See [baseline](../validation/results/performance/frozen-matched-off.json), [scoped activity](../validation/results/performance/frozen-matched-on.json) and [historical pump](../validation/results/performance/frozen-matched-pump.json).

| Historical dev8 interval | Received frames/s | Steps/s | Maximum production-poll gap |
| --- | ---: | ---: | ---: |
| Native loop, baseline | 15.45 | 15.52 | 160.80 ms |
| Native loop, scoped activity | 16.25 | 16.32 | 115.03 ms |
| Historical processEvents pump | 15.45 | 15.59 | 175.89 ms |

A single short A/B does not establish a general speedup. Worker steps were about 50–53 ms; transfer and ImageItem conversion each about 3–4 ms, potentially overlapping. The historical 5–8 FPS HUD observation and 18–20 FPS pump result did not use matched startup/state/measurement conditions, so their difference has no proven single cause.

The [source interval](../validation/results/performance/source-fixed-layout.json) includes an application-state transition and a 1024-ms poll interruption; it is not a matched source/package comparison. The [quiet dev11 package](../validation/results/performance/dev11-native-quiet/performance-results.json) ran around 25–26 frames/s with Low Power Mode off. It cannot establish an improvement over the dev8 power-saving runs.

## Unresolved resource failures

- [Dev8 resource run](../validation/results/performance/balanced-resource-dev8.json): a 500.86-ms one-view GUI interruption fails the frozen 250-ms criterion. Six Pause acknowledgements were 72.33–99.39 ms; Reset/release and shutdown checks passed. Peak RSS 949.8 MiB and MPS driver allocation 1117.1 MiB overlap on unified memory and must not be summed.
- [Quiet dev11 resource run](../validation/results/performance/dev11-resources-quiet/resource-results.json): a 252.316-ms GUI interruption still fails the same criterion. Thresholds were not relaxed. Event/GC instrumentation did not prove a single cause.

The full reports retain the original outcomes. No universal 20-FPS guarantee, final large-grid interaction acceptance or High Quality optical acceptance follows from them.

## Reproduction

Use the production-loop commands in [DEVELOPMENT.md](DEVELOPMENT.md) with no concurrent benchmarks/builds. Record warmup, application/accessibility state, Low Power Mode and thermal conditions. Distinguish solver steps, received frames and image conversions.

`python scripts/trace_gui_events.py --output local-results/trace` records opt-in dispatch/GC/sleep spans without extra polling timers. `--resource-check` traces the existing resource workflow. Instrumented runs diagnose context and do not replace an uninstrumented acceptance run. See the [validation index](../validation/README.md) for output policy and provenance. Superseded exploratory traces remain in Git history.
