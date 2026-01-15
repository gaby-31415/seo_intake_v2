"""Core page selection logic."""

from __future__ import annotations

from typing import Dict, List

CORE_KEYWORDS = {
    "/menu": "Menu",
    "/private-events": "Private Events",
    "/locations": "Locations",
    "/about": "About",
}


def rank_core_pages(urls: List[str]) -> List[Dict[str, str]]:
    """Rank core pages based on known path keywords."""

    ranked: List[Dict[str, str]] = []
    for url in urls:
        label = "Other"
        for path, name in CORE_KEYWORDS.items():
            if path in url:
                label = name
                break
        ranked.append({"url": url, "label": label})
    return ranked
