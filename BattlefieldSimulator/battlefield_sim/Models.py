"""Core data models for the battlefield simulator."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class Phase(str, Enum):
    COMMAND = "command"
    MOVEMENT = "movement"
    SHOOTING = "shooting"
    CHARGE = "charge"
    FIGHT = "fight"
    MORALE = "morale"


PHASE_ORDER = [
    Phase.COMMAND,
    Phase.MOVEMENT,
    Phase.SHOOTING,
    Phase.CHARGE,
    Phase.FIGHT,
    Phase.MORALE,
]


@dataclass
class Unit:
    """Static metadata about a unit, loaded from the unit registry."""

    uid: str  # RFID tag UID, e.g. "04A3B2C1"
    name: str
    faction: str
    owner: Optional[str] = None  # player name/id, useful for multiplayer
    points: Optional[int] = None
    metadata: dict = field(default_factory=dict)  # wounds, keywords, whatever else you need


@dataclass
class UnitState:
    """Live, changing state for a unit currently tracked on the battlefield."""

    unit: Unit
    on_field: bool = False
    last_seen: Optional[datetime] = None