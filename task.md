# Wave Studio – Fortschritt

Stand: 18. Oktober 2026. **Studio / Engine 0.1.0.dev4**, Apple M1 / 8 GiB, macOS 27.0.1 arm64. Maßgeblich bleiben DEVELOPMENT_PLAN.md, PRD.md und PROJECT_PLAN.md.

Der Nutzer hat Windows und Linux ausdrücklich auf später verschoben. Dieser Tracker trennt die lokale Mac-Abnahme von einem stabilen plattformübergreifenden Release. Frühere Zwischenstände und Ausgangsentscheidungen stehen in `docs/DEVELOPMENT_HISTORY.md`.

## Implementierung

- [x] B01/E01/B02: getrennte Repositories, installierbare Engine und Studio, exakte Versionskopplung, Wheel-Integration, Einheiten-/Puffer-/Lebenszyklusvertrag.
- [x] E02–E07: kalibrierter Neunpunkt-Stencil, c0=1, additive Punkt-/Linienquellen, feste Referenzgeometrie, Materialreihenfolge, Dirichlet-Wände, getrennte zeitbezogene Material-/Randdämpfung und reproduzierbare T01–T04.
- [x] S01–S06: Qt-Oberfläche, ein Solver-Worker, Run/Pause/Step/Reset, Revisionen, freie Geometrie, numerische Eigenschaften, Griffe, Reihenfolge, Copy/Delete, Undo/Redo, validiertes atomisches Projekt-JSON und begrenzte Wiederherstellung.
- [x] E08/S07–S09: passive Punkt-/Liniendetektoren, bilineares Feldquadrat pro Zeitschritt, endliche Messfenster, eigener Messzustand, Live-Intensität, vier Referenzen samt Herkunft, PNG und Rohwert-CSV.
- [x] S10/S11: parametrisierte bikonvexe Linse mit fester Kontur, zweite Ansicht desselben Laufs mit quadratischen Einheiten und gemeinsamem Maßstab/Zentrum, Abstand und Winkel.
- [x] S12/S13: qualitätsbezogene Rasterwahl und Expertenwerte, CPU/MPS/Auto, unabhängiger sparsamer/höherer Rechenmodus, drei Beispiele, Hilfe, native Menüs, Tastaturpfade, helle/dunkle Themes und 100/125/150-%-Text.

## Mac-Qualitätsabnahme

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

## Ressourcen und Paket

- [x] Vorab festgelegte 512²-Budgets auf CPU/MPS bestanden: ≥20 angezeigte Frames/s bei einer/zwei Ansichten, Pause <100 ms, RSS ≤1 GiB, stationärer Leerlauf/Pause ≤0,10 CPU-Sekunden je Sekunde, pausiert null Schritte/Frames. Sparsam ≤240 Schritte/s, Anzeige ≤30/s; Moduswechsel erhält Lauf/Raster/Messungen.
- [x] Großes zulässiges Linsenraster: ein Schritt pro Befehlsgrenze; Pause etwa 57 ms, danach konstante Schrittzahl (`docs/large-grid-results.json`). Das 512²-Leistungsbudget gilt nicht pauschal für jedes große Raster.
- [x] Zusätzlich zwei verspätete Pause-Stichproben erhalten (115,5 ms CPU; 103,8 ms MPS). Fertige Profile werden nur bei sichtbaren Änderungen neu gezeichnet; MPS fragt Befehle jetzt nach jedem Schritt ab. Die maximale sparsame Rate bleibt 240 Schritte/s. Danach alle fünf Pause-Vorgänge je Backend bestanden: maximal 8,82 ms CPU / 36,37 ms MPS; angezeigte Bildraten 22–27/s einschließlich Performance, RSS maximal 286 MiB.
- [x] Direkte systemweite GPU-Zähler ausgelesen. Eine kalibrierte Energie-/Prozesszuordnung liegt nicht vor: powermetrics verlangt Superuser-Zugriff. Kein zusätzlicher privilegierter Eingriff dafür.
- [x] Finaler Build aus den unveränderlichen dev3-Wheels (`3533c86`), vollständiger Pakettest aus `/private/tmp` und nativer MPS-PNG-Export bestanden; Importpfade liegen im Bundle, Wheel-Inhalte stimmen mit Quellen überein, Hashes in `docs/build-results.json`. Ressourcenmessung enthält alle Laufzeitkorrekturen; danach wurde ausschließlich das statische Footer-Layout angepasst.

## Später / außerhalb dieser lokalen Abnahme

- [ ] Windows/Linux: native Pakete, Funktions-/Offline-Abnahme und schwächere Hardware – ausdrücklich vom Nutzer zurückgestellt.
- [ ] E09/B05: Mindestbetriebssysteme/Architekturen, sauberer fremder Mac, öffentliche Signierung/Notarisierung, Verteilung/Updates und stabiles plattformübergreifendes Release.
- Beliebige Interfaces, konkave Engstellen und andere Linsenparameter brauchen eigene Konvergenzprüfungen. Die skalare 2D-Linse ist keine Zusage für Präzisionsoptik.

## Git

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

- Dev4-Implementierung committet: Studio `8b8e23e`, Engine `10f7ce9`. Der native dev4-Build ist geprüft; die Nachweise werden im anschließenden Abschluss-Commit gesichert.
