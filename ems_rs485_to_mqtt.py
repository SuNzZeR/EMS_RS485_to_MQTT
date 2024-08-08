################################################################################
#                        RS485 zu MQTT Schnittstelle für EMS                   #
#                               Autor: Patrick Völker                          #
################################################################################
import serial
import time
import struct
import paho.mqtt.client as mqtt
from datetime import datetime
import threading
import logging
import queue

################################################################################
#                                   Variablen                                  #
################################################################################
# EMS
device_address = 0x01
EMS_Nr = "0001";

# Logging
LOG_LEVEL = logging.INFO
LOG_FILE = "/home/pi/ems_mqtt/your_script_name.log"
LOG_LEVEL_NAMES = {
    logging.NOTSET: 'NOTSET',
    logging.DEBUG: 'DEBUG',
    logging.INFO: 'INFO',
    logging.WARNING: 'WARNING',
    logging.ERROR: 'ERROR',
    logging.CRITICAL: 'CRITICAL'
}

# RS485
RS485_PORT = "/dev/ttyUSB0"
RS485_BAUD_RATE = 9600
RS485_PARITY = serial.PARITY_NONE
RS485_STOPBITS = serial.STOPBITS_ONE
RS485_BYTESIZE = serial.EIGHTBITS

# MQTT
MQTT_BROKER = "192.168.178.123"
MQTT_PORT = 1883
MQTT_USERNAME = "mqtt"
MQTT_PASSWORD = "12345"

# EMS Steuerung
EMS_EM_FLG = False
EMS_EM_Value = 0x0000

EMS_Bypass_FLG = False
EMS_Bypass_Value = 0x0000

EMS_Power_Limit_FLG = False
EMS_Power_Limit_Value = 0x0000

################################################################################
#                                  Funktionen                                  #
################################################################################

################################################################################
# Funktion zum Schreiben von Protokollnachrichten
# Diese Funktion erstellt eine Protokollnachricht mit einem bestimmten
# Protokollierungsgrad und gibt sie je nach festgelegtem Protokollierungsgrad aus.
# Die Nachricht wird mit einem Zeitstempel und dem Protokollierungsgrad versehen.
#
# Parameter:
# - message: Die zu protokollierende Nachricht.
# - log_level: Der Protokollierungsgrad der Nachricht (DEBUG, INFO, WARNING, ERROR, CRITICAL).
def write_log(message, log_level):
    
    # Holt den Namen des Protokollierungsgrads.
    log_level_text = LOG_LEVEL_NAMES.get(log_level)
    
    # Formatiert die Nachricht mit dem aktuellen Zeitstempel und dem Protokollierungsgrad.
    message = f"{datetime.now()}: {log_level_text}: {message}"
    
    # Gibt die Nachricht aus, wenn der Protokollierungsgrad größer oder gleich dem festgelegten Grad ist.
    if log_level >= LOG_LEVEL:
    
        print(message)
    
    # Schreibt die Nachricht in das entsprechende Protokoll basierend auf dem Protokollierungsgrad.
    if log_level == logging.DEBUG:
    
        logging.debug(message)
            
    elif log_level == logging.INFO:
    
        logging.info(message)
            
    elif log_level == logging.WARNING:
    
        logging.warning(message)
            
    elif log_level == logging.ERROR:
    
        logging.error(message)
            
    elif log_level == logging.CRITICAL:
    
        logging.critical(message)

################################################################################
# Funktion für die MQTT-Verbindung
# Diese Funktion wird aufgerufen, wenn der Client erfolgreich eine Verbindung zum MQTT-Broker hergestellt hat.
# Sie protokolliert den Verbindungsstatus und abonniert alle relevanten Themen.
#
# Parameter:
# - client: Das Client-Objekt, das die Verbindung initiiert hat.
# - userdata: Vom Benutzer definierte Daten, die dem Client zugeordnet sind.
# - flags: Antwortflags vom Broker.
# - rc: Rückgabecode der Verbindungsanfrage.
def on_connect(client, userdata, flags, rc):
    
    # Definiert mögliche Rückgabecodes und ihre entsprechenden Nachrichten.
    connection_results = {
        0: "Connection successful",
        1: "Connection refused - incorrect protocol version",
        2: "Connection refused - invalid client identifier",
        3: "Connection refused - server unavailable",
        4: "Connection refused - bad username or password",
        5: "Connection refused - not authorised"
    }
    
    # Abonniert relevante Themen für den Client.
    client.subscribe("solar/ems/" + EMS_Nr + "/EMS_EM/turn")
    client.subscribe("solar/ems/" + EMS_Nr + "/EMS_Bypass/turn")
    client.subscribe("solar/ems/" + EMS_Nr + "/EMS_Power_Limit/set")
    
    # Überprüft den Rückgabecode und protokolliert entsprechend den Verbindungsstatus.
    if rc == 0:
    
        write_log(f"MQTT - Connected to MQTT broker with result code {rc}: {connection_results.get(rc)}", logging.INFO)
        write_log(f"MQTT - Client: {client}, Userdata: {userdata}, Flags: {flags}", logging.DEBUG)
        
    else:
    
        write_log(f"MQTT - Failed to connect to MQTT broker with result code {rc}: {connection_results.get(rc, 'Unknown error')}", logging.CRITICAL)
        write_log(f"MQTT - Client: {client}, Userdata: {userdata}, Flags: {flags}", logging.DEBUG)
        
        running.clear()

# Funktion zur Verarbeitung empfangener MQTT-Nachrichten
# Diese Funktion wird aufgerufen, wenn der Client eine Nachricht von einem abonnierten Thema empfängt.
# Sie protokolliert die empfangene Nachricht und leitet sie zur weiteren Verarbeitung weiter.
#
# Parameter:
# - client: Das Client-Objekt, das die Nachricht empfangen hat.
# - userdata: Vom Benutzer definierte Daten, die dem Client zugeordnet sind.
# - msg: Die empfangene Nachricht, die das Thema und den Payload enthält.
def on_message(client, userdata, msg):
    
    # Protokolliert die empfangene Nachricht.
    write_log(f"MQTT - Message received: {msg.topic} - {msg.payload}", logging.DEBUG)
    
    # Verarbeitet die empfangene Nachricht weiter.
    process_mqtt_message(msg.topic, msg.payload)

# Funktion zur Handhabung der MQTT-Trennung
# Diese Funktion wird aufgerufen, wenn der Client die Verbindung zum MQTT-Broker verliert.
# Sie protokolliert unerwartete Trennungen und versucht, die Verbindung wiederherzustellen.
#
# Parameter:
# - client: Das Client-Objekt, das die Verbindung verloren hat.
# - userdata: Vom Benutzer definierte Daten, die dem Client zugeordnet sind.
# - rc: Rückgabecode der Trennung.
def on_disconnect(client, userdata, rc):
    
    # Überprüft, ob die Trennung unerwartet war (Rückgabecode ungleich 0).
    if rc != 0:
    
        write_log("MQTT - Unexpected disconnection. Trying to reconnect...", logging.WARNING)
        
        try:
        
             # Versucht, die Verbindung wiederherzustellen.
            client.reconnect()
            
        except Exception as e:
        
            # Protokolliert, wenn der Verbindungsversuch fehlschlägt, und führt eine Fehlerbehandlung durch.
            write_log(f"MQTT - Reconnect failed: {e}", logging.CRITICAL)
            
            running.clear()

################################################################################
# Funktion zur Verarbeitung spezifischer MQTT-Nachrichten
# Diese Funktion wird aufgerufen, um empfangene MQTT-Nachrichten basierend auf ihrem Thema und Inhalt zu verarbeiten.
# Sie aktualisiert globale Variablen und protokolliert entsprechende Aktionen.
#
# Parameter:
# - topic: Das Thema der empfangenen Nachricht.
# - message: Die empfangene Nachricht, die den Payload enthält.
def process_mqtt_message(topic, message):
    
    # Globale Variablen für EMS-Status und Werte.
    global EMS_EM_FLG
    global EMS_EM_Value
    global EMS_Bypass_FLG
    global EMS_Bypass_Value
    global EMS_Power_Limit_FLG
    global EMS_Power_Limit_Value
    
    # Dekodiert die empfangene Nachricht.
    decoded_message = message.decode('utf-8')
    
    # Verarbeitet Nachrichten für das Thema "EMS_EM/turn".
    if topic == "solar/ems/" + EMS_Nr + "/EMS_EM/turn" and decoded_message == "on":
        EMS_EM_FLG = True
        EMS_EM_Value = 1
        write_log(f"EMS - EMS_EM turn on is set", logging.INFO)
    elif topic == "solar/ems/" + EMS_Nr + "/EMS_EM/turn" and decoded_message == "off":
        EMS_EM_FLG = True
        EMS_EM_Value = 0
        write_log(f"EMS - EMS_EM turn off is set", logging.INFO)
    
    # Verarbeitet Nachrichten für das Thema "EMS_Bypass/turn".
    elif topic == "solar/ems/" + EMS_Nr + "/EMS_Bypass/turn" and decoded_message == "on":
        EMS_Bypass_FLG = True
        EMS_Bypass_Value = 1
        write_log(f"EMS - EMS_Bypass turn on is set", logging.INFO)
    elif topic == "solar/ems/" + EMS_Nr + "/EMS_Bypass/turn" and decoded_message == "off":
        EMS_Bypass_FLG = True
        EMS_Bypass_Value = 0
        write_log(f"EMS - EMS_Bypass turn off is set", logging.INFO)
    
    # Verarbeitet Nachrichten für das Thema "EMS_Power_Limit/set".
    elif topic == "solar/ems/" + EMS_Nr + "/EMS_Power_Limit/set" and is_valid_EMS_Power_Limit(decoded_message):
        EMS_Power_Limit_FLG = True
        EMS_Power_Limit_Value = int(decoded_message)
        write_log(f"EMS - EMS_Power_Limit change to {EMS_Power_Limit_Value}W is set", logging.INFO)

# Funktion zur Überprüfung der Gültigkeit eines EMS-Leistungsbegrenzungswerts
# Diese Funktion überprüft, ob ein gegebener Wert ein gültiger Leistungsbegrenzungswert
# für das EMS ist. Ein gültiger Wert muss eine Ganzzahl zwischen 0 und 1600 (einschließlich) sein.
#
# Parameter:
# - value: Der zu überprüfende Wert.
#
# Rückgabewert:
# - is_valid: Ein boolescher Wert, der angibt, ob der Wert gültig ist (True) oder nicht (False).
def is_valid_EMS_Power_Limit(value):
    
    is_valid = False
    
    try:
    
        # Versucht, den Wert in eine Ganzzahl umzuwandeln.
        value = int(value)
        
        # Überprüft, ob der Wert im gültigen Bereich liegt.
        if 0 <= value <= 1600:
        
            is_valid = True
            
        else:
        
            is_valid = False
            
    except ValueError:
    
        # Setzt is_valid auf False, wenn eine Umwandlung in eine Ganzzahl fehlschlägt.
        is_valid = False
    
    return is_valid

################################################################################
# Funktion zur Berechnung der CRC-16-Prüfsumme
# Diese Funktion berechnet die CRC-16-Prüfsumme für ein gegebenes Datenarray.
# Das CRC-Verfahren wird verwendet, um die Integrität von Daten zu überprüfen.
#
# Parameter:
# - data: Ein Array von Bytes, für das die CRC-Prüfsumme berechnet werden soll.
#
# Rückgabewert:
# - crc: Die berechnete CRC-16-Prüfsumme.
def calculate_crc(data):
    
    crc = 0xFFFF
    
    for pos in data:
    
        crc ^= pos
        
        for i in range(8):
        
            if (crc & 0x0001) != 0:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
                
    return crc
    
# Funktion zur Konstruktion eines Modbus-Rahmens
# Diese Funktion erstellt einen Modbus-Rahmen basierend auf den angegebenen Parametern.
# Ein Modbus-Rahmen enthält Steuerinformationen, die an ein Gerät gesendet werden.
#
# Parameter:
# - boot_code: Eine Liste von Initialisierungsbytes.
# - device_address: Die Adresse des Zielgeräts.
# - function_code: Der Funktionscode, der die Art der Operation angibt.
# - register_address: Die Adresse des Registers, auf das zugegriffen werden soll.
# - register_count: Die Anzahl der Register, auf die zugegriffen werden soll.
#
# Rückgabewert:
# - message: Ein Byte-Array, das den vollständigen Modbus-Rahmen darstellt.
def construct_frame(boot_code, device_address, function_code, register_address, register_count):
    
    # Erstellt die Nachricht durch Kombination der Parameter in der richtigen Reihenfolge.
    message = boot_code + [device_address, function_code] + \
              list(struct.pack('>H', register_address)) + \
              list(struct.pack('>H', register_count))
              
    # Gibt die Nachricht als Byte-Array zurück
    return bytes(message)

# Funktion zum Senden eines Modbus-Rahmens
# Diese Funktion sendet einen vorbereiteten Modbus-Rahmen über eine serielle Schnittstelle.
# Sie protokolliert den gesendeten Rahmen im Hexadezimalformat und schreibt ihn in den seriellen Puffer.
#
# Parameter:
# - frame: Der zu sendende Modbus-Rahmen als Byte-Array.
def send_frame(frame):
    
    # Protokolliert den zu sendenden Rahmen im Hexadezimalformat.
    write_log(f"EMS - Sending frame: {frame.hex()}", logging.DEBUG)
    
    # Schreibt den Rahmen in den seriellen Puffer.
    ser.write(frame)

# Funktion zum Empfangen und Validieren einer Modbus-Antwort
# Diese Funktion liest die Antwort von der seriellen Schnittstelle und prüft,
# ob sie mit dem Basisrahmen übereinstimmt. Sie versucht bis zu dreimal,
# eine gültige Antwort zu empfangen.
#
# Parameter:
# - frame_base: Der Basisrahmen der gesendeten Nachricht, gegen den die Antwort validiert wird.
#
# Rückgabewert:
# - response: Der empfangene Antwortrahmen als Byte-Array.
def receive_response(frame_base):
    
    found = False
    count = 0
    response = ""
    
    while found == False and count < 3 and running.is_set():
    
        # Liest alle verfügbaren Daten aus der seriellen Schnittstelle.
        response = ser.readall()
        
        # Extrahiert den Basisrahmen aus der Antwort.
        response_base = response[:8]
        
        count += 1
        
        # Überprüft, ob der Basisrahmen der Antwort mit dem gesendeten Basisrahmen übereinstimmt.
        if frame_base == response_base:
            
            # Protokolliert den empfangenen Rahmen im Hexadezimalformat.
            write_log(f"EMS - Response frame: {response.hex()}", logging.DEBUG)
            write_log(f"EMS - Response frame: Is valid!", logging.DEBUG)
            
            found = True
        
        else:
        
            # Protokolliert den empfangenen Rahmen im Hexadezimalformat.
            write_log(f"EMS - Response frame: {response.hex()}", logging.DEBUG)
            
    # Gibt die empfangene Antwort zurück
    return response

################################################################################
# Funktion zum Anfordern und Verarbeiten von EMS-Registerwerten
# Diese Funktion erstellt und sendet einen Modbus-Rahmen, um Daten aus spezifizierten EMS-Registern anzufordern.
# Sie versucht, eine gültige Antwort zu erhalten, und verarbeitet die Registerwerte.
#
# Parameter:
# - register_address: Die Adresse des ersten Registers, das angefordert werden soll.
# - register_count: Die Anzahl der Register, die angefordert werden sollen.
def request_ems(register_address,register_count):

    response_valid = False
    
    boot_code = [0xA5, 0x5A]
    device_address = 0x01
    function_code = 0x03
    
    # Konstruiert den Basisrahmen.
    frame_base = construct_frame(boot_code, device_address, function_code, register_address, register_count)
    
    # Berechnet die CRC-Prüfsumme und fügt sie an den Rahmen an.
    frame_crc = calculate_crc(frame_base)
    frame = bytes(frame_base) + struct.pack('<H', frame_crc)
    
    # Temporäre Variablen zur Speicherung von Registerwerten.
    Temp_400E_value = 0x0000
    has_400E_value = False
    
    Temp_4010_value = 0x0000
    has_4010_value = False
    
    Temp_4029_value = 0x0000
    has_4029_value = False
    
    Temp_402B_value = 0x0000
    has_402B_value = False
    
    Temp_402D_value = 0x0000
    has_402D_value = False
    
    Temp_403A_value = 0x0000
    has_403A_value = False
    
    # Sendet den Rahmen und wartet auf eine gültige Antwort.
    while response_valid == False and running.is_set():
    
        send_frame(frame)
        
        response = receive_response(frame_base)
        
        if response:
        
            response_valid, register_values = parse_response(response, frame_base, register_count)
            
            if response_valid == True:
            
                for i, value in enumerate(register_values):
                
                    value_address = register_address + i
                    
                    # Verarbeitung für spezielle Register, die 4 Byte umfassen.
                    # 0x400E
                    if value_address == 0x400E:
                    
                        Temp_400E_value = value
                        has_400E_value = True
                        
                    elif value_address == 0x400F and has_400E_value == True:
                    
                        Temp_400E_value = format(Temp_400E_value, '04x') + format(value, '04x')
                        Temp_400E_value = int(Temp_400E_value, 16)
                        
                        data_queue.put({"value_address": hex(0x400E), "value": Temp_400E_value})
                        
                        Temp_400E_value = 0x0000
                        has_400E_value = False
                        
                    # 0x4010
                    elif value_address == 0x4010:
                    
                        Temp_4010_value = value
                        has_4010_value = True
                        
                    elif value_address == 0x4011 and has_4010_value == True:
                    
                        Temp_4010_value = format(Temp_4010_value, '04x') + format(value, '04x')
                        Temp_4010_value = int(Temp_4010_value, 16)
                        
                        data_queue.put({"value_address": hex(0x4010), "value": Temp_4010_value})
                        
                        Temp_4010_value = 0x0000
                        has_4010_value = False
                        
                    # 0x4029
                    elif value_address == 0x4029:
                    
                        Temp_4029_value = value
                        has_4029_value = True
                        
                    elif value_address == 0x402A and has_4029_value == True:
                    
                        Temp_4029_value = format(Temp_4029_value, '04x') + format(value, '04x')
                        Temp_4029_value = int(Temp_4029_value, 16)
                        
                        data_queue.put({"value_address": hex(0x4029), "value": Temp_4029_value})
                        
                        Temp_4029_value = 0x0000
                        has_4029_value = False
                        
                    # 0x402B
                    elif value_address == 0x402B:
                    
                        Temp_402B_value = value
                        has_402B_value = True
                        
                    elif value_address == 0x402C and has_402B_value == True:
                    
                        Temp_402B_value = format(Temp_402B_value, '04x') + format(value, '04x')
                        Temp_402B_value = int(Temp_402B_value, 16)
                        
                        data_queue.put({"value_address": hex(0x402B), "value": Temp_402B_value})
                        
                        Temp_402B_value = 0x0000
                        has_402B_value = False
                        
                    # 0x402D
                    elif value_address == 0x402D:
                    
                        Temp_402D_value = value
                        has_402D_value = True
                        
                    elif value_address == 0x402E and has_402D_value == True:
                    
                        Temp_402D_value = format(Temp_402D_value, '04x') + format(value, '04x')
                        Temp_402D_value = int(Temp_402D_value, 16)
                        
                        data_queue.put({"value_address": hex(0x402D), "value": Temp_402D_value})
                        
                        Temp_402D_value = 0x0000
                        has_402D_value = False
                        
                    # 0x403A
                    elif value_address == 0x403A:
                    
                        Temp_403A_value = value
                        has_403A_value = True
                        
                    elif value_address == 0x403B and has_403A_value == True:
                    
                        Temp_403A_value = format(Temp_403A_value, '04x') + format(value, '04x')
                        Temp_403A_value = int(Temp_403A_value, 16)
                        
                        data_queue.put({"value_address": hex(0x403A), "value": Temp_403A_value})
                        
                        Temp_403A_value = 0x0000
                        has_403A_value = False
                        
                    # Alle anderen 2 Byte Register  
                    else:
                    
                        data_queue.put({"value_address": hex(value_address), "value": value})

# Funktion zum Schreiben von Daten in EMS-Register
# Diese Funktion erstellt und sendet einen Modbus-Rahmen, um Daten in spezifizierte EMS-Register zu schreiben.
# Sie versucht, eine gültige Antwort zu erhalten, und wiederholt den Vorgang bei Bedarf.
#
# Parameter:
# - register_address: Die Adresse des ersten zu beschreibenden Registers.
# - register_count: Die Anzahl der Register, die beschrieben werden sollen.
# - register_data: Die Daten, die in die Register geschrieben werden sollen.
def write_ems(register_address,register_count,register_data):

    response_valid = False
    
    boot_code = [0xA5, 0x5A]
    device_address = 0x01
    function_code = 0x10
    
    # Konstruiert den Basisrahmen.
    frame_base = construct_frame(boot_code, device_address, function_code, register_address, register_count)
    frame = bytes(frame_base) + struct.pack('>H', register_data)
    
     # Berechnet die CRC-Prüfsumme und fügt sie an den Rahmen an.
    frame_crc = calculate_crc(frame)
    frame = bytes(frame) + struct.pack('<H', frame_crc)
    
    # Sendet den Rahmen und wartet auf eine gültige Antwort.
    while response_valid == False and running.is_set():
    
        send_frame(frame)
        
        response = receive_response(frame_base)
        
        if response:
        
            response_valid = True

################################################################################
# Funktion zur Analyse und Validierung einer Modbus-Antwort
# Diese Funktion prüft die Länge und Gültigkeit der empfangenen Antwort, extrahiert Registerwerte
# und validiert die CRC-Prüfsumme.
#
# Parameter:
# - response: Der empfangene Modbus-Antwortrahmen als Byte-Array.
# - frame_base: Der Basisrahmen der gesendeten Nachricht, gegen den die Antwort validiert wird.
# - register_count: Die Anzahl der Register, deren Werte extrahiert werden sollen.
#
# Rückgabewert:
# - response_valid: Ein boolescher Wert, der angibt, ob die Antwort gültig ist (True) oder nicht (False).
# - register_values: Eine Liste der extrahierten Registerwerte.
def parse_response(response, frame_base, register_count):
   
    response_valid = True
    
    # Extrahiert den Basisrahmen aus der Antwort.
    response_base = response[:8]
    register_values = []
    
    # Überprüft die Länge der Antwort.
    if len(response) >= 10 + (register_count * 2):
    
        response = response[:10 + (register_count * 2)]
        
    if len(response) < 10 + (register_count * 2):
    
        response_valid = False
        
        write_log(f"EMS - Response frame: Lenght is to short!", logging.DEBUG)
        
    elif frame_base != response_base:
    
        response_valid = False
        
        write_log(f"EMS - Response frame: Isn't valid!", logging.DEBUG)
        
    else:
    
        # Extrahiert die Registerwerte aus der Antwort.
        for i in range(register_count):
        
            value = response[8 + i*2:10 + i*2]
            value = int(value.hex(), 16)
            
            register_values.append(value)
        
        # Überprüft die CRC-Prüfsumme.
        crc_received = struct.unpack('<H', response[-2:])[0]
        crc_calculated = calculate_crc(response[:-2])
        
        if crc_received != crc_calculated:
        
            response_valid = False
            
            write_log(f"EMS - Response frame: CRC is wrong!", logging.DEBUG)
    
    # Gibt die Gültigkeit der Antwort und die Registerwerte zurück
    return response_valid, register_values

# Funktion zur Interpretation und Umwandlung von EMS-Registerwerten
# Diese Funktion interpretiert die Werte von EMS-Registern basierend auf deren Adressen und wandelt sie
# in lesbare oder anderweitig nützliche Formate um.
#
# Parameter:
# - value_address: Die Adresse des Registers als Hexadezimalzeichenkette.
# - value: Der Wert des Registers.
#
# Rückgabewert:
# - value_address: Die Adresse des Registers als Ganzzahl.
# - parsed_value: Der interpretierte und umgewandelte Wert.
def ems_parse_value(value_address, value):
    
    # Konvertiert die Adresse in eine Ganzzahl
    value_address = int(value_address, 16)
    parsed_value = None
    
    # Interpretiert die Werte basierend auf der Adresse.
    if value_address in [0x302D, 0x303B, 0x3039]:
    
        if value == 1:
        
            parsed_value = "on" 
        
        else: 
        
            parsed_value = "off"

    elif value_address in [0x4001, 0x401F, 0x4002, 0x4005, 0x4018, 0x4017, 0x4020, 0x3027, 0x3029, 0x302A, 0x302C, 0x4023, 0x4024, 0x4025]:
        
        parsed_value = value / 10

    elif value_address in [0x4003, 0x4006, 0x4019, 0x401C, 0x401B, 0x4026, 0x4027, 0x4028]:
        
        parsed_value = value / 100

    elif value_address in [0x4004, 0x4007]:
        
        parsed_value = value / 1

    elif value_address == 0x4029 or value_address == 0x402B or value_address == 0x402D or value_address == 0x403A:
        
        if value >= 2**31:
        
            value -= 2**32
        
        parsed_value = value / 10

    elif value_address == 0x4016 or value_address == 0x4042:
        
        if value == 1:
        
            parsed_value = "Online" 
        
        else: 
        
            parsed_value = "Offline"

    elif value_address == 0x3020:
        
        if value == 1:
        
            parsed_value = "Bleigel/Säure Batterie"
            
        elif value == 2:
        
            parsed_value = "LiFePo4 Batterie"

    elif value_address == 0x3021:
    
        if value == 0:
        
            parsed_value = "48V"
            
        elif value == 1:
        
            parsed_value = "51.2V"

    elif value_address == 0x4022:
    
        if value == 1:
        
            parsed_value = "Online"
            
        elif value == 2:
        
            parsed_value = "Disabled"
            
        else:
        
            parsed_value = "Offline"

    else:
    
        parsed_value = value

    # Gibt die Adresse und den interpretierten Wert zurück
    return value_address, parsed_value

# Funktion zur Veröffentlichung von EMS-Daten auf MQTT-Themen
# Diese Funktion veröffentlicht interpretierte EMS-Daten auf entsprechenden MQTT-Themen basierend auf der Registeradresse.
#
# Parameter:
# - value_address: Die Adresse des Registers als Ganzzahl.
# - parsed_value: Der interpretierte und umgewandelte Wert des Registers.
def ems_publish_data(value_address,parsed_value):

    topics = {
        0x302D: "solar/ems/{}/EMS_Limit",
        0x302E: "solar/ems/{}/EMS_Power_Limit",
        0x4021: "solar/ems/{}/EMS_Load_Power",
        0x303B: "solar/ems/{}/EMS_EM",
        0x3039: "solar/ems/{}/EMS_Bypass",
        0x4001: "solar/ems/{}/EMS_Temperature",
        0x401F: "solar/ems/{}/EMS_Load_Energy",
        0x3072: "solar/ems/{}/EMS_Address",
        0x4002: "solar/ems/{}/MPPT1_Voltage",
        0x4003: "solar/ems/{}/MPPT1_Current",
        0x4004: "solar/ems/{}/MPPT1_Power",
        0x400E: "solar/ems/{}/MPPT1_Energy",
        0x4005: "solar/ems/{}/MPPT2_Voltage",
        0x4006: "solar/ems/{}/MPPT2_Current",
        0x4007: "solar/ems/{}/MPPT2_Power",
        0x4010: "solar/ems/{}/MPPT2_Energy",
        0x401E: "solar/ems/{}/MPPT_Total_Energy",
        0x4016: "solar/ems/{}/Battery_Online",
        0x4042: "solar/ems/{}/Battery_BMS_Online",
        0x401D: "solar/ems/{}/Battery_SOC",
        0x4018: "solar/ems/{}/Battery_Voltage",
        0x401A: "solar/ems/{}/Battery_Charging_Power",
        0x4019: "solar/ems/{}/Battery_Charging_Current",
        0x401C: "solar/ems/{}/Battery_Discharging_Power",
        0x401B: "solar/ems/{}/Battery_Discharging_Current",
        0x4017: "solar/ems/{}/Battery_Temperature",
        0x4020: "solar/ems/{}/Battery_Energy",
        0x301F: "solar/ems/{}/Battery_BMS_Type",
        0x3020: "solar/ems/{}/Battery_Type",
        0x3021: "solar/ems/{}/Battery_Voltage_Type",
        0x3022: "solar/ems/{}/Battery_Capacity",
        0x3027: "solar/ems/{}/Battery_BMS_Max_Voltage",
        0x3028: "solar/ems/{}/Battery_BMS_Max_Current",
        0x3029: "solar/ems/{}/Battery_BMS_Min_Voltage",
        0x302A: "solar/ems/{}/Battery_Max_Voltage",
        0x302B: "solar/ems/{}/Battery_Max_Current",
        0x302C: "solar/ems/{}/Battery_Min_Voltage",
        0x4022: "solar/ems/{}/EM_Online",
        0x4029: "solar/ems/{}/EM_A_Power",
        0x4026: "solar/ems/{}/EM_A_Current",
        0x4023: "solar/ems/{}/EM_A_Voltage",
        0x402B: "solar/ems/{}/EM_B_Power",
        0x4027: "solar/ems/{}/EM_B_Current",
        0x4024: "solar/ems/{}/EM_B_Voltage",
        0x402D: "solar/ems/{}/EM_C_Power",
        0x4028: "solar/ems/{}/EM_C_Current",
        0x4025: "solar/ems/{}/EM_C_Voltage",
        0x403A: "solar/ems/{}/EM_Total_Power"
    }

    topic = topics.get(value_address, None)
    
    if topic:
    
        # Veröffentlicht die Daten auf dem entsprechenden MQTT-Thema.
        result = client.publish(topic.format(EMS_Nr), parsed_value)
        
        write_log(f"MQTT - Published to {topic.format(EMS_Nr)}: {parsed_value}", logging.DEBUG)
            
        # Wartezeit zwischen den Veröffentlichungen.
        time.sleep(0.2)

################################################################################
#                                   Threads                                    #
################################################################################

# Thread zur Überwachung und Steuerung von EMS-Registerwerten
# Dieser Thread überwacht den Status von EMS-Flags und führt entsprechende Schreib- und Leseoperationen auf EMS-Registern durch.
# Er läuft in einer Schleife, bis das Flag `running` zurückgesetzt wird.
def read_ems():
    
    global EMS_EM_FLG
    global EMS_EM_Value
    global EMS_Bypass_FLG
    global EMS_Bypass_Value
    global EMS_Power_Limit_FLG
    global EMS_Power_Limit_Value
       
    sequence = 0

    while running.is_set():
    
        # Überprüft und schreibt den EMS_EM-Wert, wenn das Flag gesetzt ist.
        if EMS_EM_FLG == True:
        
            write_ems(0x303B,0x0001,EMS_EM_Value)
            
            request_ems(0x302E,0x0010)
            
            EMS_EM_FLG = False
        
            write_log(f"EMS - EMS_EM changed changed successful", logging.INFO)
        
        # Überprüft und schreibt den EMS_Bypass-Wert, wenn das Flag gesetzt ist.
        elif EMS_Bypass_FLG == True:
        
            write_ems(0x3039,0x0001,EMS_Bypass_Value)
            
            request_ems(0x302E,0x0010)
            
            EMS_Bypass_FLG = False
        
            write_log(f"EMS - EMS_Bypass changed changed successful", logging.INFO)
        
        # Überprüft und schreibt den EMS_Power_Limit-Wert, wenn das Flag gesetzt ist.
        elif EMS_Power_Limit_FLG == True:
        
            write_ems(0x302E,0x0001,EMS_Power_Limit_Value)
            
            request_ems(0x302E,0x0010)
            
            EMS_Power_Limit_FLG = False
        
            write_log(f"EMS - EMS_Power_Limit changed successful", logging.INFO)
        
        # Regelmäßige Leseanforderungen an das EMS.
        # Temperatur und MPPT Informationen
        request_ems(0x4001,0x0010)
        
        # Zyklische zusätzliche Leseanforderungen.
        # EMS Einstellungen
        if sequence == 0:
        
            request_ems(0x302D,0x000F) 
        
        # Batterie Einstellungen
        elif sequence == 1:
        
            request_ems(0x301F,0x000E) 
        
        # Batterie & EMS Informationen
        elif sequence == 2:
        
            request_ems(0x4016,0x000C) 
        
        # CT Informationen
        elif sequence == 3:
        
            request_ems(0x3022,0x000C) 
        
        # Batterie & CT Informationen
        elif sequence == 4:
        
            request_ems(0x303A,0x0009)
            
        
        if sequence == 4:
        
            sequence = 0
            
        else:
        
            sequence += 1

# Thread zur Veröffentlichung von EMS-Daten
# Dieser Thread überwacht eine Warteschlange auf neue EMS-Daten, bereitet diese auf und veröffentlicht sie,
# solange das Flag `running` gesetzt ist.
def publish_ems():
    
    while running.is_set():
    
        # Überprüft, ob die Warteschlange nicht leer ist.
        if not data_queue.empty():
        
            # Holt EMS-Daten aus der Warteschlange.
            ems_data = data_queue.get()
            
            # Bereitet die EMS-Daten auf und Veröffentlicht diese.
            value_address, parsed_value = ems_parse_value(ems_data["value_address"],ems_data["value"])
            ems_publish_data(value_address, parsed_value)
            
# Thread zur Ausführung der MQTT-Ereignisschleife
# Dieser Thread führt die Ereignisschleife des MQTT-Clients in regelmäßigen Abständen aus,
# solange das Flag `running` gesetzt ist.
def mqtt_read_loop():

    while running.is_set():
    
        client.loop(timeout=1.0) 

################################################################################
#                                 Hauptprogramm                                #
################################################################################
# Hauptprogramm zur Initialisierung und Ausführung von EMS-Kommunikation und MQTT-Veröffentlichung
# Dieses Programm initialisiert die serielle Kommunikation, den MQTT-Client und Threads für das Lesen und
# Veröffentlichen von EMS-Daten. Es enthält Fehlerbehandlung und sorgt für eine ordnungsgemäße
# Beendigung bei einem Abbruch durch den Benutzer.

try:
    
    # Threading Event
    running = threading.Event()
    running.set()

    # Logging konfigurieren
    logging.basicConfig(filename=LOG_FILE, level=LOG_LEVEL, format='%(message)s')

    # Serial konfigurieren
    ser = serial.Serial(RS485_PORT, baudrate=RS485_BAUD_RATE, parity=RS485_PARITY, stopbits=RS485_STOPBITS, bytesize=RS485_BYTESIZE, timeout=1)

    # MQTT-Client konfigurieren
    client = mqtt.Client(f"EMS_{EMS_Nr}_Client")

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.keep_alive = 120

    # Response Queue konfigurieren
    data_queue = queue.Queue()
    
    # Erstellen und starten der Threads
    read_ems_thread = threading.Thread(target=read_ems)
    publish_ems_thread = threading.Thread(target=publish_ems)
    mqtt_read_loop_thread = threading.Thread(target=mqtt_read_loop)
    
    # Threads starten
    read_ems_thread.start()
    publish_ems_thread.start()
    mqtt_read_loop_thread.start()
    
    # Warten auf Thread Ende
    read_ems_thread.join()
    publish_ems_thread.join()
    mqtt_read_loop_thread.join()
    

except KeyboardInterrupt:
    
    print("Beendet durch Benutzer")
    
    # Stoppt die Schleifen in den Threads
    running.clear()  
    
    read_ems_thread.join()
    publish_ems_thread.join()
    mqtt_read_loop_thread.join()
    
finally:
    
    client.disconnect()
    ser.close()