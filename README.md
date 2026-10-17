# Wave Studio

Lokale Desktop-Anwendung für skalare 2D-Wellenexperimente. Entwicklungsstand **0.1.0.dev8**, Python 3.12, PySide6, PyQtGraph und separat paketierte PyTorch-Engine. Die Oberfläche ist Englisch.

Implementiert sind freier Aufbau mit Quellen, Materialien, Polygonen, Wänden und bikonvexen Linsen, Undo/Redo, Run/Pause/Step/Reset, passive Detektoren mit endlichen Messfenstern, Referenzvergleich, zwei Ansichten, Abstand/Winkel, sichere Projektdateien, Wiederherstellung sowie PNG/CSV. Drei bearbeitbare Beispiele liegen unter `examples/` und im File-Menü.

Der aktuelle Mac (Apple M1, 8 GB) ist die lokale Prüfplattform. Windows/Linux folgen gemäß Nutzerentscheidung später. Ein plattformübergreifendes Release ist noch nicht abgenommen. Qualitätsstufen sind nachvollziehbare Auflösungsvorschläge; sie ersetzen keine Genauigkeitsprüfung des eigenen Aufbaus. Bekannte Grenzen und offene Nachweise stehen in [task.md](task.md).

## Start auf diesem Mac

Das gebaute Anwendungspaket liegt unter `dist/WaveStudio.app`. Es enthält seine Python-Laufzeit und die fest gebaute Engine. Alternativ aus der eingerichteten Entwicklungsumgebung:

```sh
cd WaveStudio
.venv/bin/wave-studio
```

Aus diesem Repository heraus genügt `.venv/bin/wave-studio`. Die Anwendung speichert keine fortsetzbaren Wellenfelder. Projektdateien enthalten Aufbau, Anzeige und eingefrorene Referenzprofile.

## Entwicklungsumgebung neu einrichten

Beide Repositories liegen nebeneinander in `WaveStudioApp/`. Python 3.12 verwenden, eine isolierte Umgebung erstellen und zuerst die Engine installieren:

```sh
cd WaveStudio
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e "../WaveSimulator2D[dev]"
python -m pip install -e ".[dev]"
wave-studio
```

Unter Windows statt `source` die Aktivierung `.venv\Scripts\activate` verwenden. Die Windows-/Linux-Pakete sind noch nicht geprüft. Die lokale Entwicklungsumgebung nutzt vorhandene Conda-Laufzeitbibliotheken; für reproduzierbare neue Builds wird eine isolierte Umgebung mit PyPI-Wheels empfohlen. Insbesondere NumPy aus Conda in einer darüberliegenden venv kann den PyInstaller-Conda-Hook stören.

```sh
python -m pytest tests ../WaveSimulator2D/tests -q
python ../WaveSimulator2D/validation/run_references.py --output /tmp/wave-physical-results.json
python -m wave_studio --check-workflow /tmp/wave-studio-check
```

Die Referenzprüfung setzt eine installierte Engine voraus und verwendet keinen lokalen Importpfad. Der Qt-Integrationstest öffnet ein Fenster, führt den Doppelspalt-Ablauf aus, schreibt prüfbare Artefakte ins angegebene Verzeichnis und schließt wieder. Für Umgebungen ohne Bildschirm kann `QT_QPA_PLATFORM=offscreen` gesetzt werden. CPU/MPS- und Ressourcenprüfungen: `scripts/check_backends.py`, `scripts/check_resources.py` auf realer Hardware.

## Dokumentation

- [Fortschritt und offene Abnahmen](task.md)
- [Bedienung und Modellgrenzen](docs/USER_GUIDE.md)
- [Entwicklungs- und Build-Anleitung](docs/DEVELOPMENT.md)
- [API-/Lebenszyklusvertrag](docs/CONTRACT.md)
- [Lokale Abnahme](docs/ACCEPTANCE.md)
- [Konfigurierbare Budgets und Balanced auf dem Mac](docs/BALANCED_MAC_ACCEPTANCE.md)
- [PRD](PRD.md), [Projektplan](PROJECT_PLAN.md), [Development Plan](DEVELOPMENT_PLAN.md)

Numerische Verfahren gehören in `../WaveSimulator2D/`; Editor, Laufsteuerung, Dateien und Darstellung in dieses Repository. Git-Versionierung und Commits erfolgen getrennt.
