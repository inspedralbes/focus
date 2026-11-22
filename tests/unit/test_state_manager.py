import json
import logging

import pytest

from focus.core.errors import StateError, PluginError
from focus.core.plugin_loader import PluginRegistry
from focus.core.state_manager import Phase, StateManager, read_state


class FakePlugin:
    def __init__(self, name, events):
        self.name, self.events = name, events
        self.fail = set()

    def _call(self, hook, context):
        self.events.append((self.name, hook, context.current_state, context.target_state))
        if hook in self.fail:
            raise RuntimeError(f"{self.name} {hook} secret-password")

    def on_enter(self, context): self._call("on_enter", context)
    def on_tick(self, context): self._call("on_tick", context)
    def on_exit(self, context): self._call("on_exit", context)


@pytest.fixture
def setup(tmp_path):
    path = tmp_path / "state.json"
    path.write_text('{"state":"classe"}', encoding="utf-8")
    events = []
    plugins = {name: FakePlugin(name, events) for name in ("classe", "test", "practica")}
    manager = StateManager(PluginRegistry(plugins))
    return path, events, plugins, manager


def test_read_state_rejects_missing_malformed_and_unknown(tmp_path):
    path = tmp_path / "state.json"
    with pytest.raises(StateError): read_state(path)
    for content in ('{', '{"state":"other"}', '{"state":"classe","extra":1}', '[]'):
        path.write_text(content, encoding="utf-8")
        with pytest.raises(StateError): read_state(path)


def test_plugin_contract_is_validated_before_exit(setup):
    path, events, plugins, manager = setup
    manager.start(path)
    plugins["test"].on_enter = None
    assert not manager.transition("test")
    assert events == [("classe", "on_enter", None, "classe")]
    assert manager.active_state == "classe"
    with pytest.raises(PluginError): manager.registry.load("unknown")


def test_order_commit_and_noop(setup):
    path, events, plugins, manager = setup
    manager.start(path)
    assert manager.phase is Phase.RUNNING
    assert manager.transition("classe")
    assert manager.transition("test")
    assert [e[:2] for e in events] == [("classe", "on_enter"), ("classe", "on_exit"), ("test", "on_enter")]
    assert manager.active_state == "test"
    assert manager.actual_state_verified


def test_bad_read_preserves_active_state(setup, caplog):
    path, events, plugins, manager = setup
    manager.start(path)
    path.write_text("{", encoding="utf-8")
    manager.poll(path)
    assert manager.active_state == "classe"
    assert len(events) == 1
    assert "state read rejected" in caplog.text


@pytest.mark.parametrize("failed_hook", ["on_exit", "on_enter"])
def test_transition_failure_restores_source(setup, failed_hook, caplog):
    path, events, plugins, manager = setup
    manager.start(path)
    plugins["classe" if failed_hook == "on_exit" else "test"].fail.add(failed_hook)
    assert not manager.transition("test")
    assert manager.active_state == "classe"
    assert manager.phase is Phase.RUNNING
    assert manager.actual_state_verified
    assert events[-1][:2] == ("classe", "on_enter")
    if failed_hook == "on_exit":
        assert not any(e[:2] == ("test", "on_enter") for e in events)
    assert "recovery succeeded" in caplog.text


def test_failed_recovery_enters_error_and_rejects_work(setup):
    path, events, plugins, manager = setup
    manager.start(path)
    plugins["classe"].fail.add("on_enter")
    plugins["test"].fail.add("on_enter")
    assert not manager.transition("test")
    before = len(events)
    assert manager.phase is Phase.ERROR
    assert not manager.actual_state_verified
    assert not manager.transition("practica")
    manager.tick()
    manager.poll(path)
    assert len(events) == before
    assert manager.failure_policy == "preserve"


def test_startup_failures_enter_error(setup):
    path, events, plugins, manager = setup
    path.unlink()
    manager.start(path)
    assert manager.phase is Phase.ERROR
    assert manager.active_state is None
    path.write_text('{"state":"classe"}', encoding="utf-8")
    plugins["classe"].fail.add("on_enter")
    manager.start(path)
    assert manager.phase is Phase.ERROR
    assert manager.active_state is None


def test_tick_retries_degrades_and_resets(setup, caplog):
    path, events, plugins, manager = setup
    manager.start(path)
    plugins["classe"].fail.add("on_tick")
    for _ in range(5): manager.tick()
    assert manager.phase is Phase.RUNNING
    assert manager.degraded
    assert manager.consecutive_tick_errors == 5
    assert not manager.actual_state_verified
    assert "DEGRADED" in caplog.text
    plugins["classe"].fail.clear()
    manager.tick()
    assert not manager.degraded
    assert manager.consecutive_tick_errors == 0


def test_logging_contains_context_without_state_file_contents(setup, caplog):
    path, events, plugins, manager = setup
    manager.start(path)
    plugins["test"].fail.add("on_enter")
    with caplog.at_level(logging.INFO): manager.transition("test")
    assert "source=classe target=test plugin=test hook=on_enter" in caplog.text
    assert "recovery succeeded" in caplog.text
    assert "secret-password" not in caplog.text
