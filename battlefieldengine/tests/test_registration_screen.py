import importlib.util
import sys
from types import SimpleNamespace
from pathlib import Path


def _load_registration_screen_module():
    repo_root = Path(__file__).resolve().parents[1] / ".."
    console_ui_dir = (repo_root / "console_ui").resolve()
    sys.path.insert(0, str(console_ui_dir))
    module_path = console_ui_dir / "RegistrationScreen.py"
    spec = importlib.util.spec_from_file_location("registration_screen", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_registration_screen_marshals_mqtt_callback_to_app():
    module = _load_registration_screen_module()
    screen = module.RegistrationScreen(
        SimpleNamespace(), SimpleNamespace(), "topic/start", "topic/result", "topic/end"
    )
    captured = {}

    def fake_handle_scan_result(payload):
        captured["payload"] = payload

    screen._handle_scan_result = fake_handle_scan_result
    object.__setattr__(screen, "_app", SimpleNamespace(call_from_thread=lambda callback, payload: callback(payload)))

    screen._on_scan_result("topic/result", {"uid": "ABC"})

    assert captured["payload"] == {"uid": "ABC"}


def test_registration_screen_handles_callback_without_attached_app():
    module = _load_registration_screen_module()
    screen = module.RegistrationScreen(
        SimpleNamespace(), SimpleNamespace(), "topic/start", "topic/result", "topic/end"
    )
    captured = {}

    def fake_handle_scan_result(payload):
        captured["payload"] = payload

    screen._handle_scan_result = fake_handle_scan_result
    object.__setattr__(screen, "_app", None)

    screen._on_scan_result("topic/result", {"uid": "DEF"})

    assert captured["payload"] == {"uid": "DEF"}


def test_registration_screen_sends_end_message_on_finish():
    module = _load_registration_screen_module()
    published = {}

    class FakeMqtt:
        def publish(self, topic, payload):
            published["topic"] = topic
            published["payload"] = payload

    screen = module.RegistrationScreen(
        FakeMqtt(), SimpleNamespace(save=lambda: None), "topic/start", "topic/result", "topic/end"
    )
    object.__setattr__(screen, "_app", SimpleNamespace(pop_screen=lambda: None))

    screen.action_finish()

    assert published["topic"] == "topic/end"
    assert published["payload"] == {"action": "end"}
