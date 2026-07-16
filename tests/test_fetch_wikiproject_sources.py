import sys
from pathlib import Path
from typing import Any

import requests
from scripts.common import HEADERS

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.fetch_wikiproject_sources import fetch_page, parse_page


def test_fetch_page(monkeypatch: Any) -> None:
    """Ensure page is requested with the correct headers."""

    def fake_get(url: str, params: Any | None = None, timeout: int = 30, headers: dict | None = None) -> Any:
        assert headers == HEADERS

        class Response:
            def raise_for_status(self) -> None:
                pass

            def json(self) -> dict:
                return {"query": {"pages": {"1": {"revisions": [{"*": "text"}]}}}}

        return Response()

    monkeypatch.setattr(requests, "get", fake_get)

    result = fetch_page("Dummy")
    assert result == "text"


def test_parse_page_extracts_entries() -> None:
    wikitext = (
        "==Reliable sources==\n"
        "===Generally reliable===\n"
        "{| class=\"wikitable\"\n"
        "|-\n! Name !! Notes\n"
        "|-\n| [[Foo News]] || Some ''notes''\n"
        "|}\n"
    )

    entries = parse_page(wikitext)
    assert len(entries) == 1
    entry = entries[0]
    assert entry.source_name == "Foo News"
    assert entry.reliability_status == "gr"
    assert entry.notes == "Some notes"


def test_parse_page_handles_row_headers() -> None:
    """Rows starting with ``th`` cells should not be skipped."""

    wikitext = (
        "==Unreliable sources==\n"
        "{| class=\"wikitable\"\n"
        "|-\n! Name !! Notes\n"
        "|-\n! [[Bad Source]] || Some ''notes''\n"
        "|}\n"
    )

    entries = parse_page(wikitext)
    assert len(entries) == 1
    entry = entries[0]
    assert entry.source_name == "Bad Source"
    assert entry.reliability_status == "gu"


def test_parse_page_extracts_bullet_entries() -> None:
    wikitext = (
        "==Reliable sources==\n"
        "===Generally reliable===\n"
        "* [[Foo Site]] \u2013 Example notes\n"
    )

    entries = parse_page(wikitext)
    assert len(entries) == 1
    entry = entries[0]
    assert entry.source_name == "Foo Site"
    assert entry.reliability_status == "gr"
    assert entry.notes == "Example notes"


def test_parse_page_handles_numbered_lists() -> None:
    wikitext = (
        "==Unreliable sources==\n"
        "# [[Bad Site]] - info\n"
    )

    entries = parse_page(wikitext)
    assert len(entries) == 1
    entry = entries[0]
    assert entry.source_name == "Bad Site"
    assert entry.reliability_status == "gu"


def test_parse_page_extracts_table_entries_with_discussion_last_cell() -> None:
    """Anime and manga's reliable-sources table keeps a discussion-link last cell as notes."""

    wikitext = (
        "==Reliable==\n"
        "===General===\n"
        "{| class=\"wikitable sortable\"\n"
        "|-\n! Source !! Owner !! Description !! Evidence !! Usable content !! Discussion(s)\n"
        "|-\n| [https://example.com/ Example Site] || Jane Doe || A review site."
        " || Cited elsewhere. || style=\"text-align: center;\"| Reviews"
        " || Project: [[Talk:Example#Example Site|1]]\n"
        "|}\n"
    )

    entries = parse_page(wikitext)
    assert len(entries) == 1
    entry = entries[0]
    assert entry.source_name == "Example Site"
    assert entry.reliability_status == "gr"
    assert "Project" in entry.notes


def test_parse_page_extracts_unreliable_bullet_entries_without_dash() -> None:
    """Anime and manga's Unreliable bullets often have no dash separator."""

    wikitext = (
        "==Unreliable==\n"
        "* Animetric (<code>www.animetric.com</code>) [https://www.animetric.com]"
        " Self-published website by a person who is not a vetted industry expert\n"
    )

    entries = parse_page(wikitext)
    assert len(entries) == 1
    entry = entries[0]
    assert "Animetric" in entry.source_name
    assert entry.reliability_status == "gu"


def test_parse_page_undetermined_heading_resets_inherited_status() -> None:
    """Board and table games' 'Undetermined' section must not inherit prior status."""

    wikitext = (
        "==Unreliable==\n"
        "* [[BoardGameGeek]] - User-based content.\n"
        "==Undetermined==\n"
        "* Di6dent\n"
        "* GameFan\n"
    )

    entries = parse_page(wikitext)
    assert len(entries) == 3
    assert entries[0].source_name == "BoardGameGeek"
    assert entries[0].reliability_status == "gu"
    assert entries[1].source_name == "Di6dent"
    assert entries[1].reliability_status is None
    assert entries[2].source_name == "GameFan"
    assert entries[2].reliability_status is None


def test_parse_page_situational_table_leaves_status_unmapped() -> None:
    """Board and table games' Situational table has no gr/gu/nc/d/m mapping."""

    wikitext = (
        "==Situational ==\n"
        "{| class=\"wikitable sortable\"\n"
        "|-\n! Name !! Notes\n"
        "|-\n| [[Comic Book Resources]] || Marginally reliable to unreliable.\n"
        "|}\n"
    )

    entries = parse_page(wikitext)
    assert len(entries) == 1
    assert entries[0].source_name == "Comic Book Resources"
    assert entries[0].reliability_status is None


def test_parse_page_handles_columns_list_wrapped_bullets() -> None:
    """Bullet lists wrapped in a {{columns-list}} template still parse per line."""

    wikitext = (
        "==Unreliable or questionable sources==\n"
        "{{columns-list|colwidth=22em|\n"
        "* ''101dogbreeds.com'' [https://101dogbreeds.com]\n"
        "* ''allthingsdogs.com'' [https://allthingsdogs.com]\n"
        "}}\n"
    )

    entries = parse_page(wikitext)
    assert len(entries) == 2
    assert entries[0].reliability_status == "gu"
    assert "101dogbreeds.com" in entries[0].source_name
    assert entries[1].reliability_status == "gu"
    assert "allthingsdogs.com" in entries[1].source_name


def test_parse_page_nba_wikilinked_status_headings() -> None:
    """WikiProject NBA uses piped wikilinks in its status headings."""

    wikitext = (
        "==[[WP:GREL|Generally reliable]]==\n"
        "===Websites===\n"
        "*https://www.espn.com ([[Wikipedia:Reliable sources/Noticeboard/Archive 318#ESPN|1]])\n"
        "==[[WP:MREL|No consensus, unclear, or additional considerations apply]]==\n"
        "*[[ClutchPoints]] ([[Wikipedia:Reliable sources/Noticeboard/Archive 436#ClutchPoints|1]])\n"
        "==[[WP:GUNREL|Generally unreliable]]==\n"
        "*[[Bleacher Report]] ([[Wikipedia:Reliable sources/Noticeboard/Archive 91#Bleacher Report|1]])\n"
    )

    entries = parse_page(wikitext)
    assert len(entries) == 3
    assert entries[0].reliability_status == "gr"
    assert "espn.com" in entries[0].source_name
    assert entries[1].reliability_status == "nc"
    assert "ClutchPoints" in entries[1].source_name
    assert entries[2].reliability_status == "gu"
    assert "Bleacher Report" in entries[2].source_name


def test_parse_page_class_based_status() -> None:
    """Rows with reliability class attributes should set the status."""

    wikitext = (
        "{| class=\"wikitable\"\n"
        "|- class=\"ko-unrel\"\n"
        "| [[Foo Source]] || Some notes\n"
        "|}\n"
    )

    entries = parse_page(wikitext)
    assert len(entries) == 1
    entry = entries[0]
    assert entry.source_name == "Foo Source"
    assert entry.reliability_status == "gu"
    assert entry.notes == "Some notes"

