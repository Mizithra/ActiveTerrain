#
# Copyright 2021 HiveMQ GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
MqttClient: owns the whole MQTT lifecycle -- connecting (TLS + credentials
from environment variables) and the publish(topic, dict) / subscribe(topic,
callback) interface Battlefield and TerrainNode expect.

Replaces the previous split between mqtt_client.py's create_mqtt_client()
factory and mqtt_adapter.py's MQTTAdapter wrapper -- one class now owns the
connection AND translates its interface, since there was never a reason
those needed to be two separate objects.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Callable, Optional

import paho.mqtt.client as paho
from paho import mqtt
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()


class MqttClient:
    """
    Usage:
        client = MqttClient()
        client.start()
        client.subscribe("some/topic", my_callback)
        client.publish("some/topic", {"key": "value"})
        ...
        client.stop()

    host/username/password default to the MQTT_HOST / MQTT_USERNAME /
    MQTT_PASSWORD environment variables (via python-dotenv) if not passed
    explicitly -- same as the original create_mqtt_client().
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: int = 8883,
        username: Optional[str] = None,
        password: Optional[str] = None,
        qos: int = 1,
    ):
        self._qos = qos
        self._callbacks: dict[str, Callable[[str, dict], None]] = {}

        host = host or os.getenv("MQTT_HOST")
        username = username or os.getenv("MQTT_USERNAME")
        password = password or os.getenv("MQTT_PASSWORD")

        # MQTT v5, TLS -- same setup as the original create_mqtt_client()
        self._client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
        self._client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        self._client.username_pw_set(username, password)

        self._client.on_connect = self._on_connect
        self._client.on_subscribe = self._on_subscribe
        self._client.on_publish = self._on_publish
        self._client.on_message = self._on_message

        self._client.connect(host, port)

    # --- lifecycle --------------------------------------------------
    def start(self) -> None:
        self._client.loop_start()

    def stop(self) -> None:
        self._client.loop_stop()

    # --- pub/sub ------------------------------------------------------
    def publish(self, topic: str, payload: dict) -> None:
        self._client.publish(topic, json.dumps(payload), qos=self._qos)

    def subscribe(self, topic: str, callback: Callable[[str, dict], None]) -> None:
        self._callbacks[topic] = callback
        self._client.subscribe(topic, qos=self._qos)

    # --- internal paho callbacks --------------------------------------
    def _on_connect(self, client, userdata, flags, rc, properties=None) -> None:
        logger.info("MQTT connected (rc=%s)", rc)

    def _on_subscribe(self, client, userdata, mid, granted_qos, properties=None) -> None:
        logger.debug("MQTT subscribed: mid=%s qos=%s", mid, granted_qos)

    def _on_publish(self, client, userdata, mid, properties=None) -> None:
        logger.debug("MQTT publish acked: mid=%s", mid)

    def _on_message(self, client, userdata, msg) -> None:
        callback = self._callbacks.get(msg.topic)
        if not callback:
            logger.debug("No handler registered for %s", msg.topic)
            return
        try:
            payload = json.loads(msg.payload.decode())
        except (UnicodeDecodeError, json.JSONDecodeError):
            logger.warning("Non-JSON payload on %s: %r", msg.topic, msg.payload)
            return
        callback(msg.topic, payload)


if __name__ == "__main__":
    # Quick manual test: subscribe to one topic, publish to it, watch it log.
    # NOTE: callback dispatch is exact-topic-match only -- it doesn't resolve
    # MQTT wildcards (# or +) against the subscribed topic, so subscribe()
    # and publish() need to use the same literal topic string here.
    logging.basicConfig(level=logging.DEBUG)

    def _print_any(topic: str, payload: dict) -> None:
        print(f"{topic}: {payload}")

    client = MqttClient()
    client.subscribe("AWencyclopedia/temperature", _print_any)
    client.start()
    client.publish("AWencyclopedia/temperature", {"value": "hot"})
    input("Press Enter to stop...\n")
    client.stop()