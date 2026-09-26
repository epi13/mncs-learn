"""Atomic JSON persistence for learned artifacts and evaluations.

Learn owns the semantic structure of what is stored; durability itself
is plain atomic files (write temp + fsync + rename) under a state dir.
No database, no pickle: artifacts are inspectable JSON by construction.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any


def ensure(state_dir: str | Path) -> dict[str, Path]:
    root = Path(state_dir)
    paths = {"root": root, "artifacts": root / "artifacts",
             "evaluations": root / "evaluations"}
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def write_json(path: Path, document: Any) -> None:
    path = Path(path)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(document, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def read_json(path: Path) -> Any:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)
