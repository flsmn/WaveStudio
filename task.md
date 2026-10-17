# Wave Studio – Fortschritt

Stand: 17. Oktober 2026. Maßgeblich sind DEVELOPMENT_PLAN.md, PRD.md und PROJECT_PLAN.md.

## Ausgangslage

- Zwei eigenständige Repositories; der Workspace selbst ist kein Git-Repository.
- Engine-Baseline: `5620234f539b1be3974f4dca122c16f272845271`.
- Vorhandene Engine-Änderungen: korrigierter Beispiel-Link im README, portabler Importpfad in test_comprehensive.py und neun gelöschte versionierte Cachedateien. Diese Änderungen werden erhalten; Cachebereinigung wird separat versioniert.
- Studio: Planungsdokumente vorhanden, bisher kein Commit und kein Anwendungscode.

## Arbeitspakete

- [x] B01: Python-3.12-Entwicklungsumgebung, Baseline, Entwicklungsanleitung.
- [x] E01: installierbare Engine, optionale Visualisierung, Wheel-/Editable-Prüfung.
- [x] B02: versionierter API-, Einheiten- und Lebenszyklusvertrag.
- [x] E02: kalibrierter Stencil, Stabilitätsprüfung, Parametergrenzen.
- [x] E03: explizites Gerät, Initialfeld, vollständiger Reset, kontrollierte Schritte.
- [x] E04: additive, räumlich und zeitlich skalierte Quellen.
- [x] E05: Materialreihenfolge, Rasterisierung, Dirichlet-Wände.
- [x] E06: zeitbezogene Dämpfung und getrennte Randzone.
- [x] E07: T01–T04 mit vorab festgelegten Toleranzen und numerischem Bericht.
- [x] S01: startbares PySide6-/PyQtGraph-Anwendungspaket.
- [x] S02: Qt-unabhängiges Projektmodell und Scene Compiler.
- [x] S03: einzelner Worker mit begrenzter Frame-Übergabe.
- [x] S04: Run/Pause/Step/Reset, Revisionen, Fehlerpfade.
- [ ] B03: Ressourcenmessungen und native Erstpakete auf drei Systemen.
- [ ] S05–S06 / M2: freier Editor, Undo/Redo, sichere Projektdateien.
- [ ] E08, S07–S09, B04 / M3: Messung, Referenzen, Export, Doppelspalt-Ablauf.
- [ ] S10–S13, E09, B05 / M4: vollständiger Umfang und Release-Abnahme.

## Prüfungen und Grenzen

Engine: 7 Kernprüfungen bestanden; historische Prüfung 9/9 Gruppen. Studio: 4 Kern-/Worker-Prüfungen bestanden. T01–T04 bestanden innerhalb der vorab eingefrorenen, begrenzten Referenztoleranzen; Rohwerte und bekannte Grenzen unter ../WaveSimulator2D/docs/. Wheel in sauberer temporärer Python-Umgebung außerhalb des Quellbaums mit CPU-Lauf und pip check geprüft. PySide6-Prototyp startet/schließt kontrolliert; Screenshot visuell geprüft. Nativer macOS-Prototyp gebaut; Paketstart noch zu prüfen. Physikalische Abnahme und Plattformnachweise werden getrennt vom Implementierungsstand geführt. Gemäß Development Plan beginnt der umfangreiche Editor-Ausbau erst nach E07/B03. Nicht verfügbare Zielplattformen werden ausdrücklich offen geführt.

## Arbeitsprotokoll

- 17.10.2026: Plan und Bestand geprüft; Umsetzung von M0a und frühem M1-Prototyp begonnen.

- 17.10.2026: Nutzer bestätigt: vorerst nur dieser Mac (M1/8 GB); Linux-/Windows-Tests folgen später. Diese Abnahmen bleiben offen, lokale Funktionsentwicklung wird fortgesetzt. MPS ist außerhalb der Sandbox verfügbar; T08 folgt.
