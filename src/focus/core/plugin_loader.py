"""Resolve and validate the fixed set of initial plugins."""

from importlib import import_module
from typing import Mapping

from .errors import PluginError
from .plugin_contract import Plugin

STATES = ("classe", "test", "practica")


class PluginRegistry:
    def __init__(self, plugins: Mapping[str, Plugin] | None = None) -> None:
        self._plugins = dict(plugins) if plugins is not None else None

    def load(self, state: str) -> Plugin:
        if state not in STATES:
            raise PluginError(f"Unknown state: {state!r}")
        try:
            plugin = self._plugins[state] if self._plugins is not None else import_module(f"focus.plugins.{state}")
        except (KeyError, ImportError) as exc:
            raise PluginError(f"Cannot load plugin for {state!r}") from exc
        for hook in ("on_enter", "on_tick", "on_exit"):
            if not callable(getattr(plugin, hook, None)):
                raise PluginError(f"Plugin {state!r} lacks callable {hook}")
        return plugin
