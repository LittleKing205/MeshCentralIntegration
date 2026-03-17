# MeshCentral Home Assistant Integration

[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Integration-18BCF2.svg)](https://www.home-assistant.io/)

Die Integration verbindet MeshCentral mit Home Assistant und stellt geraetebezogene Entitaeten sowie Services bereit.

## Funktionen

- Konfiguration ueber Home Assistant UI (Config Flow), keine YAML-Konfiguration erforderlich.
- Power-Status als `binary_sensor`.
- Batterie, letzter Boot-Zeitpunkt, eingeloggte Benutzer und IP als Sensoren.
- Sicherheitsbezogene Binary Sensoren (z. B. Laden, Windows Security Center, Defender RTP).
- Services zum Senden von Power-Befehlen und Benachrichtigungen an MeshCentral-Geraete.

## Installation

### Option 1: HACS (empfohlen)

1. HACS in Home Assistant installieren (falls noch nicht vorhanden).
2. In HACS zu Integrationen wechseln.
3. Dieses Repository als benutzerdefiniertes Repository vom Typ Integration hinzufuegen.
4. `MeshCentral` installieren.
5. Home Assistant neu starten.

### Option 2: Manuell

1. Den Ordner `custom_components/meshcentral` in dein Home-Assistant-Config-Verzeichnis kopieren.
2. Home Assistant neu starten.

## Einrichtung

1. In Home Assistant: Einstellungen -> Geraete & Dienste -> Integration hinzufuegen.
2. Nach `MeshCentral` suchen.
3. Folgende Daten eintragen:
	 - URL (z. B. `localhost:5222`)
	 - Benutzername
	 - Passwort
	 - SSL aktivieren/deaktivieren

## Entitaeten

Je nach MeshCentral-Knoten koennen unter anderem diese Entitaeten erstellt werden:

- Binary Sensoren: Power, Battery Charging, WSC/Defender-Zustaende
- Sensoren: Battery (%), Last Boot, Logged-in Users, IP

## Dienste

Die Integration registriert u. a. folgende Dienste:

- `meshcentral.power`
	- Modi: `wake`, `off`, `sleep`, `reset`
- `meshcentral.notify`
	- Nachricht an ein MeshCentral-Geraet senden

## Hinweise

- Diese Integration ist nicht offiziell von Home Assistant oder MeshCentral.
- Bei Verbindungsproblemen URL/SSL-Kombination und Zugangsdaten pruefen.

## Support

- Dokumentation: https://github.com/LittleKing205/MeshCentralIntegration
- Issues: https://github.com/LittleKing205/MeshCentralIntegration/issues
