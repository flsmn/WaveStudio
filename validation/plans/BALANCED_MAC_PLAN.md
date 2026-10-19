# Balanced resource acceptance — dev4

Frozen before the new measurements, Apple M1 / 8 GiB / macOS arm64. This follow-up concerns resource admission and interaction under load, not a new optical focus certification. Windows/Linux remain deferred.

Use the unmodified biconvex-lens example with actual Balanced dx 4/189, 3780 × 2268 cells, MPS, one Torch CPU thread. Explicit project budget: 768 MiB numerical buffers and 4096 cells per axis; defaults remain 512 MiB / 4096. Report 588.7 MiB estimated buffers separately from measured process RSS and MPS allocations. Unified-memory figures overlap and must not be summed.

Exercise the actual editor and worker: field view, simultaneous field/intensity views, Economical/Performance, at least five real pause/resume pairs, exact Step, same-run identity, saved resource limits, Reset and worker shutdown. Observe each active view configuration for at least ten seconds after warmup. Record displayed frame and step rates without applying the earlier 512² 20-fps target to this 8.6-million-cell grid.

Large-grid local budgets: all Pause acknowledgements <250 ms; steady-state GUI heartbeat gaps <250 ms (10-ms timer); Run/Resume/Reset handlers <250 ms; preparation <5 s; first frame <10 s; worker reset and shutdown <2 s; process peak RSS <2 GiB; MPS driver allocation <2 GiB independently. Paused numerical steps must remain constant. Record preparation separately because rasterization still runs synchronously while accepting geometry/settings. Record system swap before/after as context, not per-process attribution. Retain failed reports if a correction is necessary; do not loosen thresholds afterward.

Also exercise the resource controls and Balanced run in the native packaged app. Standard regression coverage must include old JSON defaults, explicit-budget roundtrip, rejection before raster allocation, preset/custom/axis enforcement, unchanged numerics, and changing only limits without resetting the paused experiment.
