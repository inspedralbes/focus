"""Desired state parsing and sequential, conservative transitions."""

import json
import logging
from enum import Enum
from pathlib import Path

from .errors import StateError, PluginError
from .plugin_contract import Plugin, PluginContext
from .plugin_loader import PluginRegistry, STATES


class Phase(Enum):
    RUNNING = "RUNNING"
    TRANSITIONING = "TRANSITIONING"
    ERROR = "ERROR"


def read_state(path: Path) -> str:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise StateError(f"Cannot read valid state from {path}") from exc
    if not isinstance(data, dict) or set(data) != {"state"} or data["state"] not in STATES:
        raise StateError(f"Invalid state in {path}")
    return data["state"]


class StateManager:
    def __init__(
        self,
        registry: PluginRegistry | None = None,
        logger: logging.Logger | None = None,
        degraded_threshold: int = 5,
    ) -> None:
        if degraded_threshold < 1:
            raise ValueError("degraded_threshold must be positive")
        self.registry = registry or PluginRegistry()
        self.logger = logger or logging.getLogger("focus")
        self.degraded_threshold = degraded_threshold
        self.phase = Phase.ERROR
        self.active_state: str | None = None
        self._plugin: Plugin | None = None
        self.actual_state_verified = False
        self.consecutive_tick_errors = 0
        self.degraded = False
        self.failure_policy = "preserve"

    def _context(self, plugin_state: str, target: str | None) -> PluginContext:
        return PluginContext(self.active_state, target, self.logger.getChild(plugin_state))

    def _error(self, reason: str) -> None:
        self.phase = Phase.ERROR
        self.actual_state_verified = False
        self.logger.error("entered ERROR: %s", reason)

    def start(self, path: Path) -> None:
        try:
            state = read_state(path)
            plugin = self.registry.load(state)
            plugin.on_enter(self._context(state, state))
        except Exception as exc:
            self.logger.error("startup failed state=%s plugin=%s hook=on_enter exception=%s", locals().get("state"), locals().get("state"), type(exc).__name__)
            self._error("startup failed")
            return
        self.active_state, self._plugin = state, plugin
        self.actual_state_verified = True
        self.phase = Phase.RUNNING
        self.logger.info("startup succeeded state=%s", state)

    def transition(self, target: str) -> bool:
        source = self.active_state
        if self.phase is not Phase.RUNNING:
            self.logger.warning("transition rejected source=%s target=%s phase=%s", source, target, self.phase.value)
            return False
        if target == source:
            return True
        try:
            target_plugin = self.registry.load(target)
        except PluginError as exc:
            self.logger.error("transition rejected source=%s target=%s plugin=%s: %s", source, target, target, exc)
            return False
        assert source is not None and self._plugin is not None
        self.phase = Phase.TRANSITIONING
        try:
            self._plugin.on_exit(self._context(source, target))
        except Exception as exc:
            self.logger.error("transition failed source=%s target=%s plugin=%s hook=on_exit exception=%s", source, target, source, type(exc).__name__)
            self._restore(source, target)
            return False
        try:
            target_plugin.on_enter(self._context(target, target))
        except Exception as exc:
            self.logger.error("transition failed source=%s target=%s plugin=%s hook=on_enter exception=%s", source, target, target, type(exc).__name__)
            self._restore(source, target)
            return False
        self.active_state, self._plugin = target, target_plugin
        self.phase = Phase.RUNNING
        self.actual_state_verified = True
        self.consecutive_tick_errors = 0
        self.degraded = False
        self.logger.info("transition succeeded source=%s target=%s", source, target)
        return True

    def _restore(self, source: str, target: str) -> None:
        self.actual_state_verified = False
        try:
            assert self._plugin is not None
            self._plugin.on_enter(self._context(source, source))
        except Exception as exc:
            self.logger.error("recovery failed source=%s target=%s plugin=%s hook=on_enter exception=%s", source, target, source, type(exc).__name__)
            self._error("recovery failed")
            return
        self.phase = Phase.RUNNING
        self.actual_state_verified = True
        self.logger.warning("recovery succeeded source=%s target=%s", source, target)

    def poll(self, path: Path) -> None:
        if self.phase is not Phase.RUNNING:
            return
        try:
            target = read_state(path)
        except StateError as exc:
            self.logger.error("state read rejected path=%s: %s", path, exc)
            return
        self.transition(target)

    def tick(self) -> None:
        if self.phase is not Phase.RUNNING:
            return
        assert self.active_state is not None and self._plugin is not None
        try:
            self._plugin.on_tick(self._context(self.active_state, None))
        except Exception as exc:
            self.consecutive_tick_errors += 1
            self.actual_state_verified = False
            self.logger.error("tick failed state=%s plugin=%s hook=on_tick exception=%s", self.active_state, self.active_state, type(exc).__name__)
            if self.consecutive_tick_errors >= self.degraded_threshold and not self.degraded:
                self.degraded = True
                self.logger.critical("plugin DEGRADED state=%s consecutive_tick_errors=%d", self.active_state, self.consecutive_tick_errors)
            return
        self.consecutive_tick_errors = 0
        self.degraded = False
