import json
import logging
from typing import Callable

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, Footer, Header, Log, Static

import battlefield_sim.mqtt_client as mqtt_client_module
from battlefield_sim.Battlefield import TOPIC_COMMAND, TOPIC_TURN_STATE, TOPIC_UNIT_EVENT

logger = logging.getLogger(__name__)


class MQTTAdapter:
    """Wraps a raw paho-mqtt client so it matches the publish(topic, dict) /
    subscribe(topic, callback) interface Battlefield expects. If your
    mqtt_client.py already does this, skip this class and pass your client
    straight through instead.
    """

    def __init__(self, client, qos: int = 1):
        self._client = client
        self._qos = qos
        self._callbacks: dict[str, Callable[[str, dict], None]] = {}
        self._client.on_message = self._on_message

    def publish(self, topic: str, payload: dict) -> None:
        self._client.publish(topic, json.dumps(payload), qos=self._qos)

    def subscribe(self, topic: str, callback: Callable[[str, dict], None]) -> None:
        self._callbacks[topic] = callback
        self._client.subscribe(topic)

    def _on_message(self, client, userdata, msg) -> None:
        callback = self._callbacks.get(msg.topic)
        if not callback:
            return
        try:
            payload = json.loads(msg.payload.decode())
        except (UnicodeDecodeError, json.JSONDecodeError):
            logger.warning("Non-JSON payload on %s: %r", msg.topic, msg.payload)
            return
        callback(msg.topic, payload)

    def loop_stop(self) -> None:
        self._client.loop_stop()


class BattlefieldUI(App):
    """Thin client: publishes turn/phase commands, displays whatever state
    Battlefield broadcasts back, and logs unit arrival/departure events.
    Holds no game state of its own — Battlefield is the source of truth.
    """

    CSS = """
    Screen {
        align: center middle;
    }
    #container {
        width: 50;
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
        height: 8;
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
        ("q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        raw_client = mqtt_client_module.create_mqtt_client()
        raw_client.loop_start()
        self.mqtt = MQTTAdapter(raw_client)
        self.turn = 1
        self.phase = "command"

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
            yield Log(id="event_log", max_lines=8)
        yield Footer()

    def _status_text(self) -> str:
        return f"Turn {self.turn} \u2014 {self.phase.title()}"

    # --- user actions: publish commands, don't mutate local state ------
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "next_phase":
            self.action_next_phase()
        elif event.button.id == "new_turn":
            self.action_increment_turn()

    def action_next_phase(self) -> None:
        self.mqtt.publish(TOPIC_COMMAND, {"action": "next_phase"})

    def action_increment_turn(self) -> None:
        self.mqtt.publish(TOPIC_COMMAND, {"action": "increment_turn"})

    # --- MQTT inbound: these fire on the network thread, so marshal
    # updates back onto the app via call_from_thread before touching widgets
    def _on_turn_state(self, topic: str, payload: dict) -> None:
        self.turn = payload.get("turn", self.turn)
        self.phase = payload.get("phase", self.phase)
        self.call_from_thread(self._refresh_status)

    def _on_unit_event(self, topic: str, payload: dict) -> None:
        name = payload.get("name", "Unknown unit")
        event = payload.get("event", "event")
        self.call_from_thread(self._log_event, f"{name}: {event}")

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