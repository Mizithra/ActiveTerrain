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
import logging
import re
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")
    return slug or "unit"


@dataclass
class UnitEntry:
    name: str
    faction: str
    owner: Optional[str] = None
    # Optional user-provided unit name (a human-friendly or alternate name)
    shared_name: Optional[str] = None
    # Optional numeric control value associated with the unit
    control_value: Optional[int] = None
    # Track tag UIDs assigned to this unit (migrates TagAssignments into Units.json)
    tags: list[str] = field(default_factory=list)


class RegistryManager:
    def __init__(self, units_path: Path, tags_path: Path | None = None):
        """units_path: path to Units.json
        tags_path: legacy (ignored) kept for compatibility with callers.
            file that the backend expects (UnitRegistry.json). If None, no export is written.
        """
        self.units_path = units_path
        # Tags are now stored inside Units.json; ignore legacy tags_path
        self.tags_path = tags_path
        self.units: dict[str, UnitEntry] = {}
        self._load()

    def _load(self) -> None:
        if self.units_path.exists():
            with open(self.units_path) as f:
                raw = json.load(f)
            # Support older Units.json that didn't include new fields.
            self.units = {}
            for uid, data in raw.items():
                unit = UnitEntry(**data)
                unit.tags = [self._normalize_tag_uid(tag) for tag in (unit.tags or [])]
                self.units[uid] = unit
            logger.info("Loaded %d registry entries from %s", len(self.units), self.units_path)


    def _normalize_tag_uid(self, tag_uid: str) -> str:
        return tag_uid.strip().upper()

    def save(self) -> None:
        # Ensure parent folders exist for the primary file.
        self.units_path.parent.mkdir(parents=True, exist_ok=True)
        logger.debug("Saving %d registry entries to %s", len(self.units), self.units_path)
        with open(self.units_path, "w") as f:
            json.dump({uid: asdict(u) for uid, u in self.units.items()}, f, indent=2)


    def find_unit_id_by_name(self, name: str) -> Optional[str]:
        for unit_id, unit in self.units.items():
            if unit.name.strip().lower() == name.strip().lower():
                return unit_id
            if unit.shared_name and unit.shared_name.strip().lower() == name.strip().lower():
                return unit_id
        return None

    def get_unit_id_by_tag(self, tag_uid: str) -> Optional[str]:
        """Return the unit_id that currently lists tag_uid, or None."""
        normalized_uid = self._normalize_tag_uid(tag_uid)
        for unit_id, unit in self.units.items():
            if normalized_uid in (unit.tags or []):
                return unit_id
        return None

    def register_tag(self, tag_uid: str, unit_name: str, faction: str, owner: Optional[str] = None, shared_name: Optional[str] = None, control_value: Optional[int] = None) -> tuple[str, bool]:
        """Attach tag_uid to a unit named unit_name, creating the unit if it
        doesn't exist yet, or reusing it if it does. The tag UIDs are stored
        inside the unit entry under 'tags'. Returns (unit_id, created_new_unit).
        """
        logger.info(
            "Registering tag %s to unit '%s' faction=%s owner=%s shared_name=%s control_value=%s",
            tag_uid,
            unit_name,
            faction,
            owner,
            shared_name,
            control_value,
        )
        tag_uid = self._normalize_tag_uid(tag_uid)
        existing_unit_id = self.get_unit_id_by_tag(tag_uid)
        target_unit_id = self.find_unit_id_by_name(unit_name)

        if existing_unit_id is not None and existing_unit_id != target_unit_id:
            existing_unit = self.units.get(existing_unit_id)
            if existing_unit and tag_uid in existing_unit.tags:
                existing_unit.tags.remove(tag_uid)

        if target_unit_id is None:
            base = slugify(tag_uid).upper()
            unit_id = base
            counter = 2
            while unit_id in self.units:
                unit_id = f"{base}_{counter}"
                counter += 1
            self.units[unit_id] = UnitEntry(name=unit_name, faction=faction, owner=owner, shared_name=shared_name, control_value=control_value, tags=[tag_uid])
            created_new_unit = True
        else:
            unit_id = target_unit_id
            unit = self.units[unit_id]
            # update optional fields if provided
            if shared_name:
                unit.shared_name = shared_name
            if control_value is not None:
                unit.control_value = control_value
            if tag_uid not in unit.tags:
                unit.tags.append(tag_uid)
            created_new_unit = False

        return unit_id, created_new_unit
