# Native Mac-Accessibility – Nachprüfung vom 18. Oktober 2026

MAC-03 bleibt offen. Qt-Tests, programmatischer Paketablauf, native AX-Snapshots und menschliche VoiceOver-Prüfung sind unterschiedliche Nachweise.

## Bisherige Kandidaten mit PySide6 6.12.0

Der dev8-Fehler ist nativ reproduziert: Nach einer Änderung der Quellenamplitude verschwindet die Szenenliste aus dem AX-Baum. Unbedingtes Neuanwenden des Styles bei jeder physikalischen Änderung war ein Auslöser. Dev9 wendet Styles nur bei tatsächlicher Theme-/Textgrößenänderung an. Die native Eigenschaftsänderung und Command-Z/Redo erhalten daraufhin Liste und Zeile; die Amplitude wechselt 1,0 → 1,1 → 1,0 → 1,1. Simulation bleibt gestoppt. Auf der deutschen Tastatur sendet die Automatisierung das physische `y` für das logische Z; die Anwendung verwendet weiterhin Standard-Undo/Redo.

Dev10–dev12 erneuern die native Liste bei tatsächlichen Style- bzw. Modellwechseln. Qt bestätigt Erhalt von Auswahl, Fokus, Scrollposition, Projekt, History und Laufidentität. Dev11 behebt dabei den zusätzlich gefundenen verzögerten Scrollsprung. Native 150-%-Schrift mit einer Zeile ist erreichbar. **Der Ansatz genügt jedoch nicht:** Nach dem Hinzufügen einer zweiten Quelle fehlen in dev11 und dev12 die AX-Zeilen trotz korrekt sichtbarer Liste. Dev12, native Aktion `+`, Name „AX added“: beide sichtbaren Zeilen, benanntes AX-Outline, aber keine Row-/Container-Kinder. Ein nachfolgender direkter AX-Klick lieferte `AXError.notImplemented`. Dieser Fehlbefund bleibt erhalten; kein vollständiger AX-Pass.

Dev12 hat [77 bestandene Regressionstests](native-dev12/regression-results.txt) und einen [bestandenen eingefrorenen Paketablauf](native-dev12/workflow-results.json) aus `/private/tmp`. Diese Prüfungen widerlegen den nativen Fehlbefund nicht. Ursprüngliches dev8 und die Kandidaten liegen getrennt unter `dist/`.

## Abhängigkeitsvergleich

Die [Qt-6.12-Cocoa-Implementierung](https://github.com/qt/qtbase/blob/6.12/src/plugins/platforms/cocoa/qcocoaaccessibilityelement.mm) verwendet für synthetische Zeilen/Spalten die Accessibility-ID der Tabelle. Der Freigabepfad ruft `deleteInterface(axid)` auf. Das ist ein konkreter Verdacht für die beobachtete Invalidierung, noch kein durch einen isolierten Qt-Patch bewiesener Ursachenbefund. Die [Qt-6.8.3-Implementierung](https://github.com/qt/qtbase/blob/v6.8.3/src/plugins/platforms/cocoa/qcocoaaccessibilityelement.mm) besitzt diesen Freigabeaufruf nicht. Ein isolierter Vergleich ist der nächste Schritt; keine eigenmächtige Änderung an globalen Accessibility-Einstellungen und kein gepatchtes Qt-Binärpaket.

Offen: stabile native Liste nach Add/Delete/Umbenennen/Undo/Redo und Theme/Textwechsel, Tab-/Fokuspfade am tatsächlichen Kandidaten, danach menschliche VoiceOver-/Bedienabnahme. Ein sichtbarer Listeninhalt allein genügt nicht.

Vergleichsumgebung: offizielle PyPI-Wheels PySide6/Essentials/Addons/Shiboken 6.8.3 nach `build/qt68-runtime` isoliert installiert. `.venv` behält 6.12.0. Der erste Sandbox-Import bricht mit „Incompatible processor … neon“ ab; die CPU-Erkennung dieser Qt-Version benötigt hier den nativen Host-Kontext. Das ist kein AX-Prüfergebnis. Vergleichs-Build und Regression laufen deshalb außerhalb der Sandbox.

Die vollständige Regression mit isoliertem Qt 6.8.3 besteht: **77 Tests in 13,54 s**, außerhalb der Sandbox, Qt offscreen. Dies ist noch kein nativer AX-Pass. Der Vergleich verwendet dasselbe Studio-dev12-/Engine-dev4-Wheelpaar.

**Nativer Vergleich dev12/Qt 6.8.3 nicht bestanden:** Nach Add/OK endet die App mit SIGSEGV (EXC_BAD_ACCESS) beim Freigeben von Cocoa-Arrays im Cocoa-Plug-in; [auf das eigene Testpaket begrenzte Absturzzusammenfassung](native-dev12/qt68-crash-summary.json). Der komplexe Listenersatz ist damit auch in der Vergleichsvariante nicht akzeptiert. Dev13 entfernt diesen Workaround und behält die einfachere Zeilenabstimmung und die bestätigte Vermeidung unnötiger Styles. Weitere native Prüfung erforderlich.

**Auch dev13 ohne Listenersatz besteht den nativen Qt-6.8-Vergleich nicht:** Derselbe Add-Vorgang beendet die App; [Absturzzusammenfassung](native-dev13/qt68-crash-summary.json). Damit ist ein einfacher Rückgang auf 6.8.3 kein akzeptierter Fix auf diesem Mac. Die Hauptumgebung behält Qt 6.12.0, keine ältere Version wird als Produktabhängigkeit festgeschrieben. Dev13 behält die gezielte Style-Korrektur und benennt die Szene zugänglich, aber die vollständige AX-Freigabe bleibt offen. Vergleichspakete unter `dist/qt68-*` sind verworfene Diagnoseartefakte.

## Regulärer dev13-Kandidat / Qt 6.12.0

[76 Regressionstests](native-dev13/regression-results.txt) und der [vollständige eingefrorene Paketablauf](native-dev13/workflow-results.json) aus `/private/tmp` bestehen. [Wheel-/Quell-/Bytecode-Abgleich](native-dev13/build-results.json) stimmt; SciPy ist im App-Codearchiv nicht enthalten.

Die bestätigte Korrektur besteht erneut im **tatsächlichen dev13-Fenster**: Quellenamplitude 1,0 → 1,1, natives Command-Z → 1,0, Command-Shift-Z → 1,1. AX-Outline, Zeile, Objektname und Zeilenfokus bleiben sichtbar; die Simulation bleibt bei null Schritten. Danach Add „AX added“: Eigenschaften korrekt, App läuft weiter, aber die gesamte Szenenliste fehlt im AX-Snapshot. [Getrennter nativer Ergebnisbericht](native-dev13/accessibility-results.json). Eigene Teständerungen wurden beim Schließen verworfen. MAC-03 bleibt für strukturelle/Style-Wechsel und menschliche VoiceOver-Prüfung offen.
