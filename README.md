# MeshCore XIAO nRF52840 – Spezial-Gateway (EXPERIMENTELL)

Aufbau wie **RAW**, aber zusätzlich eigene CLI-Aliase und vorläufige PowerSafe-Logik. **Noch nicht auf XIAO-Hardware kompiliert oder getestet**. `powersafe` ist standardmäßig **OFF**. Bitte nicht unbeaufsichtigt auf Solarmasten verwenden, bevor Testbetrieb erfolgreich war.

## GitHub

ZIP entpacken, Inhalt in neues leeres GitHub-Repository hochladen (inkl. `.github`, `scripts`, `tests`). Unter **Actions → Build XIAO nRF52840 UART Bridge SPECIAL** starten. `meshcore_version=latest` sucht wie RAW das neueste **offizielle Repeater-Release**.

**Wichtig:** Der Firmware-Patch ist nur für `repeater-v1.18.0` freigegeben. Falls `latest` in Zukunft 1.19.0 auswählt, stoppt das Build bewusst. Ein Upgrade der Spezialversion verlangt vorher erneute technische Prüfung. Mit Eingabe `1.18.0` kannst du jederzeit den getesteten Quellstand auswählen. Dass Kompilierung erfolgreich ist, beweist nicht, dass der Wiederanlauf auf echter Hardware funktioniert.

## CLI (beide Boards separat)

```
set gateway on
set gateway off
get gateway
set powersafe on
set powersafe off
get powersafe
get powersafe.status
set powersafe.low 3450
set powersafe.high 3750
```

`gateway` ist ein Alias für das offizielle `bridge.enabled`, dessen Einstellung in MeshCore-Prefs gesichert wird. `powersafe` wird in eigener Datei im internen Dateisystem gesichert. Es ersetzt nicht MeshCores schon vorhandenes `powersaving`.

## PowerSafe – experimenteller Algorithmus

- Alle 30 Sekunden Batteriespannung über offiziellen XIAO-ADC-Pfad lesen.
- Drei aufeinanderfolgende Werte <= `powersafe.low` (Default 3450 mV): nur bei aktivem RX-Radio die UART-Bridge vorübergehend stoppen, SX1262 softwareseitig in Sleep bringen und MeshCore-/UART-Verarbeitung pausieren.
- Bei Messwerten >= `powersafe.high` (Default 3750 mV) über 300 Sekunden: Radio-Hardware und Wrapper neu initialisieren, UART-Bridge nur wieder anschalten, falls `gateway` aktiviert ist.
- `set powersafe off` holt den Funkbetrieb auf der nächsten Messrunde aus dem Schlaf (sofern die Hardware reinitialisiert werden kann).
- Invalides ADC-Ergebnis führt nicht zum Abschalten. Kein Messwert kann einen extern abgeschalteten TP4056-Ausgang wieder einschalten.
- Zwischen den beiden Boards findet **keine** automatische PowerSafe-Synchronisierung statt. Da sie denselben 1S2P-Akku nutzen, sollten die Schwellwerte gleich gesetzt sein. ADC-Toleranzen verursachen leicht unterschiedliche Schaltpunkte.

### Einschränkungen (vor Einsatz prüfen)

Diese Firmware ist ein **Prototyp**: RadioLib-Reinitialisierung nach SX1262-Sleep, unterbrochene Aussendung, UART-Buffer und ausstehende MeshCore-Sendequeues müssen auf echter Hardware untersucht werden. Der nRF52840 läuft im PowerSafe-Modus zunächst weiter: das ist **kein vollständiger Tiefschlaf** und die Stromersparnis des Gesamtsystems ist noch nicht gemessen. Bei vollem Akku und ausgeschaltetem PowerSafe unterscheidet sie sich fast nicht von RAW.

## Hardware

Zwei *fachgerecht parallelgeschaltete* 2.000-mAh-1S-LiPo-Zellen (zusammen nominell 4.000 mAh) über **einen** TP4056 mit Schutzplatine, beide XIAOs am geschützten BAT-Ausgang. Gleiche Polung, angeglichene Zellspannungen, geeignete Schutz- und Ladeauslegung. Der TP4056 ist kein Solar-Power-Path. **USB-Laden über die XIAOs beim gemeinsamen TP4056-Akku vermeiden**. BAT ist nicht identisch mit 3V3.

## Tests vor Solar-Einsatz

1. Beide XIAOs zunächst am USB mit getrenntem, sicherem Testaufbau (keine konkurrierenden Lader) prüfen und ohne Powersafe UART in beide Richtungen testen.
2. Spannung mit geeignetem Labornetzteil *am BAT-Eingang innerhalb des zulässigen Bereichs* langsam reduzieren; `get powersafe.status`, SX-Sleep und UART-Stopp prüfen. Nicht ungeschützt an LiPo-Packs experimentieren.
3. Versorgung langsam anheben, 5 Minuten abwarten; Funkempfang/-sendung, UART und CLI prüfen.
4. Test mit Geräteneu-Start, Fehlerfall, PowerSafe OFF, Recovery und mehrfachem A↔B-Paketverkehr wiederholen. Bei unzuverlässigem Verhalten **RAW** benutzen.

## Update

`latest` nur mit strikter Sicherheitsfreigabe: unabhängig vom neusten Tag wird SPECIAL niemals ungeprüft auf einen anderen Upstream-Release gepatcht. `build_info.txt` enthält genauen Tag/Commit.
