"""Render clipboard payload for the pipeline."""

from __future__ import annotations

from typing import Any, Dict, List


def render_clipboard(
    locations: List[Dict[str, Any]],
    core_pages: List[Dict[str, Any]],
    dish_categories: List[Dict[str, Any]],
    ahrefs_snapshot: Dict[str, Any],
) -> str:
    """Render a simple clipboard package text."""

    lines = ["SEO Intake Summary"]
    lines.append("Locations:")
    for location in locations:
        lines.append(f"- {location.get('name', '')}")
    lines.append("Core Pages:")
    for page in core_pages:
        lines.append(f"- {page.get('url', '')}")
    lines.append("Dish Categories:")
    for category in dish_categories:
        lines.append(f"- {category.get('name', '')}")
    lines.append("Ahrefs Snapshot:")
    lines.append(str(ahrefs_snapshot))
    return "\n".join(lines)
