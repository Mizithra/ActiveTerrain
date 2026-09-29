# ActiveTerrain: Product & Technical Analysis

*Snapshot: 2026-09-28 · Author: Austin · Working assumption: ~10 hours/week*
*Companion document: [GitHub-Backlog.md](GitHub-Backlog.md), which turns every finding below into a tracked issue.*

**Contents**
1. [Current state](#1-current-state)
2. [Elevator pitch](#2-elevator-pitch)
3. [Roadmap to market](#3-roadmap-to-market)
4. [Firmware & backend review](#4-firmware--backend-review)
5. [Security to a reasonable standard](#5-security-to-a-reasonable-standard)
6. [Code structure & the three-layer pipeline](#6-code-structure--the-three-layer-pipeline)
7. [Shortcut ledger](#7-shortcut-ledger)

---

## 1. Current state

A working vertical slice exists: an ESP32 marker (PN532 RFID + LED + OLED + DFPlayer) publishes over TLS MQTT, the Python backend (`Battlefield`, `TerrainNode`, `GameServer`) tracks presence and sends the light command back, and a Textual UI (`BattlefieldUI`) drives turn/phase and a tag-registration flow. A rig/theme/mission config system is designed, with JSON Schemas and a cross-validator, but **no runtime engine executes it yet**.

The pasted snapshot has hardcoded pins and a single-GPIO LED. RigConfig/LittleFS loading, WS2812B and DRV2605 code are not present in it. This document treats those as planned or living elsewhere.

**Maturity:** impressive proof of concept. It is not yet a product.

---

## 2. Elevator pitch

**One line:** ActiveTerrain makes tabletop terrain react to the game. Objective markers know which units are standing on them and respond with light, sound and a live display, with no apps and no bookkeeping.

**30 seconds:** Wargames are tactile and social, but the tracking is still pencil and paper. ActiveTerrain hides an RFID reader in a piece of terrain, tags the bases of your models, and lets the table itself run the game. A unit steps onto an objective and the terrain glows in the army's colors, plays a sting, and shows who controls it. The hardware is generic. Scenario packs (Reactor Meltdown, Arms Deal, whatever the community writes) reskin the same kit through JSON files. You buy the terrain once and get new games as content.

**Commercial angle:** hardware margin at launch, then recurring revenue from mission packs and community-authored content.

---

## 3. Roadmap to market

| Phase | Weeks | Hours | Outcome | Milestone |
|---|---|---|---|---|
| 0. Decide and de-risk | 1–4 | ~40 | Architecture and branding decisions; multi-tag and magnet tests done | M0 |
| 1. Fix core, build the pipeline | 5–14 | ~100 | Three-layer pipeline running one mission on 2–3 nodes; CI | M1 |
| 2. Productize software | 15–28 | ~140 | Provisioning, security baseline, signed OTA, hub packaging, web UI | M2 |
| 3. Hardware v1 | 22–40 (overlaps) | ~140 | Custom PCB, enclosure, power design, unit-cost model | M3 |
| 4. Alpha and campaign prep | 36–52 | ~160 | 5–10 real players, video, landing page, campaign plan | M4 |
| 5. Compliance and pilot build | 52–70 | ~150 | Test-lab results, 50–100 unit run | M5 |

- **Crowdfunding-ready:** about week 52 (roughly 12 months).
- **First shipped units:** about 17 months if nothing slips. Hardware always slips, so plan for **18–24 months**.

### Phase 0 decisions that shape everything else

1. **Local-first hub or cloud broker.** Local-first means a small hub at the table, no per-customer cloud cost, and it works in a game store with bad WiFi. The cost is that you own hub packaging and local certificates. Cloud makes remote and spectator features easy but adds running costs and multi-tenant security. This decision changes topic names, so make it before touching them.
2. **Multi-tag reads.** `RfidTracker::poll()` calls `readPassiveTargetID`, which returns one card per call. Unless each card is deselected after reading, the same tag tends to answer every poll. The README says a marker tracks multiple models. The backend data structures can, but the reader path likely can't yet. Test 5+ magnetized bases on a real objective. If the PN532 can't do it, evaluate ISO15693 inventory-style readers. That changes the hardware.
3. **IP.** The repo contains faction art and "Space Marines" strings. Games Workshop is protective of its trademarks. For a commercial product, brand it system-agnostic ("any tabletop wargame") and treat 40K as a community launch context. Get a proper opinion before any campaign. This is not legal advice.
4. **Licensing.** PolyForm Noncommercial doesn't stop you selling your own product. It does stop others from doing so. Weigh that if you open-source the firmware for community growth, and decide on a DCO or CLA.

### Rough out-of-pocket (ballparks; get quotes)

- Prototype PCBs: a few hundred to ~$1.5K.
- Test-lab compliance (FCC/ISED for the 13.56 MHz reader, CE/RED including its cybersecurity requirements): roughly $5–15K. Verify scope with a lab.
- Injection-mold tooling: $5–20K+. Wait for crowdfunding money.

---

## 4. Firmware & backend review

### What's good
- The class-based firmware split (`MqttRouter`, `LedController`, `OledController`, `RfidTracker`, `ObjectiveNode`) is sound.
- The OLED task with a depth-1 queue and interruptible animations is a well-chosen pattern.
- Heartbeat plus presence window suits QoS 0 and lossy links.
- The `TerrainNode`/`Battlefield` split is the right instinct.
- Config-driven design: adding a marker or a theme is data, not code.

### Firmware gaps (most urgent first)
1. **Audio blocks ~6.5 s in an MQTT callback.** `AudioController::playFile` runs a hardcoded 3×(1 s on/1 s off) buzzer test with `delay()`. It stalls RFID polling and MQTT servicing, and it ignores the payload (always track 1).
2. **Undefined behavior:** `Serial.printf("...%s", payload)` passes an Arduino `String` to `%s`. Use `.c_str()`. `_mp3.loop()` is never called, so DFPlayer notifications aren't serviced.
3. **Registration topics are global** (`battlefield/terrain/registration/...`, ignoring `objectiveTopic`), so every marker responds. The blocking handler also re-enters `PubSubClient::loop()` from inside a callback.
4. **`_nfc(sdaPin, sclPin)`** resolves to Adafruit_PN532's `(irq, reset)` constructor, so GPIO 21/22 (the default I2C pins) become irq/reset and reset is toggled in `begin()`. This matches the earlier bus-contention symptom, so verify it.
5. **`rig.json` puts the haptic on gpio22**, which is I2C SCL.
6. **Boot can hang forever:** unbounded WiFi wait and `while(1)` on PN532 failure. There is no watchdog and no recovery.
7. **OLED payload is capped at 31 chars.** The theme text is ~37 chars. `begin()` also logs "display found" even when init failed.
8. **LED ignores `color`/`pattern`**, so roles don't do anything yet.
9. **No last-will, online heartbeat, or firmware version report,** which you need for support.
10. **DFPlayer plays by track number**, but themes reference filenames. An asset manifest is needed.
11. **Only one tag per poll** (see Phase 0, item 2).

### Backend gaps
1. **`check_departures()` hardcodes** `terrain_nodes["battlefield/terrain/home_base"].light_off()`. It turns off the wrong node, raises `KeyError` if it's absent, and turns the light off even if other units remain.
2. **Presence isn't per terrain.** `UnitState` has no terrain, `TerrainNode.occupying_units` never shrinks (`remove_unit` is never called), and moving between markers inside the timeout produces no event.
3. **Multi-tag registry is broken.** The backend looks up by scanned tag UID, but the file is keyed by unit ID, so second tags are "unrecognized". In `RegistryManager.register_tag`, "add tag to existing unit" makes a duplicate unit when the tag is new, and reassigning a tag edits the old unit and appends a duplicate tag.
4. **`MqttClient`:** exact-match callbacks (no `+`/`#`), one callback per topic (a second `subscribe` overwrites the first), no resubscribe after reconnect (MQTT v5 with session expiry 0 loses subscriptions), blocking connect in the constructor, and unguarded callbacks.
5. **Missions can't run.** There is no runtime, `validate_config.py` looks for `schemas/` and `hardware/` folders that don't exist, and `arms-deal.json` fails its own validator (`led_1` isn't in the rig, `briefcase_led` isn't an alias).
6. **Three topic conventions:** `/LedControl` in the rig, `led_control` in firmware and Python, `game/events/...` in themes.
7. **Working-directory-dependent paths;** `run.sh` starts the server before `cd`. `pyproject.toml` lists only paho, and there are two requirements files. There are no tests, though pytest is installed.

---

## 5. Security to a reasonable standard

Target baseline: **ETSI EN 303 645** (no shared or default passwords, updatable, secure storage, vulnerability-disclosure contact).

| Item | Effort |
|---|---|
| Embed a root CA and drop `setInsecure()` | 2–4 h |
| Per-device broker credentials plus topic ACLs (a device publishes only its scans and reads only its own commands; only the backend publishes commands and turn state) | 8–12 h |
| Provisioning: SoftAP captive portal, credentials in NVS instead of `secrets.h` | 20–30 h |
| Signed OTA with rollback | 20–30 h |
| Secure boot v2 and flash encryption (production builds only) | 15–25 h |
| Tenant topic namespace (`tables/{id}/...`) | 10–15 h |
| Input validation, watchdog, payload limits | 8–12 h |
| Backend: secret scanning, `pip-audit`, pinned deps, log redaction | 6–10 h |
| Threat model plus `SECURITY.md` | 8–12 h |

**Total: ~100–150 h, or 10–15 weeks at your pace.** Difficulty is moderate. There is no exotic cryptography, and most effort is provisioning and update plumbing. About 60% of it overlaps work Phase 2 needs anyway.

Notes:
- UID-only RFID identification is trivially cloneable. For a game that is a cheating concern, not a security one.
- If any secret ever reached a remote, history rewriting does not un-leak it. Rotate it.
- Regulatory items (FCC/ISED, CE/RED cybersecurity, battery transport) are from general knowledge. Verify with a test lab.

---

## 6. Code structure & the three-layer pipeline

The three layers are read here as **Sense → Decide → Act**, mapping onto the existing config split (devices and presence; game logic and missions; rig and actuation).

**Current problem:** `Battlefield` does presence tracking, game state, MQTT publishing and LED control. `TerrainNode` is half device adapter and half domain object and calls `light_on()` itself, so the pipeline is bypassed. `ObjectiveRoles.json` (flavor) is consumed at the sensing layer.

```
ESP32 -MQTT-> L1 SENSE --PresenceEvent--> L2 DECIDE --EffectIntent--> L3 ACT -MQTT-> ESP32
              TerrainNode adapter          Battlefield (turn/phase)    Rig + alias resolver
              PresenceTracker              ControlCalculator           payload encoders
                                           Mission engine              dispatcher
```

### Contracts between layers
- **L1 emits** `UnitArrived` / `UnitDeparted(terrain_id, uid, ts)` and nothing else. It knows nothing about games or LEDs.
- **L2 consumes** those plus `TurnChanged`, computes `ObjectiveStatus(objective_id, status, team...)` (empty, standing, contested, secured), and runs theme rules. It emits `EffectIntent("led", target="objective_1_led", mode, color)` using narrative names only.
- **L3 consumes** intents, resolves `objective_1_led` through the theme alias to a rig ID and then to a node and topic, encodes the firmware payload, checks capabilities (for example `supports_rgb`), and publishes.

### Design decisions
1. **In-process event bus with MQTT-style wildcard matching.** Reuse the same matcher in `MqttClient` so theme triggers like `game/events/objective/+/status` work unchanged. Mirror L2 events out to MQTT for a spectator display and debugging.
2. **One engine thread fed by a `queue.Queue`.** MQTT callbacks only enqueue, which removes most locking and makes tests deterministic. *Shortcut:* not asyncio. If the web UI is built on FastAPI, `aiomqtt` may be worth a later migration, which stays contained if the engine is queue-driven.
3. **`PresenceTracker` keyed by `(terrain, uid)` with an injectable clock.** Later, firmware publishes an explicit "left" event and the timeout remains as a dead-node fallback.
4. **Control calculation** implements what the registration UI already promises: units sharing a `shared_name` count only their highest `control_value`. "Secured" needs a defined rule (held for N seconds, or at end of turn).
5. **Rig v2 is multi-node:** `nodes[]` with an `mqtt_base` and their peripherals, aliases like `"objective_1_led": "home_base/led_1"`, and an `objective_id → node` map. Move role colors and patterns from `ObjectiveRoles.json` into the theme.
6. **One `topics.py` owns every topic string.** Generate a firmware header from a shared `topics.json`, as `bitmap_generator/codegen.py` already does for icons.

### Target layout

```
battlefieldengine/
  core/       events.py  bus.py  topics.py
  mqtt/       client.py            (wildcards, resubscribe, reconnect)
  sensing/    terrain_node.py  presence.py
  game/       battlefield.py  control.py  registry.py
  missions/   loader.py  engine.py  state_store.py
  actuation/  rig.py  resolver.py  encoders.py  dispatcher.py
  server.py
```

### Migration order

| Step | Hours |
|---|---|
| `topics.py` plus wildcard-aware, resubscribing `MqttClient` | 6–8 |
| Events, bus, `PresenceTracker`, with tests | 12–16 |
| Rig v2, resolver, encoders | 12–16 |
| Mission engine MVP (matching, conditions, templating, cooldown, state) | 25–35 |
| `ControlCalculator` and `ObjectiveStatus` | 10–15 |
| Firmware: NeoPixel color/pattern, explicit left events, per-node registration | 15–20 |

**~80–110 h, about 8–11 weeks.**

**Shortcut to take on purpose:** build the engine only for what the two themes use (`mqtt_topic` and `interval` triggers; `led`, `oled`, `audio`, `vibrate`, `state_update` actions) and skip `state_change`, `mqtt_publish` and `per_team` scope. The schema promises more than the engine will deliver, so have the validator warn on unsupported features instead of passing them silently.

---

## 7. Shortcut ledger

| Shortcut | Why it's fine now | When it bites | Cost to undo |
|---|---|---|---|
| Shared broker credentials and `setInsecure()` TLS | Alpha runs on your own broker with throwaway credentials | The moment devices leave people you trust | ~30–45 h |
| Hand-flashed per-device topic in `main.cpp` | Fine for 2–3 nodes | When anyone else assembles a unit | 20–30 h (provisioning) |
| Textual TUI as the only UI | Hobbyist alpha testers will tolerate it | Not for backers | 40–60 h (web UI) |
| Devkit ESP32 + PN532 breakouts | Fast iteration | Antenna tuning changes on a custom PCB; certification applies to the final design | ~15 h retuning plus lab fees |
| Departure inferred by timeout only | Works | ~5–7 s latency; false "departed" on a dead node | ~6 h (explicit edge events) |
| Skip secure boot and flash encryption on dev units | The efuses are one-way and can brick boards | Shipping without them means firmware and secrets can be extracted | Do it on production builds only |
| 3D-printed enclosures, no tooling | Cheap and flexible | Cost and consistency at volume | Tooling spend after funding |
| Engine supports only the trigger/action types the two themes use | Keeps the MVP small | When a third theme needs `state_change` or `per_team` | 8–15 h per feature |
