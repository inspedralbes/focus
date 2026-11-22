"""Synchronous plugin contract."""

from dataclasses import dataclass
from logging import Logger
from typing import Protocol


@dataclass(frozen=True)
class PluginContext:
    current_state: str | None
    target_state: str | None
    logger: Logger


class Plugin(Protocol):
    def on_enter(self, context: PluginContext) -> None: ...

    def on_tick(self, context: PluginContext) -> None: ...

    def on_exit(self, context: PluginContext) -> None: ...
