"""Whitelist-only categories; keep lists conservative; add categories not ingredients."""

from __future__ import annotations

from typing import Dict, Tuple

MARKETING: Tuple[str, ...] = (
    "award",
    "winning",
    "signature",
)
PREP: Tuple[str, ...] = (
    "grilled",
    "fried",
    "crispy",
    "smoked",
)
INGREDIENTS: Tuple[str, ...] = (
    "ahi",
    "tuna",
    "guacamole",
)
BEV: Tuple[str, ...] = (
    "beer",
    "cocktail",
    "soda",
    "wine",
)

CATEGORY_MAP: Dict[str, Tuple[str, ...]] = {
    "ribs": ("ribs",),
}
