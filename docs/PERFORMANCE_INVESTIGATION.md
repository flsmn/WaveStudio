# Native-package performance investigation

Same biconvex-lens Balanced selector, MPS, 3780 × 2268, 768-MiB project buffer budget, one Torch CPU thread, 1320 × 860 Qt points / DPR 2. The app and engine remain independently versioned; the engine stays dev4 because the stencil and sampling are unchanged.

The original 18–20 result used a tight processEvents/sleep pump plus a 10-ms measurement timer, with a warmup before the interval. The original 5–8 result was a HUD observation during native startup/interaction, not a matched steady-state interval. The new `--check-performance OUTPUT` entry point runs the production 33-ms GUI poll in Qt exec, records advancing received frames separately from ImageItem conversions, and does not add fast Python timers. `--event-loop pump` explicitly reproduces the historical method. Reports include app/accessibility state, worker-step/display-transfer/render durations, startup latency, power/thermal state and raw native thread QoS.

## Confirmed rate-display correction

The old HUD starts its denominator when Run is clicked, before solver allocation/initial Metal work. Resume also reuses an interval that can include a long pause. It counts duplicate view snapshots as frames. The new meter waits for advancing initialized frames, restarts on Resume, ignores duplicate step snapshots, and displays “Measuring rate…” until a full interval exists. Paused rates remain zero. Core and Qt-slot regression tests cover delayed initialization, duplicate views, long pauses and late worker frames. This corrects reporting; it does not claim to accelerate the numerical stencil.

## Scheduling experiment

macOS scheduling hints are scoped to actual requested work, with automatic restoration at Pause, Reset, failure and shutdown. The NSProcessInfo activity permits idle system sleep and does not change global power settings. Qt worker service level is High while running and Auto while idle (when the API is available). An A/B diagnostic flag `--without-run-activity` disables both hints in the same binary. Source probes verify native token balancing and QoS class changes. The final package A/B comparison determines the performance effect; no gain is inferred from those API changes alone.

API references: [Apple user-initiated activity allowing idle sleep](https://developer.apple.com/documentation/foundation/processinfo/activityoptions/userinitiatedallowingidlesystemsleep?language=objc), [Qt thread service levels](https://doc.qt.io/qt-6/qthread.html#QualityOfService-enum).

## Retained exploratory probes

`docs/performance/` retains early active/hidden and accessibility probes. Early diagnostic versions added 10/50-ms timers; they are exploratory and not used as the final production-loop comparison. The two early source probes carrying a scalar worker_qos value recorded the API status rather than its output parameter; their notes explicitly exclude that field. Later structured status/class/relative-priority values use the SDK declaration. One “hidden-activity” probe remained foreground because CUA found an additional ready window; its note excludes it from background comparisons.

Final native comparisons and conclusions follow below. No Windows/Linux, High Quality optical or cross-machine performance claim is made.

The first multi-case package A/B was not a valid inactive comparison: enabling the second pane changed application state at different times. Its final before interval is inactive while the after interval is active. These raw reports remain as exploratory data and do not establish a scheduling gain. The isolated comparisons fix both views and Performance before Run. A requested hidden single-case probe completed before Hide could be sent; its report is correctly classified as foreground, not hidden.

## Final fixed-layout results

All rows use Studio dev8 / engine dev4, the same Balanced grid, MPS, two views and Performance. The three primary package comparisons explicitly activate Qt accessibility before Run and retain ApplicationActive throughout. No other builds or tests run during their intervals. Low Power Mode is **on** and thermal state **nominal**; global settings were not changed. Repeated runs show real variability, so a single short A/B is not a statistically established speedup.

| Report in `performance/` | Loop / scheduling | Received frames/s | Steps/s | Peak RSS MiB | Maximum production-poll gap ms |
| --- | --- | ---: | ---: | ---: | ---: |
| `frozen-matched-off.json` | native / baseline | 15.45 | 15.52 | 861.3 | 160.80 |
| `frozen-matched-on.json` | native / scoped hints | 16.25 | 16.32 | 752.2 | 115.03 |
| `frozen-matched-pump.json` | historical pump / scoped hints | 15.45 | 15.59 | 805.5 | 175.89 |
| `frozen-cua-observed.json` | native / scoped hints, live AX/screenshot observation on next-day resume | 15.70 | 15.70 | 807.9 | 129.09 |

The median worker step is 50–53 ms in these package intervals. Each display transfer and each ImageItem conversion takes about 3–4 ms; GUI bookkeeping takes below 1 ms. Their timings can overlap and must not simply be added. A reduction of image resolution or numerical quality was not introduced. The production Qt event loop itself does not impose a factor-of-two limit relative to the historical pump in these samples. The 15.45 → 16.25 A/B is about 5%; it does **not** establish that App Nap caused the original 5–8 result.

The same source diagnostic (`source-fixed-layout.json`) averages 12.68 frames/s / 13.07 steps/s, with a final one-second HUD of 6 frames/s and a 1024-ms poll interruption. It includes an application-state transition, so it is not a strictly matched foreground source/package pair. It does demonstrate that a low instantaneous HUD observation can coexist with a higher whole-interval average outside a frozen package as well. Earlier source production-poll intervals range around 12–16 frames/s. The package is not consistently slower than the sources in the collected data.

Manual CUA control of the ordinary packaged MainWindow (without the diagnostic subclass) confirms “Measuring rate…” at initialization and Resume, advancing Balanced steps, zero paused rates and exact Step 560 → 561. During that session the HUD varied around 10–12 frames/s; this is retained as a separate UI observation, not substituted for the fixed-interval result. On next-day resume, the observed diagnostic package shows 16–18 on the HUD and averages 15.70. Neither Qt accessibility alone nor CUA observation alone is proven to explain the old gap. The prior AX scene-list limitation remains open.

## Conclusion and limits

**Fixed:** a reproducible rate-display bug, plus measurement methods that previously compared startup/interaction snapshots with warmed whole-interval averages. The diagnostic now makes application state, warmup, loop, accessibility, power state and stage costs explicit. macOS work scheduling is explicitly scoped to requested computation, with balanced cleanup and portable fallback.

**Not established:** a single cause for the entire historical 5–8 versus 18–20 gap. The old native observation lacks a matched interval, power state and stage trace, so that original operating context cannot be reconstructed from it. A sustained 18–20 FPS in the normal package is not certified by this work. The new data do not justify a claim that packaging, App Nap or accessibility is the sole cause. Residual context-dependent interruptions remain a follow-up if the slowdown can be reproduced with the new trace.

66 core/Qt tests pass (16.24 s), including startup/duplicate/Resume rates, scoped token lifecycle, failure cleanup and worker QoS restoration. The dev8 frozen workflow passes from `/private/tmp`: actual bundled imports, finite-window measurements, references, Pause/Resume/Step, second view, persistence, PNG/CSV, Reset and themes. `native-results.json` and `build-results.json` identify the final package; dev4 reports are preserved separately. The numerical engine is unchanged, so no new optical certification is claimed.

## Resource/interaction follow-up — retained failure

The existing resource runner was repeated once on dev8 after tests and the frozen workflow had stopped. The raw report is `performance/balanced-resource-dev8.json`; its full-detail paused screenshot is retained beside it. The legacy pump/10-ms heartbeat is explicitly not used for the production-loop FPS comparison.

Peak RSS is **949.8 MiB**; MPS driver allocation separately **1117.1 MiB** (overlaps RSS on unified memory). All six Pause acknowledgements pass at **72.33–99.39 ms**. Exact Step, stable paused counts, same-run Resume, full paused resolution, Reset acknowledgement **21.52 ms**, zero live MPS tensors after Reset and active shutdown **129.41 ms** pass. The unchanged 250-ms GUI-gap criterion **fails**: the first one-view interval has a **500.86-ms** interruption; the two subsequent active intervals peak at 129.22/138.56 ms. No other build/test ran concurrently. The overall report remains `passed=false`; the threshold was not relaxed and no passing rerun was selected.

This transient gap and the source diagnostic's 1024-ms poll interruption leave a context-dependent GUI responsiveness issue open. The measured drawing/profile/transfer costs do not identify a matching in-app stall in these traces. A single definitive cause cannot be assigned from the existing stage summaries. Accordingly, this change fixes the confirmed rate bug and improves reproducibility/scheduling, but does not claim that every runtime interruption or the complete historical FPS gap has been resolved.


## MAC-02 follow-up — dev11, 18 October 2026

The opt-in `scripts/trace_gui_events.py` records Qt dispatches, Python GC spans and dispatcher sleep intervals without introducing extra polling timers. It is diagnostic instrumentation, not a replacement acceptance runner. Resource checks now accept `--output-dir` so each pass or failure retains its own report and artifacts. No timing threshold, rendering resolution, numerical grid or global GC policy changed.

The [dev10 exploratory trace](performance/dev10-exploratory-under-load/event-trace.json) overlapped reference runs, builds and tests, with the application inactive. Its 17.78 frames/s cannot be compared as a performance improvement. A generation-2 GC span of 92.3 ms overlaps a 101-ms paint dispatch; correlation alone does not explain the earlier 500-ms gap.

A separate **frozen dev11** production-loop run used 15-s warmup and 30-s intervals with no concurrent build, test or reference computation. Application active, accessibility active, Low Power Mode **off**, thermal state nominal: [native report](performance/dev11-native-quiet/performance-results.json). Received rates were 26.09 / 25.45 / 25.52 frames/s for one economical view, two economical views and two performance views. Maximum production-poll gaps were 36.81 / 76.39 / 33.80 ms. The earlier dev8 comparisons had Low Power Mode on; these samples do not establish a code-induced speedup or explain the complete historical FPS difference.

The subsequent uninstrumented legacy resource workflow still **failed** its unchanged GUI-gap criterion: **252.316 ms > 250 ms** in two-view Performance. [Retained report](performance/dev11-resources-quiet/resource-results.json). All six Pause acknowledgements were at most 77.015 ms; Reset release 21.377 ms and active close 99.876 ms. Peak RSS was 844.7 MiB and MPS driver allocation separately 1117.1 MiB, with overlapping unified memory not added. Exact Step, same-run Resume, full paused raster and zero live MPS tensors after Reset passed. This is source dev11, not a frozen dev11 resource acceptance.

A separate [instrumented resource trace](performance/dev11-resource-trace/event-trace.json) did not reproduce the >250-ms interruption. GUI-gap maxima were 122.51 / 36.31 / 29.14 ms. Generation-2 GC took 69.82 ms inside an approximately 78-ms dispatch. The 137.94-ms maximum overall dispatch includes shutdown. No long dispatcher-block interval identifies a sleep cause. Its passing resource sample does **not** replace the retained uninstrumented failure. MAC-02 remains open: trace evidence supports further investigation but does not yet justify a causal fix, a global GC intervention or an accepted resource budget for the final release.
