# Balanced on this Mac — dev4

Apple M1, 8 GiB unified memory, macOS 27.0.1 arm64, actual MPS. Frozen criteria: [BALANCED_MAC_PLAN.md](BALANCED_MAC_PLAN.md). Raw samples: [balanced-resource-results.json](balanced-resource-results.json). **Resource/interaction acceptance passes.** Optical focus certification was not repeated at Balanced; the dev3 Preview/custom optical results remain separately scoped.

The fixed lens uses the same physical geometry and Balanced selector as before: dx 4/189, **3780 × 2268**, **588.7 MiB estimated numerical buffers**. An explicit project budget of **768 MiB / 4096 cells per axis** admits it. Defaults stay 512 MiB / 4096; old JSON inherits defaults. Both admission values persist per project. Presets and Custom use the same pre-allocation rejection; quality/grid are never silently reduced. Higher axis settings are propagated through the engine constructor. The finite editor/import ranges (1–65536 MiB, 8–65536 cells/axis) are input bounds, not tested hardware limits.

| Measurement | Final observation |
| --- | --- |
| Peak process RSS | 1000.0 MiB |
| MPS driver allocation, separately | 1117.1 MiB |
| Field, economical | 19.90 frames/s |
| Field + intensity, economical | 18.40 frames/s |
| Field + intensity, Performance | 19.56 frames/s |
| Six Pause acknowledgements | 47.26–137.37 ms |
| Worst active GUI heartbeat gap | 135.08 ms |
| Prepare geometry | 0.766 s |
| First frame after Run | 1.279 s |
| Run / Resume handlers | 0.89 / 1.12 ms |
| Reset acknowledged after solver/cache release | 25.48 ms |
| Close while computing | 284.86 ms |

RSS and MPS allocations overlap on unified memory and must not be added. RSS is the process lifetime peak, not current post-reset memory. After Reset, current MPS tensor allocation is zero; driver allocation retains 69.1 MiB of backend state. System swap was already in use before the run; its recorded machine-wide change cannot be attributed exclusively to this app. In this final sample swap usage decreased by 8 MiB. These observations describe this run and machine, not guaranteed worst-case latency under arbitrary system load.

The run also passes: paused numerical steps do not advance, Step advances exactly once, Resume/display/mode changes preserve run/grid/measurements, resource limits survive JSON roundtrip, Reset remains stopped, active shutdown terminates the worker. The earlier 512² ≥20-fps budget is not applied to this 8.6-million-cell scene.

## Corrections and retained evidence

- Run/Resume reuse the validated prepared scene instead of synchronously rasterizing it again.
- `balanced-resource-initial-failure.json` retains a 395-ms two-view GUI interruption. `balanced-resource-after-render-downsampling.json` records that ImageItem downsampling alone did not fix every interruption (up to 1177 ms); that run also overlapped regression tests initially.
- Live field/intensity frames above 1024 cells/axis now use device-side bilinear display sampling before CPU transfer. The UI and PNG metadata mark the preview. **Numerical fields and detector integration remain at 3780 × 2268. Pause and Step restore every cell.** Image extents stay physical and rendering downsamples independently to the screen. This bounds transfer/render work without certifying a different numerical grid.
- Reset/shutdown drop solver state and release unused MPS allocator cache. `balanced-resource-reset-probe-failure.json` retains a rejected supplemental test assumption: all UI/Pause samples passed, but a demand that driver memory return within 64 MiB of startup timed out. Driver memory includes persistent backend state. The corrected measurement uses an explicit worker acknowledgement after dropping the solver and emptying cache, with memory figures reported separately. The frozen 2-second reset/shutdown and other thresholds are unchanged.
- 59 core/Qt tests cover old-file compatibility, persistent/invalid budgets, pre-allocation rejection, both preset guards, explicit >4096-cell engine grids, bitwise-identical numerics with different budgets, budget-only run preservation, display-only sampling, full paused/Step data and correct physical image extents/metadata.

Implementation commits: Studio `8b8e23e`, Engine `10f7ce9`.

## Native package

The final dev4 package was rebuilt from the exact matching wheels; hashes/source comparison are in `build-results-dev4.json`. Its frozen workflow from `/private/tmp` passes and imports both packages inside the bundle (`native-results-dev4.json`).

Native UI checks also pass (`balanced-native-results.json`): 512-MiB rejection, explicit 768-MiB admission, editing the axis budget to 8192/back to 4096, retained Balanced preset and MPS device, Run/Performance/second view, Pause, Step 543→544, Resume to 709, native Save/PNG and Reset to Ready/0 with Step disabled. The PNG records actual MPS, engine dev4 and a full paused image of 2268 × 3780 cells. The saved native project contains both resource budgets. During native automation the HUD showed about 5–8 frames/s, lower than the separate controlled resource run. This is retained as an observed limitation, without inferring a specific cause or guaranteeing either rate. Budget changes improve admission, not a fixed frame-rate promise. High Quality has configurable admission but remains untested on this Mac. Windows/Linux remain deferred. The earlier AX scene-list bridge limitation is unrelated and remains open.

## Later FPS investigation

The 18–20 rates above belong to the dev4 processEvents/10-ms-heartbeat resource test. They are not a matched steady-state native-package comparison. The dev8 investigation corrects the rate display and records production-loop measurements and their limits in [PERFORMANCE_INVESTIGATION.md](PERFORMANCE_INVESTIGATION.md); it does not certify a sustained 20 FPS or assign the entire old gap to a proven single cause. Historical dev4 resource/optical scope remains unchanged.
