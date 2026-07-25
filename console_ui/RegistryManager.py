"""
RegistryManager: owns reading/writing the unit registry files.

Two-tier design: a unit is defined once in Units.json, and any number of
physical RFID tags can point at the same unit via TagAssignments.json.
This supports registering multiple tags per unit (per your override-flag /
multi-tag design) without duplicating unit info per tag.

This class has zero knowledge of MQTT or Textual -- pure data logic, so
it's easy to reuse from the Registration screen, a future CLI tool, tests,
or anything else.
"""
from __future__ import annotations

import json
import re
import logging
from dataclasses import dataclass, asdict
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


@dataclass
class TagAssignment:
    unit_id: str
    tag_role: str = "unit"


class RegistryManager:
    def __init__(self, units_path: Path, tags_path: Path, unit_registry_export_path: Path | None = Path("battlefieldengine/battlefieldengine/configurations/UnitRegistry.json")):
        """units_path: path to Units.json
        tags_path: path to TagAssignments.json
        unit_registry_export_path: optional path to write the merged UID->unit metadata
            file that the backend expects (UnitRegistry.json). If None, no export is written.
        """
        self.units_path = units_path
        self.tags_path = tags_path
        self.unit_registry_export_path = unit_registry_export_path
        self.units: dict[str, UnitEntry] = {}
        self.tags: dict[str, TagAssignment] = {}
        self._load()

    def _load(self) -> None:
        if self.units_path.exists():
            with open(self.units_path) as f:
                raw = json.load(f)
            self.units = {uid: UnitEntry(**data) for uid, data in raw.items()}
        if self.tags_path.exists():
            with open(self.tags_path) as f:
                raw = json.load(f)
            self.tags = {tag: TagAssignment(**data) for tag, data in raw.items()}

    def _build_unit_registry_export(self) -> dict:
        """Build the merged mapping expected by the backend UnitRegistry.json:
        { "<tag_uid>": {"name": ..., "faction": ..., "owner": ...}, ... }
        Tags that reference missing units are omitted with a warning.
        """
        export: dict[str, dict] = {}
        for tag_uid, assignment in self.tags.items():
            unit = self.units.get(assignment.unit_id)
            if unit is None:
                # Skip inconsistent entries; keep a helpful hint for operators.
                logger = logging.getLogger(__name__)
                logger.warning("RegistryManager: tag %s references missing unit %s", tag_uid, assignment.unit_id)
                continue
            export[tag_uid] = {
                "name": unit.name,
                "faction": unit.faction,
                # owner may be None; include it explicitly (will be null in JSON)
                "owner": unit.owner,
            }
        return export

    def save(self) -> None:
        # Ensure parent folders exist for the two primary files.
        self.units_path.parent.mkdir(parents=True, exist_ok=True)
        self.tags_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.units_path, "w") as f:
            json.dump({uid: asdict(u) for uid, u in self.units.items()}, f, indent=2)
        with open(self.tags_path, "w") as f:
            json.dump({tag: asdict(t) for tag, t in self.tags.items()}, f, indent=2)

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
        return None

    def get_tag_assignment(self, tag_uid: str) -> Optional[TagAssignment]:
        return self.tags.get(tag_uid)

    def register_tag(
        self, tag_uid: str, unit_name: str, faction: str, owner: Optional[str] = None
    ) -> tuple[str, bool]:
        """Attach tag_uid to a unit named unit_name, creating the unit if it
        doesn't exist yet, or reusing it if it does. Returns
        (unit_id, created_new_unit).

        Overwrites tag_uid's existing assignment (if any) without asking --
        callers should confirm with the user first via get_tag_assignment()
        before calling this.
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
            self.units[unit_id] = UnitEntry(name=unit_name, faction=faction, owner=owner)

        self.tags[tag_uid] = TagAssignment(unit_id=unit_id, tag_role="unit")
        return unit_id, created_new_unit