# macOS accessibility findings

Current application source is dev16. The selected native accessibility evidence is from **dev13 / Qt 6.12.0** and does not automatically qualify the current bundle. MAC-03 remains open in [ROADMAP.md](ROADMAP.md).

## Confirmed improvement

Unconditionally reapplying the Qt style on physical edits invalidated the native scene outline. The editor now restyles only when theme/text scale changes and reconciles existing rows. In the actual dev13 package, changing source amplitude and native Command-Z/Command-Shift-Z preserved the outline, row and focus while restoring the values correctly. See the [native report](../validation/results/native-dev13/accessibility-results.json).

## Remaining failure

Adding a source left the visible scene and properties correct, but the scene outline disappeared from the native accessibility snapshot. Earlier replacement-widget workarounds were rejected after missing AX rows and crashes. Software Qt regressions, a visible list and a passing scripted workflow do not establish native accessibility acceptance.

An isolated Qt 6.8.3 dependency comparison also crashed on Add without the replacement workaround. The [crash summary](../validation/results/native-dev13/qt68-crash-summary.json) preserves that failure; a dependency downgrade is not an accepted fix. The main environment retained Qt 6.12.0. No global accessibility settings were changed.

## Completion checks

Verify the actual final candidate after Add/Delete/Rename/Undo/Redo and theme/text-scale changes; check tab order, focus and native shortcuts. Then perform human VoiceOver/usability acceptance. Distinguish application, Qt and operating-system causes using a small reproducible case before changing dependencies. Older intermediate runs and rejected workaround details remain in Git history.
