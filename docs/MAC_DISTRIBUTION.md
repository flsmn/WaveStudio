# Mac-Auslieferung – vorbereiteter Stand, 18. Oktober 2026

MAC-04/MAC-06 bleiben offen. Die lokale Entwicklung und Paketprüfung laufen auf Apple M1 / 8 GiB, macOS 27.0.1 arm64. Windows und Linux sind zurückgestellt. Eine öffentliche Verteilung oder ein unterstütztes Mindestbetriebssystem ist noch nicht freigegeben.

## Statische Systembasis

[mac-distribution-audit.json](mac-distribution-audit.json) beschreibt das vorhandene dev8-Paket vor den AX-Korrekturen. Der lesende Prüfer [audit_mac_distribution.py](../scripts/audit_mac_distribution.py) findet 264 Mach-O-Dateien, ausschließlich arm64. Der höchste deklarierte macOS-Minimumwert ist **26.0.0**; zwölf Qt-/Shiboken-Bindings tragen diesen Wert, darunter QtCore/QtGui/QtWidgets. Die aktuelle [dev13-Inventur](native-dev13/mac-distribution-audit.json) bestätigt ebenfalls 264 Mach-O-Dateien, nur arm64 und höchsten Mindestwert 26.0.0. Ein unabhängiger `otool -l`-Abgleich für QtCore bestätigt `LC_BUILD_VERSION`, `minos 26.0`, `sdk 26.0`. Minimum und SDK werden getrennt ausgewertet.

Damit ist eine Unterstützung älterer macOS-Versionen durch dieses konkrete Paket nicht belegt. Die Python-/Wheel-Buildbezeichnung allein bestimmt die Kompatibilität des gesamten Bundles nicht. Unterstützung älterer Macs erfordert einen entsprechend gebauten und real geprüften Abhängigkeitsstand. Auch macOS 26 ist bisher lediglich ein aus den Binärdateien abgeleiteter Kandidat; ein Lauf auf einem sauberen fremden Mac fehlt. Getestet bleibt macOS 27.0.1 auf dem aktuellen M1.

## Lizenznachweise und Abhängigkeiten

Die Inventur erfasst ausgewählte installierte Distributionen mit Versionen, Lizenz-Metadaten und Hashes vorhandener Lizenz-/NOTICE-Dateien. Sie ersetzt weder die Zuordnung aller tatsächlich eingebundenen Binärbibliotheken noch die abschließende Zusammenstellung ihrer Verteilungsunterlagen.

| Bereich | Vorliegender Nachweis | Offen für die Auslieferung |
| --- | --- | --- |
| WaveStudio / Engine-Fork | In beiden lokalen Repositories fehlt eine Lizenzdatei auf oberster Ebene. Auch auf den gesichteten Seiten von [Fork](https://github.com/flsmn/WaveSimulator2D) und [Ausgangsrepository](https://github.com/0x23/WaveSimulator2D) ist keine Lizenzdatei ausgewiesen. | Projektlizenz bzw. erforderliche Erlaubnis für übernommene Beiträge klären; vorhandene anderweitige Vereinbarungen sind hier nicht bekannt. Keine Lizenz eigenmächtig auf fremde Beiträge anwenden. |
| PySide6 / Qt / Shiboken | Installierte Metadaten nennen Lizenzalternativen; im Distribution-Dateiverzeichnis wurden keine separaten Lizenztexte aufgeführt. | Zum konkreten Paket passende Qt-/Drittkomponenten-Texte und erforderliche Verteilungsunterlagen vollständig zusammenstellen. Offizielle Grundlage: [Qt-for-Python-Lizenzen](https://doc.qt.io/qtforpython-6/licenses.html). |
| NumPy / Torch / PyQtGraph | Lokale Lizenz-/NOTICE-Dateien und ihre Hashes erfasst. | Alle tatsächlich gebündelten Komponenten einschließlich Python-Laufzeit, Bibliotheken und Farbtabellen mit den finalen Artefakten abgleichen und erforderliche Hinweise beilegen. |
| PyInstaller | Lizenznachweis des Buildwerkzeugs erfasst. | Buildkonfiguration und bootloaderbezogene Nachweise zum finalen Build dokumentieren. |
| SciPy | Neu installierte reine Prüfabhängigkeit, vom Desktop-Build explizit ausgeschlossen. | Im dev13-PYZ keine SciPy-Module enthalten ([Buildnachweis](native-dev13/build-results.json)); keine zusätzliche Laufzeitabhängigkeit der App. Finalen Auslieferungsstand erneut zuordnen. |

Die fehlende lokale Lizenzdatei allein beschreibt noch keine vollständige Rechteprüfung. [GitHubs Hinweise zur Repository-Lizenzierung](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository) erläutern, warum eine öffentliche Repository-Seite eine ausdrückliche Lizenzentscheidung nicht ersetzt. Die lokale technische Arbeit wird fortgeführt; die offene Rechte-/Lizenzzuordnung ist vor öffentlicher Auslieferung zu klären.

## Konkrete nächste Entscheidungen und Nachweise

- Unterstützte Mac-Basis und verfügbaren fremden Test-Mac benennen. Vorschlag für die erste Abnahme: das tatsächlich gebaute arm64-Paket auf macOS 26 oder neuer prüfen; bisher nur 27.0.1 nachgewiesen. Eine verbindliche Zusage folgt erst nach dem realen Test.
- Lokale/private Nutzung oder öffentliche Verteilung festlegen; erforderliche Developer-ID-Signierung und Notarisierung für den gewählten Weg klären. Die bisherigen Pakete sind lokal ad-hoc signiert.
- Ersten Aktualisierungsweg dokumentieren. Ein manuell heruntergeladenes und ausgetauschtes Anwendungspaket ist vom Plan gedeckt; ein automatischer Updater ist keine Voraussetzung.
- Am endgültigen Versionspaar Paketstart, Run/Pause, Speichern/Laden und PNG/CSV ohne Nutzer-Python und ohne Netzwerk auf sauberer Installation nachweisen. Hash, Hardware, macOS, Backends und Installationshinweise gemeinsam sichern.
- Restaufwand nach den noch offenen Physik-/GUI-Befunden schätzen. Eine belastbare Zeitspanne lässt sich aus den bisherigen Forschungs-/Fehlbefunden noch nicht zusagen.

Diese Entscheidungen sind als offene Aufgaben dokumentiert. Es wurden keine Entwicklerzertifikate, Konten oder globalen Sicherheits-/Energieeinstellungen geändert und keine Nachricht an Dritte versandt.
