# Goggle generator diff

What the data-driven base produces versus the committed goggle.

- Base rules generated: **369**
- Generated-only (new from data): **0**
- Current-only, path-qualified (overlay `# path-qualified`): **444**
- Current-only, plain (overlay `# manual`): **3210**
- Conflicts (curated value kept; review): **22**
- Total preserved in overlay: **3676**

## Generated-only (additions the automation contributes)

_none_

## Conflicts (base disagrees with the committed goggle)

| domain | base | committed |
|---|---|---|
| allmovie.com | `$discard,site=allmovie.com` | `$boost=2,site=allmovie.com` |
| astronautix.com | `$downrank=2,site=astronautix.com` | `$boost=2,site=astronautix.com` |
| ballotpedia.org | `$boost=2,site=ballotpedia.org` | `$downrank=2,site=ballotpedia.org` |
| catholic-hierarchy.org | `$discard,site=catholic-hierarchy.org` | `$boost=2,site=catholic-hierarchy.org` |
| cnet.com | `$discard,site=cnet.com` | `$boost=2,site=cnet.com` |
| encyclopedia.com | `$downrank=2,site=encyclopedia.com` | `$boost=2,site=encyclopedia.com` |
| forbes.com | `$downrank=2,site=forbes.com` | `$discard,site=forbes.com` |
| foxnews.com | `$discard,site=foxnews.com` | `$boost=2,site=foxnews.com` |
| google.com | `$downrank=2,site=google.com` | `$boost=2,site=google.com` |
| heritage.org | `$discard,site=heritage.org` | `$boost=2,site=heritage.org` |
| hopenothate.org.uk | `$boost=2,site=hopenothate.org.uk` | `$downrank=2,site=hopenothate.org.uk` |
| huffpost.com | `$discard,site=huffpost.com` | `$downrank=2,site=huffpost.com` |
| investopedia.com | `$discard,site=investopedia.com` | `$downrank=2,site=investopedia.com` |
| mashable.com | `$discard,site=mashable.com` | `$downrank=2,site=mashable.com` |
| rollingstone.com | `$discard,site=rollingstone.com` | `$boost=2,site=rollingstone.com` |
| sciencebasedmedicine.org | `$downrank=2,site=sciencebasedmedicine.org` | `$boost=2,site=sciencebasedmedicine.org` |
| si.com | `$downrank=2,site=si.com` | `$boost=2,site=si.com` |
| sixthtone.com | `$discard,site=sixthtone.com` | `$downrank=2,site=sixthtone.com` |
| straitstimes.com | `$boost=2,site=straitstimes.com` | `$downrank=2,site=straitstimes.com` |
| thejc.com | `$downrank=2,site=thejc.com` | `$boost=2,site=thejc.com` |
| venturebeat.com | `$downrank=2,site=venturebeat.com` | `$boost=2,site=venturebeat.com` |
| zdnet.com | `$discard,site=zdnet.com` | `$boost=2,site=zdnet.com` |

## Current-only — preserved in the overlay

Path-qualified (444) and plain (3210) rules the base cannot derive. These live in `goggle_overlay.txt`; the path-qualified set is the target for future generation.

