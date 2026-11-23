# Meshcore Gateway

**Bidirektionale UART-Bridge für zwei MeshCore-Repeater auf Seeed XIAO nRF52840 mit Wio-SX1262.**

> **Projektstatus:** Community-Build-Rezept / experimentell. Die enthaltenen Skripte wurden lokal geprüft, aber ein erfolgreicher vollständiger PlatformIO-Build und ein Praxistest mit zwei Boards sind für dieses Paket noch nicht nachgewiesen. Dies ist **keine offizielle MeshCore-Firmware**.

## Was ist das?

Dieses Repository erstellt per **GitHub Actions** eine angepasste Repeater-Firmware aus dem **offiziellen MeshCore-Quellcode**. Die vorhandene RS232/UART-Bridge wird für den XIAO nRF52840 mit Wio-SX1262 aktiviert. Dabei wird **keine eigene Paket- oder Routinglogik** in MeshCore eingepatcht.

Zwei Repeater können so jeweils mit einer eigenen Funkkonfiguration arbeiten (Frequenz, Bandbreite, Spreading Factor, Coding Rate) und MeshCore-Pakete über ein 3,3-V-UART-Kabel miteinander austauschen – **ohne PC oder Raspberry Pi im Dauerbetrieb**.

```text
MeshCore-Netz A                UART                  MeshCore-Netz B
Frequenz / SF / CR A                                  Frequenz / SF / CR B
       ~~~>  XIAO A (Repeater) <==== TX/RX ====> XIAO B (Repeater)  <~~~
                    |                 |                 |
                  SX1262           GND               SX1262
```

Das Paket wurde für den Betrieb mit **zwei** XIAO-Boards entworfen. Die Firmware kann auf **beiden** Boards identisch sein; ihre Funkparameter werden anschließend getrennt konfiguriert.

### Enthaltene Anpassung gegenüber MeshCore

- Zusätzliche PlatformIO-Umgebung `Xiao_nrf52_repeater_rs232` mit `WITH_RS232_BRIDGE=Serial1`.
- UART-Belegung `D6 = TX`, `D7 = RX` und Einbindung der offiziellen `RS232Bridge.cpp`.
- GitHub-Actions-Workflow zur automatisierten Auswahl eines offiziellen Repeater-Releases, zum Build und zur Ausgabe der Firmware-Artefakte.
- Vorabtests für Rezeptstruktur und grundlegende Upstream-Kompatibilität.

**Nicht enthalten:** zusätzliche `gateway`- oder `powersafe`-CLI-Befehle, Low-Battery-Sleep, Regions-Umschreibung oder ein eigenständiger Paketfilter. Dafür gibt es die separate Variante **Meshcore Gateway - Advanced**.

## Voraussetzungen

- 2 × [Seeed XIAO nRF52840 + Wio-SX1262](https://wiki.seeedstudio.com/xiao_nrf52840%26_wio_SX1262_kit_for_meshtastic/)
- 3 UART-Leitungen und eine passende 3,3-V-Versorgung
- GitHub-Repository mit aktivierten Actions
- Kenntnisse zum Flashen des nRF52840 sowie zur MeshCore-Repeater-Konfiguration

## Verdrahtung

| XIAO A | XIAO B | Bedeutung |
|---|---|---|
| **D6 / TX** | **D7 / RX** | A → B |
| **D7 / RX** | **D6 / TX** | B → A |
| **GND** | **GND** | Gemeinsame Masse |

Es handelt sich um **3,3-V-UART (TTL)**, **nicht** um ±12-V-RS232. Bei getrennten Stromquellen die Versorgungsschienen **nicht** zusätzlich verbinden. Bei gemeinsamer Batterie auf eine fachgerechte Schutz- und Ladeauslegung achten.

## Build über GitHub Actions

1. Ein neues GitHub-Repository erstellen.
2. Dieses Paket **entpacken** und den **Inhalt** direkt ins Repository-Hauptverzeichnis laden. `.github/workflows/build.yml` muss am angegebenen Pfad liegen – **keinen zusätzlichen `recipe/`-Ordner** erstellen.
3. Änderungen committen; ggf. GitHub Actions für das Repository aktivieren.
4. Unter **Actions → Build Meshcore Gateway → Run workflow** den Workflow starten.
5. Im Eingabefeld `meshcore_version` entweder `1.18.0` für einen reproduzierbaren Ausgangspunkt oder `latest` auswählen.
6. Nach erfolgreichem Build das **Artifact** des Workflow-Laufs herunterladen. Es enthält `firmware.uf2`, `firmware.bin` und `build_info.txt`.

`firmware.uf2` ist für einen **kompatiblen nRF52840-UF2-Bootloader** vorgesehen. `firmware.bin` ist die reine Anwendungs-Binärdatei für geeignete alternative Flashwege. Die hier beschriebene Build-Pipeline flasht selbst kein Gerät. `build_info.txt` dokumentiert verwendeten Upstream-Tag und Git-Commit.

**Wichtig:** Ein grüner Workflow zeigt einen erfolgreichen Build, noch keinen bestätigten UART-, LoRa- oder Batteriebetrieb auf echter Hardware.

## Konfiguration der beiden Repeater

Beide XIAOs erhalten eine eigene LoRa-Konfiguration über die **offizielle MeshCore-CLI**. Danach auf **beiden** Geräten beispielsweise:

```text
get bridge.type
set bridge.baud 115200
set bridge.source tx
set bridge.enabled on
set repeat on
```

`bridge.source tx` bestimmt, **welche lokalen Pakete zur Bridge gespiegelt werden**: diejenigen, die der Repeater tatsächlich zur LoRa-Aussendung auswählt. Es setzt die UART-Verbindung **nicht** auf unidirektional; TX und RX sind über Kreuz verdrahtet und die Bridge kann in **beide** Richtungen arbeiten. **Hinweis zu MeshCore 1.18.0:** `get bridge.source` zeigt den TX-Modus als `logTx` an, obwohl der hier verwendete Set-Befehl `tx` lautet.

Mit `set bridge.enabled off` lässt sich die UART-Bridge an einem Board abschalten, während das Gerät normaler Repeater bleiben kann. Für eine kontrollierte Abschaltung des gesamten Gateways beide Seiten deaktivieren. Die Regions-Konfiguration und Funkparameter bleiben getrennte MeshCore-Einstellungen; konkrete Befehle stehen in der verlinkten offiziellen CLI-Referenz.

### Verhalten von Paketen und Regions

- Die Bridge **übersetzt keine Regions** und erzeugt keine neue Nachricht im Namen des Gateways.
- MeshCore-Routing, Pfade und Duplikaterkennung arbeiten weiterhin nach den Regeln der jeweils ausgecheckten Firmware.
- `bridge.source tx` ist **kein strenger Firewall- oder Whitelist-Filter**. Insbesondere Direct Messages können nicht allein über Flood-Regions gefiltert werden.
- Mehrere parallel betriebene Gateways können dieselbe Nachricht mehrfach über Funk aussenden; die normale Duplikaterkennung unterdrückt Kopien nur, solange die zugehörigen Einträge noch gespeichert sind. Vermeidung jeglicher Funkduplikate wird **nicht garantiert**.

## Testempfehlung

1. Zunächst nur zwei Boards verwenden und mit unterschiedlichen LoRa-Profilen einrichten.
2. Die drei UART-Leitungen verbinden und `get bridge.type` kontrollieren.
3. Nachrichten **A → B** und **B → A** testen; TX/RX-Verwechslungen ausschließen.
4. Erlaubte und gesperrte Flood-Regions testen sowie Direct Messages separat betrachten.
5. Erst danach weitere Gateways hinzufügen und Duplikate, Schleifen sowie Airtime beobachten.

## Versionsverwaltung

Das Build-Rezept enthält **keine Kopie der MeshCore-Firmware**. Es checkt den offiziellen Quellcode bei jedem Lauf neu aus:

| `meshcore_version` | Verhalten |
|---|---|
| `1.18.0` | Baut `repeater-v1.18.0` aus dem offiziellen Repository |
| `latest` | Sucht den numerisch höchsten offiziellen Tag `repeater-vX.Y.Z` (keine Entwicklungs-Branches) |

**Automatisch neuester Release bedeutet nicht automatisch kompatibel.** Ein neuer Tag kann APIs oder das Boardlayout verändern. Bei fehlenden Quellcode-Ankern oder Buildfehlern stoppt der Workflow; auch ein erfolgreicher Build muss vor einem produktiven Update getestet werden. Für reproduzierbare Installationen immer `build_info.txt` aufbewahren.

## Stromversorgung und Sicherheit

Die Gateway-Firmware bietet **keine eigene Unterspannungsabschaltung**. Bei Solar- und Batteriebetrieb gelten die Schutzfunktionen der Hardware sowie der offiziellen MeshCore-Firmware. Ein TP4056 ist **kein MPPT-Solarlader** und garantiert nach Tiefentladung keinen sauberen Neustart. Bei gemeinsamer 1S2P-LiPo-Versorgung nur fachgerecht aufgebaute, geschützte Akkupacks verwenden und konkurrierende USB-/TP4056-Ladevorgänge vermeiden. Frequenz, Sendeleistung und Duty Cycle müssen den lokalen Vorschriften entsprechen.

## Projektdateien

| Datei | Zweck |
|---|---|
| `.github/workflows/build.yml` | Build, UF2-Konvertierung und Artifact-Upload |
| `platformio.local.ini` | zusätzliche XIAO-Repeater-Umgebung mit UART-Bridge |
| `scripts/resolve_version.sh` | offizielle Repeater-Version auswählen |
| `scripts/check_compat.py` | grundlegende Upstream-Schnittstellen prüfen |
| `tests/` | lokale Rezepttests |

## Quellen und weiterführende Dokumentation

1. [MeshCore – offizielles Quellcode-Repository](https://github.com/meshcore-dev/MeshCore)
2. [Offizielle MeshCore-Releases](https://github.com/meshcore-dev/MeshCore/releases)
3. [MeshCore CLI-Referenz, Release 1.18.0](https://github.com/meshcore-dev/MeshCore/blob/repeater-v1.18.0/docs/cli_commands.md)
4. [RS232Bridge.cpp, offizieller Quellcode v1.18.0](https://github.com/meshcore-dev/MeshCore/blob/repeater-v1.18.0/src/helpers/bridges/RS232Bridge.cpp)
5. [MeshCore-Diskussion zur seriellen Repeater-Bridge](https://github.com/meshcore-dev/MeshCore/discussions/2957)
6. [Seeed Studio: XIAO nRF52840 + Wio-SX1262 Kit](https://wiki.seeedstudio.com/xiao_nrf52840%26_wio_SX1262_kit_for_meshtastic/)
7. [Seeed Studio: XIAO nRF52840 Pinbelegung](https://wiki.seeedstudio.com/XIAO_BLE/)
8. [GitHub Actions – Dokumentation](https://docs.github.com/en/actions)

## Credits, Lizenz und Hinweis

**Projektidee, Anforderungen und Praxiskonzept:** Projektinitiator / Repository-Betreiber.  
**Erstellung des Build-Rezepts, der Konfiguration, Tests und Dokumentation:** gemeinsam mit **ChatGPT von OpenAI (GPT-6)** im interaktiven Entwicklungsprozess. Die Inhalte wurden KI-gestützt erstellt und sind keine offizielle Freigabe oder Qualitätssicherung durch OpenAI.

**MeshCore selbst** stammt vom Projekt [meshcore-dev](https://github.com/meshcore-dev/MeshCore) und seinen Mitwirkenden (Upstream-Lizenz: [MIT](https://github.com/meshcore-dev/MeshCore)). Dieses Repository ist ein **inoffizielles Community-Build-Rezept**, kein offizielles Produkt von MeshCore, Seeed oder OpenAI. Bitte die Lizenzbedingungen der verwendeten Quellcode-Version beachten.
