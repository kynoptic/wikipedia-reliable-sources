# Goggle generator diff

What the data-driven base produces versus the committed goggle.

- Base rules generated: **2**
- Generated-only (new from data): **2**
- Current-only, path-qualified (overlay `# path-qualified`): **0**
- Current-only, plain (overlay `# manual`): **1**
- Conflicts (curated value kept; review): **0**
- Total preserved in overlay: **1**

## Generated-only (additions the automation contributes)

- `$discard,site=bad.com`
- `$boost=2,site=good.com`

## Conflicts (base disagrees with the committed goggle)

None.

## Current-only — preserved in the overlay

Path-qualified (0) and plain (1) rules the base cannot derive. These live in `goggle_overlay.txt`; the path-qualified set is the target for future generation.
