"""Stable JSON helpers for deterministic artifacts."""

from __future__ import annotations

import json
from typing import Any


def json_dumps_stable(obj: Any) -> str:
    """Serialize JSON with deterministic formatting."""

    return json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=2)


def json_dump_stable(obj: Any, path: str) -> None:
    """Write JSON to disk with deterministic formatting and newline."""

    with open(path, "w", encoding="utf-8") as handle:
        handle.write(json_dumps_stable(obj))
        handle.write("\n")


def json_load(path: str) -> Any:
    """Load JSON from disk."""

    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)
