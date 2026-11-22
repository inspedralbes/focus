"""Keep pytest's temporary files inside this writable checkout.

The test runner may use a different Windows account from the workspace owner.
A unique base directory per run avoids cross-account cleanup failures.
"""

import tempfile
from pathlib import Path


_temporary_directory = None


def pytest_configure(config):
    global _temporary_directory
    if config.option.basetemp is None:
        _temporary_directory = tempfile.TemporaryDirectory(
            prefix=".pytest_tmp_", dir=Path(__file__).resolve().parent
        )
        config.option.basetemp = _temporary_directory.name


def pytest_unconfigure(config):
    global _temporary_directory
    if _temporary_directory is not None:
        _temporary_directory.cleanup()
        _temporary_directory = None
