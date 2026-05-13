

from enum import Enum
import numpy as np

# This class represents a Players Faction in the battlefield simulator. 
# Each faction has a name and a color. The color is used to differentiate between different factions on the battlefield.
# A faction also have a 

class Faction:
    def __init__(self, name: str, color: str):
        self.name = name
        self.color = color #LED / Visual color for the faction
        self.faction_name = "Tau"
        self.faction = 0#TabletopEnums.Faction.TAU
