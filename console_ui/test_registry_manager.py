import json
from pathlib import Path

from console_ui.RegistryManager import RegistryManager


def test_register_tag_creates_new_unit(tmp_path: Path) -> None:
    registry = RegistryManager(tmp_path / "Units.json", None)

    unit_id, created_new_unit = registry.register_tag(
        "abc123", "Alpha", "red", owner="tester"
    )

    assert created_new_unit is True
    assert unit_id in registry.units
    assert registry.units[unit_id].name == "Alpha"
    assert registry.units[unit_id].faction == "red"
    assert registry.units[unit_id].owner == "tester"
    assert registry.units[unit_id].tags == ["ABC123"]
    assert registry.get_unit_id_by_tag("ABC123") == unit_id


def test_register_tag_overrides_existing_tag_to_new_unit(tmp_path: Path) -> None:
    registry = RegistryManager(tmp_path / "Units.json", None)
    original_id, _ = registry.register_tag("abc123", "Alpha", "red")

    new_id, created_new_unit = registry.register_tag("abc123", "Bravo", "blue")

    assert created_new_unit is True
    assert original_id != new_id
    assert "ABC123" not in registry.units[original_id].tags
    assert registry.units[new_id].name == "Bravo"
    assert registry.units[new_id].faction == "blue"
    assert registry.units[new_id].tags == ["ABC123"]
    assert registry.get_unit_id_by_tag("ABC123") == new_id


def test_register_tag_moves_existing_tag_to_existing_unit(tmp_path: Path) -> None:
    registry = RegistryManager(tmp_path / "Units.json", None)
    source_id, _ = registry.register_tag("abc123", "Alpha", "red")
    target_id, _ = registry.register_tag("def456", "Bravo", "blue")

    moved_id, created_new_unit = registry.register_tag("abc123", "Bravo", "blue")

    assert created_new_unit is False
    assert moved_id == target_id
    assert "ABC123" not in registry.units[source_id].tags
    assert "ABC123" in registry.units[target_id].tags
    assert registry.get_unit_id_by_tag("ABC123") == target_id


def test_register_tag_normalizes_tag_uid(tmp_path: Path) -> None:
    registry = RegistryManager(tmp_path / "Units.json", None)

    unit_id, created_new_unit = registry.register_tag(" abc123 ", "Alpha", "red")

    assert created_new_unit is True
    assert registry.units[unit_id].tags == ["ABC123"]
    assert registry.get_unit_id_by_tag("abc123") == unit_id

    same_id, created_again = registry.register_tag("AbC123", "Alpha", "red")

    assert created_again is False
    assert same_id == unit_id
    assert registry.units[unit_id].tags == ["ABC123"]

    new_id, created_new_unit = registry.register_tag("  AbC123  ", "Bravo", "blue")

    assert created_new_unit is True
    assert new_id != unit_id
    assert "ABC123" not in registry.units[unit_id].tags
    assert registry.units[new_id].tags == ["ABC123"]
    assert registry.get_unit_id_by_tag("abc123") == new_id


def test_load_normalizes_tags_from_json(tmp_path: Path) -> None:
    units_path = tmp_path / "Units.json"
    units_path.write_text(json.dumps({
        "unit1": {
            "name": "Alpha",
            "faction": "red",
            "tags": ["abc123", " def456 "],
        }
    }))

    registry = RegistryManager(units_path, None)

    assert registry.get_unit_id_by_tag("ABC123") == "unit1"
    assert registry.get_unit_id_by_tag("def456") == "unit1"
    assert registry.units["unit1"].tags == ["ABC123", "DEF456"]
