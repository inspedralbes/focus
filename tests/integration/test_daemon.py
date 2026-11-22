import json
import threading
import time

from focus.core.daemon import Daemon
from focus.core.plugin_loader import PluginRegistry
from focus.core.state_manager import Phase, StateManager


class RecordingPlugin:
    def __init__(self, name, events):
        self.name, self.events = name, events

    def on_enter(self, context): self.events.append((self.name, "enter"))
    def on_exit(self, context): self.events.append((self.name, "exit"))
    def on_tick(self, context): self.events.append((self.name, "tick"))


def test_daemon_polls_ticks_and_stops(tmp_path):
    path = tmp_path / "state.json"
    path.write_text('{"state":"classe"}', encoding="utf-8")
    events = []
    registry = PluginRegistry({name: RecordingPlugin(name, events) for name in ("classe", "test", "practica")})
    daemon = Daemon(path, poll_interval=0.02, tick_interval=0.03, manager=StateManager(registry))
    thread = threading.Thread(target=daemon.run)
    thread.start()
    try:
        time.sleep(0.08)
        path.write_text('{"state":"test"}', encoding="utf-8")
        time.sleep(0.08)
    finally:
        daemon.stop()
        thread.join(timeout=1)
    assert not thread.is_alive()
    assert daemon.manager.phase is Phase.RUNNING
    assert ("classe", "enter") in events
    assert ("classe", "tick") in events
    assert events.index(("classe", "exit")) < events.index(("test", "enter"))
    assert ("test", "tick") in events


def test_long_tick_drops_missed_ticks(tmp_path):
    path = tmp_path / "state.json"
    path.write_text('{"state":"classe"}', encoding="utf-8")
    events = []
    class SlowPlugin(RecordingPlugin):
        def on_tick(self, context):
            events.append(time.monotonic())
            time.sleep(0.045)
    plugin = SlowPlugin("classe", events)
    daemon = Daemon(path, poll_interval=0.01, tick_interval=0.01,
                    manager=StateManager(PluginRegistry({"classe": plugin})))
    thread = threading.Thread(target=daemon.run)
    thread.start()
    time.sleep(0.16)
    daemon.stop()
    thread.join(timeout=1)
    ticks = [event for event in events if isinstance(event, float)]
    assert len(ticks) >= 2
    assert all(b - a >= 0.045 for a, b in zip(ticks, ticks[1:]))


def test_error_daemon_stays_alive_without_ticks(tmp_path):
    events = []
    daemon = Daemon(tmp_path / "missing.json", poll_interval=0.01, tick_interval=0.01)
    thread = threading.Thread(target=daemon.run)
    thread.start()
    time.sleep(0.05)
    assert thread.is_alive()
    assert daemon.manager.phase is Phase.ERROR
    daemon.stop()
    thread.join(timeout=1)
    assert not thread.is_alive()
