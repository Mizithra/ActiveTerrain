# ActiveTerrain: GitHub Backlog

*Generated 2026-09-28 · 82 issues (6 epics) · ~726 estimated hours · derived from [ActiveTerrain-Product-Analysis.md](ActiveTerrain-Product-Analysis.md)*

## 1. How to use this pack

I can't create GitHub issues from here (no repository access), so this pack gives you three ways in:

1. **Fast (recommended): run the script.** `scripts/create_github_backlog.sh` uses the GitHub CLI to create all labels, milestones and issues in the right order. Preview first with `DRY_RUN=1 ./scripts/create_github_backlog.sh`.
   Run it once, on a repo with **no existing issues or PRs**: cross-references like `#12` assume GitHub numbers issues 1, 2, 3... in creation order. If your repo already has issues, replace the `#N` references by hand.
2. **Manual copy-paste.** Section 5 lists every issue with its title, labels, milestone and a body inside a code block ready to paste into GitHub's *New issue* form.
3. **Templates for future issues.** Commit the `.github/` folder from this pack. New issues then use GitHub **issue forms** (structured web forms: title, Bug/Feature, description, related files).

**Related files use symbols, not line numbers**, because line numbers drift with every commit. When you triage an issue, open the file on GitHub, select the lines and press `y` to convert the URL to a permalink, then paste it into the issue.

### GitHub features this pack is built around

| Feature | How it's used here |
|---|---|
| **Issue forms** (`.github/ISSUE_TEMPLATE/*.yml`) | Structured bug and feature templates; blank issues disabled; links to Discussions and private security reporting |
| **Labels** | `type:`, `area:`, `priority:`, `size:` plus flags. The same labels drive release-note categories |
| **Milestones** | One per roadmap phase (M0-M5), with target dates at ~10 h/week |
| **Sub-issues / task lists** | Each epic tracks its children via a checklist of `#N` references. GitHub shows progress on the epic, and you can convert children to native sub-issues |
| **Projects (v2)** | Board, Table and Roadmap views (see 2 below) |
| **Pull request template** | Enforces `Closes #N`, a test checklist and a secrets check |
| **Actions** | Python CI, firmware build, validator, release builds (tracked as issues) |
| **Branch protection / rulesets** | Require PR plus passing checks on `main`, even solo |
| **Dependabot, secret scanning, push protection, CodeQL** | Supply-chain and secret hygiene (tracked as issues) |
| **SECURITY.md + private vulnerability reporting** | Disclosure path for a product that ships hardware |
| **Discussions** | Alpha-tester feedback and Q&A, keeping issues for actionable work |
| **Releases + `release.yml`** | Auto-generated changelogs grouped by label; release assets host OTA firmware images |

> GitHub's newer org-level "Issue types" (Bug/Feature/Task) aren't available on personal repos, so this pack uses `type:` labels. If you move the repo into an organization, you can switch to native types.

### 2. Suggested Project setup (5 minutes)

1. **Projects to New project to Board.** Name it *ActiveTerrain Roadmap*.
2. Add fields: **Priority** (single select, P0-P3), **Size** (S/M/L/XL), **Estimate (h)** (number). Milestone is built in.
3. Workflow automations (Project to Workflows): *Item added to project: set Status = Backlog*; *Item closed: Status = Done*; *Pull request merged: Status = Done*. Enable *Auto-add to project* for this repo.
4. Views: **Board** (group by Status, filter `-label:"type: epic"`), **Roadmap** (group by Milestone), **Table** (group by Area, sort by Priority).
5. Add all issues (search `is:issue` in the repo and *Add to project*, or the auto-add workflow).

### 3. Workflow conventions

- **Branches:** `fix/12-audio-blocking`, `feat/27-mission-core` (type/issue-number-slug).
- **Commits:** [Conventional Commits](https://www.conventionalcommits.org): `fix(firmware): stop blocking audio callback (#1)`.
- **PRs:** small, one issue each, description says `Closes #N`; squash-merge.
- **Definition of done:** acceptance criteria ticked, tests or bench evidence attached, docs updated, CI green.
- **Versioning:** SemVer per artifact (`fw-v0.2.0`, `hub-v0.2.0`); tag = GitHub Release.
- **Working agreement:** work P0 first, only 1-2 issues in progress, re-estimate at each milestone.

### Size legend

`size: S` up to ~3 h · `M` ~4-8 h · `L` ~9-20 h · `XL` more than ~20 h (consider splitting).

## 4. Milestones and label scheme

| Milestone | Target date (10 h/week) | Goal |
|---|---|---|
| M0 - Decide & De-risk | 2026-10-25 | Architecture, IP and RFID risk decisions made before more code is written. |
| M1 - Core Fixes & Pipeline | 2027-01-03 | P0 bugs fixed; Sense-Decide-Act pipeline running one mission end-to-end on 2-3 nodes; CI in place. |
| M2 - Productize | 2027-04-11 | Provisioning, security baseline, signed OTA, hub packaging, web UI. |
| M3 - Hardware v1 | 2027-07-04 | Custom PCB, enclosure, power design, unit-cost model. |
| M4 - Alpha & Campaign Prep | 2027-09-26 | 5-10 external testers, landing page, demo video, campaign plan. |
| M5 - Compliance & Pilot | 2028-01-30 | Test-lab certification and a 50-100 unit pilot run. |

*Dates assume a 2026-09-28 start and ~10 h/week. Re-baseline at each milestone; hardware phases usually slip.*

| Label | Meaning |
|---|---|
| `type: bug` | Something is broken |
| `type: feature` | New capability |
| `type: task` | Chore, decision or non-code work |
| `type: spike` | Time-boxed investigation |
| `type: epic` | Parent issue tracking a group of issues |
| `area: firmware` | ESP32 / C++ / PlatformIO |
| `area: backend` | Python engine and MQTT client |
| `area: ui` | Textual TUI / future web UI |
| `area: config` | Rig, theme, mission and schema files |
| `area: security` | Security hardening |
| `area: hardware` | PCB, enclosure, power, RFID hardware |
| `area: infra` | CI, packaging, repo tooling |
| `area: docs` | Documentation |
| `area: business` | Go-to-market, compliance, IP |
| `priority: P0 - blocker` | Fix before anything else |
| `priority: P1 - high` | Needed for the current milestone |
| `priority: P2 - medium` | Should be done this phase |
| `priority: P3 - low` | Nice to have |
| `size: S` | Up to ~3 hours |
| `size: M` | ~4-8 hours |
| `size: L` | ~9-20 hours |
| `size: XL` | More than ~20 hours; consider splitting |
| `needs verification` | Suspected from code review; reproduce first |
| `good first issue` | Good for a first contributor |
| `help wanted` | Extra hands welcome |
| `blocked` | Waiting on another issue or decision |
| `icebox` | Not planned for a current milestone |

### Issue index

| # | Title | Type | Priority | Milestone | Size |
|---|---|---|---|---|---|
| 1 | EPIC: Firmware stabilization and capability | Epic | P1 | M1 | - |
| 2 | EPIC: Backend stabilization | Epic | P1 | M1 | - |
| 3 | EPIC: Three-layer pipeline (Sense - Decide - Act) | Epic | P1 | M1 | - |
| 4 | EPIC: Security baseline (ETSI EN 303 645 target) | Epic | P1 | M2 | - |
| 5 | EPIC: Hardware v1 | Epic | P2 | M3 | - |
| 6 | EPIC: Go-to-market and compliance | Epic | P2 | M4 | - |
| 7 | Audio: playFile() blocks ~6.5 s inside the MQTT callback and runs a leftover buzzer test | Bug | P0 | M1 | S |
| 8 | Audio: Serial.printf('%s') receives an Arduino String (undefined behavior); DFPlayer notifications never serviced | Bug | P1 | M1 | S |
| 9 | Registration topics are global: every marker responds to a registration start | Bug | P0 | M1 | S |
| 10 | Registration blocking loop re-enters PubSubClient::loop() from inside a callback | Bug | P2 | M1 | S |
| 11 | PN532 constructed with (irq, reset) = GPIO 21/22, likely driving the I2C SCL line | Bug | P0 | M1 | S |
| 12 | rig.json assigns the haptic motor to gpio22, the I2C SCL pin used by the PN532 | Bug | P1 | M1 | S |
| 13 | Boot can hang forever: unbounded WiFi wait and while(1) on PN532 init failure | Bug | P1 | M1 | M |
| 14 | OLED: payload truncated at 31 chars, multi-line theme text does not fit; init failure logged as success | Bug | P2 | M1 | S |
| 15 | RFID: only one tag per poll; multiple models on an objective are not reliably detected | Bug | P0 | M0 | M |
| 16 | MqttRouter::loop() logs 'WiFi lost' on every iteration and has no reconnect or last-will handling | Bug | P2 | M1 | S |
| 17 | check_departures() hardcodes home_base light_off and raises KeyError if that node is absent | Bug | P0 | M1 | S |
| 18 | Unit presence is not tracked per terrain; TerrainNode.occupying_units never shrinks | Bug | P0 | M1 | M |
| 19 | Multi-tag units are not recognized: registry is keyed by unit ID but scans arrive as tag UIDs | Bug | P1 | M1 | M |
| 20 | RegistryManager.register_tag creates duplicate units, duplicate tags, and does not move reassigned tags | Bug | P1 | M1 | S |
| 21 | MqttClient: exact-match, single callback per topic; wildcards unsupported and a second subscribe overwrites the first | Bug | P0 | M1 | M |
| 22 | MqttClient does not resubscribe after a reconnect | Bug | P0 | M1 | S |
| 23 | MqttClient: blocking connect in constructor, unguarded callbacks, deprecated TLS setup | Bug | P1 | M1 | S |
| 24 | validate_config.py points at schemas/ and hardware/ paths that do not exist | Bug | P1 | M1 | S |
| 25 | arms-deal.json fails validation against rig.json | Bug | P1 | M1 | S |
| 26 | MQTT topic naming is inconsistent across rig.json, firmware, Python and themes | Bug | P1 | M1 | S |
| 27 | Config and log paths depend on the working directory; run.sh launches the server before cd | Bug | P2 | M1 | S |
| 28 | Dependencies are split and stale: pyproject lists only paho; two requirements files | Bug | P2 | M1 | S |
| 29 | UID normalization goes through slugify() and Unit.tags typing is inconsistent | Bug | P3 | M1 | S |
| 30 | Rotate any credential that ever touched git history; enable secret scanning and push protection | Task | P1 | M2 | S |
| 31 | ADR: local-first hub vs cloud MQTT broker | Spike | P0 | M0 | M |
| 32 | Spike: evaluate multi-tag RFID readers (PN532 workaround vs ISO15693 inventory) | Spike | P0 | M0 | M |
| 33 | Spike: RFID range and reliability with magnetized bases and metal terrain | Spike | P1 | M3 | M |
| 34 | Branding and IP review: make the product system-agnostic | Task | P0 | M0 | M |
| 35 | Decide licensing model and contribution policy (PolyForm NC vs alternatives; DCO/CLA) | Task | P2 | M0 | S |
| 36 | Repo scaffolding: issue forms, PR template, CONTRIBUTING, SECURITY.md, Dependabot, release notes config | Task | P2 | M0 | S |
| 37 | Central topic registry (topics.py) with a generated firmware header | Feature | P1 | M1 | M |
| 38 | In-process EventBus with MQTT-style wildcard matching, plus typed events | Feature | P1 | M1 | M |
| 39 | PresenceTracker keyed by (terrain, uid) with an injectable clock | Feature | P1 | M1 | M |
| 40 | Refactor TerrainNode into a pure Layer 1 adapter (no LED control) | Feature | P2 | M1 | M |
| 41 | ControlCalculator and ObjectiveStatus (standing / contested / secured, shared_name de-duplication) | Feature | P1 | M1 | L |
| 42 | Rig v2: multi-node schema, loader and alias resolver | Feature | P1 | M1 | L |
| 43 | Payload encoders and ActuationDispatcher (Layer 3) with capability fallback | Feature | P1 | M1 | M |
| 44 | Mission engine (1/3): loader, trigger matching and conditions | Feature | P1 | M1 | L |
| 45 | Mission engine (2/3): templating and action execution to EffectIntents | Feature | P1 | M1 | M |
| 46 | Mission engine (3/3): state store, sliding-window counters, cooldowns and interval triggers | Feature | P2 | M1 | M |
| 47 | Single engine thread fed by a queue (concurrency model) | Feature | P2 | M1 | M |
| 48 | Move ObjectiveRoles into the theme layer; deprecate ObjectiveRoles.json | Feature | P3 | M1 | S |
| 49 | Retain turn/phase state and unit status so new UIs sync on connect | Feature | P2 | M1 | S |
| 50 | Validator: warn on schema features the engine does not support; run on every mission in CI | Feature | P2 | M1 | S |
| 51 | CI: pytest and ruff on GitHub Actions | Feature | P1 | M1 | S |
| 52 | CI: PlatformIO firmware build on GitHub Actions | Feature | P1 | M1 | S |
| 53 | Firmware: addressable LED driver (WS2812B) with color and pattern support | Feature | P1 | M1 | L |
| 54 | Audio: non-blocking DFPlayer task and asset manifest (filename to track number) | Feature | P2 | M1 | M |
| 55 | Firmware: DRV2605 haptic controller for vibrate actions | Feature | P3 | M1 | M |
| 56 | Firmware: last-will, retained online/offline, heartbeat with firmware version, explicit 'left' events | Feature | P1 | M1 | M |
| 57 | Firmware: load pins, topics and peripherals from LittleFS config (no hardcoded topic in main.cpp) | Feature | P2 | M2 | M |
| 58 | Verify the broker TLS certificate on the ESP32 (remove setInsecure) | Feature | P1 | M2 | S |
| 59 | Per-device MQTT credentials and topic ACLs | Feature | P1 | M2 | L |
| 60 | Provisioning: SoftAP captive portal storing WiFi and MQTT settings in NVS | Feature | P1 | M2 | XL |
| 61 | Signed OTA updates with rollback | Feature | P1 | M2 | XL |
| 62 | Multi-table topic namespace (tables/{id}/...) | Feature | P2 | M2 | L |
| 63 | Firmware robustness: task watchdog, bounded buffers, payload and JSON limits | Feature | P2 | M2 | L |
| 64 | Backend hardening: dependency pinning and audit, log redaction, Dependabot | Feature | P2 | M2 | M |
| 65 | Threat model, SECURITY.md and vulnerability disclosure (private vulnerability reporting) | Feature | P2 | M2 | L |
| 66 | Production hardening: secure boot v2 and flash encryption build profile | Feature | P2 | M3 | L |
| 67 | Web UI (FastAPI + WebSocket) as the primary interface; keep the TUI as a dev tool | Feature | P2 | M2 | XL |
| 68 | Hub packaging: Docker Compose (Mosquitto + backend + web UI) and a Raspberry Pi image | Feature | P2 | M2 | L |
| 69 | Mission authoring CLI (validate, simulate) and a third mission (Signal Jamming) | Feature | P3 | M2 | L |
| 70 | Docs: architecture overview, protocol reference, pinout, getting started | Feature | P2 | M2 | L |
| 71 | Custom carrier PCB: schematic (ESP32 module, RFID front-end, LEDs, OLED, audio, haptic, power) | Feature | P2 | M3 | XL |
| 72 | PCB layout, DFM checks, order rev A | Feature | P2 | M3 | XL |
| 73 | Board bring-up and firmware port; errata list | Task | P2 | M3 | XL |
| 74 | Enclosure and terrain integration design (printable), RFID antenna placement under the surface | Feature | P2 | M3 | XL |
| 75 | Power design: USB-C and battery options, brownout behavior | Task | P2 | M3 | L |
| 76 | BOM, sourcing and unit-cost model; pricing hypotheses | Task | P2 | M3 | L |
| 77 | Alpha program: recruit 5-10 testers and set up a feedback loop | Task | P2 | M4 | L |
| 78 | Landing page, demo video and mailing list | Task | P2 | M4 | L |
| 79 | Crowdfunding campaign plan: goal, tiers, fulfillment costs, risk section | Task | P2 | M4 | L |
| 80 | Compliance plan: FCC/ISED (13.56 MHz reader), CE/RED including cybersecurity, battery transport | Task | P2 | M5 | L |
| 81 | Pilot manufacturing run (50-100 units): assembly partner, test jig, QA checklist | Task | P2 | M5 | XL |
| 82 | Spectator display: companion screen fed by the live event stream | Feature | P3 | - | L |

## 5. Issues (copy-paste ready)

Each entry gives the **Title**, **Type**, **Labels**, **Milestone** and the **Body** to paste. Body cross-references (`#N`) assume the creation order below.

### #1: EPIC: Firmware stabilization and capability

- **Type:** Epic
- **Labels:** `type: epic`, `area: firmware`, `priority: P1 - high`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `EPIC: Firmware stabilization and capability`

````markdown
## Goal
Fix the firmware bugs found in code review and add the capabilities the pipeline needs (color/pattern LEDs, non-blocking audio, haptics, status reporting).

## Tracked issues
- [ ] #7
- [ ] #8
- [ ] #9
- [ ] #10
- [ ] #11
- [ ] #12
- [ ] #13
- [ ] #14
- [ ] #15
- [ ] #16
- [ ] #53
- [ ] #54
- [ ] #55
- [ ] #56
- [ ] #57
````

### #2: EPIC: Backend stabilization

- **Type:** Epic
- **Labels:** `type: epic`, `area: backend`, `priority: P1 - high`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `EPIC: Backend stabilization`

````markdown
## Goal
Fix the presence, registry and MQTT client bugs found in code review and clean up packaging and paths.

## Tracked issues
- [ ] #17
- [ ] #18
- [ ] #19
- [ ] #20
- [ ] #21
- [ ] #22
- [ ] #23
- [ ] #24
- [ ] #25
- [ ] #26
- [ ] #27
- [ ] #28
- [ ] #29
````

### #3: EPIC: Three-layer pipeline (Sense - Decide - Act)

- **Type:** Epic
- **Labels:** `type: epic`, `area: backend`, `area: config`, `priority: P1 - high`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `EPIC: Three-layer pipeline (Sense - Decide - Act)`

````markdown
## Goal
Re-structure the backend into Sense (presence), Decide (game state and mission engine) and Act (rig resolution and payload encoding) layers connected by an in-process event bus, so a theme file can drive real hardware end-to-end. See docs/ActiveTerrain-Product-Analysis.md section 6.

## Tracked issues
- [ ] #37
- [ ] #38
- [ ] #39
- [ ] #40
- [ ] #41
- [ ] #42
- [ ] #43
- [ ] #44
- [ ] #45
- [ ] #46
- [ ] #47
- [ ] #48
- [ ] #49
- [ ] #50
- [ ] #51
- [ ] #52
````

### #4: EPIC: Security baseline (ETSI EN 303 645 target)

- **Type:** Epic
- **Labels:** `type: epic`, `area: security`, `priority: P1 - high`
- **Milestone:** M2 - Productize
- **Title to paste:** `EPIC: Security baseline (ETSI EN 303 645 target)`

````markdown
## Goal
Bring transport, identity, provisioning, updates and disclosure up to a reasonable consumer-IoT baseline before any device leaves trusted hands.

## Tracked issues
- [ ] #58
- [ ] #59
- [ ] #60
- [ ] #61
- [ ] #62
- [ ] #63
- [ ] #64
- [ ] #65
- [ ] #66
- [ ] #30
````

### #5: EPIC: Hardware v1

- **Type:** Epic
- **Labels:** `type: epic`, `area: hardware`, `priority: P2 - medium`
- **Milestone:** M3 - Hardware v1
- **Title to paste:** `EPIC: Hardware v1`

````markdown
## Goal
Move from devkit-and-breakout prototypes to a custom carrier board and an enclosure that fits inside terrain.

## Tracked issues
- [ ] #71
- [ ] #72
- [ ] #73
- [ ] #74
- [ ] #75
- [ ] #76
- [ ] #33
````

### #6: EPIC: Go-to-market and compliance

- **Type:** Epic
- **Labels:** `type: epic`, `area: business`, `priority: P2 - medium`
- **Milestone:** M4 - Alpha & Campaign Prep
- **Title to paste:** `EPIC: Go-to-market and compliance`

````markdown
## Goal
Everything required to sell the product: IP position, licensing, alpha feedback, campaign, certification and a pilot production run.

## Tracked issues
- [ ] #31
- [ ] #32
- [ ] #34
- [ ] #35
- [ ] #36
- [ ] #77
- [ ] #78
- [ ] #79
- [ ] #80
- [ ] #81
- [ ] #67
- [ ] #68
- [ ] #70
- [ ] #69
- [ ] #82
````

### #7: Audio: playFile() blocks ~6.5 s inside the MQTT callback and runs a leftover buzzer test

- **Type:** Bug
- **Labels:** `type: bug`, `area: firmware`, `priority: P0 - blocker`, `size: S`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `Audio: playFile() blocks ~6.5 s inside the MQTT callback and runs a leftover buzzer test`

````markdown
## Description
`AudioController::playFile` sets the volume, plays the track, then runs a hardcoded 3x(1 s on / 1 s off) buzzer loop on GPIO 26 using `delay()`. `handleMqttEvent` calls it directly from the PubSubClient callback, so the main loop (RFID polling, MQTT servicing) stalls about 6.5 s per audio message. That risks keepalive disconnects and missed scans. It also ignores the payload and always plays track 1.

## Expected behavior
Audio commands return immediately, play the requested track, and never stall RFID or MQTT.

## Related files
- `ESP32/ObjectiveMarker/lib/AudioController/AudioController.cpp` - `playFile()`, `handleMqttEvent()`

## Acceptance criteria
- [ ] No `delay()` longer than 50 ms on the main task
- [ ] Payload such as `{"track": 3, "volume": 15}` is honored
- [ ] RFID heartbeats continue during playback (verify in serial log)
- [ ] Buzzer code removed or behind `#ifdef DEBUG_BUZZER`

**Estimate:** ~3 h
````

### #8: Audio: Serial.printf('%s') receives an Arduino String (undefined behavior); DFPlayer notifications never serviced

- **Type:** Bug
- **Labels:** `type: bug`, `area: firmware`, `priority: P1 - high`, `size: S`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `Audio: Serial.printf('%s') receives an Arduino String (undefined behavior); DFPlayer notifications never serviced`

````markdown
## Description
`handleMqttEvent` passes `payload` (a `const String&`) to a `%s` format, which is undefined behavior and can crash. Separately, the Makuna DFMiniMp3 library expects `loop()` to be called regularly to dispatch notify callbacks (`OnPlayFinished`, `OnError`), and nothing calls `_mp3.loop()`.

## Related files
- `ESP32/ObjectiveMarker/lib/AudioController/AudioController.cpp` - `handleMqttEvent()`
- `ESP32/ObjectiveMarker/lib/AudioController/AudioController.h` - `Mp3Notify`
- `ESP32/ObjectiveMarker/lib/ObjectiveNode/ObjectiveNode.cpp` - `loop()`

## Acceptance criteria
- [ ] Use `payload.c_str()`; grep for other `printf` calls passing `String`
- [ ] `_mp3.loop()` called from `ObjectiveNode::loop()`
- [ ] Playback errors appear in the serial log

**Estimate:** ~1.5 h
````

### #9: Registration topics are global: every marker responds to a registration start

- **Type:** Bug
- **Labels:** `type: bug`, `area: firmware`, `area: ui`, `priority: P0 - blocker`, `size: S`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `Registration topics are global: every marker responds to a registration start`

````markdown
## Description
`RegistrationController::begin` ignores its `objectiveTopic` argument and hardcodes `battlefield/terrain/registration/...`. Every ESP32 running this firmware subscribes to the same topics, so with more than one marker powered they all light their LED and block waiting for a scan. The UI likewise hardcodes `REGISTRATION_OBJECTIVE_TOPIC`.

## Expected behavior
Registration topics are derived from the device's own base topic (or device ID) and the UI picks which device performs the scan.

## Related files
- `ESP32/ObjectiveMarker/lib/RegistrationController/RegistrationController.cpp` - `begin()`
- `ESP32/ObjectiveMarker/src/main.cpp` - `OBJECTIVE_TOPIC`
- `console_ui/battlefield_ui.py` - `REGISTRATION_OBJECTIVE_TOPIC`, `REGISTER_*_TOPIC`

## Acceptance criteria
- [ ] With 2+ nodes powered, only the selected node lights up and responds
- [ ] UI lets the user choose the registration device (or defaults to a configured one)

**Estimate:** ~2 h · **Depends on:** #37
````

### #10: Registration blocking loop re-enters PubSubClient::loop() from inside a callback

- **Type:** Bug
- **Labels:** `type: bug`, `area: firmware`, `priority: P2 - medium`, `size: S`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `Registration blocking loop re-enters PubSubClient::loop() from inside a callback`

````markdown
## Description
`handleStart` runs a blocking scan loop inside an MQTT callback and calls `_mqtt.pump()` (`PubSubClient::loop()`) to keep the connection alive. PubSubClient is not re-entrant, and a `register_end` message arriving during the wait invokes `handleEnd` nested inside the first callback.

## Expected behavior
Registration is a non-blocking state machine driven from `loop()` with a timeout (or runs in its own task), and the LED remains the 'waiting for you' signal.

## Related files
- `ESP32/ObjectiveMarker/lib/RegistrationController/RegistrationController.cpp` - `handleStart()`, `handleEnd()`
- `ESP32/ObjectiveMarker/lib/MqttRouter/MqttRouter.cpp` - `pump()`

## Acceptance criteria
- [ ] No blocking wait inside a message callback
- [ ] Cancel via `register_end` works mid-scan
- [ ] 30 s timeout still publishes `{"uid": null, "error": "timeout"}`

**Estimate:** ~3 h
````

### #11: PN532 constructed with (irq, reset) = GPIO 21/22, likely driving the I2C SCL line

- **Type:** Bug
- **Labels:** `type: bug`, `area: firmware`, `area: hardware`, `priority: P0 - blocker`, `size: S`, `needs verification`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `PN532 constructed with (irq, reset) = GPIO 21/22, likely driving the I2C SCL line`

````markdown
## Description
`_nfc(sdaPin, sclPin)` resolves to Adafruit_PN532's two-argument constructor, which is `(irq, reset)`. That hands GPIO 21/22 (the default ESP32 I2C pins) to irq/reset, and `begin()` toggles the reset pin. This matches the I2C bus-contention symptoms seen before, so confirm whether the fix is actually in this code.

## Expected behavior
PN532 uses dedicated, otherwise-unused GPIOs for irq/reset (wired or floating) and I2C is started explicitly with `Wire.begin(SDA, SCL)`.

## Related files
- `ESP32/ObjectiveMarker/lib/ObjectiveNode/ObjectiveNode.cpp` - constructor init list `_nfc(sdaPin, sclPin)`
- `ESP32/ObjectiveMarker/src/main.cpp` - `SDA_PIN`, `SCL_PIN`

## Acceptance criteria
- [ ] Verify with a scope or logic analyzer that GPIO 22 is not toggled as a reset line
- [ ] Constructor uses the intended overload
- [ ] Pin usage documented in the pinout doc

**Estimate:** ~2 h
````

### #12: rig.json assigns the haptic motor to gpio22, the I2C SCL pin used by the PN532

- **Type:** Bug
- **Labels:** `type: bug`, `area: firmware`, `area: config`, `priority: P1 - high`, `size: S`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `rig.json assigns the haptic motor to gpio22, the I2C SCL pin used by the PN532`

````markdown
## Description
The rig lists the haptic at `gpio22`, but GPIO 22 is SCL for the PN532 in `main.cpp`. The OLED uses GPIO 33/32 (`I2C_1`/`I2C_2` defines in `OledController.cpp`), which appear in neither the rig nor `main.cpp`. There is no single pin map.

## Related files
- `battlefieldengine/battlefieldengine/configurations/rig.json` - `haptics[0].device_id`
- `ESP32/ObjectiveMarker/src/main.cpp`
- `ESP32/ObjectiveMarker/lib/OledController/OledController.cpp` - `I2C_1`, `I2C_2`

## Acceptance criteria
- [ ] `docs/hardware/pinout.md` lists every pin in use
- [ ] Rig no longer double-books any pin
- [ ] Validator rejects duplicate `device_id` pins (see validator issue)

**Estimate:** ~1 h
````

### #13: Boot can hang forever: unbounded WiFi wait and while(1) on PN532 init failure

- **Type:** Bug
- **Labels:** `type: bug`, `area: firmware`, `priority: P1 - high`, `size: M`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `Boot can hang forever: unbounded WiFi wait and while(1) on PN532 init failure`

````markdown
## Description
`connectWifi` loops until connected with no timeout. `begin()` enters `while (1);` if the PN532 is not found or returns no firmware version. A node with a loose cable or wrong WiFi is dead until physically reset, with no signal to the operator and no watchdog.

## Expected behavior
Timeouts with retry and backoff, a status pattern on the LED, PN532 failure retried and reported over MQTT, and a hardware/task watchdog that resets a hung node.

## Related files
- `ESP32/ObjectiveMarker/lib/ObjectiveNode/ObjectiveNode.cpp` - `connectWifi()`, `begin()`

## Acceptance criteria
- [ ] Unplugging the PN532 does not brick the node
- [ ] WiFi loss recovers automatically
- [ ] Watchdog resets a deliberately hung loop in a test build

**Estimate:** ~4 h
````

### #14: OLED: payload truncated at 31 chars, multi-line theme text does not fit; init failure logged as success

- **Type:** Bug
- **Labels:** `type: bug`, `area: firmware`, `area: config`, `priority: P2 - medium`, `size: S`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `OLED: payload truncated at 31 chars, multi-line theme text does not fit; init failure logged as success`

````markdown
## Description
`OledTextRequest::payload` is `char[32]`, but theme text such as `REACTOR 1\nSTABILIZING\nCrew: Red Squad` is about 37 chars and is truncated. In `begin()`, `display->begin(...)` failure is logged, then 'display found' is logged anyway and the render task starts regardless.

## Related files
- `ESP32/ObjectiveMarker/lib/OledController/OledController.h` - `OledTextRequest`
- `ESP32/ObjectiveMarker/lib/OledController/OledController.cpp` - `parseMqttPayload()`, `begin()`, `calcOptimalTextSize()`
- `battlefieldengine/missions/reactor-meltdown.json` - `oled` action `text`

## Acceptance criteria
- [ ] Request buffer sized for the longest theme text (e.g. 96 bytes)
- [ ] Max lines/characters documented in the protocol doc
- [ ] Init failure is logged accurately and the task is not started

**Estimate:** ~3 h
````

### #15: RFID: only one tag per poll; multiple models on an objective are not reliably detected

- **Type:** Bug
- **Labels:** `type: bug`, `area: firmware`, `area: hardware`, `priority: P0 - blocker`, `size: M`, `needs verification`
- **Milestone:** M0 - Decide & De-risk
- **Title to paste:** `RFID: only one tag per poll; multiple models on an objective are not reliably detected`

````markdown
## Description
`RfidTracker::poll()` calls `readPassiveTargetID`, which returns a single target per call. Without halting or deselecting a card after reading it, the same card tends to answer every poll, so other tags under the reader may never be seen. The README states a marker can track multiple models at once.

## Expected behavior
N>=5 tagged bases on one objective are all reported within an agreed latency, or the limitation is documented and the hardware choice revisited.

## Related files
- `ESP32/ObjectiveMarker/lib/RfidTracker/RfidTracker.cpp` - `poll()`, `findOrCreate()`
- `ESP32/ObjectiveMarker/lib/RfidTracker/RfidTracker.h` - `MAX_TAGS`

## Acceptance criteria
- [ ] Bench test results table committed to `docs/hardware/rfid-testing.md`
- [ ] Decision recorded: PN532 workaround vs different reader
- [ ] README claim updated to match reality

**Estimate:** ~6 h · **Depends on:** #32
````

### #16: MqttRouter::loop() logs 'WiFi lost' on every iteration and has no reconnect or last-will handling

- **Type:** Bug
- **Labels:** `type: bug`, `area: firmware`, `priority: P2 - medium`, `size: S`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `MqttRouter::loop() logs 'WiFi lost' on every iteration and has no reconnect or last-will handling`

````markdown
## Description
When WiFi drops, `loop()` prints a message every pass, flooding serial and slowing the loop. It never calls `WiFi.reconnect()`, and `reconnect()` connects without a last-will message.

## Related files
- `ESP32/ObjectiveMarker/lib/MqttRouter/MqttRouter.cpp` - `loop()`, `reconnect()`

## Acceptance criteria
- [ ] Log rate-limited (e.g. once per 5 s)
- [ ] WiFi reconnect attempted with backoff

**Estimate:** ~2 h · **Depends on:** #56
````

### #17: check_departures() hardcodes home_base light_off and raises KeyError if that node is absent

- **Type:** Bug
- **Labels:** `type: bug`, `area: backend`, `priority: P0 - blocker`, `size: S`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `check_departures() hardcodes home_base light_off and raises KeyError if that node is absent`

````markdown
## Description
Whenever any unit departs, `terrain_nodes["battlefield/terrain/home_base"].light_off()` runs. It targets the wrong node, raises `KeyError` if that node is not configured, and turns the light off even when other units remain on it.

## Expected behavior
Only the terrain the unit was on is updated, and its light turns off only when no units remain there.

## Related files
- `battlefieldengine/battlefieldengine/Battlefield.py` - `check_departures()`

## Acceptance criteria
- [ ] Unit test: two units on one node, one leaves, light stays on
- [ ] No `KeyError` with a single configured node
- [ ] Permanent fix arrives with the PresenceTracker issue

**Estimate:** ~2 h · **Depends on:** #39
````

### #18: Unit presence is not tracked per terrain; TerrainNode.occupying_units never shrinks

- **Type:** Bug
- **Labels:** `type: bug`, `area: backend`, `priority: P0 - blocker`, `size: M`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `Unit presence is not tracked per terrain; TerrainNode.occupying_units never shrinks`

````markdown
## Description
`UnitState` has no terrain, `TerrainNode.remove_unit()` is never called, and `TerrainNode.occupying_units` only grows. A unit moving between markers within the presence timeout produces no arrival or departure event. Faction-aware control is impossible without per-terrain presence.

## Related files
- `battlefieldengine/battlefieldengine/Models.py` - `UnitState`
- `battlefieldengine/battlefieldengine/Battlefield.py` - `_on_terrain_scan()`
- `battlefieldengine/battlefieldengine/TerrainNode.py` - `handle_scan()`, `remove_unit()`

## Acceptance criteria
- [ ] Presence keyed by (terrain, uid)
- [ ] Departures emitted per terrain
- [ ] Tests cover move-between-markers and multi-unit cases

**Estimate:** ~4 h · **Depends on:** #39
````

### #19: Multi-tag units are not recognized: registry is keyed by unit ID but scans arrive as tag UIDs

- **Type:** Bug
- **Labels:** `type: bug`, `area: backend`, `priority: P1 - high`, `size: M`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `Multi-tag units are not recognized: registry is keyed by unit ID but scans arrive as tag UIDs`

````markdown
## Description
A second tag registered to an existing unit is stored under that unit's `tags` list, but `UnitRegistry.get(uid)` only looks up top-level keys. Scanning the second tag logs 'Unrecognized RFID UID'.

## Expected behavior
Lookups by any registered tag resolve to the owning unit.

## Related files
- `battlefieldengine/battlefieldengine/Battlefield.py` - `UnitRegistry.load()`, `UnitRegistry.get()`
- `console_ui/RegistryManager.py` - `register_tag()`
- `battlefieldengine/battlefieldengine/configurations/UnitRegistry.json`

## Acceptance criteria
- [ ] Build a tag-to-unit index at load
- [ ] Test: unit with 2 tags resolves from either
- [ ] Backend and UI share one registry module

**Estimate:** ~4 h
````

### #20: RegistryManager.register_tag creates duplicate units, duplicate tags, and does not move reassigned tags

- **Type:** Bug
- **Labels:** `type: bug`, `area: backend`, `area: ui`, `priority: P1 - high`, `size: S`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `RegistryManager.register_tag creates duplicate units, duplicate tags, and does not move reassigned tags`

````markdown
## Description
(a) The modal says 'Unit X already exists. Add this tag to it?' but `register_tag` only checks for an existing tag, so a new tag plus an existing name creates a second unit with the same name. (b) Reassigning an already-registered tag edits the old unit in place and appends the tag again instead of moving it. (c) `tags.append` has no de-duplication.

## Related files
- `console_ui/RegistryManager.py` - `register_tag()`, `find_unit_id_by_name()`
- `console_ui/RegistrationScreen.py` - `_submit_unit_name()`

## Acceptance criteria
- [ ] Existing name plus new tag adds the tag to that unit
- [ ] Reassign moves the tag and removes it from the old unit
- [ ] No duplicate tags
- [ ] Unit tests

**Estimate:** ~3 h
````

### #21: MqttClient: exact-match, single callback per topic; wildcards unsupported and a second subscribe overwrites the first

- **Type:** Bug
- **Labels:** `type: bug`, `area: backend`, `priority: P0 - blocker`, `size: M`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `MqttClient: exact-match, single callback per topic; wildcards unsupported and a second subscribe overwrites the first`

````markdown
## Description
`_callbacks` maps one callback to one literal topic. Mission triggers such as `game/events/objective/+/status` never match, and subscribing twice to a topic silently replaces the earlier handler. paho's `message_callback_add` supports wildcard filters and could be used.

## Related files
- `battlefieldengine/battlefieldengine/MqttClient.py` - `subscribe()`, `_on_message()`

## Acceptance criteria
- [ ] Multiple callbacks per filter
- [ ] `+` and `#` filters dispatch correctly
- [ ] Unit tests for the matcher

**Estimate:** ~4 h · **Depends on:** #38
````

### #22: MqttClient does not resubscribe after a reconnect

- **Type:** Bug
- **Labels:** `type: bug`, `area: backend`, `priority: P0 - blocker`, `size: S`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `MqttClient does not resubscribe after a reconnect`

````markdown
## Description
`subscribe()` is called once. With MQTT v5 and session expiry 0, subscriptions are lost when the connection drops, so after a broker restart or network blip the backend goes silent while still appearing connected.

## Related files
- `battlefieldengine/battlefieldengine/MqttClient.py` - `_on_connect()`, `subscribe()`

## Acceptance criteria
- [ ] `_on_connect` re-subscribes every registered filter
- [ ] Verified by restarting the broker mid-run

**Estimate:** ~2 h
````

### #23: MqttClient: blocking connect in constructor, unguarded callbacks, deprecated TLS setup

- **Type:** Bug
- **Labels:** `type: bug`, `area: backend`, `priority: P1 - high`, `size: S`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `MqttClient: blocking connect in constructor, unguarded callbacks, deprecated TLS setup`

````markdown
## Description
`__init__` calls `connect()` synchronously, so an unreachable broker raises at construction. Exceptions inside callbacks can disturb the network thread. `tls_set(tls_version=PROTOCOL_TLS)` is deprecated. Environment variables are not validated, and `paho-mqtt` is pinned to 1.6.1 (callback API differs in 2.x; plan the upgrade).

## Related files
- `battlefieldengine/battlefieldengine/MqttClient.py` - `__init__()`, `_on_message()`

## Acceptance criteria
- [ ] `connect_async` or retry loop
- [ ] Callbacks wrapped in try/except with logging
- [ ] Clear error when `MQTT_HOST` is missing
- [ ] Upgrade path to paho 2.x noted

**Estimate:** ~3 h
````

### #24: validate_config.py points at schemas/ and hardware/ paths that do not exist

- **Type:** Bug
- **Labels:** `type: bug`, `area: config`, `area: infra`, `priority: P1 - high`, `size: S`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `validate_config.py points at schemas/ and hardware/ paths that do not exist`

````markdown
## Description
`HARDWARE_SCHEMA_PATH` and `THEME_SCHEMA_PATH` expect `schemas/*.json`, and the README expects `hardware/rig.json` and `themes/*.json`. In the repo the schemas sit flat in `missions/` and the rig lives in `configurations/`.

## Related files
- `battlefieldengine/missions/validate_config.py` - `HARDWARE_SCHEMA_PATH`, `THEME_SCHEMA_PATH`
- `battlefieldengine/missions/README.md`
- `battlefieldengine/battlefieldengine/configurations/rig.json`

## Acceptance criteria
- [ ] `python missions/validate_config.py <rig> <theme>` runs from the repo root
- [ ] README file layout matches reality

**Estimate:** ~1 h
````

### #25: arms-deal.json fails validation against rig.json

- **Type:** Bug
- **Labels:** `type: bug`, `area: config`, `priority: P1 - high`, `size: S`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `arms-deal.json fails validation against rig.json`

````markdown
## Description
`hardware_aliases.objective_1_led` points to `led_1`, which does not exist (the rig has only `led_test`), and the `hot_streak_vibrate` rule targets `briefcase_led`, which is not an alias.

## Related files
- `battlefieldengine/missions/arms-deal.json` - `hardware_aliases`, `hot_streak_vibrate`
- `battlefieldengine/battlefieldengine/configurations/rig.json` - `leds`

## Acceptance criteria
- [ ] Validator passes for both missions
- [ ] CI validates every mission

**Estimate:** ~1 h · **Depends on:** #24
````

### #26: MQTT topic naming is inconsistent across rig.json, firmware, Python and themes

- **Type:** Bug
- **Labels:** `type: bug`, `area: backend`, `area: firmware`, `area: config`, `priority: P1 - high`, `size: S`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `MQTT topic naming is inconsistent across rig.json, firmware, Python and themes`

````markdown
## Description
`rig.json` uses `/LedControl`, `/OledControl`; firmware uses `/led_control`, `/oled_control`; `TerrainNode.led_topic` uses `led_control`; the docstring mentions `/rfid`; themes use `game/events/...`. Naming mismatches are a recurring source of silent failures.

## Expected behavior
One source of truth for topic strings, shared by Python and firmware.

## Related files
- `battlefieldengine/battlefieldengine/configurations/rig.json` - `mqtt_topic` fields
- `ESP32/ObjectiveMarker/lib/LedController/LedController.cpp` - `begin()`
- `battlefieldengine/battlefieldengine/TerrainNode.py` - `rfid_topic`, `led_topic`

## Acceptance criteria
- [ ] Fixed by the central topic registry
- [ ] No literal topic strings outside `topics.py` and generated headers

**Estimate:** ~2 h · **Depends on:** #37
````

### #27: Config and log paths depend on the working directory; run.sh launches the server before cd

- **Type:** Bug
- **Labels:** `type: bug`, `area: backend`, `area: infra`, `priority: P2 - medium`, `size: S`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `Config and log paths depend on the working directory; run.sh launches the server before cd`

````markdown
## Description
`DEFAULT_CONFIG_PATH`, `UNITS_PATH` and the log paths are relative to the current directory. `run.sh` starts the server before `cd "$REPO_ROOT"`, and its header comment calls itself `run_all.sh`. Running `server.py` as a script also relies on the package being installed.

## Related files
- `run.sh`
- `battlefieldengine/battlefieldengine/server.py` - `DEFAULT_CONFIG_PATH`
- `console_ui/battlefield_ui.py` - `UNITS_PATH`
- `battlefieldengine/battlefieldengine/configurations/server_config.json`

## Acceptance criteria
- [ ] Paths resolved relative to the repo root or the config file
- [ ] `python -m battlefieldengine.server` works from anywhere
- [ ] `run.sh` fixed

**Estimate:** ~2 h
````

### #28: Dependencies are split and stale: pyproject lists only paho; two requirements files

- **Type:** Bug
- **Labels:** `type: bug`, `area: infra`, `priority: P2 - medium`, `size: S`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `Dependencies are split and stale: pyproject lists only paho; two requirements files`

````markdown
## Description
`pyproject.toml` declares only `paho-mqtt`, while `requirements.txt` adds dotenv, textual, numpy and pytest, and `full_requirements.txt` looks like an environment dump (jupyter, nbconvert). The `commands to automate` note references pipreqs.

## Related files
- `battlefieldengine/pyproject.toml`
- `requirements.txt`
- `full_requirements.txt`
- `commands to automate`

## Acceptance criteria
- [ ] pyproject is the single source of truth with `ui` and `dev` extras
- [ ] `full_requirements.txt` removed or regenerated by CI

**Estimate:** ~1.5 h
````

### #29: UID normalization goes through slugify() and Unit.tags typing is inconsistent

- **Type:** Bug
- **Labels:** `type: bug`, `area: backend`, `priority: P3 - low`, `size: S`, `good first issue`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `UID normalization goes through slugify() and Unit.tags typing is inconsistent`

````markdown
## Description
`_on_terrain_scan` uses `slugify(reading.uid).upper()`; an empty UID becomes 'UNIT'. `Unit.tags` is typed `dict` while the registry file stores a list.

## Related files
- `battlefieldengine/battlefieldengine/Battlefield.py` - `_on_terrain_scan()`
- `battlefieldengine/battlefieldengine/Models.py` - `Unit.tags`

## Acceptance criteria
- [ ] Shared `normalize_uid()` (strip, upper, validate hex)
- [ ] `tags: list[str]`

**Estimate:** ~1 h
````

### #30: Rotate any credential that ever touched git history; enable secret scanning and push protection

- **Type:** Task
- **Labels:** `type: task`, `area: security`, `area: infra`, `priority: P1 - high`, `size: S`
- **Milestone:** M2 - Productize
- **Title to paste:** `Rotate any credential that ever touched git history; enable secret scanning and push protection`

````markdown
## Description
History rewriting removes a secret from the repo but does not un-leak it if it ever reached a remote or a fork. Rotate WiFi and MQTT credentials, then turn on GitHub secret scanning and push protection and add a pre-commit or CI scanner.

## Related files
- `ESP32/ObjectiveMarker/src/example_secrets.h`
- `.gitignore`
- `.env` (not committed)

## Acceptance criteria
- [ ] Credentials rotated
- [ ] Secret scanning and push protection enabled
- [ ] gitleaks (or equivalent) runs in CI

**Estimate:** ~1.5 h
````

### #31: ADR: local-first hub vs cloud MQTT broker

- **Type:** Spike
- **Labels:** `type: spike`, `area: business`, `area: backend`, `priority: P0 - blocker`, `size: M`
- **Milestone:** M0 - Decide & De-risk
- **Title to paste:** `ADR: local-first hub vs cloud MQTT broker`

````markdown
## Description
Decide where the broker lives. It determines topic namespacing, provisioning, hub packaging, running costs, offline behavior and the security model. Write an Architecture Decision Record with a decision matrix (cost, offline play, security surface, remote and spectator features, support burden).

## Related files
- `docs/adr/0001-broker-deployment.md` (new)

## Acceptance criteria
- [ ] ADR committed with the decision and rejected alternatives
- [ ] Follow-up issues (tenant namespace, hub packaging) updated

**Estimate:** ~6 h
````

### #32: Spike: evaluate multi-tag RFID readers (PN532 workaround vs ISO15693 inventory)

- **Type:** Spike
- **Labels:** `type: spike`, `area: hardware`, `area: firmware`, `priority: P0 - blocker`, `size: M`
- **Milestone:** M0 - Decide & De-risk
- **Title to paste:** `Spike: evaluate multi-tag RFID readers (PN532 workaround vs ISO15693 inventory)`

````markdown
## Description
Time-boxed to 8 hours. Test 5+ tagged bases under one objective and measure detection rate and latency with the PN532 plus card deselection, then with at least one alternative reader. Feeds the multi-tag bug and the PCB design.

## Related files
- `docs/hardware/rfid-testing.md` (new)
- `ESP32/ObjectiveMarker/lib/RfidTracker/RfidTracker.cpp`

## Acceptance criteria
- [ ] Results table (readers, tags, distance, latency, misses)
- [ ] Recommendation with cost impact

**Estimate:** ~8 h
````

### #33: Spike: RFID range and reliability with magnetized bases and metal terrain

- **Type:** Spike
- **Labels:** `type: spike`, `area: hardware`, `priority: P1 - high`, `size: M`
- **Milestone:** M3 - Hardware v1
- **Title to paste:** `Spike: RFID range and reliability with magnetized bases and metal terrain`

````markdown
## Description
Magnetized bases and metal-loaded terrain detune 13.56 MHz antennas. Measure read range with and without ferrite shielding and different antenna placements under the terrain surface.

## Related files
- `docs/hardware/rfid-testing.md`

## Acceptance criteria
- [ ] Read-range matrix
- [ ] Shielding recommendation feeds the enclosure design

**Estimate:** ~5 h
````

### #34: Branding and IP review: make the product system-agnostic

- **Type:** Task
- **Labels:** `type: task`, `area: business`, `priority: P0 - blocker`, `size: M`
- **Milestone:** M0 - Decide & De-risk
- **Title to paste:** `Branding and IP review: make the product system-agnostic`

````markdown
## Description
The repo contains faction art and 'Space Marines'/'Tau'/'Orks' strings. Games Workshop is protective of its trademarks, so a commercial product should not depend on them. Define neutral naming, replace or remove faction assets, and get a qualified opinion before any campaign. (Not legal advice.)

## Related files
- `bitmap_generator/assets/generated/tau.h`
- `bitmap_generator/assets/factions.json`
- `battlefieldengine/battlefieldengine/Battlefield.py` - `UnitRegistry` docstring
- `README.md`

## Acceptance criteria
- [ ] Neutral name/tagline decided
- [ ] Faction assets replaced with original placeholders
- [ ] Legal consult booked or completed

**Estimate:** ~5 h
````

### #35: Decide licensing model and contribution policy (PolyForm NC vs alternatives; DCO/CLA)

- **Type:** Task
- **Labels:** `type: task`, `area: business`, `area: docs`, `priority: P2 - medium`, `size: S`
- **Milestone:** M0 - Decide & De-risk
- **Title to paste:** `Decide licensing model and contribution policy (PolyForm NC vs alternatives; DCO/CLA)`

````markdown
## Description
PolyForm Noncommercial permits your own commercial use as owner but forbids others'. Decide whether that fits an open-source-for-community strategy, whether the firmware and hub software are licensed differently, and whether contributions need a DCO or CLA. Check third-party licenses (e.g. the HiveMQ Apache-2.0 header in `MqttClient.py`, Arduino libraries).

## Related files
- `LICENSE`
- `battlefieldengine/battlefieldengine/MqttClient.py` - license header

## Acceptance criteria
- [ ] Decision recorded in the ADR folder
- [ ] `LICENSE`/`NOTICE` updated
- [ ] CONTRIBUTING references the policy

**Estimate:** ~3 h
````

### #36: Repo scaffolding: issue forms, PR template, CONTRIBUTING, SECURITY.md, Dependabot, release notes config

- **Type:** Task
- **Labels:** `type: task`, `area: infra`, `area: docs`, `priority: P2 - medium`, `size: S`
- **Milestone:** M0 - Decide & De-risk
- **Title to paste:** `Repo scaffolding: issue forms, PR template, CONTRIBUTING, SECURITY.md, Dependabot, release notes config`

````markdown
## Description
Adopt the GitHub project files delivered with this backlog: `.github/ISSUE_TEMPLATE/*.yml`, `pull_request_template.md`, `dependabot.yml`, `release.yml`, and `SECURITY.md`. Add CONTRIBUTING, CODE_OF_CONDUCT and CODEOWNERS, and turn on branch protection for `main`.

## Related files
- `.github/`
- `SECURITY.md`
- `CONTRIBUTING.md` (new)

## Acceptance criteria
- [ ] Files committed
- [ ] Branch protection/ruleset requires PR and passing CI
- [ ] Labels and milestones created (script provided)

**Estimate:** ~3 h
````

### #37: Central topic registry (topics.py) with a generated firmware header

- **Type:** Feature
- **Labels:** `type: feature`, `area: backend`, `area: firmware`, `area: config`, `priority: P1 - high`, `size: M`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `Central topic registry (topics.py) with a generated firmware header`

````markdown
## Description
Create one module that builds every MQTT topic (device base + suffix, global game topics). Generate a C++ header from a shared `topics.json` in the same way `bitmap_generator/codegen.py` generates icons, so Python and firmware cannot drift apart.

## Related files
- `battlefieldengine/battlefieldengine/core/topics.py` (new)
- `topics.json` (new)
- `battlefieldengine/battlefieldengine/Battlefield.py` - `TOPIC_*` constants
- `battlefieldengine/battlefieldengine/configurations/rig.json`

## Acceptance criteria
- [ ] No literal topic strings outside generated/topics files
- [ ] Firmware builds using the generated header
- [ ] Rig `mqtt_topic` fields become suffixes relative to a device base

**Estimate:** ~6 h
````

### #38: In-process EventBus with MQTT-style wildcard matching, plus typed events

- **Type:** Feature
- **Labels:** `type: feature`, `area: backend`, `priority: P1 - high`, `size: M`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `In-process EventBus with MQTT-style wildcard matching, plus typed events`

````markdown
## Description
Add `core/events.py` (dataclasses: `UnitArrived`, `UnitDeparted`, `TurnChanged`, `ObjectiveStatus`, `EffectIntent`) and `core/bus.py` (publish/subscribe with `+` and `#`). Reuse the matcher in `MqttClient`.

## Related files
- `battlefieldengine/battlefieldengine/core/events.py` (new)
- `battlefieldengine/battlefieldengine/core/bus.py` (new)

## Acceptance criteria
- [ ] Matcher passes the MQTT spec examples
- [ ] Handlers isolated (one exception does not stop others)
- [ ] Unit tests

**Estimate:** ~8 h
````

### #39: PresenceTracker keyed by (terrain, uid) with an injectable clock

- **Type:** Feature
- **Labels:** `type: feature`, `area: backend`, `priority: P1 - high`, `size: M`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `PresenceTracker keyed by (terrain, uid) with an injectable clock`

````markdown
## Description
Layer 1 core. Replaces `UnitState.on_field` and `check_departures()`. Emits `UnitArrived`/`UnitDeparted` per terrain, supports multiple units per terrain, and takes a clock parameter so timeouts are testable without sleeping.

## Related files
- `battlefieldengine/battlefieldengine/sensing/presence.py` (new)
- `battlefieldengine/battlefieldengine/Battlefield.py`
- `battlefieldengine/battlefieldengine/Models.py`

## Acceptance criteria
- [ ] Tests: arrival, heartbeat refresh, timeout departure, move between terrains, multi-unit
- [ ] `Battlefield` no longer tracks raw presence

**Estimate:** ~8 h · **Depends on:** #38
````

### #40: Refactor TerrainNode into a pure Layer 1 adapter (no LED control)

- **Type:** Feature
- **Labels:** `type: feature`, `area: backend`, `priority: P2 - medium`, `size: M`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `Refactor TerrainNode into a pure Layer 1 adapter (no LED control)`

````markdown
## Description
`TerrainNode` should only subscribe to its scan topic, parse readings and publish scan events. Remove `light_on`/`light_off`, `occupying_units` and role-derived `led_color`/`led_pattern`; actuation moves to Layer 3.

## Related files
- `battlefieldengine/battlefieldengine/TerrainNode.py`
- `battlefieldengine/battlefieldengine/Battlefield.py` - `load_terrain_nodes()`

## Acceptance criteria
- [ ] TerrainNode has no publish-to-LED code
- [ ] Existing behavior preserved through the pipeline

**Estimate:** ~4 h · **Depends on:** #39, #43
````

### #41: ControlCalculator and ObjectiveStatus (standing / contested / secured, shared_name de-duplication)

- **Type:** Feature
- **Labels:** `type: feature`, `area: backend`, `priority: P1 - high`, `size: L`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `ControlCalculator and ObjectiveStatus (standing / contested / secured, shared_name de-duplication)`

````markdown
## Description
Layer 2. From per-terrain presence and the unit registry, compute who controls each objective. Units sharing a `shared_name` count only their highest `control_value` (as the registration UI already promises). Define a configurable 'secured' rule (held N seconds, or at end of turn). Emit `game/events/objective/<id>/status` with `{status, team_name, team_color}`.

## Related files
- `battlefieldengine/battlefieldengine/game/control.py` (new)
- `console_ui/RegistrationScreen.py` - hint text
- `battlefieldengine/battlefieldengine/configurations/UnitRegistry.json`

## Acceptance criteria
- [ ] Tests for uncontested, contested, tie, shared_name cases
- [ ] Status events match what theme triggers expect

**Estimate:** ~10 h · **Depends on:** #39, #19
````

### #42: Rig v2: multi-node schema, loader and alias resolver

- **Type:** Feature
- **Labels:** `type: feature`, `area: config`, `area: backend`, `priority: P1 - high`, `size: L`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `Rig v2: multi-node schema, loader and alias resolver`

````markdown
## Description
The current rig describes one device. Add `nodes[]` (each with `mqtt_base` and peripherals), let aliases resolve to `node/peripheral`, and add an `objective_id` to node map. Implement `actuation/rig.py` and `resolver.py`.

## Related files
- `battlefieldengine/missions/hardware-rig.schema.json`
- `battlefieldengine/missions/theme.schema.json` - `hardware_aliases`
- `battlefieldengine/battlefieldengine/configurations/rig.json`
- `battlefieldengine/missions/validate_config.py`

## Acceptance criteria
- [ ] Schema and validator updated
- [ ] Templated targets such as `objective_{{trigger.objective_id}}_led` resolve
- [ ] Backward-compatible migration note for v1 rigs

**Estimate:** ~10 h · **Depends on:** #37
````

### #43: Payload encoders and ActuationDispatcher (Layer 3) with capability fallback

- **Type:** Feature
- **Labels:** `type: feature`, `area: backend`, `area: firmware`, `priority: P1 - high`, `size: M`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `Payload encoders and ActuationDispatcher (Layer 3) with capability fallback`

````markdown
## Description
Consume `EffectIntent`s, look up the device, encode the firmware payload (led/oled/audio/haptic JSON), check capabilities (e.g. `supports_rgb: false` falls back to on/off) and publish. Document the payload contracts in `docs/protocol.md`.

## Related files
- `battlefieldengine/battlefieldengine/actuation/encoders.py` (new)
- `battlefieldengine/battlefieldengine/actuation/dispatcher.py` (new)
- `docs/protocol.md` (new)

## Acceptance criteria
- [ ] Encoders unit-tested against documented payloads
- [ ] Unknown target logs a clear error instead of silently doing nothing

**Estimate:** ~8 h · **Depends on:** #42, #38
````

### #44: Mission engine (1/3): loader, trigger matching and conditions

- **Type:** Feature
- **Labels:** `type: feature`, `area: backend`, `area: config`, `priority: P1 - high`, `size: L`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `Mission engine (1/3): loader, trigger matching and conditions`

````markdown
## Description
Load and validate a theme, collect distinct trigger topics, capture `topic_vars` from `+` wildcards, evaluate the flat AND condition list (`==, !=, >, >=, <, <=, in, not_in`) against `payload.*`, `trigger.*` and `state.*`.

## Related files
- `battlefieldengine/battlefieldengine/missions/loader.py` (new)
- `battlefieldengine/battlefieldengine/missions/engine.py` (new)
- `battlefieldengine/missions/theme.schema.json`

## Acceptance criteria
- [ ] Both example missions load
- [ ] Tests for each operator and missing-field behavior

**Estimate:** ~10 h · **Depends on:** #38, #42
````

### #45: Mission engine (2/3): templating and action execution to EffectIntents

- **Type:** Feature
- **Labels:** `type: feature`, `area: backend`, `priority: P1 - high`, `size: M`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `Mission engine (2/3): templating and action execution to EffectIntents`

````markdown
## Description
Resolve `{{payload.x}}` and `{{trigger.x}}` templates and turn `led`, `oled`, `audio`, `vibrate` actions into `EffectIntent`s in order. Define behavior for unresolved variables (fail the action, log clearly).

## Related files
- `battlefieldengine/battlefieldengine/missions/engine.py`
- `battlefieldengine/missions/reactor-meltdown.json`
- `battlefieldengine/missions/arms-deal.json`

## Acceptance criteria
- [ ] End-to-end test: MQTT status message to LED payload
- [ ] Template errors never crash the engine

**Estimate:** ~8 h · **Depends on:** #44, #43
````

### #46: Mission engine (3/3): state store, sliding-window counters, cooldowns and interval triggers

- **Type:** Feature
- **Labels:** `type: feature`, `area: backend`, `priority: P2 - medium`, `size: M`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `Mission engine (3/3): state store, sliding-window counters, cooldowns and interval triggers`

````markdown
## Description
Implement the `state` block (`counter`, `sliding_window_counter` with pruning), the `state_update` action (`increment`, `push_timestamp`, ...), `cooldown_seconds`, and `interval` triggers driven by the engine loop.

## Related files
- `battlefieldengine/battlefieldengine/missions/state_store.py` (new)
- `battlefieldengine/missions/reactor-meltdown.json` - `meltdown_warning_vibrate`

## Acceptance criteria
- [ ] Meltdown escalation rule fires after 2 takeovers in 5 minutes (fake clock test)
- [ ] Cooldown honored

**Estimate:** ~8 h · **Depends on:** #44
````

### #47: Single engine thread fed by a queue (concurrency model)

- **Type:** Feature
- **Labels:** `type: feature`, `area: backend`, `priority: P2 - medium`, `size: M`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `Single engine thread fed by a queue (concurrency model)`

````markdown
## Description
MQTT callbacks currently run on the paho network thread and share locks with the main loop. Have callbacks only enqueue; one engine thread processes events and timers. Simplifies reasoning and tests.

## Related files
- `battlefieldengine/battlefieldengine/server.py` - `run_forever()`
- `battlefieldengine/battlefieldengine/Battlefield.py` - locks
- `battlefieldengine/battlefieldengine/MqttClient.py`

## Acceptance criteria
- [ ] No shared-state locks needed in Layers 2 and 3
- [ ] Shutdown drains cleanly

**Estimate:** ~5 h · **Depends on:** #38
````

### #48: Move ObjectiveRoles into the theme layer; deprecate ObjectiveRoles.json

- **Type:** Feature
- **Labels:** `type: feature`, `area: config`, `area: backend`, `priority: P3 - low`, `size: S`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `Move ObjectiveRoles into the theme layer; deprecate ObjectiveRoles.json`

````markdown
## Description
Role colors and patterns are flavor, and belong in themes. They are currently read at load time and stored on `TerrainNode`, bypassing the pipeline.

## Related files
- `battlefieldengine/battlefieldengine/configurations/ObjectiveRoles.json`
- `battlefieldengine/battlefieldengine/configurations/ObjectiveMarkers.json`
- `battlefieldengine/battlefieldengine/Battlefield.py` - `load_terrain_nodes()`

## Acceptance criteria
- [ ] Theme defines role styling
- [ ] Roles file removed after migration

**Estimate:** ~3 h · **Depends on:** #45
````

### #49: Retain turn/phase state and unit status so new UIs sync on connect

- **Type:** Feature
- **Labels:** `type: feature`, `area: backend`, `area: ui`, `priority: P2 - medium`, `size: S`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `Retain turn/phase state and unit status so new UIs sync on connect`

````markdown
## Description
`_publish_turn_state` and unit events are not retained, so a freshly started UI shows Turn 1 / command until the next change. `MqttClient.publish` has no `retain` parameter.

## Related files
- `battlefieldengine/battlefieldengine/MqttClient.py` - `publish()`
- `battlefieldengine/battlefieldengine/Battlefield.py` - `_publish_turn_state()`
- `console_ui/battlefield_ui.py` - `on_mount()`

## Acceptance criteria
- [ ] `publish(topic, payload, retain=False)`
- [ ] UI shows the true current state immediately after start

**Estimate:** ~3 h
````

### #50: Validator: warn on schema features the engine does not support; run on every mission in CI

- **Type:** Feature
- **Labels:** `type: feature`, `area: config`, `area: infra`, `priority: P2 - medium`, `size: S`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `Validator: warn on schema features the engine does not support; run on every mission in CI`

````markdown
## Description
The schema allows `state_change` triggers, `mqtt_publish` actions and `per_team` scope, which the MVP engine will not implement. Flag them as warnings, and run the cross-check for every mission against the rig in CI. Also reject duplicate GPIO pins.

## Related files
- `battlefieldengine/missions/validate_config.py`
- `.github/workflows/python.yml`

## Acceptance criteria
- [ ] Warnings list unsupported features
- [ ] CI fails on any invalid mission

**Estimate:** ~3 h · **Depends on:** #24
````

### #51: CI: pytest and ruff on GitHub Actions

- **Type:** Feature
- **Labels:** `type: feature`, `area: infra`, `priority: P1 - high`, `size: S`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `CI: pytest and ruff on GitHub Actions`

````markdown
## Description
Add a workflow running on push and PR: install from pyproject, `ruff check`, `pytest`. Start with tests for presence, registry and topic matching. Require the check for merging to `main`.

## Related files
- `.github/workflows/python.yml` (new)
- `battlefieldengine/tests/` (new)

## Acceptance criteria
- [ ] Green check on a PR
- [ ] Required status check enabled

**Estimate:** ~3 h
````

### #52: CI: PlatformIO firmware build on GitHub Actions

- **Type:** Feature
- **Labels:** `type: feature`, `area: infra`, `area: firmware`, `priority: P1 - high`, `size: S`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `CI: PlatformIO firmware build on GitHub Actions`

````markdown
## Description
Build the firmware in CI by copying `example_secrets.h` to `secrets.h`, cache PlatformIO, and upload the `.bin` as a build artifact. Later reused for signed release builds.

## Related files
- `.github/workflows/firmware.yml` (new)
- `ESP32/ObjectiveMarker/platformio.ini`
- `ESP32/ObjectiveMarker/src/example_secrets.h`

## Acceptance criteria
- [ ] Firmware builds on every PR
- [ ] Artifact downloadable

**Estimate:** ~3 h
````

### #53: Firmware: addressable LED driver (WS2812B) with color and pattern support

- **Type:** Feature
- **Labels:** `type: feature`, `area: firmware`, `priority: P1 - high`, `size: L`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `Firmware: addressable LED driver (WS2812B) with color and pattern support`

````markdown
## Description
`LedController` drives a single GPIO on/off and ignores `color`/`pattern` in the payload (see the comment in `handleMqttEvent`). Implement patterns solid, pulse, blink and flash on WS2812B, respecting `supports_rgb`.

## Related files
- `ESP32/ObjectiveMarker/lib/LedController/LedController.h`
- `ESP32/ObjectiveMarker/lib/LedController/LedController.cpp` - `handleMqttEvent()`

## Acceptance criteria
- [ ] All four patterns work non-blocking
- [ ] Payload contract documented
- [ ] Local LED-off on tag expiry preserved

**Estimate:** ~10 h
````

### #54: Audio: non-blocking DFPlayer task and asset manifest (filename to track number)

- **Type:** Feature
- **Labels:** `type: feature`, `area: firmware`, `area: config`, `priority: P2 - medium`, `size: M`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `Audio: non-blocking DFPlayer task and asset manifest (filename to track number)`

````markdown
## Description
DFPlayer plays by numeric track (`playMp3FolderTrack(n)`), while themes reference files like `sfx/gunfire_short.wav`. Add a build step (like `bitmap_generator`) that produces the SD card layout and a filename-to-track map, and run playback in a small task with a command queue.

## Related files
- `ESP32/ObjectiveMarker/lib/AudioController/AudioController.cpp`
- `audio_generator/` (new)
- `battlefieldengine/missions/*.json` - audio `file` values

## Acceptance criteria
- [ ] Theme filenames resolve to track numbers
- [ ] SD layout generated reproducibly

**Estimate:** ~8 h · **Depends on:** #7
````

### #55: Firmware: DRV2605 haptic controller for vibrate actions

- **Type:** Feature
- **Labels:** `type: feature`, `area: firmware`, `priority: P3 - low`, `size: M`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `Firmware: DRV2605 haptic controller for vibrate actions`

````markdown
## Description
Themes use `vibrate` actions with ms on/off patterns. Add a `HapticController` library subscribed to its own topic and mapping the pattern array to DRV2605 effects.

## Related files
- `ESP32/ObjectiveMarker/lib/HapticController/` (new)
- `battlefieldengine/battlefieldengine/configurations/rig.json` - `haptics`

## Acceptance criteria
- [ ] Pattern array plays on hardware
- [ ] Pin/bus in pinout doc

**Estimate:** ~6 h · **Depends on:** #12
````

### #56: Firmware: last-will, retained online/offline, heartbeat with firmware version, explicit 'left' events

- **Type:** Feature
- **Labels:** `type: feature`, `area: firmware`, `area: backend`, `priority: P1 - high`, `size: M`
- **Milestone:** M1 - Core Fixes & Pipeline
- **Title to paste:** `Firmware: last-will, retained online/offline, heartbeat with firmware version, explicit 'left' events`

````markdown
## Description
Backend departure currently relies on a 5 s timeout, giving 5-7 s latency, while the firmware already knows when a tag expires (`RfidTracker::publishActive`). Publish an explicit left event, add an MQTT last-will and retained status message, and include the firmware version in a periodic heartbeat. Needed for support and dead-node detection.

## Related files
- `ESP32/ObjectiveMarker/lib/RfidTracker/RfidTracker.cpp` - `publishActive()`
- `ESP32/ObjectiveMarker/lib/MqttRouter/MqttRouter.cpp` - `reconnect()`
- `battlefieldengine/battlefieldengine/Battlefield.py`

## Acceptance criteria
- [ ] Departure event arrives within ~2.5 s of removing a model
- [ ] Broker shows node offline within keepalive after power-off
- [ ] Backend keeps the timeout as fallback

**Estimate:** ~8 h · **Depends on:** #37
````

### #57: Firmware: load pins, topics and peripherals from LittleFS config (no hardcoded topic in main.cpp)

- **Type:** Feature
- **Labels:** `type: feature`, `area: firmware`, `area: config`, `priority: P2 - medium`, `size: M`
- **Milestone:** M2 - Productize
- **Title to paste:** `Firmware: load pins, topics and peripherals from LittleFS config (no hardcoded topic in main.cpp)`

````markdown
## Description
`main.cpp` hardcodes `OBJECTIVE_TOPIC`, LED and I2C pins, so each marker needs a different build. Load them from a LittleFS `rig.json`/`node.json`. Prerequisite for provisioning.

## Related files
- `ESP32/ObjectiveMarker/src/main.cpp`
- `ESP32/ObjectiveMarker/lib/ObjectiveNode/ObjectiveNode.cpp`
- `ESP32/ObjectiveMarker/platformio.ini` - filesystem/partition settings

## Acceptance criteria
- [ ] One firmware image serves any marker
- [ ] Missing/invalid config produces a safe fallback and a log

**Estimate:** ~8 h · **Depends on:** #37
````

### #58: Verify the broker TLS certificate on the ESP32 (remove setInsecure)

- **Type:** Feature
- **Labels:** `type: feature`, `area: firmware`, `area: security`, `priority: P1 - high`, `size: S`
- **Milestone:** M2 - Productize
- **Title to paste:** `Verify the broker TLS certificate on the ESP32 (remove setInsecure)`

````markdown
## Description
`MqttRouter::begin` calls `_espClient.setInsecure()`, so the device accepts any certificate and is open to man-in-the-middle attacks. Embed the broker's root CA (or a small bundle) and plan for certificate rotation and clock/NTP requirements.

## Related files
- `ESP32/ObjectiveMarker/lib/MqttRouter/MqttRouter.cpp` - `begin()`

## Acceptance criteria
- [ ] `setInsecure()` removed
- [ ] Connection fails against a wrong-cert broker (negative test)
- [ ] Rotation procedure documented

**Estimate:** ~3 h
````

### #59: Per-device MQTT credentials and topic ACLs

- **Type:** Feature
- **Labels:** `type: feature`, `area: security`, `area: backend`, `area: firmware`, `priority: P1 - high`, `size: L`
- **Milestone:** M2 - Productize
- **Title to paste:** `Per-device MQTT credentials and topic ACLs`

````markdown
## Description
Firmware, backend and UI all share one broker credential, so any single compromise grants full access. Issue per-device credentials (or client certificates) and ACLs: a device publishes only its scans/status and subscribes only to its own command topics; only the backend publishes commands and turn state; the UI cannot publish device topics.

## Related files
- `docs/broker/` (new)
- `battlefieldengine/battlefieldengine/MqttClient.py`
- `ESP32/ObjectiveMarker/src/example_secrets.h`

## Acceptance criteria
- [ ] ACL file committed and tested
- [ ] A device credential cannot read another device's topics

**Estimate:** ~10 h · **Depends on:** #31, #37
````

### #60: Provisioning: SoftAP captive portal storing WiFi and MQTT settings in NVS

- **Type:** Feature
- **Labels:** `type: feature`, `area: firmware`, `area: security`, `priority: P1 - high`, `size: XL`
- **Milestone:** M2 - Productize
- **Title to paste:** `Provisioning: SoftAP captive portal storing WiFi and MQTT settings in NVS`

````markdown
## Description
Replace compile-time `secrets.h` with first-boot provisioning: node starts an access point with a captive portal, user enters WiFi and hub details, values are stored in NVS, and a button hold re-enters setup. Required before anyone else assembles a unit.

## Related files
- `ESP32/ObjectiveMarker/src/example_secrets.h`
- `ESP32/ObjectiveMarker/src/main.cpp`
- `ESP32/ObjectiveMarker/lib/ObjectiveNode/ObjectiveNode.cpp` - `begin()`, `connectWifi()`

## Acceptance criteria
- [ ] Fresh device provisioned without reflashing
- [ ] Factory reset path
- [ ] No shared default password

**Estimate:** ~25 h · **Depends on:** #57
````

### #61: Signed OTA updates with rollback

- **Type:** Feature
- **Labels:** `type: feature`, `area: firmware`, `area: security`, `area: infra`, `priority: P1 - high`, `size: XL`
- **Milestone:** M2 - Productize
- **Title to paste:** `Signed OTA updates with rollback`

````markdown
## Description
Add OTA using dual app partitions and `esp_https_ota`, verify signed images, roll back if the new image fails a health check, and publish images as GitHub Release assets with version metadata.

## Related files
- `ESP32/ObjectiveMarker/platformio.ini` - partitions
- `ESP32/ObjectiveMarker/lib/OtaUpdater/` (new)
- `.github/workflows/firmware.yml` - release job

## Acceptance criteria
- [ ] Update over WiFi succeeds
- [ ] Bad image rolls back
- [ ] Unsigned image rejected
- [ ] Signing key handling documented

**Estimate:** ~25 h · **Depends on:** #52, #58
````

### #62: Multi-table topic namespace (tables/{id}/...)

- **Type:** Feature
- **Labels:** `type: feature`, `area: backend`, `area: firmware`, `area: security`, `priority: P2 - medium`, `size: L`
- **Milestone:** M2 - Productize
- **Title to paste:** `Multi-table topic namespace (tables/{id}/...)`

````markdown
## Description
All topics live under `battlefield/...`, so two customers sharing a broker would collide and see each other's events. Prefix everything with a table ID and align ACLs. Skip if the ADR chooses strictly local hubs, but document the reasoning.

## Related files
- `battlefieldengine/battlefieldengine/core/topics.py`
- `ESP32/ObjectiveMarker/src/main.cpp`

## Acceptance criteria
- [ ] Two tables run side by side without interference

**Estimate:** ~12 h · **Depends on:** #31, #37
````

### #63: Firmware robustness: task watchdog, bounded buffers, payload and JSON limits

- **Type:** Feature
- **Labels:** `type: feature`, `area: firmware`, `area: security`, `priority: P2 - medium`, `size: L`
- **Milestone:** M2 - Productize
- **Title to paste:** `Firmware robustness: task watchdog, bounded buffers, payload and JSON limits`

````markdown
## Description
`MqttRouter::handleMessage` builds a `String` per message byte; PubSubClient's default 256-byte buffer silently drops larger messages; `MAX_ROUTES` overflow only logs. Add explicit size limits, drop-and-log behavior, and a task watchdog.

## Related files
- `ESP32/ObjectiveMarker/lib/MqttRouter/MqttRouter.cpp` - `handleMessage()`, `registerHandler()`
- `ESP32/ObjectiveMarker/lib/MqttRouter/MqttRouter.h` - `MAX_ROUTES`

## Acceptance criteria
- [ ] Oversized payload does not crash or stall the node
- [ ] `setBufferSize` chosen deliberately
- [ ] Fuzz test with malformed JSON

**Estimate:** ~10 h
````

### #64: Backend hardening: dependency pinning and audit, log redaction, Dependabot

- **Type:** Feature
- **Labels:** `type: feature`, `area: backend`, `area: security`, `area: infra`, `priority: P2 - medium`, `size: M`
- **Milestone:** M2 - Productize
- **Title to paste:** `Backend hardening: dependency pinning and audit, log redaction, Dependabot`

````markdown
## Description
Pin dependencies, run `pip-audit` in CI, enable Dependabot for pip and GitHub Actions, redact credentials and UIDs where appropriate in logs, and enable CodeQL for Python.

## Related files
- `.github/dependabot.yml`
- `.github/workflows/python.yml`
- `battlefieldengine/battlefieldengine/MqttClient.py`

## Acceptance criteria
- [ ] Dependabot PRs appear
- [ ] CI fails on known-vulnerable dependencies
- [ ] Logs contain no credentials

**Estimate:** ~8 h
````

### #65: Threat model, SECURITY.md and vulnerability disclosure (private vulnerability reporting)

- **Type:** Feature
- **Labels:** `type: feature`, `area: security`, `area: docs`, `priority: P2 - medium`, `size: L`
- **Milestone:** M2 - Productize
- **Title to paste:** `Threat model, SECURITY.md and vulnerability disclosure (private vulnerability reporting)`

````markdown
## Description
Document assets, trust boundaries and threats (rogue device, stolen credentials, MITM, malicious OTA, spoofed commands, cloned tags). Enable GitHub private vulnerability reporting and publish a disclosure contact and support window.

## Related files
- `SECURITY.md`
- `docs/security/threat-model.md` (new)

## Acceptance criteria
- [ ] Threat model reviewed against implemented mitigations
- [ ] Private vulnerability reporting enabled

**Estimate:** ~10 h
````

### #66: Production hardening: secure boot v2 and flash encryption build profile

- **Type:** Feature
- **Labels:** `type: feature`, `area: firmware`, `area: security`, `priority: P2 - medium`, `size: L`
- **Milestone:** M3 - Hardware v1
- **Title to paste:** `Production hardening: secure boot v2 and flash encryption build profile`

````markdown
## Description
Enable secure boot v2 and flash encryption for production units only. The efuses are one-way, so keep a separate production profile and rehearse on sacrificial boards first.

## Related files
- `ESP32/ObjectiveMarker/platformio.ini`
- `docs/manufacturing/secure-boot.md` (new)

## Acceptance criteria
- [ ] Production profile boots and updates via signed OTA
- [ ] Key custody documented
- [ ] Dev boards remain unaffected

**Estimate:** ~20 h · **Depends on:** #61
````

### #67: Web UI (FastAPI + WebSocket) as the primary interface; keep the TUI as a dev tool

- **Type:** Feature
- **Labels:** `type: feature`, `area: ui`, `area: backend`, `priority: P2 - medium`, `size: XL`, `help wanted`
- **Milestone:** M2 - Productize
- **Title to paste:** `Web UI (FastAPI + WebSocket) as the primary interface; keep the TUI as a dev tool`

````markdown
## Description
The Textual UI is a developer tool. Customers need a browser UI reachable from a phone: turn/phase controls, live unit events, registration flow, mission selection. Reuse the registration flow logic from `RegistrationScreen`. Consider `aiomqtt` if the engine moves to asyncio.

## Related files
- `console_ui/battlefield_ui.py`
- `console_ui/RegistrationScreen.py`
- `console_ui/RegistryManager.py`

## Acceptance criteria
- [ ] Phone-friendly UI covers all TUI functions
- [ ] Works offline on the local network

**Estimate:** ~50 h · **Depends on:** #49, #64
````

### #68: Hub packaging: Docker Compose (Mosquitto + backend + web UI) and a Raspberry Pi image

- **Type:** Feature
- **Labels:** `type: feature`, `area: infra`, `area: backend`, `priority: P2 - medium`, `size: L`
- **Milestone:** M2 - Productize
- **Title to paste:** `Hub packaging: Docker Compose (Mosquitto + backend + web UI) and a Raspberry Pi image`

````markdown
## Description
If the ADR chooses local-first, provide a one-command hub: broker with ACLs, backend and web UI, and a flashable Pi image with mDNS discovery.

## Related files
- `deploy/` (new)
- `run.sh`

## Acceptance criteria
- [ ] `docker compose up` gives a working system
- [ ] Pi image boots to a reachable UI

**Estimate:** ~20 h · **Depends on:** #31, #59
````

### #69: Mission authoring CLI (validate, simulate) and a third mission (Signal Jamming)

- **Type:** Feature
- **Labels:** `type: feature`, `area: config`, `area: backend`, `priority: P3 - low`, `size: L`
- **Milestone:** M2 - Productize
- **Title to paste:** `Mission authoring CLI (validate, simulate) and a third mission (Signal Jamming)`

````markdown
## Description
Let authors dry-run a mission against fake MQTT messages without hardware, and add a third theme to prove the reskin claim.

## Related files
- `battlefieldengine/missions/`
- `battlefieldengine/missions/README.md`

## Acceptance criteria
- [ ] `simulate` prints intents for a scripted event log
- [ ] Third mission passes validation

**Estimate:** ~12 h · **Depends on:** #45
````

### #70: Docs: architecture overview, protocol reference, pinout, getting started

- **Type:** Feature
- **Labels:** `type: feature`, `area: docs`, `priority: P2 - medium`, `size: L`, `good first issue`
- **Milestone:** M2 - Productize
- **Title to paste:** `Docs: architecture overview, protocol reference, pinout, getting started`

````markdown
## Description
Split the README into a short pitch plus `docs/`: architecture (three layers), MQTT/payload protocol, pinout, getting started, and an accurate 'what works today' section (the multi-tag claim needs to match test results).

## Related files
- `README.md`
- `docs/` (new)

## Acceptance criteria
- [ ] A new user can build one marker from the docs
- [ ] README claims match reality

**Estimate:** ~12 h
````

### #71: Custom carrier PCB: schematic (ESP32 module, RFID front-end, LEDs, OLED, audio, haptic, power)

- **Type:** Feature
- **Labels:** `type: feature`, `area: hardware`, `priority: P2 - medium`, `size: XL`
- **Milestone:** M3 - Hardware v1
- **Title to paste:** `Custom carrier PCB: schematic (ESP32 module, RFID front-end, LEDs, OLED, audio, haptic, power)`

````markdown
## Description
Design in KiCad. Use a pre-certified ESP32 module. RFID reader choice comes from the multi-tag spike. Follow JLCPCB/PCBWay assembly constraints.

## Related files
- `hardware/kicad/` (new)

## Acceptance criteria
- [ ] ERC clean
- [ ] Reviewed against pinout doc

**Estimate:** ~30 h · **Depends on:** #32, #75
````

### #72: PCB layout, DFM checks, order rev A

- **Type:** Feature
- **Labels:** `type: feature`, `area: hardware`, `priority: P2 - medium`, `size: XL`
- **Milestone:** M3 - Hardware v1
- **Title to paste:** `PCB layout, DFM checks, order rev A`

````markdown
## Description
Layout with antenna keep-outs, DFM/DRC checks, and a first order.

## Related files
- `hardware/kicad/`

## Acceptance criteria
- [ ] DRC clean
- [ ] Rev A ordered

**Estimate:** ~30 h · **Depends on:** #71
````

### #73: Board bring-up and firmware port; errata list

- **Type:** Task
- **Labels:** `type: task`, `area: hardware`, `area: firmware`, `priority: P2 - medium`, `size: XL`
- **Milestone:** M3 - Hardware v1
- **Title to paste:** `Board bring-up and firmware port; errata list`

````markdown
## Description
Bring up rev A, port firmware, retune the RFID antenna, and log errata for rev B.

## Related files
- `hardware/errata.md` (new)

## Acceptance criteria
- [ ] All peripherals verified
- [ ] Errata list drives rev B

**Estimate:** ~25 h · **Depends on:** #72
````

### #74: Enclosure and terrain integration design (printable), RFID antenna placement under the surface

- **Type:** Feature
- **Labels:** `type: feature`, `area: hardware`, `priority: P2 - medium`, `size: XL`
- **Milestone:** M3 - Hardware v1
- **Title to paste:** `Enclosure and terrain integration design (printable), RFID antenna placement under the surface`

````markdown
## Description
Design printable housings and mounting so the reader sits under the terrain surface. Use magnet-interference results for shielding.

## Related files
- `hardware/enclosure/` (new)

## Acceptance criteria
- [ ] Prototype fits a real terrain piece
- [ ] Read range verified in enclosure

**Estimate:** ~30 h · **Depends on:** #33
````

### #75: Power design: USB-C and battery options, brownout behavior

- **Type:** Task
- **Labels:** `type: task`, `area: hardware`, `priority: P2 - medium`, `size: L`
- **Milestone:** M3 - Hardware v1
- **Title to paste:** `Power design: USB-C and battery options, brownout behavior`

````markdown
## Description
A code comment notes DFPlayer clone chips brown out. Budget worst-case current (WiFi + LEDs + audio + haptic), pick a supply approach, and add brownout detection.

## Related files
- `ESP32/ObjectiveMarker/lib/AudioController/AudioController.cpp` - volume/brownout comments

## Acceptance criteria
- [ ] Power budget documented
- [ ] No resets under worst-case load

**Estimate:** ~12 h
````

### #76: BOM, sourcing and unit-cost model; pricing hypotheses

- **Type:** Task
- **Labels:** `type: task`, `area: hardware`, `area: business`, `priority: P2 - medium`, `size: L`
- **Milestone:** M3 - Hardware v1
- **Title to paste:** `BOM, sourcing and unit-cost model; pricing hypotheses`

````markdown
## Description
Build a BOM with volume price breaks, enclosure, packaging and shipping, and test target retail prices against the cost.

## Related files
- `docs/business/bom.csv` (new)

## Acceptance criteria
- [ ] Unit cost at 100/500/1000 units
- [ ] Target margin stated

**Estimate:** ~10 h
````

### #77: Alpha program: recruit 5-10 testers and set up a feedback loop

- **Type:** Task
- **Labels:** `type: task`, `area: business`, `area: docs`, `priority: P2 - medium`, `size: L`
- **Milestone:** M4 - Alpha & Campaign Prep
- **Title to paste:** `Alpha program: recruit 5-10 testers and set up a feedback loop`

````markdown
## Description
Recruit local players, enable GitHub Discussions, and point testers at the bug-report issue form. Define what you want to learn (setup time, reliability, mission appeal).

## Related files
- .github/ISSUE_TEMPLATE/bug_report.yml

## Acceptance criteria
- [ ] Testers onboarded
- [ ] Feedback triaged into issues weekly

**Estimate:** ~10 h · **Depends on:** #60, #67
````

### #78: Landing page, demo video and mailing list

- **Type:** Task
- **Labels:** `type: task`, `area: business`, `priority: P2 - medium`, `size: L`
- **Milestone:** M4 - Alpha & Campaign Prep
- **Title to paste:** `Landing page, demo video and mailing list`

````markdown
## Description
Short demo video, landing page (GitHub Pages is fine at first) and an email capture to measure interest before a campaign.

## Acceptance criteria
- [ ] Page live
- [ ] Signup conversion tracked

**Estimate:** ~20 h · **Depends on:** #34
````

### #79: Crowdfunding campaign plan: goal, tiers, fulfillment costs, risk section

- **Type:** Task
- **Labels:** `type: task`, `area: business`, `priority: P2 - medium`, `size: L`
- **Milestone:** M4 - Alpha & Campaign Prep
- **Title to paste:** `Crowdfunding campaign plan: goal, tiers, fulfillment costs, risk section`

````markdown
## Description
Model funding goal against BOM, certification, tooling and fulfillment. Be explicit about risks (certification, manufacturing slips).

## Related files
- `docs/business/campaign-plan.md` (new)

## Acceptance criteria
- [ ] Financial model reviewed
- [ ] Risk section written

**Estimate:** ~20 h · **Depends on:** #76
````

### #80: Compliance plan: FCC/ISED (13.56 MHz reader), CE/RED including cybersecurity, battery transport

- **Type:** Task
- **Labels:** `type: task`, `area: business`, `area: hardware`, `priority: P2 - medium`, `size: L`, `needs verification`
- **Milestone:** M5 - Compliance & Pilot
- **Title to paste:** `Compliance plan: FCC/ISED (13.56 MHz reader), CE/RED including cybersecurity, battery transport`

````markdown
## Description
Identify the required certifications for target markets, get lab quotes, and decide whether the reader design needs its own certification. General-knowledge starting point; verify with a lab.

## Related files
- `docs/compliance/plan.md` (new)

## Acceptance criteria
- [ ] Lab quotes collected
- [ ] Certification schedule added to the roadmap

**Estimate:** ~12 h
````

### #81: Pilot manufacturing run (50-100 units): assembly partner, test jig, QA checklist

- **Type:** Task
- **Labels:** `type: task`, `area: hardware`, `area: business`, `priority: P2 - medium`, `size: XL`
- **Milestone:** M5 - Compliance & Pilot
- **Title to paste:** `Pilot manufacturing run (50-100 units): assembly partner, test jig, QA checklist`

````markdown
## Description
Choose an assembly partner, build a functional test jig, define a QA checklist and packaging, and run a pilot batch.

## Related files
- `docs/manufacturing/` (new)

## Acceptance criteria
- [ ] Batch built
- [ ] Yield and failure modes recorded

**Estimate:** ~60 h · **Depends on:** #73, #80, #66
````

### #82: Spectator display: companion screen fed by the live event stream

- **Type:** Feature
- **Labels:** `type: feature`, `area: ui`, `priority: P3 - low`, `size: L`, `icebox`
- **Milestone:** none (icebox)
- **Title to paste:** `Spectator display: companion screen fed by the live event stream`

````markdown
## Description
From the README roadmap. Show turn/phase, objective control and recent events on a second screen using the mirrored `game/events/...` topics.

## Acceptance criteria
- [ ] Read-only display works from the event stream

**Estimate:** ~20 h · **Depends on:** #67
````
