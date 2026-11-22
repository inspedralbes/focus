import json
import signal

from focus import main
from focus.cli import write_state
from focus.core.plugin_loader import PluginRegistry
from focus.core.state_manager import StateManager


class Plugin:
    def __init__(self, name, events):
        self.name, self.events = name, events
    def on_enter(self, context): self.events.append((self.name, "enter"))
    def on_tick(self, context): self.events.append((self.name, "tick"))
    def on_exit(self, context): self.events.append((self.name, "exit"))


def test_full_state_sequence_through_cli_file(tmp_path):
    path = tmp_path / "state.json"
    events = []
    manager = StateManager(PluginRegistry({name: Plugin(name, events) for name in ("classe", "test", "practica")}))
    write_state(path, "classe")
    manager.start(path)
    for state in ("test", "practica", "classe"):
        write_state(path, state)
        manager.poll(path)
    assert events == [
        ("classe", "enter"), ("classe", "exit"), ("test", "enter"),
        ("test", "exit"), ("practica", "enter"), ("practica", "exit"),
        ("classe", "enter"),
    ]


def test_main_registers_signals_and_requests_shutdown(monkeypatch):
    handlers = {}
    class FakeDaemon:
        def __init__(self, *args, **kwargs): self.stopped = False
        def stop(self): self.stopped = True
        def run(self):
            handlers[signal.SIGTERM](signal.SIGTERM, None)
            assert self.stopped
    monkeypatch.setattr(main, "Daemon", FakeDaemon)
    monkeypatch.setattr(main.signal, "signal", lambda number, handler: handlers.setdefault(number, handler))
    assert main.main([]) == 0
    assert signal.SIGINT in handlers
    assert signal.SIGTERM in handlers
