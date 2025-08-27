from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import cast

import streamlit as st
import toml
from streamlit.navigation.page import StreamlitPage
from streamlit.runtime.metrics_util import gather_metrics
from streamlit.source_util import page_icon_and_name

HIDE_PAGES_KEY = "_st_pages_pages_to_hide"


@dataclass
class Page:
    path: str
    name: str | None = None
    is_section: bool = False
    url_path: str | None = None

    def __post_init__(self):
        if self.name is None:
            _, self.name = page_icon_and_name(Path(self.path))


class Section(Page):
    def __init__(self, name: str, url_path: str | None = None):
        super().__init__(path="", name=name, is_section=True, url_path=url_path)

def hide_pages(pages_to_hide: list[str]):
    if HIDE_PAGES_KEY not in st.session_state:
        st.session_state[HIDE_PAGES_KEY] = []

    if st.session_state[HIDE_PAGES_KEY] != pages_to_hide:
        st.session_state[HIDE_PAGES_KEY] = pages_to_hide
        st.rerun()


def _get_pages_from_config(
    path: str = "page_section.toml",
) -> list[Page] | None:
    try:
        raw_pages: list[dict[str, str | bool]] = toml.loads(
            Path(path).read_text(encoding="utf-8")
        )["pages"]
    except (FileNotFoundError, toml.decoder.TomlDecodeError, KeyError):
        st.error(
            f"""
        Không tìm thấy file {path} hợp lệ. Vui lòng tạo file TOML với định dạng như sau:

        ```toml
        [[pages]]
        path = "app.py"
        name = "Trang chủ"

        [[pages]]
        name = "Quản lý"
        is_section = true

        [[pages]]
        path = "pages/abc.py"
        name = "Trang ABC"
        ```
        """
        )
        return None

    pages: list[Page] = []
    for page in raw_pages:
        if page.get("is_section"):
            page["path"] = ""
            pages.append(Section(page["name"]))  # type: ignore
        else:
            pages.append(Page(**page))  # type: ignore

    return pages


def _get_nav_from_toml(
    path: str = "page_section.toml",
) -> list[StreamlitPage] | dict[str, list[StreamlitPage]]:
    pages = _get_pages_from_config(path)
    if pages is None:
        return []

    if HIDE_PAGES_KEY not in st.session_state:
        st.session_state[HIDE_PAGES_KEY] = []

    pages = [
        p
        for p in pages
        if (p.name not in st.session_state[HIDE_PAGES_KEY]) or p.is_section
    ]

    has_sections = any(p.is_section for p in pages)

    if not has_sections:
        return [
            st.Page(p.path, title=p.name, url_path=p.url_path) for p in pages
        ]

    pages_data: dict[str, list[StreamlitPage]] = {}
    current_section = ""

    for page in pages:
        if page.is_section:
            current_section = cast(str, page.name)
            pages_data[current_section] = []
            continue

        if current_section not in pages_data:
            pages_data[current_section] = []

        pages_data[current_section].append(
            st.Page(page.path, title=page.name, url_path=page.url_path)
        )

    return pages_data


get_nav_from_toml = gather_metrics(
    "st_pages.get_nav_from_toml", _get_nav_from_toml
)