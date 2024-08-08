
# RS485 zu MQTT Schnittstelle für den Tentek EMS
## Autor: Patrick Völker

Dieses Projekt bietet eine Schnittstelle zwischen RS485-Kommunikation und MQTT für den Tentek EMS Controller. Es ermöglicht dem EMS, mit einem MQTT-Broker zu kommunizieren, um verschiedene Themen zu veröffentlichen und zu abonnieren, was eine Fernsteuerung und -überwachung ermöglicht.

## Inhaltsverzeichnis
- [Übersicht](#übersicht)
- [Funktionen](#funktionen)
- [Setup und Installation](#setup-und-installation)
- [Konfiguration](#konfiguration)
- [Verwendung](#verwendung)
- [Protokollierung](#protokollierung)
- [Funktionen im Detail](#funktionen-im-detail)
- [Threads](#threads)
- [Lizenz](#lizenz)

## Übersicht
Das Skript liest Daten von einem EMS über RS485, verarbeitet sie und veröffentlicht sie an einen MQTT-Broker. Es abonniert auch MQTT-Themen, um das EMS zu steuern.

## Funktionen
- Lesen und Schreiben von EMS-Registerwerten über RS485
- Veröffentlichen von EMS-Daten an MQTT-Themen
- Abonnieren von MQTT-Themen zur Steuerung der EMS-Einstellungen
- Protokollierung von Ereignissen und Fehlern

## Setup und Installation
### Voraussetzungen
- Python 3.x
- `pyserial` Bibliothek für RS485-Kommunikation
- `paho-mqtt` Bibliothek für MQTT-Kommunikation

## Konfiguration
### RS485 Konfiguration
Setze die Parameter des RS485-Seriellen Ports:
```python
RS485_PORT = "/dev/ttyUSB0"
```

### MQTT Konfiguration
Setze die Verbindungsparameter des MQTT-Brokers:
```python
MQTT_BROKER = "192.168.178.123"
MQTT_PORT = 1883
MQTT_USERNAME = "mqtt"
MQTT_PASSWORD = "12345"
```

### Protokollierungskonfiguration
Setze die Protokollierungsparameter:
```python
LOG_LEVEL = logging.INFO
LOG_FILE = "/home/pi/ems_mqtt/your_script_name.log"
```

## Verwendung
1. Stelle sicher, dass dein EMS-Gerät an den RS485-Port angeschlossen ist.
2. Führe das Skript aus:
   ```bash
   python ems_rs485_to_mqtt.py
   ```

## Protokollierung
Das Skript protokolliert verschiedene Ereignisse und Fehler. Die Protokolldatei wird durch die Variable `LOG_FILE` angegeben.

### Protokollierungsstufen
- `DEBUG`: Detaillierte Informationen zur Diagnose von Problemen.
- `INFO`: Bestätigung, dass alles wie erwartet funktioniert.
- `WARNING`: Ein Hinweis darauf, dass etwas Unerwartetes passiert ist.
- `ERROR`: Ein ernsteres Problem.
- `CRITICAL`: Ein sehr ernstes Problem.

## Funktionen im Detail
### `write_log(message, log_level)`
Schreibt Protokollnachrichten mit einer bestimmten Protokollierungsstufe.

### `on_connect(client, userdata, flags, rc)`
Behandelt die erfolgreiche Verbindung zum MQTT-Broker und abonniert Themen.

### `on_message(client, userdata, msg)`
Verarbeitet empfangene MQTT-Nachrichten.

### `on_disconnect(client, userdata, rc)`
Behandelt unerwartete Trennungen und versucht, die Verbindung wiederherzustellen.

### `process_mqtt_message(topic, message)`
Verarbeitet spezifische MQTT-Nachrichten zur Aktualisierung der EMS-Einstellungen.

### `is_valid_EMS_Power_Limit(value)`
Überprüft, ob ein gegebener EMS-Leistungsbegrenzungswert gültig ist.

### `calculate_crc(data)`
Berechnet die CRC-16-Prüfsumme für ein gegebenes Datenarray.

### `construct_frame(boot_code, device_address, function_code, register_address, register_count)`
Konstruiert einen Modbus-Rahmen.

### `send_frame(frame)`
Sendet einen Modbus-Rahmen über die serielle Schnittstelle.

### `receive_response(frame_base)`
Empfängt und validiert eine Modbus-Antwort.

### `request_ems(register_address, register_count)`
Fordert EMS-Registerwerte an und verarbeitet sie.

### `write_ems(register_address, register_count, register_data)`
Schreibt Daten in EMS-Register.

### `parse_response(response, frame_base, register_count)`
Analysiert und validiert eine Modbus-Antwort.

### `ems_parse_value(value_address, value)`
Interpretiert und konvertiert EMS-Registerwerte.

### `ems_publish_data(value_address, parsed_value)`
Veröffentlicht EMS-Daten an MQTT-Themen.

## Threads
### `read_ems()`
Überwacht und steuert EMS-Registerwerte basierend auf Flags.

### `publish_ems()`
Veröffentlicht neue EMS-Daten aus der Warteschlange an MQTT-Themen.

### `mqtt_read_loop()`
Führt die Ereignisschleife des MQTT-Clients aus.

## Lizenz
Dieses Projekt ist unter der MIT-Lizenz lizenziert. Siehe die [LICENSE](LICENSE) Datei für Details.
