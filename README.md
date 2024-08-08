
# RS485 zu MQTT Schnittstelle für den Tentek EMS
## Autor: Patrick Völker

Dieses Projekt bietet eine Schnittstelle zwischen RS485-Kommunikation und MQTT für den Tentek EMS Controller. Es ermöglicht dem EMS, mit einem MQTT-Broker zu kommunizieren, um verschiedene Topics zu veröffentlichen und zu abonnieren, was eine Fernsteuerung und -überwachung ermöglicht.

## Inhaltsverzeichnis
- [Übersicht](#übersicht)
- [Funktionen](#funktionen)
- [Setup und Installation](#setup-und-installation)
- [Konfiguration](#konfiguration)
- [Verwendung](#verwendung)
- [Protokollierung](#protokollierung)
- [MQTT-Topics](#mqtt-topics)
- [Funktionen im Detail](#funktionen-im-detail)
- [Threads](#threads)
- [Lizenz](#lizenz)

## Übersicht
Das Skript liest Daten von einem EMS über RS485, verarbeitet sie und veröffentlicht sie an einen MQTT-Broker. Es abonniert auch MQTT-Topics, um das EMS zu steuern.

## Funktionen
- Lesen und Schreiben von EMS-Registerwerten über RS485
- Veröffentlichen von EMS-Daten an MQTT-Topics
- Abonnieren von MQTT-Topics zur Steuerung der EMS-Einstellungen
- Protokollierung von Ereignissen und Fehlern

## Setup und Installation
### Benötigte Hardware
- Raspberry Pi
- SD-Karte
- [USB to RS485 Converter](https://www.amazon.de/dp/B081MZLY6G) oder [RS485 CAN HAT](https://www.amazon.de/gp/product/B09JKJCMHN)


### Voraussetzungen
- Python 3.x
- `pyserial` Bibliothek für RS485-Kommunikation
- `paho-mqtt` Bibliothek für MQTT-Kommunikation

### RS485 Verkabelung 
| EMS RS485                    | RPi RS485 (ohne 120 Ohm Widerstand)  | BMS RS485                                         |
|------------------------------|--------------------------------------|---------------------------------------------------|
| Pin 1                        | Anschluss A                          | Pin 6                                             |
| Pin 5                        | Anschluss B                          | Pin 5                                             |

## Konfiguration
### EMS Konfiguration
Setze die EMS-Nummer (falls mehrere EMS ausgelesen werden):
```python
EMS_Nr = "0001"
```

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

## MQTT Topics

Ersetze `{EMS_Nr}` durch die tatsächliche EMS-Nummer in allen Topics.

| Schreibende Topics (Abonnieren)                     | Beschreibung                          | Wert                                              |
|-----------------------------------------------------|---------------------------------------|---------------------------------------------------|
| solar/ems/{EMS_Nr}/EMS_EM/turn                      | EMS Nulleinspeisung ein-/ausschalten  | String ("on" oder "off")                          |
| solar/ems/{EMS_Nr}/EMS_Bypass/turn                  | EMS Bypass ein-/ausschalten           | String ("on" oder "off")                          |
| solar/ems/{EMS_Nr}/EMS_Power_Limit/set              | EMS Leistungsbegrenzung setzen        | Integer (0-1600 W)                                |

| Lesende Topics (Veröffentlichen)                    | Beschreibung                       | Wert                                              |
|-----------------------------------------------------|------------------------------------|---------------------------------------------------|
| solar/ems/{EMS_Nr}/EMS_Limit                        | EMS Leistungsgrenze                | String ("on" oder "off")                          |
| solar/ems/{EMS_Nr}/EMS_Power_Limit                  | EMS Leistungsbegrenzung            | Integer (Watt)                                    |
| solar/ems/{EMS_Nr}/EMS_Load_Power                   | EMS Lastleistung                   | Integer (Watt)                                    |
| solar/ems/{EMS_Nr}/EMS_EM                           | EMS Nulleinspeisung                | String ("on" oder "off")                          |
| solar/ems/{EMS_Nr}/EMS_Bypass                       | EMS Bypass                         | String ("on" oder "off")                          |
| solar/ems/{EMS_Nr}/EMS_Temperature                  | EMS Temperatur                     | Gleitkommazahl (in °C)                            |
| solar/ems/{EMS_Nr}/EMS_Load_Energy                  | EMS Lastenergie                    | Gleitkommazahl (in kWh)                           |
| solar/ems/{EMS_Nr}/MPPT1_Voltage                    | MPPT1 Spannung                     | Gleitkommazahl (in Volt)                          |
| solar/ems/{EMS_Nr}/MPPT1_Current                    | MPPT1 Strom                        | Gleitkommazahl (in Ampere)                        |
| solar/ems/{EMS_Nr}/MPPT1_Power                      | MPPT1 Leistung                     | Gleitkommazahl (in Watt)                          |
| solar/ems/{EMS_Nr}/MPPT1_Energy                     | MPPT1 Energie                      | Gleitkommazahl (in kWh)                           |
| solar/ems/{EMS_Nr}/MPPT2_Voltage                    | MPPT2 Spannung                     | Gleitkommazahl (in Volt)                          |
| solar/ems/{EMS_Nr}/MPPT2_Current                    | MPPT2 Strom                        | Gleitkommazahl (in Ampere)                        |
| solar/ems/{EMS_Nr}/MPPT2_Power                      | MPPT2 Leistung                     | Gleitkommazahl (in Watt)                          |
| solar/ems/{EMS_Nr}/MPPT2_Energy                     | MPPT2 Energie                      | Gleitkommazahl (in kWh)                           |
| solar/ems/{EMS_Nr}/MPPT_Total_Energy                | Gesamte MPPT Energie               | Gleitkommazahl (in kWh)                           |
| solar/ems/{EMS_Nr}/Battery_Online                   | Batterie Online                    | String ("Online" oder "Offline")                  |
| solar/ems/{EMS_Nr}/Battery_BMS_Online               | Batterie BMS Online                | String ("Online" oder "Offline")                  |
| solar/ems/{EMS_Nr}/Battery_SOC                      | Batterie Ladezustand (SOC)         | Integer (in %)                                    |
| solar/ems/{EMS_Nr}/Battery_Voltage                  | Batteriespannung                   | Gleitkommazahl (in Volt)                          |
| solar/ems/{EMS_Nr}/Battery_Charging_Power           | Batterie Ladeleistung              | Gleitkommazahl (in Watt)                          |
| solar/ems/{EMS_Nr}/Battery_Charging_Current         | Batterie Ladestrom                 | Gleitkommazahl (in Ampere)                        |
| solar/ems/{EMS_Nr}/Battery_Discharging_Power        | Batterie Entladeleistung           | Gleitkommazahl (in Watt)                          |
| solar/ems/{EMS_Nr}/Battery_Discharging_Current      | Batterie Entladestrom              | Gleitkommazahl (in Ampere)                        |
| solar/ems/{EMS_Nr}/Battery_Temperature              | Batterietemperatur                 | Gleitkommazahl (in °C)                            |
| solar/ems/{EMS_Nr}/Battery_Energy                   | Batterie Energie                   | Gleitkommazahl (in kWh)                           |
| solar/ems/{EMS_Nr}/Battery_BMS_Type                 | Batterie BMS Typ                   | String                                            |
| solar/ems/{EMS_Nr}/Battery_Type                     | Batterietyp                        | String                                            |
| solar/ems/{EMS_Nr}/Battery_Voltage_Type             | Batteriespannungstyp               | String                                            |
| solar/ems/{EMS_Nr}/Battery_Capacity                 | Batteriekapazität                  | Integer (in Ah)                                   |
| solar/ems/{EMS_Nr}/Battery_BMS_Max_Voltage          | Batterie BMS Maximalspannung       | Gleitkommazahl (in Volt)                          |
| solar/ems/{EMS_Nr}/Battery_BMS_Max_Current          | Batterie BMS Maximalstrom          | Gleitkommazahl (in Ampere)                        |
| solar/ems/{EMS_Nr}/Battery_BMS_Min_Voltage          | Batterie BMS Minimalspannung       | Gleitkommazahl (in Volt)                          |
| solar/ems/{EMS_Nr}/Battery_Max_Voltage              | Batterie Maximalspannung           | Gleitkommazahl (in Volt)                          |
| solar/ems/{EMS_Nr}/Battery_Max_Current              | Batterie Maximalstrom              | Gleitkommazahl (in Ampere)                        |
| solar/ems/{EMS_Nr}/Battery_Min_Voltage              | Batterie Minimalspannung           | Gleitkommazahl (in Volt)                          |
| solar/ems/{EMS_Nr}/EM_Online                        | EM Online                          | String ("Online" oder "Offline")                  |
| solar/ems/{EMS_Nr}/EM_A_Power                       | EM A Leistung                      | Gleitkommazahl (in Watt)                          |
| solar/ems/{EMS_Nr}/EM_A_Current                     | EM A Strom                         | Gleitkommazahl (in Ampere)                        |
| solar/ems/{EMS_Nr}/EM_A_Voltage                     | EM A Spannung                      | Gleitkommazahl (in Volt)                          |
| solar/ems/{EMS_Nr}/EM_B_Power                       | EM B Leistung                      | Gleitkommazahl (in Watt)                          |
| solar/ems/{EMS_Nr}/EM_B_Current                     | EM B Strom                         | Gleitkommazahl (in Ampere)                        |
| solar/ems/{EMS_Nr}/EM_B_Voltage                     | EM B Spannung                      | Gleitkommazahl (in Volt)                          |
| solar/ems/{EMS_Nr}/EM_C_Power                       | EM C Leistung                      | Gleitkommazahl (in Watt)                          |
| solar/ems/{EMS_Nr}/EM_C_Current                     | EM C Strom                         | Gleitkommazahl (in Ampere)                        |
| solar/ems/{EMS_Nr}/EM_C_Voltage                     | EM C Spannung                      | Gleitkommazahl (in Volt)                          |
| solar/ems/{EMS_Nr}/EM_Total_Power                   | Gesamte EM Leistung                | Gleitkommazahl (in Watt)                          |

## Funktionen im Detail
### `write_log(message, log_level)`
Schreibt Protokollnachrichten mit einer bestimmten Protokollierungsstufe.

### `on_connect(client, userdata, flags, rc)`
Behandelt die erfolgreiche Verbindung zum MQTT-Broker und abonniert Topics.

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
Veröffentlicht EMS-Daten an MQTT-Topics.

## Threads
### `read_ems()`
Überwacht und steuert EMS-Registerwerte basierend auf Flags.

### `publish_ems()`
Veröffentlicht neue EMS-Daten aus der Warteschlange an MQTT-Topics.

### `mqtt_read_loop()`
Führt die Ereignisschleife des MQTT-Clients aus.

## Lizenz
Dieses Projekt ist unter der MIT-Lizenz lizenziert. Siehe die [LICENSE](LICENSE) Datei für Details.
