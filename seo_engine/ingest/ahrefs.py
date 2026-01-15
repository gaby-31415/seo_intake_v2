"""Ingest Ahrefs CSV exports."""

from __future__ import annotations

import csv
from typing import Any, Dict, Iterable, List, Optional


def _read_csv_rows(csv_bytes: Optional[bytes]) -> List[Dict[str, Any]]:
    if not csv_bytes:
        return []
    rows: List[Dict[str, Any]] = []
    for encoding in ("utf-16", "utf-8-sig"):
        try:
            text = csv_bytes.decode(encoding)
        except UnicodeError:
            continue
        lines = text.splitlines()
        if not lines:
            continue
        delimiter = "\t" if "\t" in lines[0] else ","
        reader = csv.DictReader(lines, delimiter=delimiter)
        rows = [row for row in reader if isinstance(row, dict)]
        if rows:
            return rows
    return rows


def _as_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    value_str = str(value).replace(",", "").strip()
    if not value_str:
        return None
    try:
        return int(float(value_str))
    except ValueError:
        return None


def _first_value(row: Dict[str, Any], keys: Iterable[str]) -> Optional[str]:
    for key in keys:
        value = row.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return None


def _parse_top_keywords(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    keywords: List[Dict[str, Any]] = []
    for row in rows:
        keyword = _first_value(row, ("Keyword", "keyword"))
        if not keyword:
            continue
        volume = _as_int(_first_value(row, ("Volume", "Search volume", "Search Volume")))
        position = _as_int(_first_value(row, ("Position", "Pos")))
        url = _first_value(row, ("URL", "Target", "Page"))
        keywords.append(
            {
                "keyword": keyword,
                "volume": volume,
                "position": position,
                "url": url,
            }
        )
    if any(entry.get("volume") is not None for entry in keywords):
        keywords.sort(key=lambda item: item.get("volume") or 0, reverse=True)
    return keywords[:10]


def _parse_traffic_trend(rows: List[Dict[str, Any]]) -> Dict[str, Optional[str]]:
    for row in rows:
        metric = _first_value(row, ("Metric", "metric"))
        if not metric:
            continue
        metric_lower = metric.lower()
        if "trend" in metric_lower or "traffic" in metric_lower:
            direction = _first_value(row, ("Direction", "Trend", "Value"))
            confidence = _first_value(row, ("Confidence", "Confidence %", "Confidence score"))
            return {"direction": direction, "confidence": confidence}
    return {"direction": None, "confidence": None}


def _parse_position_distribution(rows: List[Dict[str, Any]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for row in rows:
        metric = _first_value(row, ("Metric", "Bucket", "Range"))
        if not metric:
            continue
        value = _as_int(
            _first_value(
                row,
                (
                    "Count",
                    "Value",
                    "Keywords",
                    "Keywords count",
                    "Total",
                ),
            )
        )
        if value is not None:
            counts[metric] = value
    return counts


def build_ahrefs_overview(
    keyword_csv: Optional[bytes],
    performance_csv: Optional[bytes],
) -> Dict[str, Any]:
    if not keyword_csv and not performance_csv:
        return {}
    overview: Dict[str, Any] = {
        "traffic_trend": {"direction": None, "confidence": None},
        "position_distribution": {"latest_counts": {}},
        "top_keywords": [],
    }
    if keyword_csv:
        keyword_rows = _read_csv_rows(keyword_csv)
        overview["top_keywords"] = _parse_top_keywords(keyword_rows)
    if performance_csv:
        performance_rows = _read_csv_rows(performance_csv)
        overview["traffic_trend"] = _parse_traffic_trend(performance_rows)
        overview["position_distribution"] = {
            "latest_counts": _parse_position_distribution(performance_rows)
        }
    return overview
