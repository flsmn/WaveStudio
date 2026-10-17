# Historischer Fortschritt

Dieser archivierte Tracker enthält frühere Zwischenstände. Maßgeblich für den aktuellen Stand ist task.md.

# Wave Studio – Fortschritt

Stand: 17. Oktober 2026. Entwicklungsstand: **Studio und Engine 0.1.0.dev2**.
Maßgeblich: DEVELOPMENT_PLAN.md, PRD.md, PROJECT_PLAN.md. Dies ist eine funktionale Entwicklungsversion; keine abgeschlossene plattformübergreifende Release-Abnahme.

## Ausgangslage und Entscheidungen

- Zwei eigenständige Git-Repositories; der Workspace selbst ist kein Git-Repository.
- Engine-Ausgangscommit: `5620234f539b1be3974f4dca122c16f272845271`. Vorhandene Änderungen am README-Beispiellink und portablen Test-Import wurden erhalten. Neun bereits gelöschte versionierte Cachedateien wurden separat bereinigt (`134bd37`).
- Studio hatte anfangs nur die Planung und keinen Commit; Baseline samt Tracker in `323e453` gesichert.
- Nutzerentscheidung vom 17.10.: vorerst nur der aktuelle Apple M1 / 8 GB; Linux- und Windows-Tests folgen später. Der lokale Funktionsausbau wurde nach M0 und dem macOS-Prototyp fortgesetzt; die fehlenden Plattformnachweise bleiben ausdrücklich offen.
- B02: Step nur im initialisierten pausierten Lauf. Reset gibt den Zustand frei, erneuert die Generation, bleibt bereit und sperrt Step bis Run → Pause.
- O01: kalibrierter Neunpunkt-Stencil, c0=1, additive skalierte Delta-/Linienanregung, Zellmittelpunktraster, Dirichlet-Wände, zeitbezogene Dämpfung; Vertrag in der Engine unter `docs/MODEL.md`.
- O02: Toleranzen vor den Referenzmessungen in `d06d04b` eingefroren. Fehlgeschlagene schmale Randzone dokumentiert und räumlich verbessert; keine nachträgliche Toleranzaufweitung.
- O05: bikonvexe Linse als Schnitt zweier Kreise, symmetrisch, Randdicke null; Apertur <2R. Dieselbe feste Kontur wie T04, gitterunabhängig.
- O06: editierbare Einlauf-/Fensterdefaults 32/16 Simulationszeiteinheiten; vier Referenzen; eine Wiederherstellungsdatei, maximal 8 MiB, alle 30 Sekunden bei Änderungen. Keine automatische Aussage „eingeschwungen“.

## Abgeschlossene Implementierung

- [x] B01: unabhängige Versionierung, Python-3.12-Umgebung und Entwicklungsanleitung.
- [x] E01: installierbare Engine, optionale alte Visualisierung, Editable-Integration und isolierter Wheel-/CPU-/Detektortest außerhalb des Quellbaums.
- [x] B02: API-, Einheiten-, Puffer- und Lebenszyklusvertrag einschließlich Reset-/Messidentitäten.
- [x] E02–E06: Skalierung/Stabilität, Gerätewahl, Initialfeld/Reset/Schritte, additive Quellen, Materialreihenfolge, Rasterisierung, Wände, getrennte Randzone und physikalische Dämpfungsrate.
- [x] E07: vier ausführbare Referenzfälle; T01–T04 bestehen innerhalb der vorher festgelegten begrenzten Toleranzen. Punkt-/Linienquellen wurden auch über zwei Auflösungen verglichen.
- [x] S01–S04: startbare englische Oberfläche, Projektmodell/Compiler, ein Worker mit vier Schritten pro Block, ein Frame-Puffer, Run/Pause/Step/Reset, Revisionen und kontrollierte Fehlerpfade.
- [x] S05: freier Aufbau mit Punkt-/Linienquellen, Materialrechtecken/-polygonen, Wänden; Auswahl, Verschieben/Griffe, numerische Eigenschaften, Duplizieren/Löschen, Reihenfolge, Undo/Redo. Physikalische Änderungen bleiben angehalten.
- [x] S06: versioniertes JSON, vollständige Prüfung vor Projektwechsel, atomisches Speichern, Speicherstatus und begrenzte Wiederherstellung.
- [x] E08/S07: passive Punkt-/Liniendetektoren, bilineares Feldquadrat pro Rechenschritt, endliche Fenster mit anteiligen Randzeitschritten, geräteinterne Akkumulation, eigene Messrevision und Live-Intensitätsvorschau.
- [x] S08/S09: bis zu vier eingefrorene Profile samt Ursprungsszene, gemeinsamer Vergleich/Rohskalierung, PNG mit Skala/Metadaten, CSV mit unnormalisierten Werten und vollständiger Zuordnung.
- [x] B04 lokal: Doppelspalt im tatsächlichen Qt-/Worker-Ablauf bis Referenz, Export und Wiederöffnung geprüft. Geänderte Detektoren erhalten eine neue Messrevision, ohne Feld/Lauf oder andere Detektoren zu ändern.
- [x] S10/S11 Implementierung: parametrisierte Linse nach T04-Vertrag, zweite Ansicht desselben Laufs, synchronisierte Ausschnitte, Abstand und Winkel.
- [x] S12 Implementierung: wellenlängen-/strukturbezogene Qualitätsvorschläge, Expertenwerte, Speicherprüfung, CPU/MPS/Auto und unabhängige sparsame/höhere Rechenmodi. Finale Qualitätsfreigabe siehe offen.
- [x] S13 Implementierung: drei bearbeitbare JSON-Beispiele, englische Hilfe, helle/dunkle Darstellung, Tastaturbefehle und Benutzer-/Entwicklungsdokumentation.
- [x] T08 lokal: CPU/MPS-Feld- und Detektorprofilvergleich bestanden; CUDA wird nicht angeboten.
- [x] Native macOS-Paketierung aus fest gebauten Wheels; früher Paketstart erfolgreich. Der finale vollständige Pakettest besteht aus `/private/tmp`; `frozen=true`, Engine-/Studio-Importpfade im Bundle, Beispiele, PNG/CSV und Projekt-/Referenz-Roundtrip bestätigt (`docs/native-results.json`).

## Prüfungen

- **17 Kernprüfungen bestanden:** neun Engine-, acht Studio-Prüfungen; darunter kontrollierter Workerfehler ohne automatischen Neustart, vollständiger Reset, alte Frames, Messfenster, ungültige Dateien und fehlgeschlagener atomischer Austausch.
- **T01–T04 bestanden**, Rohwerte in `../WaveSimulator2D/docs/physical-results.json`, Protokoll/Toleranzen unter `../WaveSimulator2D/validation/`. Geschwindigkeitsfehler <0,5 %, Quellen-Amplitudenabweichung zwischen Gittern: Punkt 0,448 %, Linie 2,880 %.
- **T05/T06 lokaler Integrationstest bestanden:** tatsächliche Qt-Widgets und echter Worker; Referenz, Step/Resume, Detektoränderung, ungültige Eingabe, zwei Ansichten, PNG/CSV, Projekt-/Referenz-Roundtrip und Wiederherstellung. Artefakte unter `docs/workflow-artifacts/`.
- **MPS-Vergleich bestanden:** Feld relativ 1,04e-6, Profil relativ 5,80e-6. Ergebnisse unter `docs/backend-results.json`.
- Ressourcenmessungen unter `docs/resource-results.json`; Startkosten und stationäre Leerlauflast werden durch Aufwärmphase getrennt. Keine zusätzlichen numerischen Schritte/Frames im pausierten Lauf. GPU-Auslastung nicht direkt gemessen; MPS-Speicher nicht zum gemeinsamen RAM doppelt addiert.
- Visuelle Prüfung beider Themes und Exportbilder durchgeführt. Fehler der zweiten Ansicht, Referenz-JSON-Roundtrip und Farbbereiche wurden dabei behoben. Statische Farbskalen, Bildtransformationen und unsichtbare Ansichten werden nicht mehr pro Frame neu aufgebaut.
- Isolierter Engine-Wheel-Test 0.1.0.dev2: CPU-Lauf und abgeschlossenes Detektorfenster; Import aus separaten site-packages, `pip check` bestanden.

## Offene Abnahmen / nächste Arbeit

- [ ] **B03/B05/T09 Windows und Linux:** native Pakete, Offline-Abläufe und schwächere Testhardware – ausdrücklich auf später verschoben.
- [ ] **S12 finale Qualitäts-/Leistungsfreigabe:** Vorschläge implementiert; vollständige Preset-/Langweg-/Strukturvalidierung und abgestimmte verbindliche Budgets stehen aus. Das vorläufige 30-fps-Ziel ist kein universelles Versprechen.
- [ ] **M4 menschliche T05/T06-Abnahme:** kompletter Maus-/Tastaturablauf, alle Ziehgriffe, Messwerkzeuge, skalierte Schrift und Zugänglichkeit. Die programmatische Integration ersetzt diese Abnahme nicht.
- [ ] **B03 ergänzende Ressourcenprüfung:** direkte GPU-/Energielast und schwächere Hardware.
- [ ] **E09/B05 stabiles Release:** unterstützte Mindestbetriebssysteme, Signierung/Notarisierung, Verteilung/Updates und plattformübergreifende Freigabe. Der aktuelle Stand bleibt `0.1.0.dev2`.

Die grobe T04-Linse liegt mit 18,5 % / 11,5 % Fokusfehler und 7 % Rasterverschiebung innerhalb der bewusst breiten Demonstrationstoleranz. Daraus folgt keine Präzisionsoptik-Zusage. Die kleinere Standardrandzone und beliebige Nutzergeometrien erben ebenfalls keinen pauschalen Genauigkeitsnachweis.

## Git- und Integrationsstände

- Engine: `134bd37` Cachebereinigung; `d06d04b` vorab eingefrorene Toleranzen; `84df638` kalibrierter Kern/Referenzen; `b0c4af0` geräteinterne Detektoren und Messfenster.
- Studio: `323e453` Baseline; `c490eaa` Worker-Prototyp; `33b754c` Editor, Dateien, Messungen und Exporte. Weitere Abschlusscommits halten Verifikation, Paketierung und Darstellungsoptimierung fest.
- Beide Pakete verwenden dasselbe Entwicklungsversionspaar `0.1.0.dev2`; native Builds beziehen die Engine aus dem Wheel, nicht aus einem beweglichen Nachbarcheckout.


## Abschluss dieses Entwicklungsstands

- Finaler nativer macOS-Build aus dem gepinnten Versionspaar erfolgreich. Anwendung: `dist/WaveStudio.app`; Wheels in den jeweiligen `dist/`-Verzeichnissen. Keine Nachbarquellen zur Laufzeit erforderlich. Wheel-Hashes und Build-Zuordnung in `docs/build-results.json`.
- Abschließender T05/T06-Integrationstest im tatsächlichen eingefrorenen Paket erfolgreich; beide Importe kommen aus dem Bundle. Prüfausgaben in `docs/native-results.json` und `/tmp/wave-studio-native-final-check/`.
- Finale 512²-Messung auf dem M1: ca. 24–26 Frames/s, Pause ca. 32 ms CPU / 47 ms MPS; maximal beobachteter Prozess-RSS ca. 512 MB. Pausiert null Schritte/Frames. Das vorläufige 30-fps-Ziel ist damit noch nicht als allgemeines Ziel bestätigt; siehe offene Budget-/Qualitätsabnahme.
- Lokale Funktionsimplementierung M0–M4 verfügbar; die oben aufgeführten Plattform-, Qualitäts-, menschlichen Bedien- und Release-Abnahmen bleiben offen. Es wurde kein stabiles plattformübergreifendes Release behauptet.
- Engine-Abschlussstand: `3813481`; Studio-Anwendungscode: `d5e9c7f`. Der folgende Dokumentations-/Build-Commit hält die vollständigen lokalen Nachweise fest.

## Mac-Qualitäts- und Bedienungsabnahme (Folgeauftrag)

- Begonnen: gezielte native Bedienprüfung und zusätzliche Qualitätsprüfung nach `docs/MAC_ACCEPTANCE_PLAN.md`. Windows/Linux bleiben zurückgestellt.
- Bereits reproduziert: Nach einer über den nativen Eigenschaftendialog geänderten Wellenlänge zeigt der Dialog den neuen Wert, die ausgewählte Eigenschaftenzusammenfassung jedoch weiterhin den alten. Die Rateanzeige zeigt nach Pause/physikalischer Änderung alte positive Werte. Beides wird korrigiert.
- Bestehende Qualitätsvorschläge berücksichtigen noch keine Ausbreitungsdistanz und dünnen Material-/Linsenkonturen; skalierte Schrift wird durch feste Pixelgrößen übergangen. Dazu werden vorab festgelegte Prüfungen und begrenzte Verbesserungen umgesetzt.

### Zwischenstand der Mac-Abnahme

- [x] Vorab-Protokoll und verbindliche lokale Budgets in `13e33d1` festgelegt.
- [x] 29 automatisierte Prüfungen bestanden, einschließlich neuer Regressionen für Eigenschaftentext, Pause-Rate, Referenzauswahl, exakte Presets, Ressourcenablehnung, gleichmäßigen Zweitansichtsmaßstab und 150-%-Schrift.
- [x] Doppelspalt bei allen drei tatsächlich gewählten Rastern bestanden (Minimumfehler 6,72 / 3,39 / 3,39 %, Asymmetrie < 0,0001 %, Wandfeld null).
- [x] Preview-Fehler bei schrägem Eigenmodus gefunden (2,295 %); Mindestauflösung von 8 auf 10 Zellen/Wellenlänge erhöht, unveränderte 2-%-Grenze danach bestanden. Erstbefund bleibt in `quality-preflight-initial-failure.json` erhalten.
- [x] Engine `84c9ad9`: überprüfbare Dispersionsformeln und identische Rasterisierung mit begrenztem Polygon-Arbeitsbereich; Version dev3.
- [ ] Feinere Linsenkonvergenz, abschließende Ressourcenmessung und erneute native Bedienprüfung laufen noch.

- Native Bedienprüfung: Punkt-/Linienquelle, Materialecke, freies Polygon per Enter und beide Wandgriffe bedient; ungültige Linsenapertur abgewiesen und korrigiert; Projekt über nativen Speicherdialog nach `/tmp/wave-mac-native-objects.wave.json` gesichert.
- Zwei zusätzliche native Befunde behoben: Tab im Polygontext wechselt jetzt den Fokus, und ausgewählte Punkt-/Linsen-/Detektorgriffe liegen über den Trefferflächen überlappender Polygone. Wandkoordinaten heißen korrekt Left x / Bottom y. 31 Regressionstests bestehen.
- Feinere Linsenmessung abgeschlossen: Preview 7,75 % Fokusfehler / Verstärkung 10,78; benachbartes finanzierbares Custom-Raster 6,25 % / 11,28; Fokusverschiebung 1,5 % ≤ 5 %. Balanced/High Quality dieser Linse werden wegen 588,7 / 1322,2 MiB ausdrücklich abgewiesen.
