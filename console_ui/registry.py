"""JSON registry backend with atomic writes."""

import json
import os
from pathlib import Path


class Registry:
    def __init__(self, path: str = "registry.json"):
        self.path = Path(path)
        self._data: dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            with open(self.path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        else:
            self._data = {}

    def get(self, uuid: str) -> dict | None:
        return self._data.get(uuid)

    def set(self, uuid: str, owner: str, faction: str, unit: str) -> bool:
        """Store entry. Returns True if UUID already existed (overwrite)."""
        existed = uuid in self._data
        self._data[uuid] = {
            "owner": owner,
            "faction": faction,
            "unit": unit,
        }
        return existed

    def save(self) -> None:
        temp = self.path.with_suffix(".tmp")
        with open(temp, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)
            f.write("\n")
        os.replace(temp, self.path)

    def all(self) -> dict:
        return dict(self._data)