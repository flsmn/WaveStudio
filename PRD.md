# Wave Studio Produktanforderungen

Product Requirements Document

**Produktversion:** 0.1 · **Dokumentversion:** 1.3 · **Stand:** 16. Oktober 2026

**Grundlage:** [Projektplan vom 16. Oktober 2026](PROJECT_PLAN.md). Die Abschnittsverweise beziehen sich auf diesen Plan.

## 1 Produktziel und Erfolg

Wave Studio soll optische Wellenexperimente in zwei Dimensionen ohne Programmierung ermöglichen. Version 0.1 richtet sich an Menschen mit Grundkenntnissen in Optik und konzentriert sich auf kompakte Versuche für Lernen und Lehre. Erster Anwender ist der Projektinitiator.

Der zentrale Ablauf verbindet freien Versuchsaufbau, Simulation, relative Intensitätsmessung und Dateiaustausch. Drei bearbeitbare Beispiele erleichtern den Einstieg; eigene Experimente bleiben frei gestaltbar.

Die Anforderungen F01 bis F18 und Q01 bis Q06 sind für Version 0.1 verpflichtend; ausdrücklich genannte Bedingungen gelten. Vorläufige Zielwerte und offene Entscheidungen sind gekennzeichnet. Die Abnahmekriterien beschreiben den erforderlichen Nachweis.

Version 0.1 ist erfolgreich, wenn:

- ein selbst aufgebauter Doppelspalt ohne Code simuliert, gemessen, exportiert und erneut geöffnet werden kann;
- die vier physikalischen Referenzszenen innerhalb zuvor festgelegter Toleranzen bestehen;
- Messwerte und Referenzen eindeutig ihrem Aufbau und Lauf zugeordnet bleiben;
- Pakete auf macOS, Windows und Linux offline funktionieren und auch die schwächere Testhardware sinnvoll nutzbar bleibt.

Ein Veröffentlichungstermin ist nicht festgelegt. Eine belastbare Aufwandsschätzung folgt nach M0 und M1.

## 2 Umfang und Grenzen

### 2.1 Enthaltene Funktionen

| Bereich | Umfang von Version 0.1 |
| --- | --- |
| Experiment | Ein geöffnetes Projekt und genau eine aktive Simulation; frei bearbeitbare Szene mit Undo und Redo |
| Objekte | Kontinuierliche Punkt- und Linienquellen, Materialrechtecke und Polygone, symmetrisch bikonvexe Linse, rechteckige Wände, passive Detektoren |
| Beobachtung | Feld, relatives zeitlich gemitteltes Feldquadrat und Materialkarte; optionale zweite Ansicht desselben Laufs |
| Auswertung | Punktdetektor, Detektorlinie, Abstände und Winkel, Vergleich mit festgehaltenem Referenzprofil |
| Dateien | Projekte mit Referenzprofilen, PNG, CSV und begrenzte automatische Wiederherstellung des Aufbaus |
| Bedienung | Englische Oberfläche, helle und dunkle Darstellung, Qualitätsstufen und Experteneinstellungen |
| Auslieferung | Lokale Desktop-Pakete für macOS, Windows und Linux; CPU als gemeinsame Basis |

### 2.2 Physikalischer Geltungsbereich

Das Produkt verwendet ein skalares, lineares 2D-Wellenmodell mit statischen Materialien. Interferenz, Beugung und Brechung werden innerhalb eines überprüften Parameterbereichs dargestellt. Die Intensitätsansicht zeigt das zeitlich gemittelte Feldquadrat in relativen Einheiten. Absolute optische Leistung wird nicht ausgewiesen.

Die Dokumentation erläutert die Bedeutung des Feldes und die Grenzen der zweidimensionalen Näherung. Insbesondere ist eine 2D-Linse keine vollständige Simulation einer dreidimensionalen Laborlinse. Die Randbehandlung wird als gedämpfte Randzone bezeichnet; eine nachgewiesen reflexionsfreie PML wird nicht zugesagt.

### 2.3 Ausgeschlossene und spätere Funktionen

Für Version 0.1 entfallen Polarisation, Dispersion, nichtlineare Materialien, reale metallische Spiegel, eine Stoffdatenbank und absolute Leistungsangaben. Physikalische Eingaben in µm und fs folgen erst nach nachgewiesener Skalierung.

Spätere Optionen sind freies Malen und Bildimport, weitere Linsen und Prismen, weitergehende Spiegelmodelle, ein Komfortwerkzeug für Spalte, homogene Strahlen, Gaußstrahlen, Pulse, Videoexport, fortsetzbare Simulationszustände, sequenzielle Parameterreihen, Fourier-Auswertung, vollständige Felddatenexporte und zusätzliche Randbedingungen oder Modelle. Diese Optionen sind keine Zusage für die nächste Version. 3D liegt außerhalb des ersten Projektumfangs. Parallele Simulationen gehören auch langfristig nicht zum vorgesehenen Funktionsumfang.

## 3 Zentrale Nutzungsszenarien

### 3.1 Einen eigenen Versuch auswerten

Der Nutzer startet mit einem leeren Projekt, platziert eine Quelle und drei Wandstücke mit zwei Öffnungen und ergänzt eine Detektorlinie. Er startet den Lauf manuell, betrachtet Feld und Intensitätsmuster, wartet das Messfenster ab und exportiert das Profil als CSV sowie eine Ansicht als PNG. Er speichert das Projekt und öffnet später denselben Aufbau einschließlich festgehaltener Referenz erneut.

### 3.2 Eine Variante vergleichen

Der Nutzer hält ein abgeschlossenes Detektorprofil fest, pausiert und verändert beispielsweise einen Spaltabstand. Die Anwendung kennzeichnet den alten Lauf als überholt und bleibt angehalten. Erst ein manueller Klick auf Run startet den geänderten Versuch mit frischen Feldern und aktuellen Messungen. Das Referenzprofil bleibt erhalten und wird auf einer gemeinsamen Ortsachse und wählbaren gemeinsamen Skalierung verglichen.

### 3.3 Während eines Laufs beobachten und messen

Der Nutzer wechselt die Ansicht, zoomt und verschiebt einen passiven Detektor. Darstellungsänderungen lassen Simulation und Messung unverändert. Die bestätigte Detektorposition startet ausschließlich für diesen Detektor ein neues Messfenster. Wellenfeld, Simulationszeit, andere Detektoren und Referenzprofile bleiben erhalten.

## 4 Funktionale Anforderungen

### F01 Projekte und Beispiele

Die Anwendung muss Projekte neu anlegen, öffnen und speichern. Sie liefert Doppelspalt, Brechung an einer Grenzfläche und Fokussierung durch eine symmetrisch bikonvexe Linse als bearbeitbare Beispiele. Es ist genau ein Projekt geöffnet; ein Projektwechsel beendet den bisherigen Lauf und gibt seinen Zustand frei.

**Abnahme:** Alle drei Beispiele lassen sich öffnen und verändern. Ein eigener Aufbau kann ohne Parameterverlust gespeichert und geladen werden. Eine zweite Ansicht oder ein Referenzprofil erzeugt keine weitere Simulation.

### F02 Freier Szeneneditor

Objekte müssen sich hinzufügen, auswählen, verschieben, duplizieren und löschen lassen. Die Zeichenfläche, Szenenliste und numerischen Eigenschaften zeigen denselben Stand. Undo und Redo müssen die jeweilige Änderungsklasse beachten: physikalischer Aufbau, Messung oder Darstellung.

**Abnahme:** Ein eigener Aufbau lässt sich unabhängig von den Beispielen erstellen. Änderungen und Undo beziehungsweise Redo werden konsistent angezeigt; verschobene Materialien erscheinen beim nächsten Lauf auch im numerischen Raster an der neuen Position.

### F03 Kontinuierliche Quellen

Punkt- und Linienquellen besitzen editierbare Wellenlänge, Amplitude und Phase. Die Quellenwellenlänge bezieht sich auf das Referenzmedium. Die Einspeisung muss eine definierte Überlagerung ermöglichen und darf ankommende Wellen nicht unbeabsichtigt wie eine harte Wand behandeln. Quellen innerhalb undurchlässiger Wände sind ungültig.

**Abnahme:** Zwei kohärente Quellen zeigen die erwartete Phasenabhängigkeit. Der Rückwellenfall prüft die Einspeisung. Ungültige Positionen werden verständlich erklärt. Die genaue additive Anregung und ihre Skalierung werden in M0 festgelegt und validiert.

### F04 Materialien und Wände

Materialrechtecke und Polygone besitzen Brechungsindex und optionale Dämpfung; sie können als frei platzierbare absorbierende Bereiche dienen. Bei Überlappung bestimmt das oberste Materialobjekt Brechungsindex und Dämpfung gemeinsam. Ohne Dämpfung ist sein Bereich ungedämpft; die äußere Dämpfungszone wird separat angewendet.

Rechteckige Wände setzen unabhängig von darunterliegenden Materialien eine Hindernisbedingung durch. Ein Einzelspalt besteht aus zwei, ein Doppelspalt aus drei Wandstücken. Ein eigenes Blendenwerkzeug ist nicht erforderlich. Vorgesehen ist eine in M0 zu prüfende Dirichlet-Bedingung mit u = 0 im Wandbereich.

**Abnahme:** Die Materialreihenfolge wirkt im numerischen Feld wie angezeigt. Im Doppelspaltversuch tritt außerhalb der Öffnungen keine Welle durch die Wand; unbeabsichtigte Wege um äußere Wandenden verfälschen den Referenzfall nicht.

### F05 Symmetrisch bikonvexe Linse

Die Linse muss über Krümmung, Öffnung, Brechungsindex und optionale Dämpfung einstellbar sein. Dickenregel und gültige Parameter werden vor Umsetzung des Werkzeugs festgelegt. Qualitätswechsel erhalten die geometrische Kontur.

**Abnahme:** Ungültige Kombinationen werden am Eingabefeld erklärt. Ein einfacher Aufbau fokussiert innerhalb der festgelegten Referenztoleranz; eine feinere Rasterung verschiebt die Fokuslage nicht wesentlich über diese Toleranz hinaus.

### F06 Einheiten und Qualitätsstufen

Geometrien werden in Vielfachen einer festen Referenzwellenlänge des Projekts angegeben. Eine Änderung der Quellenwellenlänge verändert keine Position oder Objektgröße. Preview, Balanced und High Quality sowie aufklappbare Experteneinstellungen müssen verfügbar sein.

Qualitätswechsel erhalten Referenzlänge, Geometrie, Quellenparameter und beabsichtigte Dämpfung. Die Auflösung richtet sich nach Wellenlänge im Material, relevanten Strukturen und Ausbreitungsweg. Vor Run werden unzureichende Auflösung und geschätzter Speicherbedarf angezeigt. Während eines Laufs bleibt das Gitter unverändert.

**Abnahme:** Ein Qualitätswechsel verändert nur die numerische Diskretisierung gemäß der festgelegten Skalierung. Die drei Stufen werden nicht pauschal mit 256², 512² und 1024² gleichgesetzt. Numerisch ungültige Eingaben werden abgefangen.

### F07 Laufsteuerung

Run, Pause, Step und Reset steuern die einzige aktive Simulation. Pause und anschließender manueller Run ohne physikalische Änderung setzen denselben Lauf fort. Step berechnet im pausierten, zum Aufbau passenden Lauf genau einen Schritt. Reset löscht Felder und aktuelle Messungen vollständig und lässt die Anwendung angehalten; Referenzprofile bleiben erhalten.

**Abnahme:** Fortsetzen verändert die Laufidentität nicht. Step startet keinen Dauerlauf. Reset entfernt auch Messhistorien und Feldreste. Nach einem Fehler oder Gerätewechsel setzt sich die Berechnung erst durch eine Nutzeraktion wieder in Gang.

### F08 Physikalischen Aufbau ändern

Geometrie, Quellen, Materialwerte, Gitter, Zeitschritt, Simulationsbereich und Randbedingungen sind nur vor dem Start oder nach Pause editierbar. Jede solche Änderung macht den bisherigen Lauf überholt. Die Oberfläche darf dessen Feld nicht als Ergebnis des neuen Aufbaus ausgeben.

**Abnahme:** Nach Bearbeiten, Bestätigen, Schließen eines Dialogs sowie Undo oder Redo bleibt der Lauf angehalten. Step ist nach einer physikalischen Änderung bis zum nächsten manuellen Run deaktiviert. Erst dieser Run initialisiert Felder und aktuelle Messungen neu. Alte Frames und Messwerte werden verworfen; Referenzen bleiben erhalten.

### F09 Ansichten

Die Hauptansicht wechselt zwischen Feld, relativem gemitteltem Feldquadrat und Materialkarte. Zoom, Verschieben, Farbskala und Helligkeit sind bedienbar. Eine optionale zweite Ansicht übernimmt den sichtbaren Ausschnitt der Hauptansicht und zeigt denselben Simulationslauf.

**Abnahme:** Zoom und Fenstergröße verändern weder Simulationsbereich noch Gitter. Darstellungsänderungen setzen keine Messung zurück. Farbsättigung und Helligkeit verändern ausschließlich die Anzeige; Messungen verwenden das unbeschnittene Feld.

### F10 Passive Detektoren

Punktdetektoren und Detektorlinien messen relative Intensität, ohne die Ausbreitung zu beeinflussen. Sie dürfen während des Laufs bearbeitet werden. Beim Ziehen wird die Position zunächst als Vorschau gezeigt; erst Loslassen oder Bestätigen einer gültigen Position übernimmt die Änderung.

**Abnahme:** Verschieben oder Ändern von Abtastung und Messfenster setzt nur die aktuelle Messung dieses Detektors zurück. Werte unterschiedlicher Positionen werden nicht vermischt. Hinzufügen beginnt eine eigene Messung, Löschen beendet sie. Ein pausierter Lauf bleibt pausiert; neue Werte entstehen erst mit weiteren ausdrücklich ausgelösten Schritten.

### F11 Messfenster und Messstatus

Eine Live-Vorschau ist sofort verfügbar. Festgehaltene Profile und quantitative CSV-Exporte verwenden ein definiertes endliches Messfenster nach einer Einlaufphase. Beginn, Dauer, Samplezahl, Abtastung und Mittelungsverfahren gehören zur Messdefinition. Unterschiedliche Quellenfrequenzen und Schwebungen werden bei der Fensterwahl berücksichtigt.

**Abnahme:** Messungen laufen auf Basis der Simulationszeit und sind von der Bildrate unabhängig. Die Oberfläche unterscheidet laufende Messung, abgeschlossenes Fenster, Referenz und überholtes Ergebnis. Eine unbegründete automatische Aussage „eingeschwungen“ erscheint nicht.

### F12 Referenzprofile vergleichen

Ein Nutzer kann ein abgeschlossenes Profil ausdrücklich als Referenz festhalten und mit dem aktuellen Profil vergleichen. Referenzen speichern unnormalisierte relative Messwerte, Ortskoordinaten, Szenenstand und Messparameter ihres Ursprungslaufs. Die Referenzhistorie bleibt begrenzt.

**Abnahme:** Referenzen überstehen Reset, einen neuen Lauf und Speichern beziehungsweise Laden. Der Vergleich bietet eine gemeinsame wählbare Skalierung. Unterschiedliche Gitter werden auf einer gemeinsamen physikalischen Ortsachse verglichen; Interpolation überschreibt keine Originalwerte.

### F13 Abstände und Winkel

Messwerkzeuge müssen Abstände und Winkel im Aufbau bestimmen und ihre Werte mit passenden Einheiten anzeigen.

**Abnahme:** Eine bekannte geometrische Strecke und ein bekannter Winkel werden im Rahmen der festgelegten Anzeigeauflösung korrekt angezeigt. Zoom und Verschieben ändern die gemessene Geometrie nicht.

### F14 PNG und CSV exportieren

Eine Ansicht muss als PNG und ein Detektorprofil als CSV exportierbar sein. CSV-Dateien enthalten Ortskoordinaten, unnormalisierte relative Messwerte, Einheiten, Messfenster und zugehörige Parameter.

**Abnahme:** Der Export ist seinem Szenenstand und Lauf zuordenbar. Zur Ergebnisbeschreibung gehören mindestens Szenenstand, Lauf-ID, Engine-Version, Gitter, Zeitschritt, Laufdauer, Backend, Datentyp, Messfenster und Abtastung. Ein gespeichertes Referenzprofil bleibt dabei seinem Ursprungslauf zugeordnet.

### F15 Sicher speichern und wiederherstellen

Das versionierte Projektformat enthält Aufbau, Anzeigeeinstellungen sowie festgehaltene Referenzprofile mit Messparametern und stabilen Objekt-IDs. Speichern ersetzt die Zieldatei atomisch. Eine begrenzte automatische Wiederherstellung schützt den bearbeiteten Aufbau. Fortsetzbare Simulationszustände gehören nicht zu Version 0.1.

**Abnahme:** Eine beschädigte Datei oder unbekannte Formatversion wird verständlich abgewiesen und ersetzt das offene Projekt nicht. Ein fehlgeschlagener Speichervorgang lässt die letzte gültige Datei bestehen. Ein Wiederherstellungsfall kann den gesicherten Aufbau zurückholen. Änderungen an gespeicherten Detektor- oder Anzeigeeinstellungen beeinflussen den Speicherstatus unabhängig vom Simulationszustand.

### F16 Sprache und Zugänglichkeit

Oberfläche, Meldungen, Hilfen und Beispiele sind Englisch. Sprachtexte werden zentral verwaltet, um Übersetzungen vorzubereiten. Helles und dunkles Farbschema, Tastaturbedienung, skalierbare Schrift, erkennbare Auswahl und numerisch beschriftete Farbskalen gehören zum Umfang.

**Abnahme:** Die zentralen Abläufe funktionieren mit konsistenten englischen Texten. Ungültige Werte werden am betroffenen Feld mit konkreter Erklärung angezeigt. Beide Farbschemata bleiben bei skalierter Schrift lesbar und bedienbar.

### F17 Rechengerät auswählen

Die Anwendung erkennt verfügbare Geräte und ermöglicht die manuelle Auswahl angebotener, getesteter Backends. CPU-Betrieb ist auf allen drei Plattformen erforderlich. MPS wird auf dem M1 geprüft. CUDA darf nur nach verfügbarem NVIDIA-Hardwaretest und bestandenem Backendvergleich als unterstützt angeboten werden; CUDA ist keine Voraussetzung für Version 0.1.

**Abnahme:** Alle numerischen Objekte verwenden dasselbe gewählte Gerät. Ein kurzer Referenzlauf auf CPU und jedem angebotenen GPU-Backend stimmt innerhalb der dokumentierten Toleranzen überein. Bitgleichheit ist nicht erforderlich.

### F18 Rechenmodus wählen

Ein sparsamer Standardmodus begrenzt Rechenaufwand und Bildrate. Ein optionaler Modus darf mehr Rechenleistung nutzen. Rechenmodus und numerische Qualitätsstufe sind unabhängig.

**Abnahme:** Der sparsame Modus kann die Simulationszeit langsamer voranschreiten lassen, ohne Gitter oder Messdefinition zu verändern. Pausiert werden keine Simulationsschritte berechnet und unveränderte Ansichten nur bei Bedarf neu gezeichnet. Die Oberfläche zeigt Simulationsschritte pro Sekunde und Bildrate getrennt an.

## 5 Qualitätsanforderungen

### Q01 Offline nutzbare Anwendungspakete

Alle Kernfunktionen müssen lokal ohne laufende Netzwerkverbindung und ohne separat zu installierendes Python funktionieren. Für macOS, Windows und Linux sind fertige Anwendungspakete erforderlich. Projekte werden als Dateien ausgetauscht.

**Abnahme:** Paketstart, Run und Pause, Speichern und Laden sowie PNG- und CSV-Export funktionieren je Betriebssystem auf einer möglichst sauberen Testinstallation offline.

### Q02 Reaktionsfähige Bedienung

Berechnung und Anzeige müssen so entkoppelt sein, dass Pause und Abbruch zeitnah verarbeitet werden. Referenz ist ein MacBook mit Apple M1 und 8 GB RAM. Auch ein sinnvoller CPU-Betrieb auf der schwächeren verfügbaren Testhardware ist erforderlich.

**Vorläufiges Ziel:** etwa 30 Bilder/s bei einem repräsentativen 512 × 512-Beispiel und unter 100 ms Reaktion auf Pause auf dem M1. Diese Werte sind weder gemessen noch bereits endgültige Abnahmegrenzen. Verbindliche Leistungsbudgets werden in M1 anhand der Messungen festgelegt.

### Q03 Begrenzter Ressourcenverbrauch

Frame-Übergabe, Messhistorien und Referenzaufzeichnung müssen begrenzt bleiben; vollständige Felder werden nicht unbegrenzt aufgezeichnet. Beide Ansichten verwenden denselben Lauf. Eine größere Installationsdatei ist akzeptabel, wenn der laufende Betrieb sparsam bleibt.

**Abnahme:** Der Prototyp misst Prozess- und Gerätespeicher, CPU- und GPU-Auslastung, Simulationsschritte/s, Bildrate und Bedienreaktion: im Leerlauf, pausiert und unter Simulation mit einer und zwei Ansichten. Geteilter Apple-Silicon-Speicher zählt nur einmal. Startzeit und Paketgröße werden früh erfasst. Die Messungen bestimmen Speicher- und Lastgrenzen.

### Q04 Nachvollziehbare Physik

Raum- und Zeitskalierung, Kreisfrequenz, Wellenlänge, Ausbreitungsgeschwindigkeit, Quellenanregung und Dämpfung müssen konsistent definiert sein. Stabilität und numerische Dispersion werden für das tatsächlich verwendete Schema geprüft. Materialrasterisierung und Wandbedingung müssen zum Solver passen.

**Abnahme:** Vier kleine Referenzszenen prüfen die relevanten Effekte. Für verglichene Größen und Parameterbereiche werden vor der Abnahme begründete Fehlertoleranzen festgelegt. Zwei gezielte Auflösungen genügen zunächst; eine dritte wird nur bei unklarer Abweichung ergänzt. Gitterkonvergenz allein ersetzt keine physikalische Referenz.

### Q05 Konsistente Ergebnisse

Physikalischer Szenenstand, Laufidentität und Revision jeder Detektormessung müssen unterscheidbar sein. Reine Detektor- oder Darstellungsänderungen verändern die Laufidentität nicht. Verzögerte Daten dürfen keinem neuen Lauf oder Messfenster zugerechnet werden.

**Abnahme:** Nach einer physikalischen Änderung erscheinen keine alten Frames als neues Ergebnis. Nach Detektoränderung gelangen keine alten Positionsdaten in die neue Messung. Wiederholbarkeit wird innerhalb dokumentierter numerischer Toleranzen nachgewiesen.

### Q06 Fehlerbehandlung und Erhalt des Aufbaus

Ungültige Eingaben werden vor der Übernahme mit einer konkreten Erklärung am betroffenen Feld abgewiesen. Die bisher gültige Konfiguration bleibt bestehen; ein gültiger laufender Versuch und seine Messungen werden dadurch weder gestoppt noch zurückgesetzt. Ein Start mit ungültigen Simulationsparametern wird verhindert.

Fehler, die eine sichere Fortsetzung der Simulation verhindern, etwa Speichermangel im Solver, Backend-Ausfall oder numerisch ungültige Felder, stoppen den betroffenen Lauf. Die bearbeitete Szene bleibt erhalten. Fehlermeldungen erklären den konkreten Anlass; nach Behebung beginnt die Berechnung nicht automatisch erneut.

**Abnahme:** Innerhalb der bestehenden Bedienabläufe wird eine ungültige Detektorposition abgewiesen, während der gültige Lauf und die bisherige Messung weiterlaufen. Ein gezielt ausgelöster relevanter Simulationsfehler stoppt dagegen die Berechnung, erhält die Szene und führt nach Behebung zu keinem automatischen Neustart. Die gespeicherte Arbeit bleibt gemäß F15 geschützt.

## 6 Technische Rahmenbedingungen

Die bestätigte Grundlage besteht aus Python, PySide6, PyQtGraph und der bestehenden PyTorch-Engine im Fork flsmn/WaveSimulator2D. Die Entwicklung erfolgt in zwei eigenständigen Git-Repositories:

- **WaveStudio:** Desktop-Anwendung, GUI, Szeneneditor und Auswertungsfunktionen.
- **WaveSimulator2D:** Simulations-Engine und numerische Berechnungen. Numerische Korrekturen gehören in diesen Engine-Fork.

Beide Repositories liegen als eigenständige Git-Repositories im gemeinsamen Arbeitsbereich `WaveStudioApp/`:

```text
WaveStudioApp/                         # Gemeinsamer Arbeitsbereich, kein übergeordnetes Git-Repository
├── WaveStudioApp.code-workspace       # Öffnet beide Repositories gemeinsam
├── WaveSimulator2D/                   # Repository 1: Simulations-Engine
│   └── .git/
└── WaveStudio/                        # Repository 2: Desktop-Anwendung
    ├── .git/
    ├── PRD.md
    ├── PROJECT_PLAN.md
    └── DEVELOPMENT_PLAN.md
```

Die Planungsdokumente werden im Anwendungsrepository `WaveStudio/` versioniert. Die gemeinsame Workspace-Datei liegt eine Ebene darüber. Während der Entwicklung wird die Engine in der Python-Umgebung von WaveStudio als **lokal editierbares Python-Paket** eingebunden, sodass Änderungen am Engine-Quellcode direkt in Wave Studio getestet werden können.

Änderungen werden je Repository getrennt über Git versioniert. Repositoryübergreifende Anpassungen müssen mit den zusammengehörigen Ständen beider Repositories gemeinsam getestet werden. Dafür werden die betroffenen Kernprüfungen und zentralen Bedienabläufe im begrenzten Umfang aus Abschnitt 7 verwendet.

Für Releases wird die Engine weiterhin separat paketiert und an eine feste Version gebunden. Die ausgelieferte Anwendung benötigt keinen benachbarten Engine-Quellordner. Eine dauerhafte Kopie des Engine-Quellcodes in GUI-Dateien und eine Release-Abhängigkeit von einem beweglichen `main` sind ausgeschlossen.

Die Architektur trennt Projektmodell, Szenenübersetzung, Engine-Adapter, Laufsteuerung, Messlogik, Oberfläche und Persistenz. Das Projektmodell bleibt unabhängig von Qt und GPU-Tensoren. Genau eine Engine-Instanz verarbeitet den aktiven Lauf; interne CPU- oder GPU-Parallelität zur Beschleunigung dieses Laufs ist zulässig. Anzeige und Messungen erhalten Daten mit eindeutiger Zuordnung zu Szene, Lauf und Messrevision.

Qt Widgets, ein Worker in einem separaten Qt-Thread, begrenzte Schrittblöcke, unveränderliche Momentaufnahmen mit höchstens einem wartenden aktuellen Frame sowie versioniertes JSON sind der vorgesehene erste Entwurf. PyInstaller ist ein zu prüfender Paketierungskandidat. Ein eigener GPU-Renderer oder separater Simulationsprozess wird erst durch einen gemessenen Engpass begründet.

Die vorgeschlagene Build-Matrix umfasst macOS/ARM64 und Windows sowie Linux/x86-64. Mindestversionen, Linux-Distribution und endgültige Architekturunterstützung werden nach dem frühen Paketierungstest festgelegt. Die konkreten Engine-Befunde und Korrekturaufgaben bleiben im Projektplan, Abschnitt 2, dokumentiert.

## 7 Abnahme und Umsetzungsschritte

### 7.1 Begrenzter Prüfungsumfang

Die Abnahme verwendet vier physikalische Referenzszenen, zwei zentrale Bedienabläufe und kurze Leistungs-, Backend- und Paketprüfungen. Die Prüfschritte innerhalb dieser Fälle decken die Anforderungen ab; daraus entsteht keine vollständige Testkombination aller Parameter. Es gibt keine pauschale Abdeckungsquote und keine Tests für jedes Oberflächendetail.

Deterministische Kernlogik wird möglichst ohne GUI automatisiert geprüft. Sichtbare Bedienung wird zunächst manuell abgenommen. Zusätzliche Automatisierung entsteht nur für ein konkretes Risiko oder einen wiederkehrenden relevanten Fehler. Wiederholungen richten sich nach betroffenen Änderungen, auffälligen Fehlern oder der Auslieferung.

| Prüfung | Wesentlicher Nachweis | Anforderungen |
| --- | --- | --- |
| T01 Freie Ausbreitung und zwei Quellen | Geschwindigkeit, Wellenlänge, achsparallele und diagonale Ausbreitung, Phasenabhängigkeit, additive Überlagerung und Rückwellenfall | F03, F06, Q04 |
| T02 Materialgrenze und Dämpfung | Brechungswinkel, Restreflexion der Randzone und vergleichbare Dämpfung bei geänderter Auflösung | F04, F06, Q04 |
| T03 Doppelspalt | Undurchlässige Wandbereiche, Symmetrie und charakteristische Minima passend zu Beleuchtung und Messentfernung | F03, F04, F11, Q04 |
| T04 Bikonvexe Linse | Fokussierung, begründete Fokusreferenz und Empfindlichkeit gegenüber Rasterverfeinerung | F05, F06, Q04 |
| T05 Laufsteuerung und Bearbeitung | Run, Pause, Fortsetzen, Step, Reset, manuelle Wiederaufnahme nach Änderung, Undo und Redo, Rasteraktualisierung, Ansichten, Eingabe- und Fehlerverhalten | F02, F07–F09, F16, Q05–Q06 |
| T06 Speichern Messen Exportieren | Eigener Aufbau und Beispiele, Referenzvergleich, Detektoränderung, Messfenster, Abstände und Winkel, PNG und CSV, sichere Dateien und Wiederherstellung | F01, F10–F16, Q05–Q06 |
| T07 Ressourcen | Repräsentativer Lauf auf M1 und schwächerem Rechner, sparsamer Modus, eine und zwei Ansichten, CPU-Betrieb, Reaktion und Speicher | F06, F18, Q02–Q03 |
| T08 Backends | Kurzer Vergleich auf CPU und jedem tatsächlich angebotenen GPU-Backend innerhalb der festgelegten Toleranz | F17, Q04–Q05 |
| T09 Pakete | Je Plattform Start und kurzer Offline-Ablauf mit Run und Pause, Speichern und Laden sowie Export | F01, F14–F15, Q01 |

### 7.2 Meilensteine

| Schritt | Ergebnis und Abschlusskriterium |
| --- | --- |
| M0a Numerischer Kern | Einheiten, Stabilitätsbereich, Quellenanregung, Reset und Gerätewahl sind definiert; relevante Engine-Korrekturen sind umgesetzt. |
| M0b Physikalische Grundlage | T01 bis T04 sind ohne GUI ausführbar. Freie Ausbreitung, Materialgrenze und Spaltmodell funktionieren sinnvoll; ein fester Linsenaufbau prüft die Eignung früh. Grundlegende physikalische Nachweise liegen vor dem Ausbau des Editors vor. |
| M1 Durchgängiger Prototyp | Punktquelle, Feldansicht, Worker sowie Run, Pause und Reset funktionieren. Bedienbarkeit und sparsamer Betrieb auf M1/8 GB sind gemessen; erste Pakete starten auf allen drei Systemen. |
| M2 Szeneneditor | Quellen, Materialien und Wände sind bearbeitbar; Speichern und Laden, Undo und Redo, Laufsteuerung und Rasteraktualisierung funktionieren. Messung und Export folgen in M3. |
| M3 Vollständiger Beispielversuch | Ein selbst aufgebauter Doppelspalt lässt sich vollständig ohne Code starten, messen, mit einer Referenz vergleichen und als PNG beziehungsweise CSV exportieren. |
| M4 Version 0.1 | Der vereinbarte Umfang einschließlich Linsenwerkzeug, zweiter Ansicht und Messwerkzeugen ist fertiggestellt und auf allen drei Plattformen abgenommen. |

Ein einfacher GUI- und Paketierungsprototyp darf parallel zu M0 entstehen. M0 und M1 bilden den ersten Entwicklungsabschnitt; danach folgen Aufwandsschätzung und konkretisierte Leistungsbudgets.

### 7.3 Freigabekriterien für Version 0.1

- F01 bis F18 und Q01 bis Q06 sind im vereinbarten Umfang erfüllt; die CUDA-Bedingung bleibt erhalten.
- T01 bis T09 sind im jeweils festgelegten Umfang bestanden. Ergebnisse, Toleranzen, geprüfte Parameterbereiche und Hardware sind dokumentiert; die vollständige Physikprüfung wird nicht für jede Plattform und jedes Backend wiederholt.
- Vorläufige Leistungsziele sind durch bestätigte Budgets ersetzt. Qualitätsstufen und zulässige numerische Parameterbereiche sind festgelegt.
- Beispiele, Hilfen, Modellgrenzen und englische Meldungen sind konsistent mit dem tatsächlich validierten Verhalten.
- Die für die Auslieferung notwendigen Entscheidungen aus Abschnitt 8 sind geklärt. Die Freigabe behauptet keine Genauigkeit außerhalb des validierten Bereichs.

## 8 Offene Entscheidungen und Risiken

### 8.1 Entscheidungen bis zur jeweiligen Umsetzung

| ID | Entscheidung | Zeitpunkt |
| --- | --- | --- |
| O01 | Raum- und Zeitskalierung, additive Einspeisung, Stabilität, Rasterisierung, Wandbedingung und Dämpfungsumrechnung konkretisieren | M0 |
| O02 | Messgrößen, validierte Parameterbereiche und Fehlertoleranzen für die Referenzszenen festlegen | Vor ihrer Abnahme |
| O03 | Windows- und Linux-Hardware erfassen; Systemversionen, Distribution, Architekturen und mögliche CUDA-Unterstützung festlegen | Früher Paketierungstest in M1 |
| O04 | Leistungs- und Speicherbudgets, Qualitätsauflösungen und Rechenbegrenzung bestimmen | Nach Prototypmessungen in M1 |
| O05 | Dickenregel und gültige Parameter der bikonvexen Linse vervollständigen | Vor dem Linsenwerkzeug |
| O06 | Konkrete Standardmessfenster, Einlaufphase sowie Grenzen für Historie und Wiederherstellung operationalisieren | Vor Messung und Persistenzabnahme |
| O07 | Aufwandsschätzung, Veröffentlichung, Verteilungsmodell, Signierung und Aktualisierungsweg konkretisieren | Schätzung nach M0/M1; Auslieferungsfragen vor öffentlicher Veröffentlichung |

O01 bis O05 und O07 folgen den offenen Punkten des Projektplans. O06 konkretisiert dessen bereits geforderte endliche Messfenster und begrenzte Aufzeichnung; es erweitert den Funktionsumfang nicht.

### 8.2 Wesentliche Produktrisiken

| Risiko | Auswirkung | Behandlung |
| --- | --- | --- |
| Skalierung oder Anregung ist ungeprüft | Anschauliche Bilder führen zu falschen physikalischen Schlussfolgerungen | M0 und T01 bis T04 vor umfangreichem Editorausbau; Modellbereich und Toleranzen dokumentieren |
| Vorgesehene Quellen tragen einen Referenzfall nicht zuverlässig | Brechungs-, Spalt- oder Linsenauswertung wird irreführend | Zuerst Beleuchtung, Quellenenden, Messbereich und Auswertung prüfen; nötige Quellenerweiterung gesondert entscheiden |
| Überholte Daten werden weiterverwendet | Ein Feld oder Profil wird dem falschen Aufbau zugeordnet | F08, F10 und Q05 mit Szenen-, Lauf- und Messrevisionen absichern |
| Rechenlast oder Speicherbedarf überfordert schwächere Rechner | Bedienung reagiert schlecht oder Simulation bricht ab | Sparsamer Modus, begrenzte Puffer, frühe Messung und Vorabhinweise zum Ressourcenbedarf |
| Paketierung scheitert auf einer Zielplattform | Offline nutzbare Auslieferung ist nicht vollständig | Frühe native Builds und kurze Tests auf möglichst sauberen Installationen |

### 8.3 Rückverfolgbarkeit zum Projektplan

| Anforderungen | Grundlage im Projektplan |
| --- | --- |
| F01–F02 | Abschnitte 1, 4, 5 und 6 |
| F03–F06, Q04 | Abschnitte 2, 3, 4, 6, 7 und 8 |
| F07–F09, Q05–Q06 | Abschnitte 4, 5, 6 und 8 |
| F10–F15 | Abschnitte 4, 5, 6 und 8 |
| F16 | Abschnitte 1 und 5 |
| F17–F18, Q01–Q03 | Abschnitte 1, 6, 7 und 8 |
| Abnahme und offene Entscheidungen | Abschnitte 7, 8 und 9; O06 aus Abschnitten 5 und 6 abgeleitet |
