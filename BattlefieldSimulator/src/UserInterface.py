import logging

logger = logging.getLogger(__name__)

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, Static, Header, Footer

import mqtt_test  # Import the MQTT client setup from mqtt_test.py
class TurnCounter(App):

    CSS = """
    Screen {
        align: center middle;
    }

    #container {
        width: 40;
        height: auto;
        border: round cyan;
        padding: 1;
    }

    #counter {
        content-align: center middle;
        height: 3;
        border: round green;
        margin-bottom: 1;
        text-style: bold;
    }

    Button {
        margin-top: 1;
    }
    """

    BINDINGS = [
        ("up", "increment", "Increment"),
        ("down", "decrement", "Decrement"),
        ("r", "reset_counter", "Reset"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.mqtt_client = mqtt_test.create_mqtt_client()  # Initialize MQTT client
        self.mqtt_client.loop_start()  # Start the MQTT client loop
        self.turn = 0

    def __del__(self):
        self.mqtt_client.loop_stop()  # Stop the MQTT client loop when the app is closed

    def compose(self) -> ComposeResult:
        yield Header()

        with Vertical(id="container"):
            yield Static(f"Turn: {self.turn}", id="counter")

            yield Button("+ Increment Turn", id="increment")
            yield Button("- Decrement Turn", id="decrement")
            yield Button("Reset", id="reset")
            yield Button("Quit", id="quit")


        yield Footer()

    def update_counter(self):
        counter = self.query_one("#counter", Static)
        counter.update(f"Turn: {self.turn}")

    def on_button_pressed(self, event: Button.Pressed) -> None:

        button_id = event.button.id

        if button_id == "increment":
            self.turn += 1

        elif button_id == "decrement":
            self.turn -= 1

        elif button_id == "reset":
            self.turn = 0

        elif button_id == "quit":
            self.exit()


        self.update_counter()
        self.mqtt_client.publish("AWencyclopedia/turn", payload=str(self.turn), qos=1)  # Publish the current turn to MQTT

    # Keyboard shortcuts
    def action_increment(self):
        self.turn += 1
        self.update_counter()

    def action_decrement(self):
        self.turn -= 1
        self.update_counter()

    def action_reset_counter(self):
        self.turn = 0
        self.update_counter()


if __name__ == "__main__":
    logging.basicConfig(filename='UI.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    app = TurnCounter()
    app.run()
