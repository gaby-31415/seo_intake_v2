"""Artifact schemas for SEO intake outputs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class SiteFacts:
    """Basic facts about the site."""

    domain: str | None = None
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable dict."""

        return asdict(self)


@dataclass
class Locations:
    """Extracted location data."""

    locations: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable dict."""

        return asdict(self)


@dataclass
class CorePages:
    """Core page URLs identified from the sitemap."""

    urls: List[Dict[str, Any]] = field(default_factory=list)
    excluded: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable dict."""

        return asdict(self)


@dataclass
class DishTaxonomy:
    """Dish taxonomy extracted from HTML."""

    dishes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable dict."""

        return asdict(self)


@dataclass
class AhrefsSummary:
    """Placeholder for Ahrefs summary data."""

    overview: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable dict."""

        return asdict(self)
