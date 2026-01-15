from __future__ import annotations

import json
import os
import tempfile
from typing import Any, Dict

import streamlit as st

from pipeline import run_pipeline


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

run_clicked = st.button("Run")


def _read_json(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError:
        return {}


if run_clicked:
    if sitemap_file is None:
        st.warning("Please upload a sitemap XML file before running.")
    else:
        sitemap_bytes = sitemap_file.getvalue()
        html_bytes_list = [uploaded.getvalue() for uploaded in html_files or []]
        with st.spinner("Running pipeline..."):
            out_dir = tempfile.mkdtemp(prefix="seo-intake-")
            artifacts_dir = run_pipeline(sitemap_bytes, html_bytes_list, out_dir)
        st.session_state["artifacts_dir"] = artifacts_dir

artifacts_dir = st.session_state.get("artifacts_dir")

if artifacts_dir:
    clipboard_path = os.path.join(artifacts_dir, "clipboard_package.txt")
    clipboard_text = ""
    if os.path.exists(clipboard_path):
        with open(clipboard_path, "r", encoding="utf-8") as handle:
            clipboard_text = handle.read()

    st.subheader("Clipboard Package")
    st.text_area(
        "Clipboard text",
        value=clipboard_text,
        height=200,
    )
    st.download_button(
        "Download clipboard_package.txt",
        data=clipboard_text,
        file_name="clipboard_package.txt",
    )

    locations_data = _read_json(os.path.join(artifacts_dir, "locations.json"))
    core_pages_data = _read_json(os.path.join(artifacts_dir, "core_pages.json"))
    dish_taxonomy_data = _read_json(os.path.join(artifacts_dir, "dish_taxonomy.json"))

    with st.expander("Locations", expanded=False):
        locations = locations_data.get("locations", [])
        if locations:
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
            st.json(dish_categories)
        else:
            st.info("No dish categories found.")
