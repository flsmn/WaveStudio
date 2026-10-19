# Architecture and development boundaries

Wave Studio (`0.1.0.dev16`) is a Qt desktop workbench using the independently versioned WaveSimulator2D engine (`0.1.0.dev5`). [Requirements](REQUIREMENTS.md) define product scope; [ROADMAP.md](ROADMAP.md) is the single list of open work. [CONTRACT.md](CONTRACT.md) defines identities and lifecycle behavior.

## Components

| Location | Responsibility |
| --- | --- |
| `src/wave_studio/domain/` | Immutable project data, history/change classification, quality and resource admission |
| `src/wave_studio/simulation/` | Compile project geometry to engine configuration; worker, mailbox, commands, lifecycle and scoped activity |
| `src/wave_studio/persistence/` | Validated versioned JSON, recovery and atomic PNG/CSV/project operations |
| `src/wave_studio/ui/` | Editor, dialogs, visual controls and plots |
| `src/wave_studio/data/examples/` | Authoritative packaged editable examples, loaded through importlib.resources |
| `src/wave_studio/checks.py` | Real Qt editor/worker workflow check |
| `src/wave_studio/performance.py` | Explicit production-loop performance diagnostic |
| `packaging/` | Build from supplied application/engine wheels, not neighbouring editable sources |
| `scripts/run_app.py` | PyInstaller entry point; required by the build spec |

The numerical stencil, forcing, damping, geometry rasterization and detector integration belong to the engine. Scene editing, run orchestration, project files and exports belong here. Each repository has its own Git history and version.

## Runtime contracts

A physical edit invalidates the current run and requires another manual Run. Detector-only revisions restart only the changed measurement. Display edits do not alter physical state. Run/Pause preserves run identity; Step requires an initialized paused run; Reset releases solver state while retaining held references. See the full [contract](CONTRACT.md).

One worker owns the solver. Commands and frame delivery are bounded; the latest-only mailbox discards obsolete display frames without discarding measurement samples. Live large-grid previews are downsampled for transfer/display, while paused frames, solver state and detectors retain numerical detail.

Project resource checks run before raster allocation. Limits are admission rules, not guarantees about hardware capacity. Increasing them does not change the physical grid or numerical method. Presets are advisory; see [QUALITY_PRESETS.md](QUALITY_PRESETS.md).

## Files and distribution

Projects store geometry, settings, detectors and references, not resumable fields. Invalid files must not replace an active project. Saves/exports use temporary siblings and atomic replacement. The [development guide](DEVELOPMENT.md) documents bounds and build commands.

The desktop bundle excludes SciPy, OpenCV and Matplotlib; these are optional engine development/example dependencies. Current macOS builds are local arm64 candidates. Distribution, minimum OS, licensing and clean-machine acceptance remain open in the [roadmap](ROADMAP.md).

## Checks and evidence

Fast regressions live in `tests/`; static inputs live in `tests/fixtures/`. Hardware diagnostics are separate from software Qt regressions and from human/native accessibility acceptance. The [validation index](../validation/README.md) defines how to run checks and interpret selected historical evidence. Local output belongs under ignored `local-results/`, not in documentation.
