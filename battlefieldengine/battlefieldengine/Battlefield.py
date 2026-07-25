"""
Battlefield: global game-state object. Owns turn/phase tracking,
cross-marker unit presence, and TerrainNode ownership.

Battlefield does NOT subscribe to any raw RFID topic itself -- each
TerrainNode is the thing actually wired to one specific ESP32, so it hears
scans directly and notifies Battlefield via a callback (_on_terrain_scan).
This keeps topic ownership unambiguous: TerrainNode owns its own
{mqtt_topic}/rfid and /led; Battlefield owns the global turn/command/
unit-event topics, which are the same regardless of how many terrain
markers exist on the table.
"""
from __future__ import annotations

import json
import logging
import threading
from typing import Callable, Optional
from datetime import datetime, timedelta
from pathlib import Path

from battlefieldengine.Models import PHASE_ORDER, Phase, Unit, UnitState
from battlefieldengine.TerrainNode import TerrainNode
from battlefieldengine.RFIDReading import RFIDReading

logger = logging.getLogger(__name__)

# --- MQTT topic scheme (global -- one game, regardless of marker count) ---
TOPIC_TURN_STATE = "battlefield/turn/state"   # backend -> everyone: {"turn": int, "phase": str}
TOPIC_UNIT_EVENT = "battlefield/units/event"  # backend -> everyone: {"uid", "name", "event", "terrain"}
TOPIC_COMMAND = "battlefield/command"         # UI -> backend: {"action": "...", ...}


class UnitRegistry:
    """Maps RFID UID -> Unit metadata, loaded from a JSON file.

    Example UnitRegistry.json:
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
    """
    Usage:
        registry = UnitRegistry(Path("UnitRegistry.json"))
        bf = Battlefield(mqtt_client, registry)
        bf.start()
        bf.load_terrain_nodes(Path("ObjectiveMarkers.json"), Path("ObjectiveRoles.json"))
    """

    def __init__(self, mqtt_client, registry: UnitRegistry, presence_timeout_seconds: float = 3.0):
        """
        presence_timeout_seconds: how long a unit can go without a heartbeat
        (from ANY terrain node) before it's considered departed. Should be
        a bit longer than the ESP32's heartbeat interval so a single
        dropped MQTT message doesn't cause a false departure.
        """
        self._mqtt = mqtt_client
        self._registry = registry
        self._presence_timeout = timedelta(seconds=presence_timeout_seconds)

        self._lock = threading.Lock()
        self._turn = 1
        self._phase = PHASE_ORDER[0]
        self._units_seen: dict[str, UnitState] = {}

        self.terrain_nodes: dict[str, TerrainNode] = {}
        self._listeners: list[Callable[[str, dict], None]] = []

    # --- lifecycle --------------------------------------------------
    def start(self) -> None:
        """Subscribe to global topics. Call once at startup."""
        self._mqtt.subscribe(TOPIC_COMMAND, self._on_command)
        logger.info("Battlefield subscribed to MQTT topics")

    # --- terrain node ownership ----------------------------------------
    def load_terrain_nodes(self, markers_path: Path, roles_path: Path) -> list[TerrainNode]:
        """Build TerrainNode instances from config, start each one on THIS
        Battlefield's mqtt_client, and wire each node's on_scan callback
        back to this Battlefield so scans update global unit presence.
        """
        with open(roles_path) as f:
            roles = json.load(f)
        with open(markers_path) as f:
            raw_markers = json.load(f)

        for entry in raw_markers:
            role_profile = roles.get(entry["role"], {})
            node = TerrainNode(
                name=entry["name"],
                mqtt_topic=entry["mqtt_topic"],
                led_color=role_profile.get("light_color"),
                led_pattern=role_profile.get("light_pattern"),
                on_scan=self._on_terrain_scan,
            )
            node.start(self._mqtt)
            self.terrain_nodes[entry["mqtt_topic"]] = node

        logger.info("Battlefield loaded %d terrain node(s): %s",
                    len(self.terrain_nodes), list(self.terrain_nodes.keys()))
        return list(self.terrain_nodes.values())

    def get_terrain_node(self, mqtt_topic: str) -> Optional[TerrainNode]:
        return self.terrain_nodes.get(mqtt_topic)

    # --- listener/observer pattern (for UI updates) ------------------
    def add_listener(self, callback: Callable[[str, dict], None]) -> None:
        """NOTE: fires from the MQTT client's network thread. When updating
        a Textual UI, marshal back onto the app thread:
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

    # --- scan handling (called by TerrainNode, not MQTT directly) --------
    def _on_terrain_scan(self, terrain_node: TerrainNode, reading: RFIDReading) -> None:
        """Called by a TerrainNode on every scan heartbeat it receives.
        Same "first heartbeat = arrival" logic as before -- just triggered
        by TerrainNode rather than a raw MQTT subscription.
        """
        unit = self._registry.get(reading.uid)
        if unit is None:
            logger.warning("Unrecognized RFID UID scanned at %s: %s", terrain_node.name, reading.uid)
            self._notify("unknown_unit_scanned", {"uid": reading.uid, "terrain": terrain_node.name})
            return

        newly_arrived = False
        with self._lock:
            state = self._units_seen.get(reading.uid)
            now = datetime.now()
            if state is None:
                state = UnitState(unit=unit, on_field=True, last_seen=now)
                self._units_seen[reading.uid] = state
                newly_arrived = True
            else:
                if not state.on_field:
                    newly_arrived = True
                state.on_field = True
                state.last_seen = now

        if newly_arrived:
            data = {
                "uid": reading.uid,
                "name": unit.name,
                "faction": unit.faction,
                "event": "unit_arrived",
                "terrain": terrain_node.name,
            }
            self._mqtt.publish(TOPIC_UNIT_EVENT, data)
            self._notify("unit_arrived", data)
            terrain_node.light_on()

    def check_departures(self) -> None:
        """Sweep for units that haven't sent a heartbeat within the presence
        timeout and mark them departed. Call this periodically (e.g. every
        second) from a background loop.
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
            self.terrain_nodes["battlefield/terrain/home_base"].light_off()

    def _on_command(self, topic: str, payload: dict) -> None:
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
