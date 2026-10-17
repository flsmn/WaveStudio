# Development and native builds

Use Python 3.12. Application and engine are independently versioned at `0.1.0.dev3`; the application pins that exact engine distribution. Development uses editable installations from the two neighbouring repositories. Runtime packages use wheels, without a neighbour dependency.

Tested local dependency versions: Torch 2.5.1, NumPy 2.3.4, PySide6 6.12.0, PyQtGraph 0.14.0, PyInstaller 6.22.3, hooks 2026.8, pytest 9.1.1. They were installed in the local `.venv`; its base is the already installed Python 3.12.12 runtime. A fresh isolated wheel environment independently validated the engine's CPU path. New build environments should install PyPI dependencies directly rather than inherit Conda site packages.

Build wheels first:

```sh
python -m build --wheel --no-isolation ../WaveSimulator2D
python -m build --wheel --no-isolation .
python packaging/build_native.py --engine-wheel ../WaveSimulator2D/dist/wave_simulator_2d-0.1.0.dev3-py3-none-any.whl --studio-wheel dist/wave_studio-0.1.0.dev3-py3-none-any.whl
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

Current buffer guard: 512 MiB estimated numerical buffers (runtime overhead additional). Grid dimensions are 8–4096 cells, square spacing, dimensions must be exact multiples of spacing. The conservative estimate includes solver/work buffers, live intensity and CPU frames; it does not pretend to predict every backend allocator overhead. CPU has one Torch compute thread. Worker blocks contain up to four steps (one on million-cell quality grids), commands are bounded at 32, there is one latest-only frame mailbox. Paused workers wait on a condition and perform no numerical steps. Input changes and identity rules are in `CONTRACT.md`.
