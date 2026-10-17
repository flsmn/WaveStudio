# Wave Studio – Fortschritt

Stand: 17. Oktober 2026. Maßgeblich sind DEVELOPMENT_PLAN.md, PRD.md und PROJECT_PLAN.md.

## Ausgangslage

- Zwei eigenständige Repositories; der Workspace selbst ist kein Git-Repository.
- Engine-Baseline: `5620234f539b1be3974f4dca122c16f272845271`.
- Vorhandene Engine-Änderungen: korrigierter Beispiel-Link im README, portabler Importpfad in test_comprehensive.py und neun gelöschte versionierte Cachedateien. Diese Änderungen werden erhalten; Cachebereinigung wird separat versioniert.
- Studio: Planungsdokumente vorhanden, bisher kein Commit und kein Anwendungscode.

## Arbeitspakete

- [ ] B01: Python-3.12-Entwicklungsumgebung, Baseline, Entwicklungsanleitung.
- [ ] E01: installierbare Engine, optionale Visualisierung, Wheel-/Editable-Prüfung.
- [ ] B02: versionierter API-, Einheiten- und Lebenszyklusvertrag.
- [ ] E02: kalibrierter Stencil, Stabilitätsprüfung, Parametergrenzen.
- [ ] E03: explizites Gerät, Initialfeld, vollständiger Reset, kontrollierte Schritte.
- [ ] E04: additive, räumlich und zeitlich skalierte Quellen.
- [ ] E05: Materialreihenfolge, Rasterisierung, Dirichlet-Wände.
- [ ] E06: zeitbezogene Dämpfung und getrennte Randzone.
- [ ] E07: T01–T04 mit vorab festgelegten Toleranzen und numerischem Bericht.
- [ ] S01: startbares PySide6-/PyQtGraph-Anwendungspaket.
- [ ] S02: Qt-unabhängiges Projektmodell und Scene Compiler.
- [ ] S03: einzelner Worker mit begrenzter Frame-Übergabe.
- [ ] S04: Run/Pause/Step/Reset, Revisionen, Fehlerpfade.
- [ ] B03: Ressourcenmessungen und native Erstpakete auf drei Systemen.
- [ ] S05–S06 / M2: freier Editor, Undo/Redo, sichere Projektdateien.
- [ ] E08, S07–S09, B04 / M3: Messung, Referenzen, Export, Doppelspalt-Ablauf.
- [ ] S10–S13, E09, B05 / M4: vollständiger Umfang und Release-Abnahme.

## Prüfungen und Grenzen

Noch keine neuen Prüfungen ausgeführt. Physikalische Abnahme und Plattformnachweise werden getrennt vom Implementierungsstand geführt. Gemäß Development Plan beginnt der umfangreiche Editor-Ausbau erst nach E07/B03. Nicht verfügbare Zielplattformen werden ausdrücklich offen geführt.

## Arbeitsprotokoll

- 17.10.2026: Plan und Bestand geprüft; Umsetzung von M0a und frühem M1-Prototyp begonnen.
