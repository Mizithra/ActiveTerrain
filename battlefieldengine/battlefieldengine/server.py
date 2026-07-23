"""
server.py: main backend entrypoint for ActiveTerrain.
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


def load_config(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


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


class GameServer:
    def __init__(self, config: dict):
        self.config = config
        self.mqtt: Optional[MQTTAdapter] = None
        self.battlefield: Optional[Battlefield] = None

    def setup(self) -> None:
        self.mqtt = self._build_mqtt_client()
        self.battlefield = self._build_battlefield()
        self.battlefield.load_terrain_nodes(
            Path(self.config["objective_markers_path"]),
            Path(self.config["objective_roles_path"]),
        )

    def _build_mqtt_client(self) -> MQTTAdapter:
        raw_client = mqtt_client_module.create_mqtt_client()
        raw_client.loop_start()
        return MQTTAdapter(raw_client)

    def _build_battlefield(self) -> Battlefield:
        registry = UnitRegistry(Path(self.config["unit_registry_path"]))
        timeout = self.config.get("presence_timeout_seconds", 3.0)
        battlefield = Battlefield(self.mqtt, registry, presence_timeout_seconds=timeout)
        battlefield.start()
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
    server.setup()
    try:
        server.run_forever()
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
