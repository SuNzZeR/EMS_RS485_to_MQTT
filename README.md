
# RS485 to MQTT Interface for EMS
## Author: Patrick Völker

This project provides a bridge between RS485 communication and MQTT for an Tentek EMS Controller. It allows the EMS to communicate with an MQTT broker to publish and subscribe to various topics, enabling remote control and monitoring.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Setup and Installation](#setup-and-installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Logging](#logging)
- [Functions](#functions)
- [Threads](#threads)
- [License](#license)

## Overview
The script reads data from an EMS via RS485, processes it, and publishes it to an MQTT broker. It also subscribes to MQTT topics to control the EMS.

## Features
- Read and write EMS register values via RS485
- Publish EMS data to MQTT topics
- Subscribe to MQTT topics to control EMS settings
- Logging of events and errors

## Setup and Installation
### Requirements
- Python 3.x
- `pyserial` library for RS485 communication
- `paho-mqtt` library for MQTT communication

## Configuration
### RS485 Configuration
Set the RS485 serial port:
```python
RS485_PORT = "/dev/ttyUSB0"
```

### MQTT Configuration
Set the MQTT broker connection parameters:
```python
MQTT_BROKER = "192.168.178.123"
MQTT_PORT = 1883
MQTT_USERNAME = "mqtt"
MQTT_PASSWORD = "12345"
```

### Logging Configuration
Set the logging parameters:
```python
LOG_LEVEL = logging.INFO
LOG_FILE = "/home/pi/ems_mqtt/your_script_name.log"
```

## Usage
1. Ensure your EMS device is connected to the RS485 port.
2. Run the script:
   ```bash
   python ems_rs485_to_mqtt.py
   ```

## Logging
The script logs various events and errors. The log file is specified by the `LOG_FILE` variable.

### Log Levels
- `DEBUG`: Detailed information for diagnosing problems.
- `INFO`: Confirmation that things are working as expected.
- `WARNING`: An indication that something unexpected happened.
- `ERROR`: A more serious problem.
- `CRITICAL`: A very serious problem.

## Functions
### `write_log(message, log_level)`
Writes log messages with a specific log level.

### `on_connect(client, userdata, flags, rc)`
Handles successful connection to the MQTT broker and subscribes to topics.

### `on_message(client, userdata, msg)`
Processes received MQTT messages.

### `on_disconnect(client, userdata, rc)`
Handles unexpected disconnections and attempts to reconnect.

### `process_mqtt_message(topic, message)`
Processes specific MQTT messages to update EMS settings.

### `is_valid_EMS_Power_Limit(value)`
Checks if a given EMS power limit value is valid.

### `calculate_crc(data)`
Calculates the CRC-16 checksum for a given data array.

### `construct_frame(boot_code, device_address, function_code, register_address, register_count)`
Constructs a Modbus frame.

### `send_frame(frame)`
Sends a Modbus frame over the serial interface.

### `receive_response(frame_base)`
Receives and validates a Modbus response.

### `request_ems(register_address, register_count)`
Requests and processes EMS register values.

### `write_ems(register_address, register_count, register_data)`
Writes data to EMS registers.

### `parse_response(response, frame_base, register_count)`
Analyzes and validates a Modbus response.

### `ems_parse_value(value_address, value)`
Interprets and converts EMS register values.

### `ems_publish_data(value_address,parsed_value)`
Publishes EMS data to MQTT topics.

## Threads
### `read_ems()`
Monitors and controls EMS register values based on flags.

### `publish_ems()`
Publishes new EMS data from the queue to MQTT topics.

### `mqtt_read_loop()`
Runs the MQTT client's event loop.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Feel free to contribute to this project by opening issues or submitting pull requests. For any questions, contact the author.

Enjoy using the RS485 to MQTT interface for EMS!
