"""Errors for state and plugin validation."""


class StateError(ValueError):
    """The desired state file is missing or invalid."""


class PluginError(ValueError):
    """A state has no valid plugin."""
