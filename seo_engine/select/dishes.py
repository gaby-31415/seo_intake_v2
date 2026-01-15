"""Dish taxonomy building."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
import re
from typing import Dict, List, Optional
from urllib.parse import urlparse

_TRAILING_SUFFIX_RE = re.compile(
    r"-(?:[0-9]{6,}|[0-9a-f]{6,}|(?=[a-z0-9]*[0-9])[a-z0-9]{8,})$",
    re.IGNORECASE,
)


@dataclass
class DishMappingAudit:
    """Audit metrics for dish mapping."""

    unmapped: List[str] = field(default_factory=list)

    def record_unmapped(self, slug: str) -> None:
        """Record an unmapped dish slug."""

        self.unmapped.append(slug)


def normalize_dish_slug(slug: str) -> str:
    """Normalize dish slugs by stripping trailing numeric/hex suffixes."""

    normalized = slug.strip().lower()
    return _TRAILING_SUFFIX_RE.sub("", normalized)


def map_dish_slug(slug: str, audit: Optional[DishMappingAudit] = None) -> Optional[str]:
    """Map a dish slug to a taxonomy label."""

    normalized = normalize_dish_slug(slug)
    parts = normalized.split("-")
    if "ribs" in parts:
        return "ribs"
    if audit is not None:
        audit.record_unmapped(normalized)
    return None


def build_dish_taxonomy(item_urls: List[str]) -> Dict[str, List[Dict[str, List[str]]]]:
    """Build dish taxonomy from item URLs."""

    categories: Dict[str, List[str]] = defaultdict(list)
    for url in item_urls:
        path = urlparse(url).path
        parts = [part for part in path.split("/") if part]
        try:
            items_index = parts.index("items")
        except ValueError:
            continue
        category = parts[items_index + 1] if len(parts) > items_index + 1 else "uncategorized"
        item = parts[items_index + 2] if len(parts) > items_index + 2 else "unknown"
        categories[category].append(item)

    category_list = []
    for name in categories:
        category_list.append(
            {
                "name": name,
                "items": sorted(set(categories[name])),
            }
        )
    category_list.sort(
        key=lambda category: (-len(category["items"]), category["name"]),
    )

    return {"categories": category_list}
