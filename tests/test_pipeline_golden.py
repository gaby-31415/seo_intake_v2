from __future__ import annotations

import os
from pathlib import Path
import sys
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from pipeline import run_pipeline  # noqa: E402
from seo_engine.utils.json_stable import json_dump_stable, json_load  # noqa: E402

FIXTURES_DIR = Path(__file__).parent / "fixtures"
GOLDEN_DIR = Path(__file__).parent / "golden"


def _normalize_json(data: Any) -> Any:
    if isinstance(data, dict):
        return {key: _normalize_json(data[key]) for key in sorted(data)}
    if isinstance(data, list):
        return [_normalize_json(item) for item in data]
    return data


def _load_json(path: Path) -> Any:
    return json_load(str(path))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    json_dump_stable(payload, str(path))


def _run_pipeline(tmp_path: Path, html_fixture: str) -> Path:
    sitemap_xml = (FIXTURES_DIR / "sample_sitemap.xml").read_bytes()
    html_files = [(FIXTURES_DIR / html_fixture).read_bytes()]
    return Path(run_pipeline(sitemap_xml, html_files, str(tmp_path)))


def _assert_golden(payload: Any, golden_name: str) -> None:
    golden_path = GOLDEN_DIR / golden_name
    assert golden_path.exists(), f"Missing golden file: {golden_path}"
    expected = _normalize_json(_load_json(golden_path))
    assert payload == expected


def test_pipeline_golden(tmp_path: Path) -> None:
    artifacts_dir = _run_pipeline(tmp_path, "sample_location.html")

    outputs = {
        "locations.json": _normalize_json(_load_json(artifacts_dir / "locations.json")),
        "core_pages.json": _normalize_json(_load_json(artifacts_dir / "core_pages.json")),
        "dish_taxonomy.json": _normalize_json(_load_json(artifacts_dir / "dish_taxonomy.json")),
    }

    if os.getenv("REGENERATE_GOLDENS") == "1":
        for filename, payload in outputs.items():
            _write_json(GOLDEN_DIR / filename, payload)
        return

    for filename, payload in outputs.items():
        _assert_golden(payload, filename)


def test_pipeline_golden_multi_locations(tmp_path: Path) -> None:
    artifacts_dir = _run_pipeline(tmp_path, "sample_locations_multi.html")
    payload = _normalize_json(_load_json(artifacts_dir / "locations.json"))

    if os.getenv("REGENERATE_GOLDENS") == "1":
        _write_json(GOLDEN_DIR / "locations_multi.json", payload)
        return

    _assert_golden(payload, "locations_multi.json")
