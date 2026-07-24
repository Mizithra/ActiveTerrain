# Game Event Config Set

## File layout

```
schemas/
  hardware-rig.schema.json   validates hardware/rig.json
  theme.schema.json          validates every file in themes/
hardware/
  rig.json                   the ONE physical build - pins, addresses, wiring
themes/
  reactor-meltdown.json      game logic + flavor, scenario 1
  arms-deal.json             game logic + flavor, scenario 2
validate_config.py           checks a rig + theme pair are valid AND fit together
```

Five files, three roles: **schema** (shape, rarely touched), **rig** (physical
truth, touched when you rewire something), **themes** (game design, touched
constantly - this is where you'll spend most of your creative time once the
rig exists).

## Why it's split this way

You said the hardware wiring is where you'll spend the most setup time, and
that you want to reuse that work across many quickly-authored themes. So the
split is:

- **`hardware/rig.json`** knows nothing about the game. It has no idea what a
  "team" or an "objective" is. It only knows *"there is an LED at
  `strip0:pixel12`"*. You edit this file exactly once per physical build, and
  every theme you ever write reuses it unchanged.

- **`themes/*.json`** know nothing about pins. They talk entirely in
  narrative names (`objective_1_led`, `alarm_led`, `briefcase_led`) and MQTT
  topic strings. A theme's `hardware_aliases` block is the ONLY place the two
  worlds touch - it's a small map from "the name this theme calls a piece of
  hardware" to "the physical id that piece of hardware actually has in the
  rig". Everything else in a theme file (`state`, `events`) only ever refers
  to the narrative name, never the physical id directly.

That's also why the same spare LED (`led_3` in the rig) can be `alarm_led` in
Reactor Meltdown and `briefcase_led` in Arms Deal - one wire, two roles,
decided entirely by which theme's `hardware_aliases` you loaded.

## MQTT - deliberately absent

Earlier drafts of this config had a `mqtt` block with broker host/port/client
id. That's gone now. Since ActiveTerrain already owns the MQTT connection and
subscription logic in Python, these files don't need to know how to connect
to anything - they only need plain topic *strings* (`game/events/objective/+/status`)
that your existing subscriber matches against and routes to the matching
`events[].trigger`. If ActiveTerrain's existing config already has its own
topic-prefix convention, these topic strings should just match that
convention - there's nothing here to keep in sync beyond the string itself.

## How the pieces resolve at runtime

Given an incoming MQTT message on `game/events/objective/1/status` with
payload `{"status": "secured", "team_name": "Red Squad", "team_color": "#FF0000"}`:

1. Engine matches the topic against `reactor-meltdown.json`'s
   `events[].trigger.topic` patterns -> finds `objective_secured`, and
   captures `objective_id = "1"` from the wildcard (per `topic_vars`).
2. `conditions` checked: `payload.status == "secured"` -> true.
3. First action: `led` with `target: "objective_{{trigger.objective_id}}_led"`.
   Template resolves to `"objective_1_led"`.
4. Engine looks up `"objective_1_led"` in the theme's `hardware_aliases` ->
   gets `"led_1"`.
5. Engine looks up `"led_1"` in `hardware/rig.json` -> gets
   `device_id: "strip0:pixel12"`, `supports_rgb: true`.
6. Engine drives that pixel to `payload.team_color` (`#FF0000`).
7. Remaining actions in the rule fire the same way (OLED text, an
   `mqtt_publish` if present, or a `state_update` that pushes a timestamp
   into the `objective_takeovers` sliding window for the escalation rule).

Three lookups, one direction each time: **topic -> rule -> narrative
target -> rig id -> physical device.** Nothing in a theme file ever needs to
know a pin number, and nothing in the rig file ever needs to know what
"secured" means.

## Loading order for your engine

1. Load `hardware/rig.json` once at startup.
2. Load the selected theme from `themes/`.
3. Resolve every value in `hardware_aliases` against the rig's ids, building
   an in-memory map of narrative-name -> physical device record. Fail fast
   (see `validate_config.py`) if any alias doesn't resolve - better to catch
   a typo before the game starts than mid-round.
4. Collect every distinct `trigger.topic` pattern across the theme's `events`
   and hand that list to your existing ActiveTerrain MQTT subscriber.
5. On each inbound message, match topic -> rule -> evaluate conditions ->
   run actions, resolving templates via the map built in step 3.

## Validating before you trust a config

```bash
pip install jsonschema --break-system-packages
python3 validate_config.py hardware/rig.json themes/reactor-meltdown.json
```

This checks, in order:
- `rig.json` matches `hardware-rig.schema.json`
- the theme matches `theme.schema.json`
- every `hardware_aliases` value is a real id in the rig
- every static (non-templated) action `target` is a key in `hardware_aliases`
- templated targets (e.g. `objective_{{trigger.objective_id}}_led`) get a
  best-effort pattern check against alias names, and a warning if nothing
  plausible matches
- a soft warning if the theme's `meta.compatible_rig` doesn't match the
  rig's `meta.rig_id`

Run it against every theme in CI, or on your engine's startup, so a bad
config announces itself with an exit code instead of a silently-dead LED
mid-game.

## Comments in JSON

JSON has no real comment syntax, so both schemas allow an optional
`"_comment"` string field wherever it's useful (rig entries, theme meta,
individual rules/state) - purely documentation, ignored by the engine and by
`validate_config.py`. Avoid adding `_comment` keys inside `hardware_aliases`
itself though - it's a flat string-to-string map with no schema-level way to
mark a key as "not really an alias," so a stray comment key there would get
treated as a real (and broken) hardware reference by the cross-checker.

## Writing your third theme

1. Copy `arms-deal.json` (or `reactor-meltdown.json`) to
   `themes/your-theme.json`.
2. Update `meta` (`id`, `name`, `description`).
3. Decide which physical pieces from `hardware/rig.json` you're using and
   give them theme-appropriate names in `hardware_aliases`. Only rewire this
   file if the *physical* rig itself changes - reskinning never touches it.
4. Rename `state` ids if you like, or leave them - `objective_takeovers` is
   generic enough to reuse as-is.
5. Keep the `events[].id` and `trigger` shapes if the underlying game
   mechanic is the same (objective standing/contested/secured, terrain
   collision); only change the flavor leaves: `color`, `file`, `text`,
   `pattern`.
6. Run `validate_config.py` against it before you trust it on the field.

Ideas that fit the same skeleton: **Signal Jamming** (objective ->
relay tower, OLED shows a scrambling countdown, vibrate = jamming pulse) or
a timed **Heist** (lean on `cooldown_seconds` to stop alarm-spam during a
vault sequence).
