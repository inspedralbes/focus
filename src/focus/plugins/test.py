"""Test mode demonstration plugin."""

from focus.core.plugin_contract import PluginContext


def on_enter(context: PluginContext) -> None:
    context.logger.info("test on_enter")


def on_tick(context: PluginContext) -> None:
    context.logger.info("test on_tick")


def on_exit(context: PluginContext) -> None:
    context.logger.info("test on_exit")
