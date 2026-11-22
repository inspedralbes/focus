"""Single-threaded polling loop; hooks never overlap."""

import logging
import threading
import time
from pathlib import Path

from .state_manager import Phase, StateManager


class Daemon:
    def __init__(
        self,
        state_path: Path,
        *,
        poll_interval: float = 0.5,
        tick_interval: float = 3.0,
        manager: StateManager | None = None,
    ) -> None:
        if poll_interval <= 0 or tick_interval <= 0:
            raise ValueError("intervals must be positive")
        self.state_path = Path(state_path)
        self.poll_interval = poll_interval
        self.tick_interval = tick_interval
        self.manager = manager or StateManager()
        self._stop = threading.Event()
        self.logger = logging.getLogger("focus")

    def stop(self) -> None:
        self._stop.set()

    def run(self) -> None:
        self.logger.info("daemon starting path=%s", self.state_path)
        try:
            self.manager.start(self.state_path)
            now = time.monotonic()
            next_poll = now + self.poll_interval
            next_tick = now + self.tick_interval
            while not self._stop.is_set():
                now = time.monotonic()
                if now >= next_poll:
                    if self.manager.phase is Phase.RUNNING:
                        self.manager.poll(self.state_path)
                    next_poll = time.monotonic() + self.poll_interval
                now = time.monotonic()
                if now >= next_tick:
                    if self.manager.phase is Phase.RUNNING:
                        self.manager.tick()
                    next_tick = time.monotonic() + self.tick_interval
                self._stop.wait(max(0, min(next_poll, next_tick) - time.monotonic()))
        finally:
            self.logger.info("daemon stopped phase=%s", self.manager.phase.value)
