"""
Battlefield: ties together RFID scan events, MQTT messaging, and game
state (turn/phase tracking) for the smart terrain project.

This class is transport-agnostic: it doesn't know or care whether you're
using paho-mqtt, aiomqtt, or something else. Pass in any object that has:

    mqtt_client.publish(topic: str, payload: dict) -> None
    mqtt_client.subscribe(topic: str, callback: Callable[[str, dict], None]) -> None

Adapt your existing MQTTClient to match this shape (a thin wrapper is
usually enough if it doesn't already look like this).
"""
from __future__ import annotations

import json
import logging
import threading
from typing import Callable, Optional
from datetime import datetime, timedelta
from pathlib import Path

from battlefield_sim.Models import PHASE_ORDER, Phase, Unit, UnitState

logger = logging.getLogger(__name__)

# --- MQTT topic scheme --------------------------------------------------
TOPIC_RFID_SCAN = "battlefield/rfid/scan"     # ESP32 -> backend: {"uid": "..."}
TOPIC_TURN_STATE = "battlefield/turn/state"   # backend -> everyone: {"turn": int, "phase": str}
TOPIC_UNIT_EVENT = "battlefield/units/event"  # backend -> everyone: {"uid", "name", "event"}
TOPIC_COMMAND = "battlefield/command"         # UI -> backend: {"action": "...", ...}


class UnitRegistry:
    """Maps RFID UID -> Unit metadata, loaded from a JSON file.

    Example unit_registry.json:
    {
      "04A3B2C1": {"name": "Intercessor Squad", "faction": "Space Marines", "owner": "Alice", "points": 100},
      "9F1122AA": {"name": "Ork Boyz",           "faction": "Orks",          "owner": "Bob",   "points": 90}
    }
    """

    def __init__(self, path: Optional[Path] = None):
        self._units: dict[str, Unit] = {}
        if path is not None:
            self.load(path)

    def load(self, path: Path) -> None:
        with open(path, "r") as f:
            raw = json.load(f)
        for uid, data in raw.items():
            self._units[uid] = Unit(uid=uid, **data)
        logger.info("Loaded %d units from %s", len(self._units), path)

    def get(self, uid: str) -> Optional[Unit]:
        return self._units.get(uid)

    def register(self, unit: Unit) -> None:
        self._units[unit.uid] = unit


class Battlefield:
    """Central game-state object: turn/phase tracking + unit presence.

    Usage:
        registry = UnitRegistry(Path("unit_registry.json"))
        bf = Battlefield(mqtt_client, registry)
        bf.add_listener(my_callback)   # e.g. to update a Textual UI
        bf.start()
    """

    def __init__(self, mqtt_client, registry: UnitRegistry, presence_timeout_seconds: float = 3.0):
        """
        presence_timeout_seconds: how long a unit can go without a heartbeat
        before it's considered departed. Should be a bit longer than the
        ESP32's heartbeat interval (e.g. 3s if the ESP32 heartbeats every 1s)
        so a single dropped MQTT message doesn't cause a false departure.
        """
        self._mqtt = mqtt_client
        self._registry = registry
        self._presence_timeout = timedelta(seconds=presence_timeout_seconds)

        self._lock = threading.Lock()
        self._turn = 1
        self._phase = PHASE_ORDER[0]
        self._units_seen: dict[str, UnitState] = {}

        # Listeners are plain callables: fn(event_type: str, data: dict)
        self._listeners: list[Callable[[str, dict], None]] = []

    # --- lifecycle --------------------------------------------------
    def start(self) -> None:
        """Subscribe to the relevant MQTT topics. Call once at startup."""
        self._mqtt.subscribe(TOPIC_RFID_SCAN, self._on_rfid_scan)
        self._mqtt.subscribe(TOPIC_COMMAND, self._on_command)
        logger.info("Battlefield subscribed to MQTT topics")

    # --- listener/observer pattern (for UI updates) ------------------
    def add_listener(self, callback: Callable[[str, dict], None]) -> None:
        """Register a callback invoked on every state change.

        NOTE: this fires from the MQTT client's network thread, NOT from
        your Textual app's event loop. When updating a Textual UI, marshal
        back onto the app thread rather than touching widgets directly:

            def on_event(event_type, data):
                app.call_from_thread(my_widget.update, data)
        """
        self._listeners.append(callback)

    def _notify(self, event_type: str, data: dict) -> None:
        for cb in self._listeners:
            try:
                cb(event_type, data)
            except Exception:
                logger.exception("Listener raised an exception for event %s", event_type)

    # --- MQTT inbound handlers ----------------------------------------
    def _on_rfid_scan(self, topic: str, payload: dict) -> None:
        """Handle a presence heartbeat from the ESP32.

        The ESP32 should publish this message repeatedly (throttled, e.g.
        once per second) for as long as a card is on the reader, and stop
        publishing entirely once the card is removed. This handler treats
        the FIRST heartbeat after either startup or a departure as an
        "arrival"; subsequent heartbeats just refresh last_seen silently.
        Actual departure is detected by check_departures(), not here.
        """
        uid = payload.get("uid")
        if not uid:
            logger.warning("RFID scan message missing 'uid': %s", payload)
            return

        unit = self._registry.get(uid)
        if unit is None:
            logger.warning("Unrecognized RFID UID scanned: %s", uid)
            self._notify("unknown_unit_scanned", {"uid": uid})
            return

        newly_arrived = False
        with self._lock:
            state = self._units_seen.get(uid)
            now = datetime.now()
            if state is None:
                state = UnitState(unit=unit, on_field=True, last_seen=now)
                self._units_seen[uid] = state
                newly_arrived = True
            else:
                if not state.on_field:
                    newly_arrived = True
                state.on_field = True
                state.last_seen = now

        if newly_arrived:
            data = {"uid": uid, "name": unit.name, "faction": unit.faction, "event": "unit_arrived"}
            self._mqtt.publish(TOPIC_UNIT_EVENT, data)
            self._notify("unit_arrived", data)

    def check_departures(self) -> None:
        """Sweep for units that haven't sent a heartbeat within the presence
        timeout and mark them departed. Call this periodically (e.g. every
        second) from a background thread, asyncio task, or your Textual
        app's `set_interval` — this class doesn't schedule it for you, since
        that decision depends on where Battlefield lives in your app.
        """
        now = datetime.now()
        departed = []
        with self._lock:
            for uid, state in self._units_seen.items():
                if state.on_field and state.last_seen and (now - state.last_seen) > self._presence_timeout:
                    state.on_field = False
                    departed.append((uid, state.unit))

        for uid, unit in departed:
            data = {"uid": uid, "name": unit.name, "faction": unit.faction, "event": "unit_departed"}
            self._mqtt.publish(TOPIC_UNIT_EVENT, data)
            self._notify("unit_departed", data)

    def _on_command(self, topic: str, payload: dict) -> None:
        """Handle commands published by the UI (e.g. manual turn increment)."""
        action = payload.get("action")
        if action == "increment_turn":
            self.increment_turn()
        elif action == "next_phase":
            self.next_phase()
        elif action == "set_phase":
            phase = payload.get("phase")
            if phase:
                self.set_phase(Phase(phase))
        else:
            logger.warning("Unknown command action: %s", action)

    # --- game state mutation --------------------------------------------
    def increment_turn(self) -> None:
        with self._lock:
            self._turn += 1
            self._phase = PHASE_ORDER[0]
            turn, phase = self._turn, self._phase
        self._publish_turn_state(turn, phase)
        self._notify("turn_changed", {"turn": turn, "phase": phase.value})

    def set_phase(self, phase: Phase) -> None:
        with self._lock:
            self._phase = phase
            turn = self._turn
        self._publish_turn_state(turn, phase)
        self._notify("phase_changed", {"turn": turn, "phase": phase.value})

    def next_phase(self) -> None:
        """Advance to the next phase, rolling into a new turn if at the end."""
        with self._lock:
            idx = PHASE_ORDER.index(self._phase)
            rolled_over = idx + 1 >= len(PHASE_ORDER)
            if rolled_over:
                self._turn += 1
                self._phase = PHASE_ORDER[0]
            else:
                self._phase = PHASE_ORDER[idx + 1]
            turn, phase = self._turn, self._phase
        self._publish_turn_state(turn, phase)
        self._notify("turn_changed" if rolled_over else "phase_changed",
                     {"turn": turn, "phase": phase.value})

    def _publish_turn_state(self, turn: int, phase: Phase) -> None:
        self._mqtt.publish(TOPIC_TURN_STATE, {"turn": turn, "phase": phase.value})

    # --- queries ------------------------------------------------------
    def get_units_seen(self) -> list[UnitState]:
        with self._lock:
            return list(self._units_seen.values())

    def get_turn_state(self) -> tuple[int, Phase]:
        with self._lock:
            return self._turn, self._phase