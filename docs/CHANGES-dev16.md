# Wave Studio 0.1.0.dev16

Removes the unwanted pixel-dimension GUI introduced in dev15. Domain width/height again use physical project units. Grid spacing and time-step ratio are editable in Advanced settings. Quality presets retain minimum raster, wavelength, feature and phase requirements; actual resolution can be higher. Compact English numeric entry, toolbar improvements and probe Field/Intensity selection remain.

Build uses engine 0.1.0.dev5 and application 0.1.0.dev16 wheels, with `--distpath dist/ax-dev16`. Current app: `dist/ax-dev16/WaveStudio.app`. The obsolete dev15 app and application wheel are removed after successful replacement validation.

Validation: 90 working-tree tests, 88 tests on staged feature source, 24 native workflow checks, strict deep code-signature verification, wheel/source/bundled-code comparison and absence of the removed pixel-resolution module. Reports: `native-dev16/`.
