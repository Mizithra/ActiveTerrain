# ActiveTerrain

**Smart tabletop terrain for Warhammer 40k — RFID-aware objectives, live Visual & Audio feedback, and a real-time backend that turns a static battlefield into a reactive one.**

---

## What it is

ActiveTerrain is a distributed IoT system that brings physical Warhammer 40k terrain to life. Objective markers on the table know when a unit is standing on them. Lights react in real time based on what's happening in the game. A backend keeps score of the battle — turn, phase, and unit presence — without a player ever touching a phone or a laptop.

Place a model on an objective, and its RFID tag is read by a hidden sensor. That event flows over MQTT to a Python backend, which updates the state of the game and pushes a command back out to light the terrain itself — no app to open, no button to press. The tabletop becomes the interface.

## The idea behind it

Tabletop wargames are tactile and social by design — but what if we brought more of the tabletop to life.  I don't want to make a virtual way of playing Warhammer 40K, but I want to bring some of the elements of digital media to enhance the experience.  Make the tabletop more immersive by playing audio files and lighting up to match your armies theme, maybe even create your own.

This project exists at the intersection of a few things I wanted to build well at once: embedded systems talking to real hardware, a distributed architecture where independent devices coordinate through a message broker instead of direct connections, and a backend clean enough that adding a new kind of terrain feature is a config change, not a rewrite. The Warhammer setting is the fun part; the systems design underneath is the point.

## What it does today

- **Detects units on terrain** — each objective marker has its own RFID reader, and can track multiple models present on it at once, independently of every other marker on the table.
- **Reacts with light** — terrain objectives light up on arrival, with color and pattern driven by each marker's role (a primary objective glows differently than a hazard zone), fully configurable without touching firmware.
- **Tracks the game, not just the terrain** — a backend service tracks turn and phase, unit presence across the whole board, and broadcasts that state live to anything listening.
- **Runs as a terminal companion app** — a lightweight terminal UI lets a player advance the turn or phase, and reflects live game state pushed from the backend, without owning any of that state itself.
- **Scales by adding config, not code** — new objective markers, new unit rosters, new terrain roles are all defined in JSON. The system was built so growing the battlefield never means growing the codebase.

## How the pieces talk

Every physical device — each ESP32-driven terrain marker — is fully independent hardware, connected only through an MQTT broker. The Python backend is the single source of truth for game state; it never talks to a device directly, only through published and subscribed topics. This keeps every component swappable and testable in isolation: the terminal UI can run against a live game with zero knowledge of RFID or LEDs, and a terrain marker can be flashed and validated with zero knowledge of Python.

## Built with

`ESP32` · `C++ / Arduino` · `PN532 RFID` · `MQTT` · `Python` · `Textual` (terminal UI) · JSON-driven configuration

## Where it's headed

- Faction-aware objective control — terrain that recognizes *which side* holds it, not just that something's there
- Addressable RGB lighting per marker, replacing single-color LEDs
- A persistent mission/scenario system loaded from structured mission files
- A companion display for spectators, driven by the same live event stream as everything else
- OLEDS, Audio Speakers, and more to bring the immersion to you.

---

*A personal project built to explore embedded systems, event-driven architecture, and hardware/software integration — through the lens of a tabletop game I love.*