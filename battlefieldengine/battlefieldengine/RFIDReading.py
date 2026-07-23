"""
RFIDReading: a parsed representation of a single RFID scan message coming
in over MQTT.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RFIDReading:
    uid: str
    source_topic: str
    timestamp: datetime = field(default_factory=datetime.now)

    @classmethod
    def from_mqtt(cls, topic: str, payload: dict) -> "RFIDReading | None":
        uid = payload.get("uid")
        if not uid:
            return None
        return cls(uid=uid, source_topic=topic)
