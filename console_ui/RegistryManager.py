"""
RegistryManager: owns reading/writing the unit registry files.

Each unit is defined in Units.json. Tag UIDs assigned to units are
stored inside each unit's entry under the 'tags' list; TagAssignments.json
is no longer used. This keeps unit metadata and its associated tags together.

This class has zero knowledge of MQTT or Textual -- pure data logic, so
it's easy to reuse from the Registration screen, a future CLI tool, tests,
or anything else.
"""
from __future__ import annotations

import json
import re
import logging
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Optional


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")
    return slug or "unit"


@dataclass
class UnitEntry:
    name: str
    faction: str
    owner: Optional[str] = None
    # Optional user-provided unit name (a human-friendly or alternate name)
    unit_name: Optional[str] = None
    # Optional numeric control value associated with the unit
    control_value: Optional[int] = None
    # Track tag UIDs assigned to this unit (migrates TagAssignments into Units.json)
    tags: list[str] = field(default_factory=list)


class RegistryManager:
    def __init__(self, units_path: Path, tags_path: Path | None = None, unit_registry_export_path: Path | None = Path("battlefieldengine/battlefieldengine/configurations/UnitRegistry.json")):
        """units_path: path to Units.json
        tags_path: legacy (ignored) kept for compatibility with callers.
        unit_registry_export_path: optional path to write the merged UID->unit metadata
            file that the backend expects (UnitRegistry.json). If None, no export is written.
        """
        self.units_path = units_path
        # Tags are now stored inside Units.json; ignore legacy tags_path
        self.tags_path = tags_path
        self.unit_registry_export_path = unit_registry_export_path
        self.units: dict[str, UnitEntry] = {}
        self._load()

    def _load(self) -> None:
        if self.units_path.exists():
            with open(self.units_path) as f:
                raw = json.load(f)
            # Support older Units.json that didn't include new fields
            self.units = {uid: UnitEntry(**data) for uid, data in raw.items()}

    def _build_unit_registry_export(self) -> dict:
        """Build the merged mapping expected by the backend UnitRegistry.json:
        { "<tag_uid>": {"name": ..., "faction": ..., "owner": ...}, ... }
        Reads tags embedded in Units.json (unit.tags).
        """
        export: dict[str, dict] = {}
        for unit_id, unit in self.units.items():
            for tag_uid in unit.tags:
                export[tag_uid] = {
                    "name": unit.name,
                    "faction": unit.faction,
                    # owner may be None; include it explicitly (will be null in JSON)
                    "owner": unit.owner,
                }
        return export

    def save(self) -> None:
        # Ensure parent folders exist for the primary file.
        self.units_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.units_path, "w") as f:
            json.dump({uid: asdict(u) for uid, u in self.units.items()}, f, indent=2)

        # Optionally export a merged UnitRegistry.json that maps UID->unit metadata
        if self.unit_registry_export_path is not None:
            export = self._build_unit_registry_export()
            # Create parent dir and write the file
            self.unit_registry_export_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.unit_registry_export_path, "w") as f:
                json.dump(export, f, indent=2)

    def find_unit_id_by_name(self, name: str) -> Optional[str]:
        for unit_id, unit in self.units.items():
            if unit.name.strip().lower() == name.strip().lower():
                return unit_id
            if unit.unit_name and unit.unit_name.strip().lower() == name.strip().lower():
                return unit_id
        return None

    def get_unit_id_by_tag(self, tag_uid: str) -> Optional[str]:
        """Return the unit_id that currently lists tag_uid, or None."""
        for unit_id, unit in self.units.items():
            if tag_uid in (unit.tags or []):
                return unit_id
        return None

    def register_tag(self, tag_uid: str, unit_name: str, faction: str, owner: Optional[str] = None, unit_name_optional: Optional[str] = None, control_value: Optional[int] = None) -> tuple[str, bool]:
        """Attach tag_uid to a unit named unit_name, creating the unit if it
        doesn't exist yet, or reusing it if it does. The tag UIDs are stored
        inside the unit entry under 'tags'. Returns (unit_id, created_new_unit).
        """
        unit_id = self.find_unit_id_by_name(unit_name)
        created_new_unit = unit_id is None
        if created_new_unit:
            base = slugify(unit_name)
            unit_id = base
            counter = 2
            while unit_id in self.units:
                unit_id = f"{base}_{counter}"
                counter += 1
            self.units[unit_id] = UnitEntry(name=unit_name, faction=faction, owner=owner, unit_name=unit_name_optional, control_value=control_value, tags=[tag_uid])
        else:
            unit = self.units[unit_id]
            # update optional fields if provided
            if unit_name_optional:
                unit.unit_name = unit_name_optional
            if control_value is not None:
                unit.control_value = control_value
            if tag_uid not in unit.tags:
                unit.tags.append(tag_uid)

        return unit_id, created_new_unit