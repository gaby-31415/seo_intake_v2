"""Render clipboard payload for the pipeline."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple


def _collect_unknown_tokens(dish_taxonomy: Optional[Dict[str, Any]]) -> List[Tuple[str, Optional[int]]]:
    if not dish_taxonomy:
        return []
    audit = dish_taxonomy.get("audit", {})
    tokens = audit.get("top_unknown_tokens", [])
    collected: List[Tuple[str, Optional[int]]] = []
    if isinstance(tokens, dict):
        for token, count in tokens.items():
            collected.append((str(token), int(count) if count is not None else None))
        return collected
    if isinstance(tokens, Sequence) and not isinstance(tokens, (str, bytes)):
        for entry in tokens:
            if isinstance(entry, dict):
                token = entry.get("token")
                count = entry.get("count")
                if token:
                    collected.append((str(token), int(count) if count is not None else None))
            elif isinstance(entry, (list, tuple)) and len(entry) >= 2:
                token, count = entry[0], entry[1]
                if token:
                    collected.append((str(token), int(count) if count is not None else None))
            elif isinstance(entry, str):
                collected.append((entry, None))
    return collected


def render_clipboard(
    locations: List[Dict[str, Any]],
    core_pages: List[Dict[str, Any]],
    dish_categories: List[Dict[str, Any]],
    ahrefs_snapshot: Dict[str, Any],
    dish_taxonomy: Optional[Dict[str, Any]] = None,
    include_unknown_tokens: bool = False,
) -> str:
    """Render a simple clipboard package text."""

    lines = ["SEO Intake Summary"]
    lines.append("Locations:")
    for location in locations:
        lines.append(f"- {location.get('location_name') or location.get('name', '')}")
    lines.append("Core Pages:")
    for page in core_pages:
        lines.append(f"- {page.get('url', '')}")
    lines.append("Dish Categories:")
    if dish_categories:
        for category in dish_categories:
            label = category.get("category", "")
            count = category.get("count")
            if label:
                if count is None:
                    lines.append(f"- {label}")
                else:
                    lines.append(f"- {label} ({count})")
    else:
        lines.append("No dish categories mapped (strict mode)")
    lines.append("Ahrefs Snapshot:")
    lines.append(str(ahrefs_snapshot))
    if include_unknown_tokens:
        unknown_tokens = _collect_unknown_tokens(dish_taxonomy)
        if unknown_tokens:
            lines.append("DISH UNKNOWN TOKENS (for tuning)")
            for token, count in unknown_tokens:
                if count is None:
                    lines.append(f"- {token}")
                else:
                    lines.append(f"- {token}: {count}")
    return "\n".join(lines)
