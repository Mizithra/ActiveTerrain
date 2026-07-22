"""
server.py: main backend entrypoint for ActiveTerrain.

GameServer is the composition root: it owns the long-lived pieces (the
MQTT client, the Battlefield -- which in turn owns TerrainNodes) as member
variables. Config parsing and logging setup stay as plain module-level
functions since they run once, before there's a server object to attach
them to.

Adding a new feature later (a scoreboard, a sound controller, a Discord
bridge, ...) means:
  1. Add `self.<feature> = None` in __init__
  2. Add a `_build_<feature>(self)` method, called from setup()
  3. It can freely use self.mqtt / self.battlefield, no new plumbing needed

Run with:
    python server.py --config server_config.json
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Optional

from battlefieldengine import mqtt_client as mqtt_client_module
from battlefieldengine.mqtt_adapter import MQTTAdapter
from battlefieldengine.Battlefield import Battlefield, UnitRegistry

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = "battlefieldengine/battlefieldengine/configurations/server_config.json"


# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------
def load_config(path: Path) -> dict:
    """Central place for server settings. Add new keys here as the project
    grows (e.g. "sound_config_path") rather than hardcoding paths elsewhere.
    """
    with open(path) as f:
        return json.load(f)


# --------------------------------------------------------------------------
# Logging
# --------------------------------------------------------------------------
def setup_logging(config: dict) -> None:
    log_cfg = config.get("logging", {})
    log_path = Path(log_cfg.get("path", "logs/server.log"))
    log_path.parent.mkdir(parents=True, exist_ok=True)
    level = getattr(logging, log_cfg.get("level", "INFO").upper(), logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler(sys.stdout),
        ],
    )


# --------------------------------------------------------------------------
# GameServer
# --------------------------------------------------------------------------
class GameServer:
    """Owns the long-lived backend pieces: the MQTT client and the
    Battlefield (which owns TerrainNodes). Holding these as member
    variables -- rather than passing loose locals around main() -- is
    what makes it easy to bolt on new features later without threading
    new parameters through a chain of functions.
    """

    def __init__(self, config: dict):
        ### Initialize components in the order they depend on each other.
        self.config = config

        self.mqtt = self._build_mqtt_client()

        self.registry = UnitRegistry(Path(self.config["unit_registry_path"])) # must be before battlefield

        self.battlefield = self._build_battlefield()
        self.battlefield.load_terrain_nodes(
            Path(self.config["objective_markers_path"]),
            Path(self.config["objective_roles_path"]),
        )
        self.battlefield.start()



    def _build_mqtt_client(self) -> MQTTAdapter:
        raw_client = mqtt_client_module.create_mqtt_client()
        raw_client.loop_start()
        return MQTTAdapter(raw_client)

    def _build_battlefield(self) -> Battlefield:
        timeout = self.config.get("presence_timeout_seconds", 5.0)
        battlefield = Battlefield("home_base", self.mqtt, self.registry, presence_timeout_seconds=timeout)
        logger.info("Battlefield ready (presence timeout: %ss)", timeout)
        return battlefield

    def run_forever(self, interval_seconds: float = 1.0) -> None:
        """Blocks until Ctrl+C. Add other periodic checks here (e.g. a
        future TerrainNode departure sweep) alongside Battlefield's.
        """
        logger.info("Server running. Press Ctrl+C to stop.")
        try:
            while True:
                self.battlefield.check_departures()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            logger.info("Shutdown requested, exiting.")

    def shutdown(self) -> None:
        if self.mqtt:
            self.mqtt.loop_stop()
        logger.info("Server stopped.")


# --------------------------------------------------------------------------
# Entrypoint
# --------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="ActiveTerrain backend server")
    parser.add_argument(
        "--config", type=Path, default=DEFAULT_CONFIG_PATH,
        help="Path to server_config.json (default: %(default)s)",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    setup_logging(config)
    logger.info("Starting ActiveTerrain server (config: %s)", args.config)

    server = GameServer(config)
    try:
        server.run_forever()
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()