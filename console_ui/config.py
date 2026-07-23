"""Configuration — change these values as needed."""

import platform

# Auto-detect a sensible default, but override as needed
_system = platform.system()
if _system == "Windows":
    DEFAULT_SERIAL_PORT = "COM3"
elif _system == "Darwin":
    DEFAULT_SERIAL_PORT = "/dev/tty.usbserial"
else:
    DEFAULT_SERIAL_PORT = "/dev/ttyUSB0"

SERIAL_PORT = DEFAULT_SERIAL_PORT
BAUD_RATE = 115200
JSON_PATH = "registry.json"
POLL_INTERVAL = 0.1  # seconds between serial queue checks