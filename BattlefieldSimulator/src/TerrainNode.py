#####  Terrain Node

import Faction
from NeutralFaction import NeutralFac as NeutralFaction

class TerrainNode:
    def __init__(self, name):
        self.name = name
        self.controller = NeutralFaction
        print(f"Created Terrain Node: {self.name} with controller: {self.controller.name}")
        

    def capture(self, faction:Faction.Faction):
        self.controller = faction
        print(f"{self.name} captured by {self.controller.name}")
        self.updateLights()

    def updateLights(self):
        print(f"Updating lights for {self.name} controlled by {self.controller.name} to {self.controller.color}")
        
def main():
    node1 = TerrainNode("Shield Generator")
    node2 = TerrainNode("Reactor")
    node3 = TerrainNode("Data Terminal")
    node4 = TerrainNode("Radar Tower")
    TerrainNodeList = []
    TerrainNodeList.append(node1)
    TerrainNodeList.append(node2)
    TerrainNodeList.append(node3)
    TerrainNodeList.append(node4)
    node1.capture(Faction.Faction("Red Team", "red"))
    node2.capture(Faction.Faction("Blue Team", "blue"))


if __name__ == "__main__":
    main()