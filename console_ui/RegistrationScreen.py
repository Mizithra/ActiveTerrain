"""
RegistrationScreen: guides a user through registering RFID tags to units.

Flow:
  1. Enter owner name + faction (once, at the start).
  2. Loop:
     a. Publish a "start" command -> the registration station's ESP32
        turns its LED on and blocks until a tag is scanned (or times out).
     b. ESP32 publishes the scanned uid back; this screen autofills it.
     c. User types a unit name.
     d. If the tag or unit name already exists, confirm before writing.
     e. Save, then immediately request the next scan.
  3. Escape (or the Finish button) ends the loop and saves.
"""
from __future__ import annotations

import logging
from typing import Optional

from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Input, Static

from RegistryManager import RegistryManager

logger = logging.getLogger(__name__)


class ConfirmModal(ModalScreen[bool]):
    """Simple Yes/No modal. Result is delivered via the push_screen callback."""

    CSS = """
    ConfirmModal {
        align: center middle;
    }
    #confirm_box {
        width: 50;
        border: round yellow;
        padding: 1 2;
        background: $panel;
    }
    """

    def __init__(self, message: str):
        super().__init__()
        self.message = message

    def compose(self):
        with Vertical(id="confirm_box"):
            yield Static(self.message, id="confirm_message")
            with Horizontal():
                yield Button("Yes", id="yes", variant="success")
                yield Button("No", id="no", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "yes")


class RegistrationScreen(Screen):
    CSS = """
    #reg_container {
        width: 64;
        margin: 2 4;
        border: round cyan;
        padding: 1 2;
    }
    #reg_status {
        margin: 1 0;
        min-height: 3;
    }
    Input {
        margin-bottom: 1;
    }
    """

    BINDINGS = [("escape", "finish", "Finish Registration")]

    def __init__(
        self,
        mqtt,
        registry: RegistryManager,
        register_start_topic: str,
        register_result_topic: str,
    ):
        super().__init__()
        self.mqtt = mqtt
        self.registry = registry
        self.register_start_topic = register_start_topic
        self.register_result_topic = register_result_topic
        self.owner = ""
        self.faction = ""
        self.pending_uid: Optional[str] = None

    def compose(self):
        with Vertical(id="reg_container"):
            yield Static("Unit Registration", id="reg_title")
            yield Static(
                "Enter your name and faction, then start registration.",
                id="reg_status",
            )
            yield Input(placeholder="Your name", id="owner_input")
            yield Input(placeholder="Faction", id="faction_input")
            yield Button("Start Registration", id="start_btn")
            yield Input(placeholder="Unit name (after a scan)", id="unit_name_input", disabled=True)
            yield Button("Finish (Esc)", id="finish_btn")

    def on_mount(self) -> None:
        self.mqtt.subscribe(self.register_result_topic, self._on_scan_result)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "start_btn":
            self._begin_loop()
        elif event.button.id == "finish_btn":
            self.action_finish()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "unit_name_input" and self.pending_uid:
            name = event.value.strip()
            event.input.value = ""
            if name:
                self._submit_unit_name(name)

    # --- flow steps ------------------------------------------------------
    def _begin_loop(self) -> None:
        owner_input = self.query_one("#owner_input", Input)
        faction_input = self.query_one("#faction_input", Input)
        self.owner = owner_input.value.strip()
        self.faction = faction_input.value.strip()

        status = self.query_one("#reg_status", Static)
        if not self.owner or not self.faction:
            status.update("Enter your name and faction before starting.")
            return

        owner_input.disabled = True
        faction_input.disabled = True
        self.query_one("#start_btn", Button).disabled = True
        self._request_scan()

    def _request_scan(self) -> None:
        self.query_one("#reg_status", Static).update(
            "Waiting for a tag scan (station light is on)..."
        )
        self.mqtt.publish(self.register_start_topic, {"action": "start"})

    def _on_scan_result(self, topic: str, payload: dict) -> None:
        # Fires on the MQTT network thread -- marshal back onto the app.
        # On a non-Textual thread, `self.app` may not be available via the active
        # app contextvar, so use the internal _app reference when possible.
        app = getattr(self, "_app", None)
        if app is None:
            try:
                app = self.app
            except Exception:
                app = None

        if app is not None:
            app.call_from_thread(self._handle_scan_result, payload)
        else:
            self._handle_scan_result(payload)

    def _handle_scan_result(self, payload: dict) -> None:
        uid = payload.get("uid")
        status = self.query_one("#reg_status", Static)

        if not uid:
            status.update("Scan timed out. Requesting another attempt...")
            self._request_scan()
            return

        self.pending_uid = uid
        unit_input = self.query_one("#unit_name_input", Input)
        unit_input.disabled = False
        unit_input.focus()

        existing = self.registry.get_tag_assignment(uid)
        if existing:
            existing_unit = self.registry.units.get(existing.unit_id)
            existing_name = existing_unit.name if existing_unit else existing.unit_id
            status.update(
                f"Tag {uid} is already registered to '{existing_name}'. "
                f"Type a unit name to reassign it, or press Escape to skip."
            )
        else:
            status.update(f"Scanned tag: {uid}. Enter the unit name for it.")

    def _submit_unit_name(self, unit_name: str) -> None:
        uid = self.pending_uid
        if not uid:
            return

        existing_tag = self.registry.get_tag_assignment(uid)
        existing_unit_id = self.registry.find_unit_id_by_name(unit_name)

        def proceed() -> None:
            unit_id, created = self.registry.register_tag(uid, unit_name, self.faction, self.owner)
            self.registry.save()
            note = "new unit" if created else "added to existing unit"
            self.query_one("#reg_status", Static).update(
                f"Registered tag {uid} -> '{unit_name}' ({note})."
            )
            self.pending_uid = None
            self.query_one("#unit_name_input", Input).disabled = True
            self._request_scan()

        if existing_tag or existing_unit_id:
            if existing_tag:
                message = f"Tag {uid} is already assigned elsewhere. Reassign it to '{unit_name}'?"
            else:
                message = f"Unit '{unit_name}' already exists. Add this tag to it?"

            def handle_confirm(confirmed: Optional[bool]) -> None:
                if confirmed:
                    proceed()
                else:
                    self.query_one("#reg_status", Static).update(
                        "Cancelled. Enter a different unit name for this tag."
                    )

            self.app.push_screen(ConfirmModal(message), handle_confirm)
        else:
            proceed()

    def action_finish(self) -> None:
        self.registry.save()
        self.app.pop_screen()