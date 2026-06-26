"""Generate the Brave Search Goggle files from Wikipedia reliability data.

The goggles are a build artifact of the rating pipeline, not a hand-maintained
file. Generation has two layers:

* a *base* layer derived from the data — one ``site=`` rule per rated domain,
  with the reliability status mapped to a Goggle action; and
* a curated *overlay* (``goggle_overlay.txt``) holding rules the data cannot yet
  derive: per-topic path-qualified rules (``/*science^...``) and domains added
  by hand or mined from Featured/Good-article citations.

The build merges base and overlay (overlay wins on conflict) and renders both
goggle variants. A diff report records what the generator is missing relative to
the committed goggle; coverage gaps (heavily-cited but unrated domains) are
reported for human review, never auto-added.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from core.bridge_reliability import (
    UNRELIABLE,
    _most_cautious,
    coverage_gaps,
    load_domain_citations,
)


@dataclass(frozen=True)
class Rule:
    """A single Goggle instruction.

    ``prefix`` is the path-pattern segment preceding ``$`` (e.g. ``/*science^``),
    empty for a plain site rule. ``domain`` is the ``site=`` value, empty for the
    bare catch-all ``$discard``. ``value`` is the boost/downrank magnitude, ``None``
    for ``$discard``.
    """

    action: str
    value: int | None
    domain: str
    prefix: str = ""


# Reliability status (RSP legend) -> (Goggle action, value). Marginally reliable
# (``m``) and unknown codes map to no rule, matching the hand-maintained goggles.
STATUS_ACTION: dict[str, tuple[str, int | None]] = {
    "gr": ("boost", 2),
    "nc": ("downrank", 2),
    "gu": ("discard", None),
    "d": ("discard", None),
}

# Google rules the "-only" variant comments out. With the rules removed, the
# whitelist catch-all $discard drops these domains entirely — including
# google.com, which the base rates `nc` (downrank) but which becomes discarded
# in the whitelist variant, matching the hand-maintained goggle's decision.
SUPPRESS_IN_ONLY = frozenset(
    {
        "google.com",
        "news.google.com",
        "scholar.google.com",
        "news.google.co.nz",
        "maps.google.com",
    }
)

VARIANTS: dict[str, dict] = {
    "default": {
        "filename": "wikipedia-reliable-sources.goggle",
        "name": "Wikipedia reliable sources",
        "description": (
            "Aligns with Wikipedia community consensus to elevate reliable "
            "sources, reduce the ranking of contentious sources, and eliminate "
            "unreliable sources."
        ),
        "catch_all": False,
        "suppress": frozenset(),
    },
    "only": {
        "filename": "wikipedia-reliable-sources-only.goggle",
        "name": "Wikipedia reliable sources only",
        "description": (
            "Aligns with Wikipedia community consensus to elevate reliable "
            "sources and reduce the ranking of contentious sources."
        ),
        "catch_all": True,
        "suppress": SUPPRESS_IN_ONLY,
    },
}

GENERATED_SECTION = "! Source: Generated from Wikipedia reliability data"

_RULE_RE = re.compile(
    r"^(?P<prefix>\S*\^)?"
    r"\$(?P<action>boost|downrank|discard)"
    r"(?:=(?P<value>\d+))?"
    r"(?:,site=(?P<domain>[^,\s]+))?$"
)

# A dotted hostname of alphanumeric/hyphen labels. Rejects values that would
# break Goggle `site=` syntax (spaces, `$`, `=`, `,`, `/`) or carry no TLD. This
# is a syntax guard, not a real-TLD check: a syntactically valid but wrong
# resolution (e.g. ``ms.now`` for MSNBC) passes and must be fixed upstream.
_VALID_DOMAIN_RE = re.compile(
    r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?(\.[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)+$"
)


def _is_valid_domain(domain: str) -> bool:
    return bool(_VALID_DOMAIN_RE.match(domain))


# --- rule grammar ------------------------------------------------------------


def rule_key(rule: Rule) -> tuple[str, str]:
    """Identity for merge/diff: a domain may carry one plain rule plus distinct
    path-qualified rules, so both ``prefix`` and ``domain`` matter."""
    return (rule.prefix, rule.domain)


def render_rule(rule: Rule) -> str:
    head = f"${rule.action}"
    if rule.value is not None:
        head += f"={rule.value}"
    site = f",site={rule.domain}" if rule.domain else ""
    return f"{rule.prefix}{head}{site}"


def parse_rule_line(line: str) -> Rule | None:
    """Parse one Goggle line into a :class:`Rule`, or ``None`` for comments,
    blanks, and anything that is not a rule."""
    text = line.strip()
    if not text or text.startswith("!") or text.startswith("#"):
        return None
    match = _RULE_RE.match(text)
    if not match:
        return None
    value = match.group("value")
    return Rule(
        action=match.group("action"),
        value=int(value) if value is not None else None,
        domain=match.group("domain") or "",
        prefix=match.group("prefix") or "",
    )


def parse_goggle_rules(text: str) -> list[tuple[str, Rule]]:
    """Parse a goggle/overlay file into ``(section_comment, rule)`` pairs.

    The bare catch-all ``$discard`` is a per-variant structural rule, not a source
    rule, so it is excluded from the corpus.
    """
    section = ""
    pairs: list[tuple[str, Rule]] = []
    for line in text.splitlines():
        if line.startswith("! Source"):
            section = line
            continue
        rule = parse_rule_line(line)
        # Require a domain: this drops the bare catch-all ``$discard`` (a
        # variant-structural rule, re-added at render time) and rejects a
        # domain-less ``$boost``/``$downrank`` that would otherwise apply globally.
        if rule and rule.domain:
            pairs.append((section, rule))
    return pairs


# --- base generation ---------------------------------------------------------


def generate_base_rules(domain_status: dict[str, str]) -> dict[tuple[str, str], Rule]:
    """Map each ``{domain: status}`` entry to a plain ``site=`` rule.

    Domains rated ``m`` (marginal) or with an unrecognized status get no rule.
    """
    rules: dict[tuple[str, str], Rule] = {}
    for domain, status in domain_status.items():
        mapped = STATUS_ACTION.get(status)
        if mapped is None:
            continue
        action, value = mapped
        rule = Rule(action=action, value=value, domain=domain)
        rules[rule_key(rule)] = rule
    return rules


def domain_status_from_resolution(
    name_status: dict[str, str], name_domains: dict[str, set[str]]
) -> dict[str, str]:
    """Collapse resolved name->domain mappings to one most-cautious status per
    domain, so a domain unreliable for any source-split is never boosted."""
    by_domain: dict[str, list[str]] = defaultdict(list)
    for name, status in name_status.items():
        for domain in name_domains.get(name, set()):
            by_domain[domain.lower()].append(status)
    return {domain: _most_cautious(statuses) for domain, statuses in by_domain.items()}


def domain_status_from_ranking(path: Path) -> dict[str, str]:
    """Read ``{domain: status}`` from a committed ``reliability_ranking.csv``.

    The ranking is already collapsed per domain by the bridge; duplicate domains
    (should not occur) resolve to the most cautious status.
    """
    out: dict[str, str] = {}
    skipped: list[str] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            domain = (row.get("domain") or "").strip().lower()
            status = (row.get("status") or "").strip()
            if not domain or not status:
                continue
            if not _is_valid_domain(domain):
                skipped.append(domain)
                continue
            out[domain] = _most_cautious([status, out[domain]]) if domain in out else status
    if skipped:
        print(
            f"build_goggle: skipped {len(skipped)} malformed domain(s): "
            f"{', '.join(sorted(set(skipped)))}",
            file=sys.stderr,
        )
    return out


# --- merge -------------------------------------------------------------------


def merge_rules(
    base: dict[tuple[str, str], Rule], overlay: list[Rule]
) -> dict[tuple[str, str], Rule]:
    """Merge base and overlay rules; overlay wins on an identical key."""
    merged = dict(base)
    for rule in overlay:
        merged[rule_key(rule)] = rule
    return merged


def load_overlay(text: str) -> list[tuple[str, Rule]]:
    """Parse the curated overlay file into ``(section, rule)`` pairs.

    Overlay domains are not run through ``_is_valid_domain``: the overlay is
    pre-audited, source-controlled curation, and it carries hand rules the data
    cannot derive (e.g. the single-label ``site=letour``). Validating here would
    drop such rules and break the superset guarantee. Domain validation is for the
    untrusted CSV data layer only.
    """
    return parse_goggle_rules(text)


# --- diff --------------------------------------------------------------------


@dataclass
class Diff:
    generated_only: list[Rule] = field(default_factory=list)
    current_only_plain: list[Rule] = field(default_factory=list)
    current_only_path: list[Rule] = field(default_factory=list)
    conflicts: list[tuple[Rule, Rule]] = field(default_factory=list)


def diff_rules(base: dict[tuple[str, str], Rule], current: list[Rule]) -> Diff:
    """Classify the delta between the generated base and the committed goggle.

    Buckets: ``generated_only`` (base produces, goggle lacks), ``current_only_*``
    (goggle has, base cannot derive — split by path-qualified vs plain), and
    ``conflicts`` (same key, different action — ``(base_rule, current_rule)``).
    """
    current_by_key = {rule_key(rule): rule for rule in current}
    diff = Diff(generated_only=[base[key] for key in base if key not in current_by_key])
    for key, current_rule in current_by_key.items():
        base_rule = base.get(key)
        if base_rule is None:
            target = diff.current_only_path if current_rule.prefix else diff.current_only_plain
            target.append(current_rule)
        elif base_rule.action != current_rule.action or base_rule.value != current_rule.value:
            diff.conflicts.append((base_rule, current_rule))
    diff.generated_only.sort(key=lambda r: r.domain)
    diff.current_only_plain.sort(key=lambda r: r.domain)
    diff.current_only_path.sort(key=lambda r: (r.domain, r.prefix))
    diff.conflicts.sort(key=lambda pair: pair[1].domain)
    return diff


def render_diff_md(diff: Diff, base_count: int) -> str:
    current_only = len(diff.current_only_plain) + len(diff.current_only_path)
    lines = [
        "# Goggle generator diff",
        "",
        "What the data-driven base produces versus the committed goggle.",
        "",
        f"- Base rules generated: **{base_count}**",
        f"- Generated-only (new from data): **{len(diff.generated_only)}**",
        f"- Current-only, path-qualified (overlay `# path-qualified`): **{len(diff.current_only_path)}**",
        f"- Current-only, plain (overlay `# manual`): **{len(diff.current_only_plain)}**",
        f"- Conflicts (curated value kept; review): **{len(diff.conflicts)}**",
        f"- Total preserved in overlay: **{current_only + len(diff.conflicts)}**",
        "",
        "## Generated-only (additions the automation contributes)",
        "",
    ]
    lines += [f"- `{render_rule(r)}`" for r in diff.generated_only] or ["None."]
    lines += ["", "## Conflicts (base disagrees with the committed goggle)", ""]
    if diff.conflicts:
        lines.append("| domain | base | committed |")
        lines.append("|---|---|---|")
        lines += [
            f"| {cur.domain} | `{render_rule(base)}` | `{render_rule(cur)}` |"
            for base, cur in diff.conflicts
        ]
    else:
        lines.append("None.")
    lines += [
        "",
        "## Current-only — preserved in the overlay",
        "",
        f"Path-qualified ({len(diff.current_only_path)}) and plain ({len(diff.current_only_plain)}) "
        "rules the base cannot derive. These live in `goggle_overlay.txt`; the path-qualified set "
        "is the target for future generation.",
    ]
    return "\n".join(lines) + "\n"


# --- overlay seed ------------------------------------------------------------


def seed_overlay(current: list[Rule], base: dict[tuple[str, str], Rule]) -> str:
    """Produce overlay text from every current rule the base does not reproduce.

    A current rule is kept when the base lacks its key (current-only) or maps the
    key to a different action (conflict — the curated value wins). This guarantees
    ``merge(base, overlay)`` is a superset of the current corpus.
    """
    path_rules: list[Rule] = []
    manual_rules: list[Rule] = []
    conflict_rules: list[Rule] = []
    seen: set[tuple[str, str]] = set()
    for rule in current:
        key = rule_key(rule)
        if key in seen:  # the hand-maintained goggle carries duplicate lines
            continue
        seen.add(key)
        base_rule = base.get(key)
        if base_rule is not None and base_rule.action == rule.action and base_rule.value == rule.value:
            continue
        if base_rule is not None:
            conflict_rules.append(rule)
        elif rule.prefix:
            path_rules.append(rule)
        else:
            manual_rules.append(rule)

    lines = [
        "! Curated overlay — rules not yet derivable from the rating data.",
        "! Regenerate the base; hand-edit rules here. Goal: shrink this file over time.",
        "",
        "! Source: path-qualified (per-topic nuance; target for future generation)",
    ]
    lines += [render_rule(r) for r in sorted(path_rules, key=lambda r: (r.domain, r.prefix))]
    lines += ["", "! Source: manual (FA/GA-mined or hand-added; not in rated tables)"]
    lines += [render_rule(r) for r in sorted(manual_rules, key=lambda r: r.domain)]
    lines += ["", "! Source: conflicts (base disagrees; curated value kept — review)"]
    lines += [render_rule(r) for r in sorted(conflict_rules, key=lambda r: r.domain)]
    return "\n".join(lines) + "\n"


# --- render ------------------------------------------------------------------


def _header_lines(variant: str) -> list[str]:
    cfg = VARIANTS[variant]
    return [
        f"! name: {cfg['name']}",
        f"! description: {cfg['description']}",
        "! public: false",
        "! author: Wikipedia community",
        "",
        "! Uses reliability ratings from:",
        "!       Wikipedia:Reliable_sources/Perennial_sources",
        "!       WikiProject_Video_games/Sources, WikiProject_Video_games/Search_engine",
        "!       Wikipedia:WikiProject_Film/Resources",
        "!       Wikipedia:WikiProject_Albums/Sources",
        "!       Wikipedia:WikiProject_Christian_music/Sources",
        "!       Wikipedia:WikiProject_Professional_wrestling/Sources",
        "!       Wikipedia:WikiProject_Korea/Reliable_sources",
        "!       Sources often used in featured articles (FA) and good articles (GA)",
        "",
        '! $boost=2    - "Generally reliable" and "Reliable"',
        '! $downrank=2 - "No consensus"',
        '! $discard    - "Unreliable", "Blacklisted", "Deprecated"',
    ]


def render_goggle(ordered_rules: list[tuple[str, Rule]], variant: str) -> str:
    """Render the goggle text for a variant from section-tagged rules."""
    cfg = VARIANTS[variant]
    lines = _header_lines(variant)
    lines.append("")
    if cfg["catch_all"]:
        lines += ["! Exclude any results that do not match", "$discard", ""]
    suppress = cfg["suppress"]
    section = None
    for rule_section, rule in ordered_rules:
        if rule_section and rule_section != section:
            lines.append(rule_section)
            section = rule_section
        rendered = render_rule(rule)
        lines.append(f"! {rendered}" if rule.domain in suppress else rendered)
    return "\n".join(lines) + "\n"


def build_ordered_rules(
    base: dict[tuple[str, str], Rule], overlay_pairs: list[tuple[str, Rule]]
) -> list[tuple[str, Rule]]:
    """Order rules for rendering: generated base first (overlay-overridden keys
    removed), then the overlay sections in file order."""
    overlay_keys = {rule_key(rule) for _, rule in overlay_pairs}
    generated = sorted(
        (rule for key, rule in base.items() if key not in overlay_keys),
        key=lambda r: r.domain,
    )
    ordered = [(GENERATED_SECTION, rule) for rule in generated]
    ordered.extend(overlay_pairs)
    return ordered


# --- CLI ---------------------------------------------------------------------


def _write_gap_report(citations_path: Path, rated_domains: set[str], out_path: Path, limit: int) -> int:
    citations = load_domain_citations(citations_path)
    gaps = coverage_gaps(citations, rated_domains, limit)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["domain", "total_citations", "fa_citations", "ga_citations", "distinct_articles"]
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(gaps)
    return len(gaps)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ranking", type=Path, default=Path("outputs/reliability_ranking.csv"))
    parser.add_argument("--overlay", type=Path, default=Path("goggle_overlay.txt"))
    parser.add_argument("--outdir", type=Path, default=Path("."))
    parser.add_argument(
        "--current",
        type=Path,
        default=Path("wikipedia-reliable-sources.goggle"),
        help="Goggle compared against the base for the diff report.",
    )
    parser.add_argument("--diff-out", type=Path, default=Path("outputs/goggle_diff.md"))
    parser.add_argument(
        "--citations",
        type=Path,
        default=Path("data/processed/citations_2023_by_domain.csv"),
        help="Per-domain citation table for the coverage-gap report.",
    )
    parser.add_argument("--gaps-out", type=Path, default=Path("outputs/goggle_gap_candidates.csv"))
    parser.add_argument("--top", type=int, default=50)
    parser.add_argument(
        "--seed-overlay",
        action="store_true",
        help="Rewrite the overlay from the current goggle, then exit.",
    )
    args = parser.parse_args(argv)

    domain_status = domain_status_from_ranking(args.ranking)
    base = generate_base_rules(domain_status)

    # Seeding compares the base against the pristine hand-maintained goggle and
    # writes both the overlay and the diff report. After the first generated build
    # overwrites the goggle, that comparison no longer exists, so the diff is a
    # seed-time artifact — the normal build below does not regenerate it.
    if args.seed_overlay:
        current_text = args.current.read_text(encoding="utf-8")
        if GENERATED_SECTION in current_text:
            parser.error(
                f"{args.current} is already a generated goggle. Seeding is a one-time "
                "bootstrap that must read the pristine hand-maintained file; restore it "
                f"first (e.g. `git checkout HEAD -- {args.current}`)."
            )
        current = [rule for _, rule in parse_goggle_rules(current_text)]
        diff = diff_rules(base, current)
        args.diff_out.parent.mkdir(parents=True, exist_ok=True)
        args.diff_out.write_text(render_diff_md(diff, len(base)), encoding="utf-8")
        args.overlay.write_text(seed_overlay(current, base), encoding="utf-8")
        print(
            f"Seeded {args.overlay} and {args.diff_out} "
            f"(generated_only={len(diff.generated_only)}, path={len(diff.current_only_path)}, "
            f"manual={len(diff.current_only_plain)}, conflicts={len(diff.conflicts)})"
        )
        return 0

    overlay_pairs = (
        load_overlay(args.overlay.read_text(encoding="utf-8")) if args.overlay.exists() else []
    )
    ordered = build_ordered_rules(base, overlay_pairs)
    for variant, cfg in VARIANTS.items():
        (args.outdir / cfg["filename"]).write_text(render_goggle(ordered, variant), encoding="utf-8")

    if args.citations.exists():
        gap_count = _write_gap_report(args.citations, set(domain_status), args.gaps_out, args.top)
    else:
        gap_count = 0

    print(f"base={len(base)} overlay={len(overlay_pairs)} gaps={gap_count}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
