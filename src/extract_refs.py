"""Extract citation URLs from article wikitext files."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List

import mwparserfromhell

URL_RE = re.compile(r"https?://[^\s\]\|><]+")


def parse_refs_from_text(text: str) -> List[str]:
    """Return a list of citation URLs from a block of wikitext."""
    code = mwparserfromhell.parse(text)
    urls: List[str] = []
    # links within <ref> tags
    for tag in code.filter_tags(matches=lambda n: n.tag.lower() == "ref"):
        urls.extend(URL_RE.findall(str(tag.contents)))
    # bare external links
    for link in code.ifilter_external_links():
        urls.append(str(link.url))
    return urls


def extract_references(wikitext_dir: Path, output_path: Path) -> None:
    """Extract citation references from wikitext files."""
    refs = []
    for file in wikitext_dir.glob("*.txt"):
        text = file.read_text()
        for url in parse_refs_from_text(text):
            refs.append({"article": file.stem, "url": url})
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(refs, indent=2))


if __name__ == "__main__":
    extract_references(Path("data/raw/wikitext"), Path("data/processed/refs_extracted.json"))
