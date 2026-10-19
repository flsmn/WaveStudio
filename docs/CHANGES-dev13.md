# Studio 0.1.0.dev13 / Engine 0.1.0.dev4 — lokaler Mac-Kandidat

18. Oktober 2026, Apple M1 / 8 GiB, macOS 27.0.1 arm64, PySide6 6.12.0. Keine stabile Release- oder öffentliche Verteilungsfreigabe.

- Physikalische/Messänderungen wenden den globalen Style nur noch bei tatsächlichem Theme-/Textgrößenwechsel neu an. Das behebt den nativ reproduzierten AX-Verlust bei einer reinen Quellen-Eigenschaftsänderung; native Command-Z/Redo wurden für diesen Weg nachgewiesen. Die Szenenliste besitzt einen zugänglichen Namen und eine Beschreibung.
- Der zusätzliche Listenaustausch aus dev10–12 ist verworfen: Er bestand Qt-Tests, aber keine vollständige native AX-Abnahme. Der isolierte Qt-6.8-Vergleich stürzte auch ohne diesen Workaround ab. Hauptumgebung bleibt 6.12.0. [Einzelheiten](MAC_ACCESSIBILITY_FOLLOWUP.md).
- Ressourcenprüfung kann Artefakte pro Lauf getrennt ablegen. Opt-in Ereignis-/GC-Diagnose ergänzt; Messgrenzen und produktiver Abfragetakt unverändert. [Befunde](PERFORMANCE_INVESTIGATION.md).
- Historische Physikgrenzen zentralisiert. Unabhängige Quellen-/Linsenreferenzen, Kalibrierungen und versionierte Pilotprotokolle im Engine-Repository ergänzt. Numerischer Laufzeit-Solver und Engine-dev4-Wheel unverändert. SciPy bleibt Prüfabhängigkeit und ist vom App-Build ausgeschlossen. [Ergebnisse und Grenzen](../../WaveSimulator2D/docs/QUANTITATIVE_PROGRESS.md).
- Build unterstützt getrennte Zielordner. Das historische dev8-Paket bleibt unter `dist/WaveStudio.app`, der reguläre neue Kandidat unter `dist/ax-dev13/WaveStudio.app`. Verworfene Diagnosepakete unter `dist/qt68-*` sind nicht zur Nutzung empfohlen.

Aktuelle Quellregression: 76 Tests in 11,88 s bestanden. Zwei ausschließlich für den verworfenen Listenaustausch geschriebene Tests entfallen mit dessen Code; eine History-/Auswahlregression bleibt. Finale Paketnachweise stehen separat unter `native-dev13/`.

Weiter offen: quantitative Linien-/Spalt-/Linsen- und Preset-Abnahme; gelegentliche GUI-Lücke über 250 ms; AX nach strukturellen/Style-Wechseln und menschliche VoiceOver-Prüfung; Lizenz-/Verteilungsentscheidungen und sauberer fremder Mac. Windows und Linux bleiben zurückgestellt. Die Mac-Auslieferung ist in [MAC_DISTRIBUTION.md](MAC_DISTRIBUTION.md) vorbereitet.
