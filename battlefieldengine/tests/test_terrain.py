import pytest
import TerrainNode
import Faction


def test_terrain_node_creation():
    node = TerrainNode.TerrainNode("Test Node")
    assert node.name == "Test Node"
    assert node.controller.name == "Neutral"

def test_terrain_node_capture():
    node = TerrainNode.TerrainNode("Test Node")
    faction = Faction.Faction("Red Team", "red")
    node.capture(faction)
    assert node.controller.name == "Red Team"