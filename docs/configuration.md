# Configuration Guide

Several scripts use small configuration files. Edit these to customize behavior.

## `data/alias_map.json`
Maps short hostnames to their canonical domains for URL normalization. Each key is the alias and the value is the canonical form.

Example:
```json
{
  "nyti.ms": "nytimes.com"
}
```

## `revision_ids.json`
Created by `scripts/update_checker.py` to store the last seen revision ID for each perennial sources subpage.
