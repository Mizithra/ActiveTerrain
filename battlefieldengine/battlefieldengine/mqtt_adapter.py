"""
MQTTAdapter: wraps a raw paho-mqtt client to provide the
publish(topic, dict) / subscribe(topic, callback) interface Battlefield
and TerrainNode expect. Shared by server.py and any UI so there's one
implementation, not several copies.
"""
from __future__ import annotations

import json
import logging
from typing import Callable

logger = logging.getLogger(__name__)


class MQTTAdapter:
    def __init__(self, client, qos: int = 1):
        self._client = client
        self._qos = qos
        self._callbacks: dict[str, Callable[[str, dict], None]] = {}
        self._client.on_message = self._on_message

    def publish(self, topic: str, payload: dict) -> None:
        self._client.publish(topic, json.dumps(payload), qos=self._qos)

    def subscribe(self, topic: str, callback: Callable[[str, dict], None]) -> None:
        self._callbacks[topic] = callback
        self._client.subscribe(topic)

    def _on_message(self, client, userdata, msg) -> None:
        callback = self._callbacks.get(msg.topic)
        if not callback:
            return
        try:
            payload = json.loads(msg.payload.decode())
        except (UnicodeDecodeError, json.JSONDecodeError):
            logger.warning("Non-JSON payload on %s: %r", msg.topic, msg.payload)
            return
        callback(msg.topic, payload)

    def loop_stop(self) -> None:
        self._client.loop_stop()
