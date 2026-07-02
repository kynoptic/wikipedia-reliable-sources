import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from core.build_goggle import (
    DEFAULT_SAFE_ADD_FA_FLOOR,
    DEFAULT_SAFE_ADD_FA_THRESHOLD,
    DEFAULT_SAFE_ADD_GA_THRESHOLD,
    GENERATED_SECTION,
    PRODUCT_PORTAL_DOMAINS,
    Diff,
    Rule,
    SafeAddCandidate,
    _is_valid_domain,
    diff_rules,
    domain_status_from_ranking,
    domain_status_from_resolution,
    generate_base_rules,
    load_overlay,
    main,
    merge_rules,
    parse_goggle_rules,
    parse_rule_line,
    render_diff_md,
    render_goggle,
    render_rule,
    render_safe_add_overlay_seed,
    rule_key,
    safe_add_candidates,
    seed_overlay,
)


# --- rule grammar: parse + render round-trip ---------------------------------


def test_parse_plain_boost_rule() -> None:
    r = parse_rule_line("$boost=2,site=abcnews.com")
    assert r == Rule(action="boost", value=2, domain="abcnews.com", prefix="")


def test_parse_discard_rule_has_no_value() -> None:
    r = parse_rule_line("$discard,site=112.ua")
    assert r == Rule(action="discard", value=None, domain="112.ua", prefix="")


def test_parse_path_qualified_rule_keeps_prefix() -> None:
    r = parse_rule_line("/*science^$downrank=2,site=foxnews.com")
    assert r == Rule(action="downrank", value=2, domain="foxnews.com", prefix="/*science^")


def test_parse_bare_path_rule_without_leading_slash() -> None:
    r = parse_rule_line("print^$boost=2,site=unz.com")
    assert r == Rule(action="boost", value=2, domain="unz.com", prefix="print^")


def test_parse_catch_all_discard_has_no_domain() -> None:
    r = parse_rule_line("$discard")
    assert r == Rule(action="discard", value=None, domain="", prefix="")


def test_parse_ignores_comment_and_blank_lines() -> None:
    assert parse_rule_line("! Source: Perennial") is None
    assert parse_rule_line("   ") is None


def test_parse_rejects_trailing_attributes_after_domain() -> None:
    # The domain stops at a comma, so an extra attribute fails the end anchor.
    assert parse_rule_line("$discard,site=abc.com,extra=foo") is None


def test_render_is_inverse_of_parse_for_every_pattern() -> None:
    for line in (
        "$boost=2,site=abcnews.com",
        "$downrank=2,site=about.com",
        "$discard,site=112.ua",
        "/en^$boost=2,site=dw.com",
        "/*science^$downrank=2,site=foxnews.com",
        "print^$boost=2,site=unz.com",
        "$discard",
    ):
        assert render_rule(parse_rule_line(line)) == line


# --- status -> action mapping ------------------------------------------------


def test_generate_base_maps_each_status_to_its_action() -> None:
    base = generate_base_rules({"a.com": "gr", "b.com": "nc", "c.com": "gu", "d.com": "d"})
    assert base[("", "a.com")] == Rule("boost", 2, "a.com")
    assert base[("", "b.com")] == Rule("downrank", 2, "b.com")
    assert base[("", "c.com")] == Rule("discard", None, "c.com")
    assert base[("", "d.com")] == Rule("discard", None, "d.com")


def test_generate_base_omits_marginal_and_unknown_status() -> None:
    base = generate_base_rules({"m.com": "m", "x.com": "??"})
    assert base == {}


def test_resolution_lowercases_domains() -> None:
    # Wikidata P856 can yield mixed-case domains (e.g. "MS.now"); Goggle site=
    # matching expects lowercase, matching the hand-file convention.
    domain_status = domain_status_from_resolution({"MSNBC": "gr"}, {"MSNBC": {"MS.now"}})
    assert domain_status == {"ms.now": "gr"}


def test_resolution_collapses_to_most_cautious_per_domain() -> None:
    # Two source-splits share a domain; the unreliable one must win.
    name_status = {"Fox (news)": "gr", "Fox (politics)": "gu"}
    name_domains = {"Fox (news)": {"foxnews.com"}, "Fox (politics)": {"foxnews.com"}}
    domain_status = domain_status_from_resolution(name_status, name_domains)
    assert domain_status == {"foxnews.com": "gu"}
    base = generate_base_rules(domain_status)
    assert base[("", "foxnews.com")].action == "discard"


# --- merge: overlay wins -----------------------------------------------------


def test_merge_overlay_overrides_base_on_same_key() -> None:
    base = {("", "x.com"): Rule("discard", None, "x.com")}
    overlay = [Rule("boost", 2, "x.com")]
    merged = merge_rules(base, overlay)
    assert merged[("", "x.com")].action == "boost"


def test_merge_keeps_base_rules_with_no_overlay_counterpart() -> None:
    base = {("", "x.com"): Rule("boost", 2, "x.com")}
    merged = merge_rules(base, [Rule("discard", None, "y.com")])
    assert merged[("", "x.com")].action == "boost"
    assert merged[("", "y.com")].action == "discard"


def test_merge_preserves_path_qualified_overlay_rule() -> None:
    base = {("", "foxnews.com"): Rule("discard", None, "foxnews.com")}
    overlay = [Rule("downrank", 2, "foxnews.com", prefix="/*science^")]
    merged = merge_rules(base, overlay)
    # Distinct keys: the path-qualified rule coexists with the plain one.
    assert merged[("/*science^", "foxnews.com")].prefix == "/*science^"
    assert merged[("", "foxnews.com")].action == "discard"


# --- diff buckets ------------------------------------------------------------


def test_diff_classifies_generated_only_current_only_and_conflicts() -> None:
    base = {
        ("", "new.com"): Rule("boost", 2, "new.com"),        # generated-only
        ("", "shared.com"): Rule("boost", 2, "shared.com"),  # agree
        ("", "google.com"): Rule("downrank", 2, "google.com"),  # conflict
    }
    current = [
        Rule("boost", 2, "shared.com"),                       # agree
        Rule("boost", 2, "google.com"),                       # conflict (current boosts)
        Rule("boost", 2, "manual.com"),                       # current-only plain
        Rule("downrank", 2, "foxnews.com", prefix="/*science^"),  # current-only path
    ]
    diff = diff_rules(base, current)
    assert [r.domain for r in diff.generated_only] == ["new.com"]
    assert [r.domain for r in diff.current_only_plain] == ["manual.com"]
    assert [r.domain for r in diff.current_only_path] == ["foxnews.com"]
    assert len(diff.conflicts) == 1
    base_rule, current_rule = diff.conflicts[0]
    assert base_rule.action == "downrank" and current_rule.action == "boost"


# --- overlay seed + round-trip ------------------------------------------------


def test_diff_report_with_empty_buckets_is_lint_safe() -> None:
    # The empty-bucket fallback must not be standalone emphasis (MD036/MD049) and
    # the report must not end with a trailing blank line (MD012).
    out = render_diff_md(Diff(), base_count=0)
    assert "_none_" not in out
    assert "None." in out
    assert "\n\n\n" not in out
    assert out.endswith("\n") and not out.endswith("\n\n")


def test_diff_report_renders_counts_and_conflict_table() -> None:
    diff = Diff(
        generated_only=[Rule("boost", 2, "new.com")],
        conflicts=[(Rule("discard", None, "x.com"), Rule("boost", 2, "x.com"))],
    )
    out = render_diff_md(diff, base_count=42)
    assert "**42**" in out                                  # base_count surfaced
    assert "- `$boost=2,site=new.com`" in out               # generated-only listed
    assert "| x.com | `$discard,site=x.com` | `$boost=2,site=x.com` |" in out  # conflict row


def test_is_valid_domain_rejects_goggle_breaking_characters() -> None:
    assert _is_valid_domain("bbc.co.uk")
    assert _is_valid_domain("ms.now")            # syntactically valid hostname
    assert not _is_valid_domain("with space.com")
    assert not _is_valid_domain("site=inject.com")
    assert not _is_valid_domain("bad$domain.com")
    assert not _is_valid_domain("no-dot")
    assert not _is_valid_domain("")


def test_domain_status_from_ranking_skips_syntactically_invalid_domains(tmp_path: Path) -> None:
    csv_path = tmp_path / "ranking.csv"
    csv_path.write_text(
        "source_name,status,domain\n"
        "Good,gr,good.com\n"
        "Injected,gr,site=evil.com\n"   # illegal '=' would break Goggle syntax
        "Spaced,gu,bad domain.org\n"
    )
    assert domain_status_from_ranking(csv_path) == {"good.com": "gr"}


def test_parse_goggle_rules_excludes_domainless_boost_rule() -> None:
    # A domain-less $boost would become a global boost on every page if emitted.
    text = "! Source: x\n$boost=2\n$boost=2,site=real.com\n$discard\n"
    rules = [r for _, r in parse_goggle_rules(text)]
    assert rules == [Rule("boost", 2, "real.com")]


def test_domain_status_from_ranking_collapses_duplicates_to_most_cautious(tmp_path: Path) -> None:
    csv_path = tmp_path / "ranking.csv"
    csv_path.write_text(
        "source_name,status,domain\n"
        "Reliable outlet,gr,EXAMPLE.com\n"   # uppercase normalizes to lowercase
        "Bad section,gu,example.com\n"        # same domain, more cautious wins
        "Clean,gr,other.org\n"
    )
    assert domain_status_from_ranking(csv_path) == {"example.com": "gu", "other.org": "gr"}


def test_seed_overlay_reproduces_full_current_corpus_after_merge() -> None:
    # Every current rule the base does not identically reproduce must survive the
    # round-trip through the seeded overlay (superset-preserving guarantee).
    base = {
        ("", "abcnews.com"): Rule("boost", 2, "abcnews.com"),
        ("", "google.com"): Rule("downrank", 2, "google.com"),
    }
    current = [
        Rule("boost", 2, "abcnews.com"),                          # reproduced by base
        Rule("boost", 2, "google.com"),                           # conflict -> overlay
        Rule("boost", 2, "manual.com"),                           # current-only -> overlay
        Rule("downrank", 2, "foxnews.com", prefix="/*science^"),  # path -> overlay
    ]
    overlay_text = seed_overlay(current, base)
    overlay = [r for _, r in load_overlay(overlay_text)]
    merged = merge_rules(base, overlay)
    current_keys = {rule_key(r) for r in current}
    assert current_keys <= set(merged), "a current rule was dropped"
    # Conflict resolves to the curated (current) value.
    assert merged[("", "google.com")].action == "boost"


# --- variant rendering -------------------------------------------------------


def test_seed_overlay_refuses_an_already_generated_goggle(tmp_path: Path) -> None:
    # Seeding from a generated file would pollute the overlay; the guard prevents it.
    ranking = tmp_path / "ranking.csv"
    ranking.write_text("source_name,status,domain\nX,gr,x.com\n")
    generated = tmp_path / "current.goggle"
    generated.write_text(f"{GENERATED_SECTION}\n$boost=2,site=x.com\n")
    with pytest.raises(SystemExit):
        main(["--seed-overlay", "--ranking", str(ranking), "--current", str(generated),
              "--overlay", str(tmp_path / "overlay.txt"), "--diff-out", str(tmp_path / "d.md")])


def test_build_reproduces_the_committed_goggles(tmp_path: Path) -> None:
    # The goggles are committed build artifacts: rebuilding from the committed
    # ranking + overlay must reproduce them exactly, or they have drifted.
    root = Path(__file__).resolve().parents[1]
    rc = main([
        "--ranking", str(root / "outputs" / "reliability_ranking.csv"),
        "--overlay", str(root / "goggle_overlay.txt"),
        "--outdir", str(tmp_path),
        "--citations", str(tmp_path / "absent.csv"),
        "--gaps-out", str(tmp_path / "gaps.csv"),
    ])
    assert rc == 0
    for name in ("wikipedia-reliable-sources.goggle", "wikipedia-reliable-sources-only.goggle"):
        assert (tmp_path / name).read_text() == (root / name).read_text(), f"{name} drifted"


def test_main_normal_build_writes_both_merged_variants(tmp_path: Path) -> None:
    ranking = tmp_path / "ranking.csv"
    ranking.write_text("source_name,status,domain\nGood,gr,good.com\nBad,d,bad.com\n")
    overlay = tmp_path / "overlay.txt"
    overlay.write_text("! Source: manual\n$boost=2,site=manual.com\n")
    rc = main([
        "--ranking", str(ranking),
        "--overlay", str(overlay),
        "--outdir", str(tmp_path),
        "--citations", str(tmp_path / "absent.csv"),  # skip gap report
        "--gaps-out", str(tmp_path / "gaps.csv"),
    ])
    assert rc == 0
    default = (tmp_path / "wikipedia-reliable-sources.goggle").read_text()
    only = (tmp_path / "wikipedia-reliable-sources-only.goggle").read_text()
    assert "$boost=2,site=good.com" in default      # base, gr -> boost
    assert "$discard,site=bad.com" in default        # base, d -> discard
    assert "$boost=2,site=manual.com" in default     # overlay merged in
    assert "\n$discard\n" in only                    # only-variant catch-all


def test_only_variant_adds_catch_all_discard() -> None:
    rules = [("! Source: x", Rule("boost", 2, "abcnews.com"))]
    only = render_goggle(rules, "only")
    default = render_goggle(rules, "default")
    assert "\n$discard\n" in only
    assert "\n$discard\n" not in default


def test_only_variant_comments_out_suppressed_google_domains() -> None:
    rules = [("! Source: x", Rule("boost", 2, "google.com"))]
    only = render_goggle(rules, "only")
    default = render_goggle(rules, "default")
    assert "! $boost=2,site=google.com" in only
    assert "\n$boost=2,site=google.com" in default


def test_default_header_names_the_default_variant() -> None:
    out = render_goggle([], "default")
    assert out.startswith("! name: Wikipedia reliable sources\n")


def test_only_header_names_the_only_variant() -> None:
    out = render_goggle([], "only")
    assert out.startswith("! name: Wikipedia reliable sources only\n")


# --- product/portal domain exclusion -----------------------------------------


def test_product_portal_domain_excluded_from_base_rules() -> None:
    # A product/portal entry (e.g. "Google Maps (Street View)" rated nc) that
    # resolves to a generic registrable domain must not produce a base site= rule.
    for domain in PRODUCT_PORTAL_DOMAINS:
        domain_status = {domain: "nc", "legit.com": "gr"}
        base = generate_base_rules(domain_status)
        assert ("", domain) not in base, f"{domain} should be excluded from base rules"
        assert ("", "legit.com") in base, "non-excluded domain must still get a rule"


def test_legitimate_domains_still_get_base_rules(tmp_path: Path) -> None:
    # Regression: PRODUCT_PORTAL_DOMAINS must not accidentally exclude ordinary
    # editorial domains. Domains that are not products/portals still produce a
    # base rule when read from the ranking CSV.
    csv_path = tmp_path / "ranking.csv"
    csv_path.write_text(
        "source_name,status,domain\n"
        "BBC,gr,bbc.co.uk\n"
        "NYT,gr,nytimes.com\n"
    )
    domain_status = domain_status_from_ranking(csv_path)
    base = generate_base_rules(domain_status)
    # Neither bbc.co.uk nor nytimes.com are in PRODUCT_PORTAL_DOMAINS
    assert ("", "bbc.co.uk") in base
    assert ("", "nytimes.com") in base


def test_product_portal_excludes_exact_domain_only() -> None:
    # Edge case: the exclusion matches the exact registrable domain only. A
    # product entry (google.com) is excluded, but its subdomains — which appear
    # as separate, distinguishable entries (maps./news.google.com) — must not be
    # swept up by the set. This guards a legitimate editorial source on a
    # subdomain of an excluded registrable domain.
    domain_status = {
        "google.com": "nc",
        "maps.google.com": "d",
        "news.google.com": "gr",
    }
    base = generate_base_rules(domain_status)
    # google.com excluded because it's in PRODUCT_PORTAL_DOMAINS
    assert ("", "google.com") not in base
    # Subdomains are distinct entries and must not be excluded by the set
    assert ("", "maps.google.com") in base
    assert ("", "news.google.com") in base


# --- safe-add pass (FA/GA-weighted proposals) --------------------------------


def _citations(fa: int = 0, ga: int = 0, total: int | None = None, articles: int = 0) -> dict:
    return {
        "total": total if total is not None else fa + ga,
        "fa": fa,
        "ga": ga,
        "articles": articles,
    }


def test_safe_add_proposes_domain_at_or_above_fa_threshold() -> None:
    citations = {"strong.com": _citations(fa=DEFAULT_SAFE_ADD_FA_THRESHOLD)}
    proposals = safe_add_candidates(citations, rated_domains=set(), overlay_domains=set())
    assert [p.domain for p in proposals] == ["strong.com"]


def test_safe_add_rejects_domain_below_fa_threshold_without_ga_route() -> None:
    citations = {"weak.com": _citations(fa=DEFAULT_SAFE_ADD_FA_THRESHOLD - 1)}
    proposals = safe_add_candidates(citations, rated_domains=set(), overlay_domains=set())
    assert proposals == []


def test_safe_add_ties_at_threshold_are_proposed() -> None:
    # A tie at the exact threshold qualifies (>=, not >).
    citations = {"tie.com": _citations(fa=DEFAULT_SAFE_ADD_FA_THRESHOLD)}
    proposals = safe_add_candidates(
        citations, rated_domains=set(), overlay_domains=set(), fa_threshold=200
    )
    assert any(p.domain == "tie.com" for p in proposals)
    citations = {"just_below.com": _citations(fa=199)}
    proposals = safe_add_candidates(
        citations, rated_domains=set(), overlay_domains=set(), fa_threshold=200
    )
    assert proposals == []


def test_safe_add_ga_route_requires_nonzero_fa_floor_and_ga_threshold() -> None:
    # GA is a secondary signal: it only qualifies a domain in combination with a
    # nonzero FA floor. A domain below the FA floor is never proposed on GA alone.
    citations = {
        "ga_only.com": _citations(fa=DEFAULT_SAFE_ADD_FA_FLOOR - 1, ga=10_000),
    }
    proposals = safe_add_candidates(citations, rated_domains=set(), overlay_domains=set())
    assert proposals == []


def test_safe_add_ga_route_qualifies_when_fa_floor_and_ga_threshold_met() -> None:
    citations = {
        "fa_ga.com": _citations(
            fa=DEFAULT_SAFE_ADD_FA_FLOOR, ga=DEFAULT_SAFE_ADD_GA_THRESHOLD
        ),
    }
    proposals = safe_add_candidates(citations, rated_domains=set(), overlay_domains=set())
    assert [p.domain for p in proposals] == ["fa_ga.com"]


def test_safe_add_ga_route_below_ga_threshold_is_rejected() -> None:
    citations = {
        "fa_low_ga.com": _citations(
            fa=DEFAULT_SAFE_ADD_FA_FLOOR, ga=DEFAULT_SAFE_ADD_GA_THRESHOLD - 1
        ),
    }
    proposals = safe_add_candidates(citations, rated_domains=set(), overlay_domains=set())
    assert proposals == []


def test_safe_add_fa_outweighs_ga_when_both_present() -> None:
    # A domain with FA alone above the primary threshold qualifies even with no GA.
    citations = {
        "fa_only.com": _citations(fa=DEFAULT_SAFE_ADD_FA_THRESHOLD, ga=0),
    }
    proposals = safe_add_candidates(citations, rated_domains=set(), overlay_domains=set())
    assert [p.domain for p in proposals] == ["fa_only.com"]


def test_safe_add_excludes_domain_already_rated() -> None:
    citations = {"rated.com": _citations(fa=DEFAULT_SAFE_ADD_FA_THRESHOLD)}
    proposals = safe_add_candidates(
        citations, rated_domains={"rated.com"}, overlay_domains=set()
    )
    assert proposals == []


def test_safe_add_excludes_domain_already_in_overlay() -> None:
    citations = {"overlaid.com": _citations(fa=DEFAULT_SAFE_ADD_FA_THRESHOLD)}
    proposals = safe_add_candidates(
        citations, rated_domains=set(), overlay_domains={"overlaid.com"}
    )
    assert proposals == []


def test_safe_add_excludes_product_portal_domains() -> None:
    for domain in PRODUCT_PORTAL_DOMAINS:
        citations = {domain: _citations(fa=DEFAULT_SAFE_ADD_FA_THRESHOLD)}
        proposals = safe_add_candidates(citations, rated_domains=set(), overlay_domains=set())
        assert proposals == [], f"{domain} must not be proposed (product/portal)"


def test_safe_add_excludes_non_editorial_domains() -> None:
    # Government/education/archive domains are filtered like the gap report.
    citations = {
        "example.gov": _citations(fa=DEFAULT_SAFE_ADD_FA_THRESHOLD),
        "archive.org": _citations(fa=DEFAULT_SAFE_ADD_FA_THRESHOLD),
    }
    proposals = safe_add_candidates(citations, rated_domains=set(), overlay_domains=set())
    assert proposals == []


def test_safe_add_heavily_cited_non_fa_ga_domain_is_not_proposed() -> None:
    # High total citations alone (no FA/GA weight) must not qualify.
    citations = {"popular_but_unvetted.com": _citations(fa=0, ga=0, total=1_000_000)}
    proposals = safe_add_candidates(citations, rated_domains=set(), overlay_domains=set())
    assert proposals == []


def test_safe_add_output_is_sorted_by_fa_then_domain() -> None:
    citations = {
        "b.com": _citations(fa=DEFAULT_SAFE_ADD_FA_THRESHOLD),
        "a.com": _citations(fa=DEFAULT_SAFE_ADD_FA_THRESHOLD + 100),
    }
    proposals = safe_add_candidates(citations, rated_domains=set(), overlay_domains=set())
    assert [p.domain for p in proposals] == ["a.com", "b.com"]


def test_safe_add_candidate_carries_citation_counts_and_action() -> None:
    citations = {
        "strong.com": _citations(
            fa=DEFAULT_SAFE_ADD_FA_THRESHOLD, ga=10, total=DEFAULT_SAFE_ADD_FA_THRESHOLD + 10
        ),
    }
    proposals = safe_add_candidates(citations, rated_domains=set(), overlay_domains=set())
    candidate = proposals[0]
    assert candidate == SafeAddCandidate(
        domain="strong.com",
        fa_citations=DEFAULT_SAFE_ADD_FA_THRESHOLD,
        ga_citations=10,
        total_citations=DEFAULT_SAFE_ADD_FA_THRESHOLD + 10,
        proposed_action="boost=2",
    )


def test_render_safe_add_overlay_seed_produces_boost_lines_with_header() -> None:
    candidates = [
        SafeAddCandidate(
            domain="strong.com",
            fa_citations=500,
            ga_citations=10,
            total_citations=510,
            proposed_action="boost=2",
        )
    ]
    text = render_safe_add_overlay_seed(candidates)
    assert text.startswith("!")  # header comment marks this as a proposal, not applied
    assert "proposal" in text.lower()
    assert "$boost=2,site=strong.com" in text


def test_render_safe_add_overlay_seed_empty_candidates_still_has_header() -> None:
    text = render_safe_add_overlay_seed([])
    assert text.startswith("!")
    assert ",site=" not in text


def test_main_safe_add_pass_skips_gracefully_without_citation_table(tmp_path: Path) -> None:
    # CI has no citation table (gitignored); the pass must not error, matching
    # the gap-report's graceful-skip behavior.
    ranking = tmp_path / "ranking.csv"
    ranking.write_text("source_name,status,domain\nGood,gr,good.com\n")
    rc = main([
        "--ranking", str(ranking),
        "--overlay", str(tmp_path / "missing_overlay.txt"),
        "--outdir", str(tmp_path),
        "--citations", str(tmp_path / "absent.csv"),
        "--gaps-out", str(tmp_path / "gaps.csv"),
        "--safe-add-candidates-out", str(tmp_path / "safe_add_candidates.csv"),
        "--safe-add-overlay-seed-out", str(tmp_path / "safe_add_overlay_seed.txt"),
    ])
    assert rc == 0
    assert not (tmp_path / "safe_add_candidates.csv").exists()
    assert not (tmp_path / "safe_add_overlay_seed.txt").exists()


def test_main_safe_add_pass_writes_outputs_when_citations_present(tmp_path: Path) -> None:
    ranking = tmp_path / "ranking.csv"
    ranking.write_text("source_name,status,domain\nGood,gr,good.com\n")
    citations = tmp_path / "citations.csv"
    citations.write_text(
        "domain_url,suffix_url,total_citations,fa_citations,ga_citations,distinct_articles\n"
        f"strong,com,{DEFAULT_SAFE_ADD_FA_THRESHOLD + 10},{DEFAULT_SAFE_ADD_FA_THRESHOLD},5,100\n"
        "good,com,50,10,5,20\n"  # already rated; must be excluded
    )
    candidates_out = tmp_path / "safe_add_candidates.csv"
    seed_out = tmp_path / "safe_add_overlay_seed.txt"
    rc = main([
        "--ranking", str(ranking),
        "--overlay", str(tmp_path / "missing_overlay.txt"),
        "--outdir", str(tmp_path),
        "--citations", str(citations),
        "--gaps-out", str(tmp_path / "gaps.csv"),
        "--safe-add-candidates-out", str(candidates_out),
        "--safe-add-overlay-seed-out", str(seed_out),
    ])
    assert rc == 0
    candidates_text = candidates_out.read_text()
    assert "strong.com" in candidates_text
    assert "good.com" not in candidates_text
    seed_text = seed_out.read_text()
    assert "$boost=2,site=strong.com" in seed_text


def test_safe_add_pass_does_not_change_built_goggle_output(tmp_path: Path) -> None:
    # The safe-add pass is purely a reviewable proposal; it must never mutate the
    # rendered goggle files themselves.
    ranking = tmp_path / "ranking.csv"
    ranking.write_text("source_name,status,domain\nGood,gr,good.com\n")
    citations = tmp_path / "citations.csv"
    citations.write_text(
        "domain_url,suffix_url,total_citations,fa_citations,ga_citations,distinct_articles\n"
        f"strong,com,{DEFAULT_SAFE_ADD_FA_THRESHOLD + 10},{DEFAULT_SAFE_ADD_FA_THRESHOLD},5,100\n"
    )

    def build(citations_path: Path) -> tuple[str, str]:
        outdir = tmp_path / citations_path.stem
        outdir.mkdir()
        main([
            "--ranking", str(ranking),
            "--overlay", str(tmp_path / "missing_overlay.txt"),
            "--outdir", str(outdir),
            "--citations", str(citations_path),
            "--gaps-out", str(outdir / "gaps.csv"),
            "--safe-add-candidates-out", str(outdir / "safe_add_candidates.csv"),
            "--safe-add-overlay-seed-out", str(outdir / "safe_add_overlay_seed.txt"),
        ])
        default = (outdir / "wikipedia-reliable-sources.goggle").read_text()
        only = (outdir / "wikipedia-reliable-sources-only.goggle").read_text()
        return default, only

    absent = tmp_path / "absent.csv"
    with_table = build(citations)
    without_table = build(absent)
    assert with_table == without_table
