from __future__ import annotations

import csv
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from seo_engine.pipeline import run_pipeline
from seo_engine.render.clipboard import render_clipboard


st.set_page_config(page_title="SEO Intake", layout="centered")


st.title("SEO Intake")

sitemap_file = st.file_uploader(
    "Sitemap XML",
    type=["xml"],
    accept_multiple_files=False,
)
html_files = st.file_uploader(
    "HTML files",
    type=["html", "htm"],
    accept_multiple_files=True,
)
csv_files = st.file_uploader(
    "Optional CSV files",
    type=["csv"],
    accept_multiple_files=True,
)

run_clicked = st.button("Run")


def _read_json(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError:
        return {}


def _normalize_unknown_tokens(dish_taxonomy: Dict[str, Any]) -> list[Dict[str, Any]]:
    tokens_raw = dish_taxonomy.get("dishes", {}).get("audit", {}).get("top_unknown_tokens", [])
    normalized: list[Dict[str, Any]] = []
    if isinstance(tokens_raw, dict):
        for token, count in tokens_raw.items():
            normalized.append({"token": str(token), "count": count})
        return normalized
    if isinstance(tokens_raw, list):
        for entry in tokens_raw:
            if isinstance(entry, dict):
                token = entry.get("token")
                count = entry.get("count")
                if token:
                    normalized.append({"token": str(token), "count": count})
            elif isinstance(entry, (list, tuple)) and len(entry) >= 2:
                token, count = entry[0], entry[1]
                if token:
                    normalized.append({"token": str(token), "count": count})
            elif isinstance(entry, str):
                normalized.append({"token": entry, "count": None})
    return normalized


def _save_uploaded_files(uploaded_files: list[Any], target_dir: str) -> None:
    if not uploaded_files:
        return
    os.makedirs(target_dir, exist_ok=True)
    for uploaded in uploaded_files:
        safe_name = os.path.basename(uploaded.name)
        destination = os.path.join(target_dir, safe_name)
        with open(destination, "wb") as handle:
            handle.write(uploaded.getvalue())


def _read_csv_header(uploaded: Any) -> list[str]:
    if uploaded is None:
        return []
    raw_bytes = uploaded.getvalue()
    if not raw_bytes:
        return []
    for encoding in ("utf-8-sig", "utf-16"):
        try:
            text = raw_bytes.decode(encoding)
        except UnicodeError:
            continue
        first_line = text.splitlines()[0] if text.splitlines() else ""
        if not first_line:
            continue
        delimiter = "\t" if "\t" in first_line else ","
        reader = csv.reader([first_line], delimiter=delimiter)
        return [cell.strip() for cell in next(reader, []) if cell.strip()]
    return []


def _identify_ahrefs_csvs(uploaded_files: list[Any]) -> tuple[bytes | None, bytes | None]:
    keyword_csv = None
    performance_csv = None
    for uploaded in uploaded_files or []:
        header = _read_csv_header(uploaded)
        if "Keyword" in header and keyword_csv is None:
            keyword_csv = uploaded.getvalue()
        elif "Metric" in header and performance_csv is None:
            performance_csv = uploaded.getvalue()
    return keyword_csv, performance_csv


if run_clicked:
    if sitemap_file is None:
        st.warning("Please upload a sitemap XML file before running.")
    else:
        sitemap_bytes = sitemap_file.getvalue()
        html_bytes_list = [uploaded.getvalue() for uploaded in html_files or []]
        limited_csv_files = list(csv_files or [])
        if len(limited_csv_files) > 2:
            st.warning("Only the first two CSV files will be used.")
            limited_csv_files = limited_csv_files[:2]
        keyword_csv, performance_csv = _identify_ahrefs_csvs(limited_csv_files)
        with st.spinner("Running pipeline..."):
            out_dir = tempfile.mkdtemp(prefix="seo-intake-")
            _save_uploaded_files(limited_csv_files, os.path.join(out_dir, "inputs"))
            artifacts_dir = run_pipeline(
                sitemap_bytes,
                html_bytes_list,
                out_dir,
                keyword_csv=keyword_csv,
                performance_csv=performance_csv,
            )
        st.session_state["artifacts_dir"] = artifacts_dir

artifacts_dir = st.session_state.get("artifacts_dir")

if artifacts_dir:
    st.info(f"Artifacts saved to: {artifacts_dir}")
    locations_data = _read_json(os.path.join(artifacts_dir, "locations.json"))
    core_pages_data = _read_json(os.path.join(artifacts_dir, "core_pages.json"))
    dish_taxonomy_data = _read_json(os.path.join(artifacts_dir, "dish_taxonomy.json"))
    ahrefs_data = _read_json(os.path.join(artifacts_dir, "ahrefs_summary.json"))

    show_unknown_tokens = st.checkbox("Show dish unknown tokens (tuning)", value=False)

    clipboard_text = ""
    if show_unknown_tokens:
        clipboard_text = render_clipboard(
            locations=locations_data.get("locations", []),
            core_pages=core_pages_data.get("urls", []),
            dish_categories=dish_taxonomy_data.get("dishes", {}).get("categories", []),
            ahrefs_snapshot=ahrefs_data.get("overview", {}),
            dish_taxonomy=dish_taxonomy_data.get("dishes", {}),
            include_unknown_tokens=True,
        )
    else:
        clipboard_path = os.path.join(artifacts_dir, "clipboard_package.txt")
        if os.path.exists(clipboard_path):
            with open(clipboard_path, "r", encoding="utf-8") as handle:
                clipboard_text = handle.read()

    st.subheader("Clipboard Package")
    st.text_area(
        "Copy-friendly text",
        value=clipboard_text,
        height=200,
        help="Copy this text into the clipboard target.",
    )
    st.download_button(
        "Download clipboard_package.txt",
        data=clipboard_text,
        file_name="clipboard_package.txt",
    )

    with st.expander("Locations", expanded=False):
        locations = locations_data.get("locations", [])
        if locations:
            summary_lines = []
            for location in locations:
                location_name = location.get("location_name") or location.get("name", "")
                address = (
                    location.get("full_address")
                    or location.get("city_state_zip")
                    or location.get("street")
                    or ""
                )
                if location_name and address:
                    summary_lines.append(f"- **{location_name}**: {address}")
                elif location_name:
                    summary_lines.append(f"- **{location_name}**")
                elif address:
                    summary_lines.append(f"- {address}")
            if summary_lines:
                st.markdown("\n".join(summary_lines))
            st.json(locations)
        else:
            st.info("No locations found.")

    with st.expander("Core Pages", expanded=False):
        core_pages = core_pages_data.get("urls", [])
        if core_pages:
            st.json(core_pages)
        else:
            st.info("No core pages found.")

    with st.expander("Dish Categories", expanded=False):
        dish_categories = dish_taxonomy_data.get("dishes", {}).get("categories", [])
        if dish_categories:
            lines = [
                f"- {category.get('category', '')} ({category.get('count', 0)})"
                for category in dish_categories
            ]
            st.markdown("\n".join(lines))
        else:
            st.info("No dish categories mapped (strict mode).")

    with st.expander("Dish Unknown Tokens (tuning)", expanded=False):
        unknown_tokens = _normalize_unknown_tokens(dish_taxonomy_data)
        if unknown_tokens:
            st.json(unknown_tokens)
        else:
            st.info("No unknown tokens found.")
