"""
RFIDReading: a parsed representation of a single RFID scan message coming
in over MQTT. Keeping this as its own small class (rather than passing raw
dicts around) gives you one place to change the wire format later without
touching every consumer of it.
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
        """Build an RFIDReading from an incoming MQTT message. Returns None
        (and logs nothing itself — caller decides how to handle it) if the
        payload doesn't contain a uid, so callers can no-op on bad data.
        """
        uid = payload.get("uid")
        if not uid:
            return None
        return cls(uid=uid, source_topic=topic)