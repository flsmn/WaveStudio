# Pixel resolution presets

Width and Height are exact simulation pixel counts. Grid spacing and the time step are automatic; no manual spacing or Courant-ratio controls are exposed.

| Preset | Longer axis | Square | 16:9 |
| --- | ---: | ---: | ---: |
| Preview | 512 | 512 × 512 | 512 × 288 |
| Balanced | 1,024 | 1,024 × 1,024 | 1,024 × 576 |
| High Quality | 1,920 | 1,920 × 1,920 | 1,920 × 1,080 |

Presets preserve the current aspect ratio up to integer rounding. Editing either pixel count selects Custom. They are resolution templates, not optical accuracy guarantees; the GUI reports wavelength and feature sampling separately. Resource budgets can reject the requested resolution without silently reducing it.

For the existing physical domain W × H and requested nx × ny, square spacing is dx = max(W/nx, H/ny), and the new physical extent is nx·dx × ny·dx. This covers the existing scene without cropping object coordinates. The Courant ratio is 0.5; the engine derives dt from dx and wave speed. Existing project files retain their stored grids until resolution is changed.

The internal legacy physical-grid quality selector remains available for historical numerical regression checks. Its wavelength, feature and phase criteria are separate from these GUI pixel templates. Historical physical acceptance reports do not certify a newly chosen pixel grid.

Compute device, compute mode, border damping and resource budgets are in the collapsed Advanced settings section.
