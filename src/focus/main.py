"""Daemon entry point."""

import argparse
import signal
from pathlib import Path

from .core.daemon import Daemon
from .core.logging_config import configure_logging
from .core.state_manager import StateManager


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the local FOCUS daemon")
    parser.add_argument("--state-file", type=Path, default=Path("config/state.json"))
    parser.add_argument("--poll-interval", type=float, default=0.5)
    parser.add_argument("--tick-interval", type=float, default=3.0)
    parser.add_argument("--degraded-threshold", type=int, default=5)
    args = parser.parse_args(argv)
    if args.poll_interval <= 0 or args.tick_interval <= 0 or args.degraded_threshold < 1:
        parser.error("intervals and degraded threshold must be positive")
    logger = configure_logging()
    daemon = Daemon(args.state_file, poll_interval=args.poll_interval, tick_interval=args.tick_interval,
                    manager=StateManager(logger=logger, degraded_threshold=args.degraded_threshold))
    def stop_handler(signum: int, frame: object) -> None:
        logger.info("shutdown requested signal=%s", signum)
        daemon.stop()
    signal.signal(signal.SIGINT, stop_handler)
    signal.signal(signal.SIGTERM, stop_handler)
    daemon.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
