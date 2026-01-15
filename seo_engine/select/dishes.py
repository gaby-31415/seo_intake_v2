"""Dish taxonomy building."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
import re
from typing import Dict, Iterable, List, Optional, Set, Tuple
from urllib.parse import urlparse

from seo_engine.select.dish_lexicon import BEV, CATEGORY_MAP, INGREDIENTS, MARKETING, PREP

_TRAILING_SUFFIX_RE = re.compile(
    r"-(?:[0-9]{6,}|[0-9a-f]{6,}|(?=[a-z0-9]*[0-9])[a-z0-9]{8,})$",
    re.IGNORECASE,
)


@dataclass
class DishMappingAudit:
    """Audit metrics for dish mapping."""

    unmapped: List[str] = field(default_factory=list)
    mapped: List[str] = field(default_factory=list)
    unknown_token_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

    def record_mapped(self, slug: str) -> None:
        """Record a mapped dish slug."""

        self.mapped.append(slug)

    def record_unmapped(
        self,
        slug: str,
        *,
        tokens: Optional[Iterable[str]] = None,
        known_tokens: Optional[Set[str]] = None,
    ) -> None:
        """Record an unmapped dish slug."""

        self.unmapped.append(slug)
        if tokens is None or known_tokens is None:
            return
        for token in tokens:
            if token not in known_tokens:
                self.unknown_token_counts[token] += 1

    def top_unknown_tokens(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Return the most common unknown tokens deterministically."""

        return sorted(
            self.unknown_token_counts.items(),
            key=lambda item: (-item[1], item[0]),
        )[:limit]


def normalize_dish_slug(slug: str) -> str:
    """Normalize dish slugs by stripping trailing numeric/hex suffixes."""

    normalized = slug.strip().lower()
    return _TRAILING_SUFFIX_RE.sub("", normalized)


def _tokenize_slug(slug: str) -> List[str]:
    """Split a normalized slug into tokens."""

    return [part for part in slug.split("-") if part]


_CATEGORY_TOKENS = {token for tokens in CATEGORY_MAP.values() for token in tokens}
_NON_CATEGORY_TOKENS = set(MARKETING) | set(PREP) | set(INGREDIENTS) | set(BEV)
_KNOWN_TOKENS = _NON_CATEGORY_TOKENS | _CATEGORY_TOKENS


def map_dish_slug(slug: str, audit: Optional[DishMappingAudit] = None) -> Optional[str]:
    """Map a dish slug to a taxonomy label."""

    normalized = normalize_dish_slug(slug)
    tokens = _tokenize_slug(normalized)
    if tokens and all(token in _NON_CATEGORY_TOKENS for token in tokens):
        if audit is not None:
            audit.record_unmapped(normalized, tokens=tokens, known_tokens=_KNOWN_TOKENS)
        return None

    for category, category_tokens in sorted(CATEGORY_MAP.items()):
        if any(token in category_tokens for token in tokens):
            if audit is not None:
                audit.record_mapped(normalized)
            return category
    if audit is not None:
        audit.record_unmapped(normalized, tokens=tokens, known_tokens=_KNOWN_TOKENS)
    return None


def build_dish_taxonomy(
    item_urls: List[str],
    *,
    min_count: int = 5,
    top_n: int = 15,
) -> Dict[str, object]:
    """Build dish taxonomy from item URLs."""

    audit = DishMappingAudit()
    counts: Dict[str, int] = defaultdict(int)

    for url in item_urls:
        path = urlparse(url).path
        parts = [part for part in path.split("/") if part]
        try:
            items_index = parts.index("items")
        except ValueError:
            continue
        item_parts = parts[items_index + 1 :]
        if not item_parts:
            continue
        slug = item_parts[-1]
        category = map_dish_slug(slug, audit=audit)
        if category:
            counts[category] += 1

    sorted_categories = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    strict_categories = [
        {"category": name, "count": count}
        for name, count in sorted_categories
        if count >= min_count
    ][:top_n]

    return {
        "strategy": {"mode": "strict", "min_count": min_count, "top_n": top_n},
        "audit": {
            "mapped": audit.mapped,
            "unmapped": audit.unmapped,
            "top_unknown_tokens": [
                {"token": token, "count": count} for token, count in audit.top_unknown_tokens()
            ],
        },
        "categories": strict_categories,
    }
