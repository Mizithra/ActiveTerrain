import logging
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, Footer, Header, Log, Static

from battlefieldengine import mqtt_client as mqtt_client_module
from battlefieldengine.mqtt_adapter import MQTTAdapter
from battlefieldengine.Battlefield import TOPIC_COMMAND, TOPIC_TURN_STATE, TOPIC_UNIT_EVENT
from RegistryManager import RegistryManager
from RegistrationScreen import RegistrationScreen

REGISTRATION_OBJECTIVE_TOPIC = "battlefield/terrain/registration"
REGISTER_START_TOPIC = f"{REGISTRATION_OBJECTIVE_TOPIC}/register_start"
REGISTER_RESULT_TOPIC = f"{REGISTRATION_OBJECTIVE_TOPIC}/register_result"
REGISTER_END_TOPIC = f"{REGISTRATION_OBJECTIVE_TOPIC}/register_end"

logger = logging.getLogger(__name__)


# Use the backend configurations folder so registrations are saved where the server reads them
UNITS_PATH = Path("battlefieldengine/battlefieldengine/configurations/Units.json")
TAGS_PATH = Path("battlefieldengine/battlefieldengine/configurations/TagAssignments.json")
UNIT_REGISTRY_EXPORT = Path("battlefieldengine/battlefieldengine/configurations/UnitRegistry.json")


class BattlefieldUI(App):
    """Thin client: publishes turn/phase commands, displays whatever global
    state Battlefield broadcasts back, logs unit events (now tagged with
    which terrain marker they happened at), and can open Registration mode.
    Holds no game state of its own -- Battlefield is the source of truth.
    """

    CSS = """
    Screen {
        align: center middle;
    }
    #container {
        width: 56;
        height: auto;
        border: round cyan;
        padding: 1;
    }
    #status {
        content-align: center middle;
        height: 3;
        border: round green;
        margin-bottom: 1;
        text-style: bold;
    }
    #event_log {
        height: 10;
        margin-top: 1;
        border: round grey;
    }
    Button {
        margin-top: 1;
    }
    """

    BINDINGS = [
        ("n", "next_phase", "Next Phase"),
        ("t", "increment_turn", "New Turn"),
        ("g", "open_registration", "Registration"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        raw_client = mqtt_client_module.create_mqtt_client()
        raw_client.loop_start()
        self.mqtt = MQTTAdapter(raw_client)
        self.turn = 1
        self.phase = "command"
        self.registry = RegistryManager(UNITS_PATH, TAGS_PATH, UNIT_REGISTRY_EXPORT)

    def on_mount(self) -> None:
        self.mqtt.subscribe(TOPIC_TURN_STATE, self._on_turn_state)
        self.mqtt.subscribe(TOPIC_UNIT_EVENT, self._on_unit_event)

    def on_unmount(self) -> None:
        self.mqtt.loop_stop()

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="container"):
            yield Static(self._status_text(), id="status")
            yield Button("Next Phase (n)", id="next_phase")
            yield Button("New Turn (t)", id="new_turn")
            yield Button("Registration (g)", id="registration")
            yield Log(id="event_log", max_lines=10)
        yield Footer()

    def _status_text(self) -> str:
        return f"Turn {self.turn} \u2014 {self.phase.title()}"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "next_phase":
            self.action_next_phase()
        elif event.button.id == "new_turn":
            self.action_increment_turn()
        elif event.button.id == "registration":
            self.action_open_registration()

    def action_next_phase(self) -> None:
        self.mqtt.publish(TOPIC_COMMAND, {"action": "next_phase"})

    def action_increment_turn(self) -> None:
        self.mqtt.publish(TOPIC_COMMAND, {"action": "increment_turn"})

    def action_open_registration(self) -> None:
        self.push_screen(
            RegistrationScreen(
                self.mqtt,
                self.registry,
                REGISTER_START_TOPIC,
                REGISTER_RESULT_TOPIC,
                REGISTER_END_TOPIC,
            )
        )

    # --- MQTT inbound: fires on the network thread, marshal via call_from_thread
    def _on_turn_state(self, topic: str, payload: dict) -> None:
        self.turn = payload.get("turn", self.turn)
        self.phase = payload.get("phase", self.phase)
        self.call_from_thread(self._refresh_status)

    def _on_unit_event(self, topic: str, payload: dict) -> None:
        name = payload.get("name", "Unknown unit")
        event = payload.get("event", "event")
        terrain = payload.get("terrain")
        text = f"{name}: {event}" + (f" @ {terrain}" if terrain else "")
        self.call_from_thread(self._log_event, text)

    def _refresh_status(self) -> None:
        self.query_one("#status", Static).update(self._status_text())

    def _log_event(self, text: str) -> None:
        self.query_one("#event_log", Log).write_line(text)


if __name__ == "__main__":
    logging.basicConfig(
        filename="UI.log",
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    app = BattlefieldUI()
    app.run()
