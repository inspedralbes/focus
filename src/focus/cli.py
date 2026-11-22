"""Atomically request a new desired state."""

import argparse
import json
import os
import tempfile
from pathlib import Path

from .core.plugin_loader import STATES


def write_state(path: Path, state: str) -> None:
    if state not in STATES:
        raise ValueError(f"Unknown state: {state!r}")
    path = Path(path)
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=f".{path.name}.", suffix=".tmp", delete=False) as stream:
            temporary = stream.name
            json.dump({"state": state}, stream)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and os.path.exists(temporary):
            os.unlink(temporary)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Request a FOCUS state")
    parser.add_argument("state", choices=STATES)
    parser.add_argument("--state-file", type=Path, default=Path("config/state.json"))
    args = parser.parse_args(argv)
    try:
        write_state(args.state_file, args.state)
    except OSError as exc:
        parser.exit(1, f"Cannot update state: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
