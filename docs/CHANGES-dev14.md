# Wave Studio 0.1.0.dev14 / Engine 0.1.0.dev4

Lokaler macOS-Build vom 18. Oktober 2026: `dist/ax-dev14/WaveStudio.app`.

- Domain width und Domain height können im Einstellungsdialog bis 10.000 eingegeben werden. Die Raster- und Speicherprüfung gilt weiterhin.
- Field und Intensity haben eigene Farbschemata. Field: Classic, Blue / Red, Purple / Green, Grayscale. Intensity: Classic, Viridis, Inferno, Plasma, Grayscale. Beide Ansichten und ihre Farbskalen übernehmen die Auswahl sofort.
- Die Leiste über den Plots enthält getrennte Eingaben für Field range ± und Intensity max. Die Werte bleiben beim Wechsel der Plot-Typen erhalten.
- Second view kann über die Leiste ein- und ausgeblendet werden. Der Schalter und die Auswahl im View-Menü bleiben synchron.
- Anzeigeeinstellungen unterstützen Undo/Redo, Projektdateien und PNG-Metadaten. Bestehende Projektdateien verwenden für fehlende Farbschemata Classic. Anzeigeänderungen setzen eine laufende Simulation nicht zurück.

Validierung: 61 Tests im Arbeitsstand, 59 Tests im isoliert exportierten Commit-Stand sowie der erweiterte Workflow in der gebauten App bestanden. Alle neun Farbschemata wurden aus dem Paket geladen; 27 gebündelte Python-Module stimmen mit den Wheel-/Arbeitsdateien überein. `codesign --verify --deep --strict` bestätigt die lokale Ad-hoc-Signatur. Nachweise: [Build](native-dev14/build-results.json), [App-Workflow](native-dev14/workflow-results.json).

Der Build verwendet den aktuellen Arbeitsstand einschließlich der zuvor vorhandenen Accessibility-Änderungen in `editor.py`. Diese unabhängigen Änderungen bleiben außerhalb des Commits für die hier beschriebenen Einstellungen.

Erneut bauen:

```sh
.venv/bin/python -m build --wheel --no-isolation
.venv/bin/python packaging/build_native.py --engine-wheel ../WaveSimulator2D/dist/wave_simulator_2d-0.1.0.dev4-py3-none-any.whl --studio-wheel dist/wave_studio-0.1.0.dev14-py3-none-any.whl --distpath dist/ax-dev14
dist/ax-dev14/WaveStudio.app/Contents/MacOS/WaveStudio --check-workflow /tmp/wave-studio-dev14-native-check
```
