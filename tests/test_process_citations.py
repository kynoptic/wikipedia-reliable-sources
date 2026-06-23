import csv
import itertools
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.process_citations import (
    ArticleClassifier,
    CitationRow,
    aggregate_citations,
    iter_citation_rows,
    load_article_ids,
    normalize_cite_type,
    rank_by_count,
    save_domain_table,
    save_host_table,
)

REAL_TSV = (
    Path(__file__).resolve().parents[1]
    / "data/raw/citations/wikipedia-citations_enwiki_2016-06-01_CS1_citations.tsv"
)


def _row(citation_id, page_id, url, cite_type="cite web"):
    return CitationRow(
        citation_id=citation_id,
        page_id=page_id,
        timestamp="2016-04-22T10:19:33Z",
        page_title="Example",
        cite_type=cite_type,
        url=url,
    )


def test_normalize_cite_type_strips_and_lowercases():
    assert normalize_cite_type("Cite book ") == "cite book"


def test_normalize_cite_type_collapses_underscores_and_spaces():
    assert normalize_cite_type("cite_journal") == "cite journal"
    assert normalize_cite_type("cite  news") == "cite news"


def test_normalize_cite_type_empty():
    assert normalize_cite_type("") == ""


def test_iter_citation_rows_parses_valid_row(tmp_path):
    tsv = tmp_path / "c.tsv"
    tsv.write_text(
        "716\t12\t2016-04-22T10:19:33Z\tAnarchism\tcite journal \t"
        '{"URL": "http://example.com/a", "Title": "T"}\n'
    )
    rows = list(iter_citation_rows(tsv))
    assert len(rows) == 1
    row = rows[0]
    assert row.page_id == "12"
    assert row.cite_type == "cite journal"
    assert row.url == "http://example.com/a"


def test_iter_citation_rows_keeps_tab_inside_json(tmp_path):
    tsv = tmp_path / "c.tsv"
    tsv.write_text(
        '716\t12\tts\tTitle\tcite web \t{"URL": "http://x.com", "Title": "a\tb"}\n'
    )
    rows = list(iter_citation_rows(tsv))
    assert len(rows) == 1
    assert rows[0].url == "http://x.com"


def test_iter_citation_rows_reassembles_multiline_record(tmp_path):
    # Real dumps embed newlines in the cite_type/JSON column, splitting one
    # record across physical lines; the parser must rejoin them.
    tsv = tmp_path / "c.tsv"
    tsv.write_text(
        "716551092\t12\t2016-04-22T10:19:33Z\tAnarchism\tCite book\n"
        ' \t{"URL": "http://marxists.org/x", "Title": "T"}\n'
        "999\t34\t2016-04-22T10:19:33Z\tBiology\tcite web \t"
        '{"URL": "http://example.com/y"}\n'
    )
    rows = list(iter_citation_rows(tsv))
    assert len(rows) == 2
    assert rows[0].page_id == "12"
    assert rows[0].cite_type == "cite book"
    assert rows[0].url == "http://marxists.org/x"
    assert rows[1].page_id == "34"
    assert rows[1].url == "http://example.com/y"


def test_iter_citation_rows_skips_malformed_json(tmp_path):
    tsv = tmp_path / "c.tsv"
    tsv.write_text("716\t12\tts\tTitle\tcite web \t{not json}\n")
    assert list(iter_citation_rows(tsv)) == []


def test_iter_citation_rows_skips_short_rows(tmp_path):
    tsv = tmp_path / "c.tsv"
    tsv.write_text("716\t12\tts\tTitle\tcite web\n")
    assert list(iter_citation_rows(tsv)) == []


def test_iter_citation_rows_yields_empty_url_when_absent(tmp_path):
    tsv = tmp_path / "c.tsv"
    tsv.write_text('716\t12\tts\tTitle\tcite book \t{"Title": "no url here"}\n')
    rows = list(iter_citation_rows(tsv))
    assert len(rows) == 1
    assert rows[0].url == ""


def test_load_article_ids_reads_pageid_column(tmp_path):
    csv_path = tmp_path / "fa.csv"
    csv_path.write_text(
        '"number","title","pageid","namespace","length","touched"\n'
        '"1","Autism","25","","139454","20200315211208"\n'
        '"2","Amphibian","621","","133554","20200315085320"\n'
    )
    assert load_article_ids(csv_path) == {"25", "621"}


def test_load_article_ids_missing_file(tmp_path):
    assert load_article_ids(tmp_path / "nope.csv") == set()


def test_aggregate_citations_counts_host_and_domain():
    classifier = ArticleClassifier(featured_ids={"1"}, good_ids={"2"})
    rows = [
        _row("a", "1", "http://www.nytimes.com/story1"),
        _row("b", "2", "http://www.nytimes.com/story2"),
        _row("c", "3", "http://mobile.nytimes.com/story3"),
        _row("d", "1", ""),  # no URL -> excluded
    ]
    by_host, by_domain = aggregate_citations(rows, classifier)

    host_index = {r["host_url"]: r for r in by_host}
    www = host_index["www.nytimes.com"]
    assert www["subdomain_url"] == "www"
    assert www["domain_url"] == "nytimes"
    assert www["suffix_url"] == "com"
    assert www["total_citations"] == 2
    assert www["fa_citations"] == 1
    assert www["ga_citations"] == 1
    assert www["distinct_articles"] == 2

    assert host_index["mobile.nytimes.com"]["total_citations"] == 1

    domain_index = {(r["domain_url"], r["suffix_url"]): r for r in by_domain}
    nyt = domain_index[("nytimes", "com")]
    assert nyt["total_citations"] == 3
    assert nyt["fa_citations"] == 1
    assert nyt["ga_citations"] == 1
    assert nyt["distinct_articles"] == 3


def test_aggregate_citations_skips_unparseable_url():
    classifier = ArticleClassifier()
    rows = [
        _row("a", "1", "http://[malformed"),  # urlparse raises ValueError
        _row("b", "2", "http://www.bbc.co.uk/news"),
    ]
    by_host, by_domain = aggregate_citations(rows, classifier)
    assert {r["domain_url"] for r in by_domain} == {"bbc"}


def test_save_host_table_writes_expected_header(tmp_path):
    out = tmp_path / "by_host.csv"
    save_host_table([], out)
    header = out.read_text().splitlines()[0]
    assert header == (
        "host_url,subdomain_url,domain_url,suffix_url,"
        "total_citations,fa_citations,ga_citations,distinct_articles"
    )


def test_save_domain_table_writes_expected_header(tmp_path):
    out = tmp_path / "by_domain.csv"
    save_domain_table([], out)
    header = out.read_text().splitlines()[0]
    assert header == (
        "domain_url,suffix_url,"
        "total_citations,fa_citations,ga_citations,distinct_articles"
    )


def test_rank_by_count_orders_and_limits():
    data = [
        {"domain_url": "a", "total_citations": 1},
        {"domain_url": "b", "total_citations": 5},
        {"domain_url": "c", "total_citations": 3},
    ]
    ranked = rank_by_count(data, limit=2)
    assert [r["domain_url"] for r in ranked] == ["b", "c"]


@pytest.mark.skipif(not REAL_TSV.exists(), reason="3.5GB CS1 TSV not present")
def test_smoke_real_tsv_head_aggregates():
    rows = list(itertools.islice(iter_citation_rows(REAL_TSV), 1000))
    assert rows, "expected parsed rows from the real dump"
    assert any(r.url for r in rows), "expected at least one row with a URL"

    classifier = ArticleClassifier(featured_ids=set(), good_ids=set())
    by_host, by_domain = aggregate_citations(rows, classifier)
    assert by_host and by_domain
