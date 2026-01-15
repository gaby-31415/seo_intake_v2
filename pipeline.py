"""Artifact-first pipeline for SEO intake."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

from seo_engine.extract.locations import extract_locations
from seo_engine.ingest.sitemap import parse_sitemap, split_item_urls
from seo_engine.render.clipboard import render_clipboard
from seo_engine.schemas import AhrefsSummary, CorePages, DishTaxonomy, Locations, SiteFacts
from seo_engine.select.core_pages import rank_core_pages
from seo_engine.select.dishes import build_dish_taxonomy


def _write_json(path: str, payload: Dict[str, Any]) -> None:
    """Write JSON payload to disk."""

    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


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
    core_pages = rank_core_pages(non_item_urls)
    locations = extract_locations(html_files)
    dish_taxonomy = build_dish_taxonomy(item_urls)

    artifacts_dir = _ensure_artifacts_dir(out_dir)

    site_facts = SiteFacts()
    core_pages_schema = CorePages(urls=core_pages)
    locations_schema = Locations(locations=locations)
    dish_schema = DishTaxonomy(dishes=dish_taxonomy)
    ahrefs_schema = AhrefsSummary()

    _write_json(os.path.join(artifacts_dir, "site_facts.json"), site_facts.to_dict())
    _write_json(os.path.join(artifacts_dir, "locations.json"), locations_schema.to_dict())
    _write_json(os.path.join(artifacts_dir, "core_pages.json"), core_pages_schema.to_dict())
    _write_json(os.path.join(artifacts_dir, "dish_taxonomy.json"), dish_schema.to_dict())
    _write_json(os.path.join(artifacts_dir, "ahrefs_summary.json"), ahrefs_schema.to_dict())

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
