# Mac acceptance — dev3

Scope: Apple M1 / 8 GiB, macOS 27.0.1 arm64. Windows/Linux are deferred by the user. Criteria were frozen before runs in `MAC_ACCEPTANCE_PLAN.md` (commit `13e33d1`). This is a local development acceptance, separate from public distribution and a cross-platform stable release.

## Quality and numerical evidence

- Original T01–T04 repeated without changing the solver or tolerances: all pass (`../WaveSimulator2D/docs/physical-results-dev3.json`).
- Homogeneous frequencies measured on local sine-mode patches at the selected dx/dt agree with the Fourier-symbol predictions within 0.1%, and speed error is below 2%. The 64-wavelength path is estimated by that verified symbol, rather than claimed as a full-domain propagation measurement. Rotated 0.2-wide material and 0.3-wide wall are included (`quality-preflight-results.json`).
- Initial Preview refraction diagonal mode failed the unchanged 2% speed limit at 2.295%. Raising Preview's minimum from 8 to 10 cells per material wavelength fixes this case; the failed report is retained as `quality-preflight-initial-failure.json`.
- Presets preserve continuous geometry and use wavelength, thin-feature support width and source-to-detector distance. Maximum predicted homogeneous phase drift is π / π/2 / π/4. The actual chosen grid, buffers and phase estimate are visible before Run. These estimates do not bound arbitrary interfaces, concave necks or every user experiment.

| Experiment | Selected grid | Observed result | Verdict |
| --- | --- | --- | --- |
| Slit Preview | 369 × 328, dx 8/41 | minimum error 5.06%, wall 0 | Pass |
| Slit Balanced | 576 × 512, dx .125 | minimum error 3.39%, wall 0 | Pass |
| Slit High Quality | 864 × 768, dx 1/12 | minimum error 3.39%, wall 0 | Pass |
| Lens Preview | 2845 × 1707, dx 16/569 | focus error 6.00%, gain 11.37 | Pass |
| Lens adjacent Custom convergence | 3200 × 1920, dx .025 | focus error 6.25%, gain 11.28 | Pass |
| Lens Balanced | 3780 × 2268 | requires 588.7 MiB numerical buffers | Resource-rejected |
| Lens High Quality | 5665 × 3399 | requires 1322.2 MiB and exceeds axis limit | Resource-rejected |

Slit asymmetry is below 0.0001%. Lens focus shift is 0.25% of paraxial BFL against the frozen 5% limit. Lens demodulation uses on-device bilinear probes, at least 16 observations per cycle, physical settle/window 80/16, the same fixed contour and illumination, and a same-grid background. Raw data and executable methods: `quality-slit-results.json`, `quality-lens-results.json`, `scripts/check_quality.py`. Rejected presets are not labelled physically passed. The 512-MiB/4096-axis guards remain unchanged.

The first recalculated Preview slit grid (dx .2) failed asymmetry at 20.22% because wall faces coincided with cell centres under the existing half-open inclusion rule. The final selector refines past these ties (dx 8/41), preserving the raster convention, geometry and frozen 3% limit. The failed run is retained as `quality-slit-initial-failure.json`. Custom grids with this risk show a warning. A regression check now compares every published physical preset result with the live selector, preventing stale results from certifying a different grid.

## Interaction fixes

The native pass reproduced and led to fixes for stale selected properties, stale positive Pause rates, polygon Tab focus trapping and overlapping material hit areas covering lens/source/detector grips. Additional regression review fixes lost comparison selection, splitter proportions reset by unrelated display edits, distorted second-view units, fixed-pixel fonts ignoring scale, misleading wall-coordinate labels and stale recovery after explicit save/discard, low-contrast light-theme chart labels/legends, missing physical labels during style changes and loss of row identity/focus from full model resets. Autosave cleanup is restricted to the current project ID.

Selected grips now sit above overlapping polygons. Physical edits stay stopped; passive detector edits retain the run and revise only the changed measurement. Quality labels return to Custom when geometry/detector paths change, retaining the grid. Imported preset labels cannot certify an inadequate grid. Polygon rasterization is bounded to the same padded local coordinates and is regression-equivalent to the full-domain mask.

## Execution layers

1. Core and Qt regression suite: 43 tests. Software Qt checks cover history/Run shortcuts, distance 5 and angle 90° at two zooms, reference and camera preservation, every preset rejection, modal validation/Tab behavior, overlapping grip hit order, recovery cleanup, and dark/light 100/125/150% layouts at 980 × 660. These are programmatic tests, not native mouse evidence.
2. Actual editor/worker integration: complete double-slit measurement, references, exports, revisions, reset and file/recovery roundtrip. The final frozen-package result is recorded in `native-results.json`.
3. Agent-operated native Mac UI: Run/Pause, Step 836→837, Reset disables Step and retains references; all object types; point/line-source, polygon vertex, both wall corners, overlapping lens centre and passive point/line/end grips; invalid aperture rejection; native save/reopen and malformed-file rejection preserve state; CSV/PNG save panels; two held profiles, older reference retained across theme changes; two views; 100/125/150% text. Native mouse measurements at two scales gave 5.03614 / 4.96992 for rounded positions spanning five reference lengths and 90.000° at both scales. Exact-coordinate Qt tests give 5.00000 / 90.000°. Standard history/Run accelerators, material ordering, Copy/Delete and recovery are also checked programmatically. Native Command-O and modal Tab/Enter paths were exercised. This is not labelled a human review; native minimum-window resizing was not relied on, and exact 980×660 geometry is checked by Qt.

Completed profiles now retain their graphics until plotted values, sampling, normalization, theme or text size changes. A final resource pass with restored axis labels initially missed Pause at 115.5 ms CPU (`resource-pause-initial-failure.json`); removing redundant profile redraws fixed CPU response, but one MPS sample still reached 103.8 ms (`resource-pause-after-profile-cache.json`). MPS now checks commands after every numerical step while economical pacing retains the same 240-step/s cap. The final report records five real resume/pause samples per backend and checks their maximum against the unchanged 100-ms limit; both compute modes are sampled for three seconds.

The final native follow-up at source `3533c86` confirms readable light-theme labels/units/scales at 150%, native property editing and Undo through the Edit menu. A remaining limitation is recorded rather than passed: after editing, the visible scene tree is omitted from the macOS accessibility snapshot used by the automation. Incremental rows preserve Qt identity/focus in regression tests, but this does not establish complete AX/VoiceOver behavior. Native Command-Z was not independently confirmed; the native Undo menu and Qt standard-shortcut tests pass. This bridge investigation remains open in `task.md`.

## Resources

The 512² reference passes the frozen budgets on CPU and MPS. One/two economical views deliver 22.33/25.66 fps CPU and 26.31/24.33 fps MPS. Two-view Performance delivers 25.32/27.33 fps. All five Pause samples pass on each backend; worst acknowledgement is 8.81 ms CPU / 36.37 ms MPS. Process peak RSS is at most 286.0 MiB. Warmed idle/pause CPU remains below .10 CPU-seconds/wall-second; paused steps/repeated frames are zero. Mode changes preserve run, grid and measurement identities. `resource-results.json` contains every sample and system-wide GPU counters; earlier and failed reports remain alongside it.

IORegistry GPU counters were readable (the lens run also showed 97% device utilization). They include other applications and the compositor and cannot be attributed to Wave Studio alone. `powermetrics --samplers gpu_power -n 1 -i 100` reports that superuser access is required; calibrated energy was not measured. No privileged system changes were made for this test.

Large grids use one step per command boundary; `large-grid-results.json` records response on the affordable lens Preview. The 512² frame-rate/RSS budget is not extended to these grids.

## Distribution boundary

`build-results.json` records the final source commit `3533c86`, wheel hashes and source-content comparison. The frozen workflow launched from `/private/tmp` passes and imports both packages from inside the bundle. A separate native PNG export records actual MPS computation (6552 steps, engine dev3).

The app is rebuilt from the exact dev3 wheel pair, locally ad-hoc signed and checked outside both source trees. Public signing/notarization, a clean-machine/minimum-OS distribution pass and Windows/Linux remain separate work. The scalar finite-domain lens remains a demonstration, not a precision optical prediction.
