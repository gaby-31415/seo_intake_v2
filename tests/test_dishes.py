from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from seo_engine.select.dishes import DishMappingAudit, map_dish_slug, normalize_dish_slug  # noqa: E402


def test_award_winning_baby_back_ribs_maps_to_ribs() -> None:
    assert map_dish_slug("award-winning-baby-back-ribs") == "ribs"


def test_unmapped_slug_contributes_to_audit_metrics() -> None:
    audit = DishMappingAudit()

    result = map_dish_slug("ahi-tuna-guacamole-047843dd", audit=audit)

    assert result is None
    assert audit.unmapped == ["ahi-tuna-guacamole"]


def test_trailing_numeric_hex_suffix_is_stripped() -> None:
    assert normalize_dish_slug("crispy-tacos-123") == "crispy-tacos"
    assert normalize_dish_slug("crispy-tacos-047843dd") == "crispy-tacos"
