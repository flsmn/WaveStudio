# Probe display quantity

The Measurements & references toolbar has a Quantity selector:

- **Intensity** retains the existing finite-window mean of bilinearly interpolated field square. Completed window values remain frozen.
- **Field** displays the instantaneous signed field, bilinearly interpolated at the same point/line positions. The plot includes a zero line and snapshot time. Samples remain live after intensity completion, and work when the main canvas displays only Intensity or Material.

Switching quantity is a display edit. It does not reset the run, restart measurement windows or change detector revisions. The selection is saved with the project and supports Undo/Redo. Shared field normalization divides by the maximum absolute value across the displayed series, retaining negative signs; stored values and exports remain raw.

Hold reference still requires a completed intensity window. New references also freeze the field snapshot at the time they are held, including `field_time`. The current field remains live while the reference stays frozen. Old intensity-only references load as before and are explicitly unavailable in Field view; no field is inferred from their intensity.

CSV export uses the selected quantity. Field export writes `relative_field` and snapshot time/method metadata. Intensity export keeps `relative_mean_field_squared`. The existing completed-profile export requirement remains in place.

Engine `0.1.0.dev5` adds optional `field_values` and `field_time` to detector results. Existing intensity values and quadrature are unchanged. Worker reconfiguration samples the current solver field immediately, including while paused, without advancing intensity accumulators. Source installations require the matching editable engine; frozen builds need a new dev5 engine wheel and a new application wheel version.
