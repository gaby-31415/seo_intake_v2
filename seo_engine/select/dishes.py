"""Dish taxonomy building."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List
from urllib.parse import urlparse


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
    for name in sorted(categories):
        category_list.append(
            {
                "name": name,
                "items": sorted(set(categories[name])),
            }
        )

    return {"categories": category_list}
