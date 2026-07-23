"""Textual TUI for Warhammer RFID unit registration."""

import asyncio

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Header, Input, Label, Static

import config
from registry import Registry
from serial_reader import SerialReader


class DuplicateModal(ModalScreen[bool]):
    """Ask user what to do when a duplicate UUID is scanned."""

    def __init__(self, uuid: str, existing: dict) -> None:
        super().__init__()
        self.uuid = uuid
        self.existing = existing

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(f"UUID [b]{self.uuid}[/b] already exists!")
            yield Label(
                f"Owner: {self.existing['owner']}, "
                f"Faction: {self.existing['faction']}, "
                f"Unit: {self.existing['unit']}"
            )
            with Horizontal():
                yield Button("Overwrite", variant="error", id="overwrite")
                yield Button("Skip", id="skip")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "overwrite":
            self.dismiss(True)
        else:
            self.dismiss(False)


class RegistryApp(App):
    CSS = """
    Screen { align: center middle; }
    #main { width: 80; height: auto; border: solid green; padding: 1 2; }
    #inputs { height: auto; }
    Input { margin: 1 0; }
    #status { text-align: center; color: yellow; }
    #log { height: 6; border: solid blue; }
    DataTable { height: 12; border: solid yellow; }
    Button { margin: 1; }
    """

    BINDINGS = [("q", "quit", "Quit")]

    owner = reactive("")
    faction = reactive("")
    unit = reactive("")
    status = reactive("🟡 Enter owner & faction, then click Ready")

    def __init__(self) -> None:
        super().__init__()
        self.registry = Registry(config.JSON_PATH)
        self.serial_queue: asyncio.Queue = asyncio.Queue()
        self.serial_reader = SerialReader(
            self.serial_queue,
            config.SERIAL_PORT,
            config.BAUD_RATE,
        )

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="main"):
            with Vertical(id="inputs"):
                yield Input(placeholder="Owner name", id="owner")
                yield Input(placeholder="Faction (free text)", id="faction")
                yield Input(placeholder="Unit name (per scan)", id="unit")
            with Horizontal():
                yield Button("✓ Ready to Scan", variant="success", id="ready")
                yield Button("💾 Save JSON", id="save")
                yield Button("Quit", variant="primary", id="quit")
            yield Static(self.status, id="status")
            yield DataTable(id="recent")
            yield Static(id="log")

    def on_mount(self) -> None:
        self.serial_reader.bind_loop(asyncio.get_running_loop())
        self.serial_reader.start()
        self.set_interval(config.POLL_INTERVAL, self.poll_serial)

        table = self.query_one("#recent", DataTable)
        table.add_columns("UUID", "Owner", "Faction", "Unit")
        self.update_recent_table()

    def watch_status(self, status: str) -> None:
        self.query_one("#status", Static).update(status)

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "owner":
            self.owner = event.value
        elif event.input.id == "faction":
            self.faction = event.value
        elif event.input.id == "unit":
            self.unit = event.value

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id == "ready":
            self.action_ready()
        elif btn_id == "save":
            self.action_save()
        elif btn_id == "quit":
            self.exit()

    def action_ready(self) -> None:
        if not self.owner or not self.faction:
            self.status = "🔴 Owner and faction are required!"
            return
        self.status = "🟢 Ready — scan a tag or type unit name & scan"
        self.query_one("#unit", Input).focus()

    def action_save(self) -> None:
        self.registry.save()
        self.status = "💾 Registry saved to JSON"
        self.log_event("💾 Manual save")

    def log_event(self, message: str) -> None:
        log = self.query_one("#log", Static)
        current = log.renderable.plain if log.renderable else ""
        lines = (current + "\n" + message).strip().split("\n")
        log.update("\n".join(lines[-6:]))

    def update_recent_table(self) -> None:
        table = self.query_one("#recent", DataTable)
        table.clear()
        # Show last 10, most recent first
        items = list(self.registry.all().items())
        for uuid, data in reversed(items[-10:]):
            table.add_row(uuid, data["owner"], data["faction"], data["unit"])

    async def poll_serial(self) -> None:
        try:
            uuid = self.serial_queue.get_nowait()
            await self.handle_uuid(uuid)
        except asyncio.QueueEmpty:
            pass

    async def handle_uuid(self, uuid: str) -> None:
        if not self.owner or not self.faction:
            self.status = f"🔴 Tag {uuid} scanned — set owner & faction first!"
            return

        unit_name = self.unit.strip()
        if not unit_name:
            self.status = f"🔴 Tag {uuid} scanned — enter a unit name!"
            self.query_one("#unit", Input).focus()
            return

        existing = self.registry.get(uuid)
        if existing:
            self.status = f"🟠 Duplicate: {uuid} — waiting for decision..."
            should_overwrite = await self.push_screen_wait(
                DuplicateModal(uuid, existing)
            )
            if not should_overwrite:
                self.status = "🟡 Skipped — ready for next scan"
                self.log_event(f"⊘ {uuid} skipped")
                return

        self.registry.set(uuid, self.owner, self.faction, unit_name)
        self.registry.save()
        self.status = f"✓ Saved: {uuid} → {unit_name}"
        self.log_event(f"{'↻' if existing else '✓'} {uuid}: {unit_name}")
        self.update_recent_table()

        # Clear unit name for next scan, keep owner/faction
        self.unit = ""
        self.query_one("#unit", Input).value = ""
        self.query_one("#unit", Input).focus()


if __name__ == "__main__":
    app = RegistryApp()
    app.run()