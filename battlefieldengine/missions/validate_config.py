#!/usr/bin/env python3
"""
validate_config.py

Checks a hardware rig file and a theme file are internally valid AND that
they actually fit together - i.e. every hardware_alias in the theme points
at an id that really exists in the rig. This is the check you want to run
in CI / on startup, before your engine tries to blink an LED that doesn't
exist and just silently does nothing.

Usage:
    python3 validate_config.py hardware/rig.json themes/reactor-meltdown.json

Requires: pip install jsonschema --break-system-packages
"""

import json
import re
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    sys.exit("Missing dependency. Run: pip install jsonschema --break-system-packages")

SCRIPT_DIR = Path(__file__).resolve().parent
HARDWARE_SCHEMA_PATH = SCRIPT_DIR / "schemas" / "hardware-rig.schema.json"
THEME_SCHEMA_PATH = SCRIPT_DIR / "schemas" / "theme.schema.json"

TEMPLATE_RE = re.compile(r"\{\{.*?\}\}")


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def schema_validate(instance, schema, label):
    validator = jsonschema.Draft7Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)
    if errors:
        print(f"  [FAIL] {label} did not match its schema:")
        for e in errors:
            loc = "/".join(str(p) for p in e.path) or "(root)"
            print(f"         at {loc}: {e.message}")
        return False
    print(f"  [ OK ] {label} matches its schema.")
    return True


def collect_rig_ids(rig: dict) -> set:
    ids = set()
    for category in ("leds", "oled_screens", "audio_outputs", "haptics"):
        for item in rig.get(category, []):
            ids.add(item["id"])
    return ids


def collect_action_targets(theme: dict):
    """Yields (rule_id, action_index, target_string) for every action that has a target."""
    for rule in theme.get("events", []):
        for i, action in enumerate(rule.get("actions", [])):
            target = action.get("target")
            if target:
                yield rule["id"], i, target


def is_static(target: str) -> bool:
    """True if the target has no {{ }} template segments, so we can check it directly."""
    return TEMPLATE_RE.search(target) is None


def strip_template_vars(target: str) -> str:
    """
    Replaces {{...}} segments with a wildcard marker, so 'objective_{{trigger.objective_id}}_led'
    becomes 'objective_*_led' for a fuzzy sanity check against alias key patterns.
    """
    return TEMPLATE_RE.sub("*", target)


def cross_check(rig: dict, theme: dict) -> bool:
    ok = True
    rig_ids = collect_rig_ids(rig)
    aliases = theme.get("hardware_aliases", {})

    print("  Checking hardware_aliases -> rig ids ...")
    for alias_name, rig_id in aliases.items():
        if rig_id not in rig_ids:
            print(f"  [FAIL] hardware_aliases['{alias_name}'] = '{rig_id}', "
                  f"but no hardware with that id exists in the rig.")
            ok = False
    if ok:
        print(f"  [ OK ] All {len(aliases)} hardware_aliases resolve to real rig ids.")

    print("  Checking action targets -> hardware_aliases ...")
    unresolved_static = []
    dynamic_count = 0
    for rule_id, idx, target in collect_action_targets(theme):
        if is_static(target):
            if target not in aliases:
                unresolved_static.append((rule_id, idx, target))
        else:
            dynamic_count += 1
            # Fuzzy check: does the wildcard-stripped pattern match any known alias shape?
            pattern = strip_template_vars(target)
            regex = re.compile("^" + re.escape(pattern).replace(re.escape("*"), ".+") + "$")
            if not any(regex.match(a) for a in aliases):
                print(f"  [WARN] rule '{rule_id}' action[{idx}] target '{target}' is templated "
                      f"and no alias name matches the pattern '{pattern}' for ANY value - "
                      f"double check this one by hand.")

    if unresolved_static:
        ok = False
        for rule_id, idx, target in unresolved_static:
            print(f"  [FAIL] rule '{rule_id}' action[{idx}] target '{target}' "
                  f"is not a key in hardware_aliases.")
    else:
        print(f"  [ OK ] All static action targets resolve to a hardware_alias "
              f"({dynamic_count} templated targets were pattern-checked, not fully resolved).")

    return ok


def main():
    if len(sys.argv) != 3:
        sys.exit(f"Usage: python3 {sys.argv[0]} <rig.json> <theme.json>")

    rig_path = Path(sys.argv[1])
    theme_path = Path(sys.argv[2])

    hardware_schema = load_json(HARDWARE_SCHEMA_PATH)
    theme_schema = load_json(THEME_SCHEMA_PATH)
    rig = load_json(rig_path)
    theme = load_json(theme_path)

    print(f"Validating {rig_path} ...")
    rig_ok = schema_validate(rig, hardware_schema, str(rig_path))

    print(f"\nValidating {theme_path} ...")
    theme_ok = schema_validate(theme, theme_schema, str(theme_path))

    print(f"\nCross-checking {theme_path} against {rig_path} ...")
    cross_ok = cross_check(rig, theme) if (rig_ok and theme_ok) else False

    compat = theme.get("meta", {}).get("compatible_rig")
    rig_id = rig.get("meta", {}).get("rig_id")
    if compat and rig_id and compat != rig_id:
        print(f"\n  [WARN] theme.meta.compatible_rig = '{compat}' but this rig's "
              f"meta.rig_id = '{rig_id}'. May still work, but wasn't the rig this theme was built for.")

    print()
    if rig_ok and theme_ok and cross_ok:
        print("All checks passed.")
        sys.exit(0)
    else:
        print("One or more checks failed - see [FAIL] lines above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
