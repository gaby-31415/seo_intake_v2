"""Artifact-first pipeline for SEO intake."""

from __future__ import annotations

import os
from typing import Any, Dict, List

from seo_engine.extract.locations import extract_locations
from seo_engine.ingest.sitemap import parse_sitemap, split_item_urls
from seo_engine.render.clipboard import render_clipboard
from seo_engine.schemas import AhrefsSummary, CorePages, DishTaxonomy, Locations, SiteFacts
from seo_engine.select.core_pages import rank_core_pages
from seo_engine.select.dishes import build_dish_taxonomy
from seo_engine.utils.json_stable import json_dump_stable


def _stable_core_pages(core_pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return core pages in a deterministic order."""

    normalized: List[Dict[str, Any]] = []
    for page in core_pages:
        page_copy = dict(page)
        reasons = page_copy.get("reasons")
        if isinstance(reasons, set):
            page_copy["reasons"] = sorted(reasons)
        elif isinstance(reasons, tuple):
            page_copy["reasons"] = list(reasons)
        normalized.append(page_copy)
    return sorted(
        normalized,
        key=lambda item: (-(item.get("score") or 0), item.get("url") or ""),
    )


def _ensure_artifacts_dir(out_dir: str) -> str:
    """Create or clear the artifacts directory."""

    artifacts_dir = os.path.join(out_dir, "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    for filename in os.listdir(artifacts_dir):
        file_path = os.path.join(artifacts_dir, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
    return artifacts_dir


def run_pipeline(sitemap_xml: bytes, html_files: List[bytes], out_dir: str) -> str:
    """Run the SEO intake pipeline and return the artifacts directory."""

    urls = parse_sitemap(sitemap_xml)
    item_urls, non_item_urls = split_item_urls(urls)
    core_pages = _stable_core_pages(rank_core_pages(non_item_urls))
    locations = extract_locations(html_files)
    dish_taxonomy = build_dish_taxonomy(item_urls)

    artifacts_dir = _ensure_artifacts_dir(out_dir)

    site_facts = SiteFacts()
    core_pages_schema = CorePages(urls=core_pages)
    locations_schema = Locations(locations=locations)
    dish_schema = DishTaxonomy(dishes=dish_taxonomy)
    ahrefs_schema = AhrefsSummary()

    json_dump_stable(site_facts.to_dict(), os.path.join(artifacts_dir, "site_facts.json"))
    json_dump_stable(
        locations_schema.to_dict(),
        os.path.join(artifacts_dir, "locations.json"),
    )
    json_dump_stable(
        core_pages_schema.to_dict(),
        os.path.join(artifacts_dir, "core_pages.json"),
    )
    json_dump_stable(
        dish_schema.to_dict(),
        os.path.join(artifacts_dir, "dish_taxonomy.json"),
    )
    json_dump_stable(
        ahrefs_schema.to_dict(),
        os.path.join(artifacts_dir, "ahrefs_summary.json"),
    )

    clipboard_text = render_clipboard(
        locations=locations,
        core_pages=core_pages,
        dish_categories=dish_taxonomy.get("categories", []),
        ahrefs_snapshot=ahrefs_schema.overview,
    )
    clipboard_path = os.path.join(artifacts_dir, "clipboard_package.txt")
    with open(clipboard_path, "w", encoding="utf-8") as handle:
        handle.write(clipboard_text)

    return artifacts_dir
