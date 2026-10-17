# Application / engine contract v1

Engine distribution: `wave-simulator-2d==0.1.0.dev2`, import `wave_sim2d`. Application: `wave-studio==0.1.0.dev2`, import `wave_studio`. Numerical details are in the engine's `docs/MODEL.md`. There are no engine imports of Studio or Qt.

A project stores a stable project ID, fixed reference length, continuous geometry with stable object IDs, ordered materials, walls and sources, numerical settings, passive detector settings, display settings and frozen reference datasets. The model uses no Qt classes or device tensors. Coordinates x right/y up; arrays [y,x]. Quality suggestions and expert grid settings are available; final quality acceptance remains separate. Source wavelength never rescales geometry. Validation and complete scene preparation precede replacement. Invalid edits leave the previous project and run untouched.

Only the worker owns the one solver. It processes commands between bounded four-step blocks. Display reads at most one waiting owned, read-only CPU snapshot. No GPU tensors cross into the GUI. Dropped display frames must never drop measurement samples (E08 remains separate). Neither another view nor a reference owns a solver.

Every frame carries `{project_id,scene_revision,run_id,generation,time,steps}`. Future profiles additionally carry `{detector_id,measurement_revision}`. A frame is accepted only on exact identity match and an active running/paused state. Generation advances on reset, failure and invalidation even without a physical edit. Old pending frames cannot resurrect reset results.

| Action | Identity / state | Data |
| --- | --- | --- |
| First Run | New run UUID and generation; Running | Compile and initialize fresh |
| Pause → Run | Same identity; Running | Continue existing fields/time |
| Step | Only Paused with a valid run | Exactly one step, stay paused |
| Physical edit / future Undo/Redo | scene_revision +1, generation +1, no run; Changed | Clear displayed field; require manual Run |
| Reset | generation +1, no run; Ready | Release solver and clear current results; preserve references |
| Run after Reset | New run | Initialize from zero |
| View/contrast/theme | Same run and scene | May mark project dirty; no physics change |
| Detector edit | Same run; only detector revision advances at confirmed block boundary | Clear only that detector's current measurement |
| Invalid input | No change | Preserve previous valid configuration |
| Runtime error | generation +1; Error | Preserve scene, stop; no automatic retry/fallback |
| Project replacement / close | Invalidate before releasing worker | Join thread before releasing UI; reject old data |

Step is intentionally disabled in Ready, including immediately after Reset. This settles B02's open choice: only manual Run initializes a new state; Pause then enables Step.

Planned JSON envelope: `{"format":"wave-studio","version":1,"project":{...},"references":[...]}`. There are no persistent live wave fields. Reference datasets freeze physical scene content (not just revision), engine version, actual backend/dtype, grid/dt, run duration, detector geometry and spatial axis, settling/window times, sample count, sampling and averaging method, and measured values. References are independent of subsequent edits/reset. Unsupported or damaged files are fully rejected before project replacement. Persistence, finite-window measurements and reference export are implemented in S06/E08/S07–S09; see DEVELOPMENT.md for limits and metadata conventions.
