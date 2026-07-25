"""
TerrainNode: a physical piece of terrain with its own RFID sensor and LED,
wired together over MQTT. Tracks which units are currently occupying it
and reacts by lighting up when a new unit arrives.

Each TerrainNode owns a topic namespace derived from a single base topic:
    {mqtt_topic}/rfid_scan   <- ESP32 publishes scan messages here
    {mqtt_topic}/led    <- this class publishes LED commands here

TerrainNode is the thing actually wired to one specific ESP32 -- it's the
right place to hear raw scans. It notifies an optional on_scan callback
with every scan (not just new arrivals), which is how Battlefield hears
about unit presence without subscribing to any RFID topic itself.
"""
from __future__ import annotations

import logging
from typing import Callable, Optional

from battlefieldengine.RFIDReading import RFIDReading

logger = logging.getLogger(__name__)

OnScanCallback = Callable[["TerrainNode", RFIDReading], None]


class TerrainNode:
    def __init__(
        self,
        name: str,
        mqtt_topic: str,
        led_color: Optional[str] = None,
        led_pattern: Optional[str] = None,
        on_scan: Optional[OnScanCallback] = None,
    ):
        self.name = name
        self.mqtt_topic = mqtt_topic
        self.led_color = led_color
        self.led_pattern = led_pattern
        self.on_scan = on_scan
        self.occupying_units: set[str] = set()
        self._mqtt = None  # set in start()

    @property
    def rfid_topic(self) -> str:
        return f"{self.mqtt_topic}/rfid_scan"

    @property
    def led_topic(self) -> str:
        return f"{self.mqtt_topic}/led_control"

    def start(self, mqtt_client) -> None:
        self._mqtt = mqtt_client
        mqtt_client.subscribe(self.rfid_topic, self._on_message)
        logger.info("TerrainNode '%s' listening on %s", self.name, self.rfid_topic)

    def _on_message(self, topic: str, payload: dict) -> None:
        reading = RFIDReading.from_mqtt(topic, payload)
        if reading is None:
            logger.warning("%s: malformed scan payload: %s", self.name, payload)
            return
        self.handle_scan(reading)

    def handle_scan(self, reading: RFIDReading) -> None:
        is_new_arrival = reading.uid not in self.occupying_units
        self.occupying_units.add(reading.uid)

        if is_new_arrival:
            logger.info(
                "%s: unit %s arrived (%d unit(s) now present)",
                self.name, reading.uid, len(self.occupying_units),
            )

        # Fires on every scan, not just new arrivals -- Battlefield needs
        # the repeated heartbeats to keep its own presence-timeout logic
        # accurate, the same way it would if it were listening directly.
        if self.on_scan:
            self.on_scan(self, reading)

    def remove_unit(self, uid: str) -> None:
        self.occupying_units.discard(uid)
        if not self.occupying_units:
            self.light_off()

    def light_on(self) -> None:
        payload = {"state": "on"}
        if self.led_color:
            payload["color"] = self.led_color
        if self.led_pattern:
            payload["pattern"] = self.led_pattern
        self._mqtt.publish(self.led_topic, payload)

    def light_off(self) -> None:
        self._mqtt.publish(self.led_topic, {"state": "off"})