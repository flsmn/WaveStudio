# Quality presets

Domain width and height use the existing physical project units. They are not pixel counts. Grid spacing and Time step / grid spacing are editable under Advanced settings. Manual spacing selects Custom; quality changes preserve geometry.

| Preset | Minimum longer-axis cells | Minimum cells / shortest wavelength | Minimum cells / smallest feature | Maximum predicted phase drift |
| --- | ---: | ---: | ---: | ---: |
| Preview | 512 | 10 | 2 | π |
| Balanced | 1,024 | 12 | 4 | π/2 |
| High Quality | 1,920 | 20 | 6 | π/4 |

The selector meets all these requirements while retaining square cells, exact physical dimensions and wall alignment. Actual resolution and cells per wavelength can be higher. Resource budgets can reject a grid; no silent coarsening occurs. Existing saved Custom grids remain unchanged. Historical physical acceptance reports describe their recorded grids, not measurements of the revised resolution floors.

Compute device, compute mode, border damping and resource budgets also remain in the collapsed Advanced settings section.
