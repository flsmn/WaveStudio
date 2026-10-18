# Wave Studio 0.1.0.dev15 (withdrawn)

This build was withdrawn because it reintroduced a reverted pixel-dimension GUI. Use dev16, which restores physical domain dimensions and editable grid spacing/time-step ratio. The dev15 build artifacts have been removed; the description below is historical.

- Exact pixel Width/Height, automatic square grid spacing and stable time step; Preview/Balanced/High Quality templates use 512/1024/1920 pixels on the longer axis.
- Compact English numeric inputs with adaptive steps below one.
- Organized simulation/view controls, collapsible display settings, conditional second-view controls and compute-mode tooltips.
- Probe Quantity switches between finite-window Intensity and signed instantaneous Field; saved selection, frozen reference timestamps and quantity-aware CSV export.
- Engine dependency: wave-simulator-2d 0.1.0.dev5. No solver stencil changes.

Native app: `dist/ax-dev15/WaveStudio.app`. Start directly with Finder or `open dist/ax-dev15/WaveStudio.app`; this does not rebuild it.

Build:

```sh
.venv/bin/python -m build --wheel --no-isolation ../WaveSimulator2D
.venv/bin/python -m build --wheel --no-isolation .
.venv/bin/python packaging/build_native.py --engine-wheel ../WaveSimulator2D/dist/wave_simulator_2d-0.1.0.dev5-py3-none-any.whl --studio-wheel dist/wave_studio-0.1.0.dev15-py3-none-any.whl --distpath dist/ax-dev15
```

Validation: source tests, 15 selected engine tests, 24 native workflow checks and strict deep code-signature verification. Retained reports: `native-dev15/`. The bundle was built from the working tree, including existing macOS scene-outline accessibility edits that are intentionally outside this feature commit; staged-source tests also validate the committed feature state independently.
