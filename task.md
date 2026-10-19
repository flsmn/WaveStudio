# Wave Studio – Fortschritt

Stand: 18. Oktober 2026. **Studio 0.1.0.dev13 / Engine 0.1.0.dev4**, Apple M1 / 8 GiB, macOS 27.0.1 arm64. Maßgeblich: [Development Plan 1.3](DEVELOPMENT_PLAN.md), [PRD](PRD.md) und [Projektplan](PROJECT_PLAN.md), mit ausdrücklich zurückgestellten Windows-/Linux-Abnahmen.

Der Nutzer hat Windows und Linux ausdrücklich auf später verschoben. Aktuelles Ziel ist der Abschluss der Mac-Version. Der Funktionsumfang ist implementiert; quantitative Physik, einzelne GUI-Reaktionszeiten, Zugänglichkeit und finale Mac-Auslieferung sind noch offen. Frühere Zwischenstände stehen in [DEVELOPMENT_HISTORY.md](docs/DEVELOPMENT_HISTORY.md).

## Aktueller Nachweisstand

- **76 Tests bestanden**, 11,88 s; regulärer dev13-Paketablauf aus `/private/tmp` bestanden, tatsächliche Importpfade im Bundle. [Regression](docs/native-dev13/regression-results.txt), [Paketablauf](docs/native-dev13/workflow-results.json), [Wheel-/Quell-/Bytecode-Abgleich und Hashes](docs/native-dev13/build-results.json). Historisches dev8 bleibt unter `dist/WaveStudio.app`, aktueller Kandidat unter `dist/ax-dev13/WaveStudio.app`.
- **MAC-01 vorangekommen, nicht abgeschlossen:** unabhängige Quellen- und Linsenreferenzen implementiert und kalibriert, historische Grenzwerte zentralisiert, T02 mit gemessenem Einfallswinkel diagnostiziert. Definierter Punktfall besteht; Linien-Fenster/Rand und komplexe Linsen-Rasterkonvergenz bestehen noch nicht. Keine pauschale quantitative Preset-Freigabe. [Methoden und vollständige Rohberichte](../WaveSimulator2D/docs/QUANTITATIVE_PROGRESS.md).
- **MAC-02 offen:** ruhiger dev11-Paketlauf etwa 25–26 Frames/s bei ausgeschaltetem Stromsparmodus, nicht als Geschwindigkeitsgewinn gegenüber dev8 mit Stromsparmodus an gewertet. Uninstrumentierter Ressourcenlauf scheitert mit 252,316 ms an unverändert 250 ms; Ereignis-/GC-Spur erklärt den Befund noch nicht. [Untersuchung](docs/PERFORMANCE_INVESTIGATION.md).
- **MAC-03 teilweise korrigiert:** physikalische Änderungen lösen keinen unnötigen Style-Neuaufbau aus; native Undo-/Redo-Eigenschaftsprüfung auch im regulären dev13-Paket bestanden. Der Listenersatz aus dev10–12 wurde nach fehlenden AX-Zeilen und Abstürzen mit Qt 6.8 verworfen; dev13 erhält die einfachere Zeilenabstimmung. Add am dev13-Paket bestätigt den verbleibenden Verlust des AX-Outlines; strukturelle/Style-Wechsel bleiben offen. Qt-/Paket-Pass ist keine AX-Freigabe. [Nachprüfung und Abhängigkeitsverdacht](docs/MAC_ACCESSIBILITY_FOLLOWUP.md).
- **MAC-04 vorbereitet:** statische arm64-/macOS-Basis und Lizenzinventur dokumentiert. Die statischen dev8-/dev13-Inventuren enthalten Qt-Bindings mit deklarierter Mindestversion 26.0; tatsächlich geprüft bleibt M1/macOS 27.0.1. [Mac-Auslieferung](docs/MAC_DISTRIBUTION.md). Windows/Linux bleiben zurückgestellt.
- Ausgangs-Commits dieser Arbeit: Studio `148619c`, Engine `053195f`; aktuelle Änderungen noch nicht committet. Numerischer Laufzeit-Solver und Engine-dev4-Wheel unverändert. Neue Prüfabhängigkeit SciPy wird vom Desktop-Build ausgeschlossen.

## Priorisierte offene Aufgaben für die Mac-Version

Die IDs und Prioritäten entsprechen [Development Plan, Abschnitt 3.4](DEVELOPMENT_PLAN.md#34-priorisierte-offene-aufgaben-für-die-mac-version). P1 zuerst für belastbare Ergebnisse/Bedienbarkeit, P2 Abschlussvorbereitung, P3 finale Freigabe/Auslieferung nach den erforderlichen Vorarbeiten.

- [ ] **P1 · MAC-01 — Quantitative Physik und Qualitätsstufen absichern** (E07/S10/S12, O02/O04, T01–T04/Q04): passende unabhängige Quellen-/Spalt-/Linsenreferenzen und neue versionierte, begründete Grenzen festlegen; dritte gezielte Rasterstufe für unklare Spalt-/Linsenfälle sowie Zeit-, Rand-/Fenster-, Geometrie- und Auswertungsunsicherheit prüfen. Die umgesetzte T02-Diagnose und zentrale v1-Grenzwertdatei nutzen, Phasenforderung aus der Messaufgabe ableiten und Balanced-/High-Quality-Fokus gesondert nachweisen. **Fertig, wenn** Genauigkeitsbereich, Referenzen, Unsicherheiten und tatsächlich geprüfte Presets nachvollziehbar freigegeben sind. Ungetestete/abgewiesene Raster und historische v1-Berichte bleiben eindeutig gekennzeichnet.
- [ ] **P1 · MAC-02 — GUI-Unterbrechungen eingrenzen und beheben** (S03/S12/B03, T05/T07/Q02–Q03): die dev8-/dev11-Befunde 500,86/252,316 ms bei 250-ms-Grenze mit produktivem Qt-Abfragetakt und protokolliertem Aktivitäts-/Stromsparzustand untersuchen. **Fertig, wenn** die gezielte Korrektur und die betroffenen Ressourcen-/Bedienbudgets am passenden Paket nachgewiesen sind; 512² und Großraster getrennt ausweisen und Fehlberichte erhalten. Die historische FPS-Differenz bleibt ungeklärt, soweit keine reproduzierbare Erklärung vorliegt; kein pauschales 18–20-FPS-Ziel.
- [ ] **P2 · MAC-03 — Zugänglichkeit und native Tastaturbedienung abschließen** (S05/S13, T05/T06/F16): verbleibenden AX-Verlust nach strukturellen/Style-Änderungen, VoiceOver-/Fokusverhalten und native Command-Z-/Redo-Wege prüfen; verbleibende menschliche Bedienabnahme am finalen Kandidaten dokumentieren. **Fertig, wenn** die vereinbarten Bedienwege einschließlich Themes/skaliertem Text nachgewiesen sind; Qt-, agentenbediente native und menschliche Nachweise getrennt führen. Sichtbare Liste und Qt-Fokus belegen allein keine AX-Freigabe.
- [ ] **P2 · MAC-04 — Mac-Auslieferungsumfang und Restaufwand festlegen** (B03/B05, O03/O07): Mindest-macOS/Architektur und fremde Testinstallation, Verteilungsmodell, erforderliche Signierung/Notarisierung und Aktualisierungsweg klären; Abhängigkeiten/Lizenzhinweise prüfen, Restaufwand mit Voraussetzungen schätzen. **Fertig, wenn** Mac-Matrix, Entscheidungen und Aufwandsspannen dokumentiert sind. Vorbereitung unabhängig möglich; belastbare Schätzung nach Eingrenzung von MAC-01/02. Aktuell nur M1/macOS 27.0.1 arm64 geprüft; manueller Paketaustausch ist zulässig, automatischer Updater keine Pflicht.
- [ ] **P3 · MAC-05 — Finales Versionspaar und gemeinsame Mac-Abnahme erstellen** (E09/B04/B05/S13; nach MAC-01–04): Engine und Studio final versionieren, exakte Wheels/Hashes/Commits zuordnen, betroffene T01–T08 prüfen und F01–F18/Q01–Q06 mit Nachweisen, Grenzen oder zurückgestellten Plattformteilen verknüpfen. Hilfe, Preset-Aussagen, Änderungs-/Release-Notizen und Installationshinweise abgleichen. **Fertig, wenn** die Mac-Abnahmeübersicht zum finalen Stand vollständig ist und keine offene Abweichung dem beanspruchten Umfang widerspricht; alte dev3/dev4-Pässe ersetzen keinen aktuellen Nachweis.
- [ ] **P3 · MAC-06 — Mac-Paket auf sauberer Installation abnehmen und zur Verteilung vorbereiten** (B05/T09/Q01; nach MAC-04/05): aus dem finalen Versionspaar bauen, gegebenenfalls für öffentliche Verteilung signieren/notarisieren, auf fremdem sauberem Mac ohne Nutzer-Python und ohne Netzwerk testen. **Fertig, wenn** das tatsächliche Artefakt samt Hash/OS/Hardware und Start/Run/Pause, Speichern/Laden, PNG/CSV sowie Installationshinweisen dokumentiert ist. Öffentliche Veröffentlichung erst nach geklärtem Verteilungsumfang.

**Zurückgestellt:** Windows-/Linux-Pakete und native Offline-/CPU-/schwächere Hardware-Abnahmen sowie deren Systemmatrix. Sie blockieren die aktuelle Mac-Arbeit nicht. CUDA bleibt ohne NVIDIA-Hardwaretest außerhalb der Unterstützung.

**Ergänzend offen:** vollständiger Alt/Neu-Vergleich für Quellen, Dämpfung und Spalt/Linse; keine eigenständige PRD-Pflicht und kein Ersatz für MAC-01. Kalibrierte Energie-/Prozesszuordnung fehlt ebenfalls; zusätzliche privilegierte Messungen sind nicht eingeplant. Keine neuen Produktfunktionen für 0.1 aus den späteren PRD-Optionen ableiten.

## Implementierung

Die Haken bezeichnen vorhandene Implementierung und die jeweils dokumentierten Prüfungen. Finale Physik-/Qualitäts-/Release-Freigaben bleiben wie unter MAC-01–06 angegeben offen.

- [x] B01/E01/B02: getrennte Repositories, installierbare Engine und Studio, exakte Versionskopplung, Wheel-Integration, Einheiten-/Puffer-/Lebenszyklusvertrag.
- [x] E02–E07: kalibrierter Neunpunkt-Stencil, c0=1, additive Punkt-/Linienquellen, feste Referenzgeometrie, Materialreihenfolge, Dirichlet-Wände, getrennte zeitbezogene Material-/Randdämpfung und reproduzierbare T01–T04.
- [x] S01–S06: Qt-Oberfläche, ein Solver-Worker, Run/Pause/Step/Reset, Revisionen, freie Geometrie, numerische Eigenschaften, Griffe, Reihenfolge, Copy/Delete, Undo/Redo, validiertes atomisches Projekt-JSON und begrenzte Wiederherstellung.
- [x] E08/S07–S09: passive Punkt-/Liniendetektoren, bilineares Feldquadrat pro Zeitschritt, endliche Messfenster, eigener Messzustand, Live-Intensität, vier Referenzen samt Herkunft, PNG und Rohwert-CSV.
- [x] S10/S11: parametrisierte bikonvexe Linse mit fester Kontur, zweite Ansicht desselben Laufs mit quadratischen Einheiten und gemeinsamem Maßstab/Zentrum, Abstand und Winkel.
- [x] S12/S13: qualitätsbezogene Rasterwahl und Expertenwerte, CPU/MPS/Auto, unabhängiger sparsamer/höherer Rechenmodus, drei Beispiele, Hilfe, native Menüs, Tastaturpfade, helle/dunkle Themes und 100/125/150-%-Text.

## Historische Mac-Qualitätsabnahme (dev3 / v1-Grenzen)

Vorab eingefrorenes Protokoll: `docs/MAC_ACCEPTANCE_PLAN.md`, Commit `13e33d1`. Vollständige Auswertung: `docs/MAC_ACCEPTANCE.md`; Rohwerte stehen daneben als JSON.

- [x] T01–T04 mit unveränderten Grenzwerten auf dev3 wiederholt und bestanden (`../WaveSimulator2D/docs/physical-results-dev3.json`).
- [x] Dispersionsabschätzung gegen tatsächliche Eigenmoden bei axialnaher/diagonaler Ausbreitung geprüft: Frequenzabweichung ≤0,1 %, Geschwindigkeitsfehler ≤2 %. Langweg von 64 Wellenlängen und gedrehte dünne Struktur in der Rasterwahl geprüft. Der Langweg-Phasenwert ist eine verifizierte homogene Abschätzung, kein behaupteter Vollgebiet-Ausbreitungslauf.
- [x] Preview / Balanced / High Quality berücksichtigen mindestens 10 / 12 / 20 Zellen je kürzester Materialwellenlänge, 2 / 4 / 6 je erfasster Struktur und maximal π / π/2 / π/4 geschätzte Phasendrift. Geometrie und Messdefinitionen bleiben erhalten.
- [x] Tatsächlich gewählte Doppelspaltraster 369×328 / 576×512 / 864×768 bestanden: Minimumfehler 5,06 / 3,39 / 3,39 %, Asymmetrie <0,0001 %, Wandfeld null.
- [x] Tatsächliches Linsen-Preview-Raster 2845×1707 und benachbartes Custom-Raster 3200×1920 bestanden: Fokusfehler 6,00 / 6,25 %, Verstärkung 11,37 / 11,28, Fokusverschiebung 0,25 % ≤5 %.
- [x] Unter den dev3-Standardgrenzen wurden Linsen-Balanced/High Quality wegen 588,7 / 1322,2 MiB klar abgewiesen; High überschreitet zusätzlich die Achsengrenze. Diese historischen Fälle sind ressourcenbedingt abgewiesen und ausdrücklich nicht physikalisch bestanden. Dev4 erlaubt höhere explizite Projektbudgets; siehe Nachprüfung unten.
- [x] Fehlbefunde erhalten: Preview-Eigenmodus 2,295 % Geschwindigkeitsfehler und zunächst 20,22 % Doppelspalt-Asymmetrie. Mindestauflösung erhöht; die Rasterwahl meidet Wandkanten auf Zellmittelpunkten. Halb-offene Rasterregel und alle Toleranzen unverändert. Prüfungen gleichen die veröffentlichten Messraster mit der aktuellen Auswahl ab.

## Mac-Bedienungsabnahme

- [x] Agent bedient das native Paket mit Maus, nativen Menüs und Tastatur: Run/Pause/exakter Step/Reset, Änderungen ohne Autostart, alle Objektarten, Quellen-/Polygon-/Wand-/Linsengriffe, laufende passive Detektoren einschließlich Linie/Endpunkt, zwei Referenzen und Auswahl der älteren Referenz, Projekt speichern/wiederöffnen, ungültige Datei ohne Zustandsverlust, native CSV-/PNG-Exporte.
- [x] Abstand und rechter Winkel bei zwei Maßstäben nativ geprüft: 5,03614 / 4,96992 Referenzlängen bei gerundeten Mauspositionen und jeweils 90,000°. Programmatische Qt-Prüfung mit exakten Koordinaten liefert jeweils 5,00000 / 90,000°.
- [x] Zweite Ansicht, helle/dunkle Darstellung sowie 100/125/150-%-Schrift nativ sichtbar geprüft. Die Mindestgröße 980×660, beide Themes/alle Schriftstufen und lange Zähler werden zusätzlich in Qt automatisiert geprüft. Scrollbare Dialoge/Seitenleiste und umbrechende Werkzeugleisten halten Bedienelemente erreichbar.
- [x] **43 Tests im dev3-Abnahmestand bestanden**: 15 Engine-, 28 Studio-Prüfungen. Zusätzlich echter Qt-/Worker-Integrationsablauf, CPU/MPS-Vergleich und Paketablauf. Materialreihenfolge, Copy/Delete, Tastaturkürzel und Wiederherstellungsbesitz/-bereinigung sind programmatisch abgedeckt. Dies wird nicht als menschliche Abnahme bezeichnet.
- [x] Behoben: veraltete Eigenschaften und Pausenraten, verlorene Referenzauswahl/Splitteraufteilung, verzerrter Zweitansichtsmaßstab, starre Schriftgrößen, Tab-Falle im Polygontext, verdeckte Punkt-/Linsengriffe, falsche Wandkoordinaten-Bezeichnung, alte Wiederherstellung nach Speichern/Verwerfen. Szenenänderungen erhalten jetzt Listenzeilen und Tastaturfokus; die Qt-Regression bestätigt beides.
- [x] Abschließende native Sichtkontrolle: Achsen, Einheiten und Skalen im hellen Theme bei 150 % lesbar; aktuelle Referenzkurve/Legende zusätzlich im Paketablauf geprüft. Native Bearbeitung und Undo-Menü bestätigen aktualisierte Eigenschaften und sichtbare Listenzeile.
- [ ] Restbefund Mac-Zugänglichkeitsbrücke: Nach Bearbeitung fehlt die weiterhin sichtbare Szenenliste im Accessibility-Snapshot der Automatisierung. Zeilenidentität und Tastaturfokus bestehen im Qt-Test; vollständige VoiceOver-/AX-Abnahme und native Command-Z-Bestätigung bleiben offen. Dies wird nicht als behoben oder bestanden geführt.

## Historische Ressourcen- und Paketabnahme (dev3)

- [x] Vorab festgelegte 512²-Budgets auf CPU/MPS bestanden: ≥20 angezeigte Frames/s bei einer/zwei Ansichten, Pause <100 ms, RSS ≤1 GiB, stationärer Leerlauf/Pause ≤0,10 CPU-Sekunden je Sekunde, pausiert null Schritte/Frames. Sparsam ≤240 Schritte/s, Anzeige ≤30/s; Moduswechsel erhält Lauf/Raster/Messungen.
- [x] Großes zulässiges Linsenraster: ein Schritt pro Befehlsgrenze; Pause etwa 57 ms, danach konstante Schrittzahl (`docs/large-grid-results.json`). Das 512²-Leistungsbudget gilt nicht pauschal für jedes große Raster.
- [x] Zusätzlich zwei verspätete Pause-Stichproben erhalten (115,5 ms CPU; 103,8 ms MPS). Fertige Profile werden nur bei sichtbaren Änderungen neu gezeichnet; MPS fragt Befehle jetzt nach jedem Schritt ab. Die maximale sparsame Rate bleibt 240 Schritte/s. Danach alle fünf Pause-Vorgänge je Backend bestanden: maximal 8,82 ms CPU / 36,37 ms MPS; angezeigte Bildraten 22–27/s einschließlich Performance, RSS maximal 286 MiB.
- [x] Direkte systemweite GPU-Zähler ausgelesen. Eine kalibrierte Energie-/Prozesszuordnung liegt nicht vor: powermetrics verlangt Superuser-Zugriff. Kein zusätzlicher privilegierter Eingriff dafür.
- [x] Finaler Build dieses dev3-Zwischenstands aus den unveränderlichen Wheels (`3533c86`), vollständiger Pakettest aus `/private/tmp` und nativer MPS-PNG-Export bestanden; Importpfade liegen im Bundle, Wheel-Inhalte stimmen mit Quellen überein, archivierte Hashes in `docs/build-results-dev3.json`, Paketablauf in `docs/native-results-dev3.json`. Ressourcenmessung enthält die damaligen Laufzeitkorrekturen; danach wurde ausschließlich das statische Footer-Layout angepasst. Der aktuelle dev8-Nachlauf ist separat aufgeführt.

## Zurückgestellte Plattformen und Geltungsgrenzen

- [ ] Windows/Linux: native Pakete, Funktions-/Offline-Abnahme und schwächere Hardware – ausdrücklich vom Nutzer zurückgestellt.
- Mac-Mindestbasis, sauberer fremder Mac und Auslieferung gehören zur aktuellen Restarbeit MAC-04–06. Der plattformübergreifende E09/B05-Gesamtabschluss bleibt wegen der zurückgestellten Windows-/Linux-Abnahmen offen.
- Beliebige Interfaces, konkave Engstellen und andere Linsenparameter brauchen eigene Konvergenzprüfungen. Die skalare 2D-Linse ist keine Zusage für Präzisionsoptik.

## Historische Git-Stände der dev3-Abnahme

- Engine: `84c9ad9` Dispersionsformeln und identische begrenzte Polygonrasterisierung; `76e2423` wiederholte physikalische Referenzen.
- Studio: `13e33d1` Vorabkriterien; `0cc313a` qualitätsbezogene Raster und Mac-Bedienkorrekturen; `ae6d971` Griffe/Tab; `4380c53` Wiederherstellung/Tastatur/Messwerkzeuge; `11b2f1e` Listenfokus, Kontrast und eindeutige Qualitätsraster; `8c199f8` Einheitenbeschriftungen; `0017e00` Profil-Rendering und kurze MPS-Befehlsgrenzen; `3533c86` umbrechender Status bei großer Schrift. Abschlussnachweise und verbleibender AX-Befund sind im anschließenden Dokumentations-Commit festgehalten.

## Konfigurierbare Ressourcenbudgets / Balanced (dev4)

- [x] Speicherbudget und maximale Achsenlänge pro Projekt einstellbar, gespeichert und vor Rasterallokation geprüft; Vorgaben 512 MiB / 4096 bleiben für bestehende Dateien erhalten.
- [x] Engine übernimmt explizites Achsenbudget bis in den Solver; reine Budgetänderung erhält Lauf/Messungen. Run/Fortsetzen verwendet vorbereitete Szene.
- [x] 59 Regressionstests bestanden, einschließlich Altdateien, unzulässiger Budgets, Achsen oberhalb 4096, identischer Numerik und unverändertem Vollraster bei pausierter Vorschau.
- [x] Zwei UI-Aussetzer-Läufe erhalten: zunächst 395 ms, mit reiner Render-Verkleinerung bis 1177 ms. Live-Übertragung großer Felder auf höchstens 1024 Zellen/Achse begrenzt und sichtbar gekennzeichnet; Pause/Step liefert volles Raster. Reset/Schließen gibt ungenutzten MPS-Cache frei. Die vorab festgelegten Grenzwerte bleiben unverändert.
- [x] Balanced auf MPS mit 768 MiB bestanden: 3780×2268, 588,7 MiB Rechenpuffer, RSS-Spitze 1000 MiB, MPS-Treiber separat 1117,1 MiB; 18–20 Frames/s, sechs Pause-Vorgänge maximal 137,38 ms, GUI-Heartbeat maximal 135,08 ms. Reset bestätigt nach 25,49 ms, aktives Schließen 284,86 ms. Null MPS-Tensorbelegung nach Reset; 69,1 MiB Backend-Treiberspeicher verbleibt. Siehe `docs/BALANCED_MAC_ACCEPTANCE.md`.
- [x] Reset-Messung korrigiert: Treiberbelegung ist nicht gleich lebende Solver-Tensoren; explizite Worker-Bestätigung statt unbegründeter Rückkehr-zum-Startwert-Annahme. Fehlbericht erhalten, Zeitgrenzen unverändert.
- [ ] Physikalische Fokusabnahme für Balanced/High Quality weiterhin offen; diese Nachprüfung betrifft Ressourcen und Bedienbarkeit.
- [x] Natives dev4-Paket aus exakten Wheels gebaut; Paketablauf außerhalb der Quellen bestanden. Ressourcenfelder nativ bedient: 512-MiB-Ablehnung, 768-MiB-Freigabe, Achsenbudget 8192/zurück 4096, Balanced/MPS bestätigt, zwei Ansichten, Performance, Pause/Step 543→544, Fortsetzen bis 709 und Reset auf Ready/0. Native Projekt-/PNG-Dateien sichern Budgets, MPS und volles Pausenraster (`docs/balanced-native-results.json`).
- [x] Einschränkung festgehalten: Native HUD-Stichproben während der UI-Automatisierung zeigten 5–8 Frames/s, der separate Ressourcenlauf 18–20/s. Keine feste Bildrate für dieses große Raster zugesagt; High Quality bleibt auf dem Mac ungetestet.

- Dev4-Implementierung committet: Studio `8b8e23e`, Engine `10f7ce9`; Abnahmenachweise in Studio `48e524c`. Der native dev4-Build ist geprüft; seine Berichte bleiben separat archiviert.

## Paket-/Messlauf-FPS untersuchen (18. Oktober 2026)

- [x] Gemeinsamer Diagnose-Einstieg für Quellen und Paket: Balanced, 1320×860/DPR2, echter 33-ms-Qt-Abfragetakt ohne schnelle Hilfstimer, getrennte Solver-/Transfer-/Renderzeiten sowie Aktivitäts-, QoS-, Stromspar-/Temperaturzustand. Frühere Hilfstimer-Proben ausdrücklich als explorativ markiert.
- [x] Fehler der FPS-Anzeige behoben: Initialisierung und Pausenzeit aus dem Messfenster ausgeschlossen, Neustart bei Fortsetzen, doppelte Ansichts-Snapshots nicht gezählt; „Measuring rate…“ bis ein gültiges Intervall vorliegt.
- [x] Vergleich bei fest aufgebauten Ansichten und aktivierter Accessibility: natives Paket ohne/mit Scheduling-Hinweisen 15,45 / 16,25 Frames/s; historische Pump-Schleife 15,45/s. Beobachtetes natives Paket beim Fortsetzen der Arbeit 15,70/s, HUD 16–18/s. Stromsparmodus an, Temperaturstatus nominal. Der etwa 5-%-Unterschied ist kein belegter Faktor-zwei-Gewinn und kein Nachweis für App Nap als Hauptursache. Rohdaten und verworfene Proben bleiben erhalten.
- [x] macOS-Arbeit mit NSProcessInfo-Aktivität und High-Worker-QoS gekennzeichnet; Pause, Reset, Fehler und Schließen räumen auf und stellen Auto wieder her. Idle-Systemschlaf bleibt erlaubt; keine globalen Energieeinstellungen geändert.
- [x] **66 Tests bestanden** (16,24 s), pip-Abhängigkeiten konsistent. Finales dev8-Paket aus exakten Wheels; vollständiger Paketablauf aus `/private/tmp` bestanden. Normales natives Fenster: Messbeginn/Resume „Measuring rate…“, pausiert null Raten und Step 560→561 bestätigt.
- [x] Ressourcen-Nachlauf dokumentiert: RSS 949,8 MiB, MPS-Treiber separat 1117,1 MiB, sechs Pausen maximal 99,39 ms, Reset 21,52 ms, aktives Schließen 129,41 ms und anschließend null MPS-Tensorbelegung.
- [ ] **GUI-Zeitkriterium im dev8-Nachlauf nicht bestanden:** einmalig 500,86 ms im ersten Ansichtsintervall bei unverändertem Grenzwert 250 ms. Zwei spätere Intervalle 129,22/138,56 ms. Fehlbericht erhalten; kein bestandener Gesamt-Ressourcennachweis für dev8 behauptet.
- [ ] **Gesamte historische Differenz 5–8 gegenüber 18–20 weiterhin nicht eindeutig erklärt.** Bestätigt sind die falsche alte HUD-Zeitbasis und nicht vergleichbare Messkontexte. Quellenlauf ebenfalls 12,68/s im Mittel mit kurzem HUD 6/s und 1024-ms-Abfrageunterbrechung. Eine dauerhafte Paketbremse oder alleinige Ursache App Nap/Accessibility ist nicht nachgewiesen. Die neue Diagnose erlaubt eine belastbare Wiederaufnahme bei reproduzierbarem Befund; 18–20 FPS im normalen Paket werden nicht als erreicht abgenommen.
- [x] Größere Änderungen committet: Diagnose `a954c8b`, Scheduling `40587b4`, Ratenkorrektur `b1c4b6c`, feste Vergleichskonfiguration `10e1d50`; Abschlussnachweise in `e4a3758`. Quellen, Paket und offene Befunde: `docs/PERFORMANCE_INVESTIGATION.md`; weitere Arbeit unter MAC-02.

## Prüfung der physikalischen Grenzwerte (18. Oktober 2026)

- [x] Ursprung, Prüfcode und Begründung aller v1-Grenzen geprüft; 15/20 % sind vorab eingefrorene grobe Demonstrationsgrenzen, keine aus einer Fehlerbilanz abgeleitete quantitative Freigabe. Historische PASS-Ergebnisse bleiben erhalten und sind entsprechend eingeordnet.
- [x] Konkrete Schwächen dokumentiert: Zweirasterdifferenz statt absoluter Quellenfehler, Näherungsreferenzen für Spalt/Linse, unteraufgelöste grobe Linse, Fokusauswertung in 0,25-%-Schritten, fehlende getrennte Zeit-/Rand-/Fensterfehler und mehrfach fest codierte Grenzen. Vorhandene dev4-Messwerte gegen vorgeschlagene strengere Zielzahlen ausgewertet; keine neue Genauigkeit behauptet.
- [x] Bericht und maschinenlesbare Gegenprüfung: `../WaveSimulator2D/docs/TOLERANCE_REVIEW.md`, `tolerance-review-results.json`; erneut gemessene dev4-Eingangsdaten separat erhalten. Solver, aktive Grenzwerte und Presets unverändert.
- [ ] Quantitative Physikabnahme: versionierte strengere Ziele, passende unabhängige Referenzen und eine dritte gezielte Rasterstufe für die unklaren Spalt-/Linsenfälle; beobachtete Konvergenz sowie Zeit-/Rand-/Messunsicherheit prüfen. Vorgeschlagene Ziele von 2 % Positions-/Amplitudenabweichung und ≤1 % numerischer Fokusunsicherheit sind noch nicht validiert oder aktiviert.
- [x] Historische v1-Grenzwerte zentralisiert; neue versionierte Quellen-/Linsen-Teilprotokolle umgesetzt (siehe aktuellen Nachweisstand).
- [ ] Kohärente Phasenanforderung aus der Messaufgabe ableiten. Bestehende High-Quality-/Balanced-Bezeichnungen und Ressourcenfreigaben sind keine quantitative Genauigkeitszusage; Balanced-/High-Quality-Fokusnachweise bleiben offen.

## Fehlermaße und ursprüngliche Engine vergleichen (18. Oktober 2026)

- [x] Tatsächliche Fehlerformeln, Referenznenner und Messverfahren dokumentiert: `../WaveSimulator2D/docs/ERROR_METRICS.md`. Absolute Winkel-/Wandabweichung, relative Referenzabweichung und Zweirasterdifferenz klar unterschieden.
- [x] Reproduzierbarer CPU-Vergleich mit dem ersten PyTorch-Fork `40f6c78`: Geschwindigkeitsskalenfehler rund 44 % gegenüber 0,32–0,47 % aktuell. Nach analytischer Zeitkalibrierung stimmen homogene quellenfreie Felder nach 180 Schritten mit maximal 0,000127 % relativer L2-Abweichung überein. Dies ist kein allgemeiner Physikfehlervergleich. Skript und Rohdaten im Engine-Repository erhalten.
- [x] Herkunft zur früheren CuPy-Fassung im Code geprüft; kein nativer CuPy/CUDA-Lauf auf diesem Mac behauptet. Solver und aktive Grenzwerte unverändert.
- [ ] Ergänzende Untersuchung: Vollständiger Alt/Neu-Vergleich für Quellen, Dämpfung und Spalt/Linse fehlt; keine eigenständige PRD-Pflicht. Die T02-Winkelreferenz gehört zu MAC-01 und muss für strengere quantitative Abnahme den tatsächlich gemessenen Einfallswinkel berücksichtigen: 1,037592° statt 0,645968° Abweichung bei den vorhandenen Daten; keine rückwirkende Änderung des v1-Berichts.


## Quantitative Teilprotokolle / native Nachprüfung (18. Oktober 2026)

- [x] Unabhängige Hankel-Punkt-/Linienreferenz, Normierung/Phase und Quadratur geprüft; drei Engine-Raster plus Fenster-/Zeit-/Gebiets-/Randvarianten. Definierter Punktfall: max. komplexer Fehler 0,6222 %, Amplitudenfehler 0,1930 %. Kein allgemeiner Preset-Pass.
- [ ] Linienfall: direkte Feldabweichung 0,7503 %, spätes Fenster 0,9809 % und breiterer Rand 0,6032 % überschreiten jeweils 0,5-%-Pilotgrenze. Messdefinition/Referenz weiter qualifizieren.
- [x] Unabhängige Lippmann-Schwinger-Referenz implementiert; analytische Zylinderkalibrierung, singuläre Zellintegration, FFT-Matrixwirkung und Quadratur separat geprüft. Feinste Zylinderabweichung L2 0,1667 %.
- [ ] Linsenreferenz: drei Raster 0,05/0,025/0,0125; letzte komplexe Profiländerung 0,9749 % >0,5 %. Fokusverschiebung 0,1261 % besteht Einzelkriterium, qualifiziert aber nicht das Gesamtprofil. Unabhängige endliche Spaltreferenz und dritte Engine-Rasterstufe weiterhin offen.
- [x] T02 erneut gemessen: historische Nominalmetrik 0,645968°, mit gemessenem Einfall 1,037592°. Beide Werte erhalten, keine quantitative Winkelabnahme.
- [x] Native dev12-Regression/Paketablauf bestanden; AX-Fehler bei Add ausdrücklich erhalten. Zwischenkandidaten dev9–12 nicht als vollständige Accessibility-Freigabe gewertet. Qt-6.8-Vergleich auch ohne Listenersatz nativ abgestürzt und verworfen; Hauptumgebung bleibt Qt 6.12.0.
- [x] Neue Ereignis-/GC-Diagnose ohne zusätzliche Abfragetimer, getrennte Rohberichte und Auslieferungsinventur ergänzt. Keine Grenzwerte gelockert und keine globale GC-/Energiepolitik geändert.

- [x] Regulärer dev13-Kandidat mit Qt 6.12.0: 76 Tests, vollständiger Paketablauf, unverändertes Engine-Wheel und eingebetteter Bytecode geprüft; SciPy ausgeschlossen. Native Eigenschaftsänderung/Undo/Redo erhält AX-Liste und Fokus. Add verliert das AX-Outline weiterhin; keine vollständige Accessibility-Abnahme. Aktuelle Berichte unter `docs/native-dev13/`.
