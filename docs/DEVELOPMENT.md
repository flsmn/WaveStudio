# Development and native builds

Use Python 3.12. Application and engine are independently versioned at `0.1.0.dev4`; the application pins that exact engine distribution. Development uses editable installations from the two neighbouring repositories. Runtime packages use wheels, without a neighbour dependency.

Tested local dependency versions: Torch 2.5.1, NumPy 2.3.4, PySide6 6.12.0, PyQtGraph 0.14.0, PyInstaller 6.22.3, hooks 2026.8, pytest 9.1.1. They were installed in the local `.venv`; its base is the already installed Python 3.12.12 runtime. A fresh isolated wheel environment independently validated the engine's CPU path. New build environments should install PyPI dependencies directly rather than inherit Conda site packages.

Build wheels first:

```sh
python -m build --wheel --no-isolation ../WaveSimulator2D
python -m build --wheel --no-isolation .
python packaging/build_native.py --engine-wheel ../WaveSimulator2D/dist/wave_simulator_2d-0.1.0.dev4-py3-none-any.whl --studio-wheel dist/wave_studio-0.1.0.dev4-py3-none-any.whl
```

Run this on each native platform. PyInstaller bundles the runtime and numeric engine. The script stages only the supplied wheels into generated `build/wheel-runtime/`, then invokes the spec. Example JSON files are explicitly collected. OpenCV, Matplotlib, TorchVision, TorchAudio and Qt WebEngine are excluded because the application does not use them. The current macOS bundle is ad-hoc signed for local development; public signing/notarization, distribution and updates are not decided. Windows/Linux native build/start checks remain deferred by the user. macOS was tested on arm64/macOS 27.0.1; minimum OS support has not been independently verified.

A native bundle can run the same integration check without installed Python or either source folder:

```sh
dist/WaveStudio.app/Contents/MacOS/WaveStudio --check-workflow /tmp/wave-studio-native-check
```

The engine core tests stay in the engine repository; project, lifecycle, worker and file tests stay in Studio. `wave_studio.checks` exercises real Qt widgets and the actual worker with programmatic actions; it is not a claim of exhaustive human keyboard/accessibility acceptance. Full numerical T01–T04 is run only after relevant numerical changes. The reference tolerances were frozen before measurement; the retained initial report records the failed narrow border configuration.

## Data and bounds

Project format: JSON envelope `format=wave-studio`, integer `version=1`, project data. Stable IDs and tagged object types; no device tensors or live fields. The loader validates all content before activation. Save and CSV export write a temporary sibling file, flush/fsync, then replace atomically. Maximum project/recovery file: 8 MiB; 256 physical objects; 16 detectors; 2048 spatial samples per detector; four held references; 100 undo entries. Recovery: one file, 30-second interval, under Qt's application-data directory; `WAVESTUDIO_RECOVERY_DIR` overrides its directory for isolated checks.

CSV begins with comment lines (including full JSON measurement/origin metadata), followed by distance, x, y and unnormalized mean field-square columns. PNG metadata key is `wave-studio-metadata`. Reference metadata freezes scene content, run/generation, actual backend/dtype, engine version, grid/dt, time/step count, detector path, window, sample count and temporal sampling. Display normalization never changes stored values.

Resource admission is project-configurable: `settings.buffer_limit_mib` defaults to 512; `settings.max_axis_cells` defaults to 4096. Both persist in version-1 JSON with backward-compatible defaults. Integer editor/import ranges are 1–65536 MiB and 8–65536 cells/axis; these ranges do not certify hardware capacity. Admission happens in `Project.validate` before raster allocation, for presets and Custom alike. The engine receives the explicit axis budget in `Grid` and `WaveSimulator2D`; its default remains 4096. Budget metadata is excluded from physical change classification. Grid spacing remains square, with exact multiples of spacing for domain dimensions. The conservative estimate includes solver/work buffers, live intensity and CPU frames; it does not pretend to predict every backend allocator overhead. CPU has one Torch compute thread. Worker blocks contain up to four CPU steps, one MPS step, and one step on million-cell quality grids. Economical pacing scales with block size to retain the 240-step/s cap, commands are bounded at 32, there is one latest-only frame mailbox. Paused workers wait on a condition and perform no numerical steps. Input changes and identity rules are in `CONTRACT.md`.

Balanced follow-up: `scripts/check_balanced_resources.py` exercises actual MPS editor/worker interaction under `docs/BALANCED_MAC_PLAN.md`. It records RSS, separate overlapping MPS allocations, GUI heartbeat, rates, repeated Pause/Resume, exact Step, Reset/release and active shutdown. The original dev3 physical/512² reports remain historical evidence; higher admission limits alone do not certify optical quality.

Large live field/intensity frames are bilinearly resampled on the worker device to at most 1024 cells per axis before the CPU transfer. Paused/Step frames remain full resolution and read-only; `Frame.preview` and PNG metadata expose the distinction. ImageItem display downsampling remains independent of numerical sampling. Changes in frame shape restore the full physical image rectangle. Reset/shutdown release unused MPS cache. These changes address the retained initial Balanced GUI-gap failures; thresholds in BALANCED_MAC_PLAN.md remain unchanged.
