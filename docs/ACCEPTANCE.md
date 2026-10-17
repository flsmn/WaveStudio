# Local acceptance – 17 October 2026

Scope: development pair `wave-studio==0.1.0.dev2` / `wave-simulator-2d==0.1.0.dev2`, Apple M1 / 8 GiB, macOS 27.0.1 arm64. The user explicitly deferred Windows and Linux testing. This is a functional development application, not a completed cross-platform 0.1 release.

## Functional evidence

Seventeen automated core checks pass (nine engine, eight Studio). They cover invalid numerical inputs and runtime non-finite fields, complete reset, additive source superposition and incoming waves, spatial source normalization, material order and fresh rasterization, wall transmission, fractional finite-window boundaries, frame-rate-independent measurements, detector-only reconfiguration, lifecycle generations, bounded latest-frame delivery, controlled worker failure without restart, project/reference roundtrip, invalid files, failed atomic replacement and history change classes.

The actual Qt editor/worker integration check passes the double-slit workflow: complete detector window, hold reference, same-run pause/resume, exact single step, move one detector while running without changing run identity or another detector, reject invalid changes, show intensity and a second view, export PNG and CSV, preserve references through reset and physical Undo/Redo, save/reopen, recovery roundtrip and compile all three examples. It operates the real model/worker/widgets programmatically. It does not replace a human acceptance pass for every mouse/keyboard action, scaled fonts or accessibility. Artifacts: `workflow-artifacts/`.

The four physical references pass their frozen v1 limits with the current engine; detailed raw results and known limitations are in the engine's `docs/physical-results.json` and `docs/VALIDATION.md`. Point-source amplitude differs by 0.448% across the compared grids; line-source amplitude by 2.880%. The coarse lens remains a demonstration with 18.5% / 11.5% back-focal errors and 7% grid shift, not a precision preset.

CPU/MPS T08 passes at relative field error 1.04e-6, maximum absolute error 2.01e-7 and detector-profile relative error 5.80e-6, against frozen comparison limits .005 / .0005 / .005. CUDA is not offered. See `backend-results.json`. The wheel's CPU/detector path was independently installed into a clean temporary environment outside both source repositories; `pip check` passes and imports resolve to that environment's site-packages.

## Resources and packages

`resource-results.json` measures a representative 512² point-source experiment with one passive detector, economical/performance modes and one/two views. CPU is one Torch compute thread. Measurements include application process CPU time, displayed snapshots, numerical steps, actual pause acknowledgement latency and peak RSS. The initial report is retained separately; its first idle interval included startup work, so the final method adds a warm-up and excludes the unchanged starting snapshot from frame counts. GPU utilization was not sampled; MPS allocation is reported separately from RSS and never added to shared Apple memory.

Implementation bounds are explicit: four numerical steps per block; economical mode ≤60 blocks/s; display ≤30 snapshots/s; one waiting frame; 32 commands; 512 MiB estimated numerical-buffer guard; 16 detectors ×2048 samples; four references; one 8 MiB recovery file every 30 seconds. These keep memory bounded, but are not final universal performance/accuracy budgets. The representative local pause target remains <100 ms. The final economical UI sample delivered about 24–26 displayed snapshots/s, 199–219 numerical steps/s, and 32.0 ms CPU / 46.8 ms MPS pause acknowledgement. Peak process RSS was 477 MB CPU / 512 MB after MPS use (process-wide high-water marks). Paused runs produced zero steps and frames; warmed idle/pause process CPU was about 0.04–0.07 CPU-seconds per wall-second. These short local measurements do not establish 30 fps universally. Rendering avoids rebuilding static colorbars, transforms and hidden views per frame. Raw measured values are in the JSON report.

The native macOS application is built from supplied engine/Studio wheels, contains the runtime and packaged JSON examples, and is ad-hoc signed for local development. Its file contents total 642,893,259 bytes (allocated disk usage about 642 MiB). Wheel sizes/SHA-256 and the source pair are in `build-results.json`. The final native integration check passes from `/private/tmp`, records `frozen=true` and both engine/application module paths inside the bundle (`native-results.json`), proving active imports do not use neighbouring source folders. PNG/CSV and project/recovery roundtrips pass in that bundle.

## Open acceptance

- Windows/Linux native build and offline checks, plus the weaker test machine: deferred by the user.
- Final supported OS versions/architectures, public signing/notarization, distribution and update policy.
- Final quality-preset accuracy/long-path/feature-size validation and agreed performance budgets. Current presets are advisory; the buffer guard may reject costly choices rather than silently change geometry.
- Direct GPU utilization/energy sampling and a clean-machine macOS distribution check.
- Full human T05/T06 pass, keyboard/scaled-font/accessibility review, including geometric tools and all drag handles.

These remain visible in `task.md`; E09/B05 stable release and T09 across all platforms are not marked complete.
