import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.extract_refs import parse_refs_from_text


def test_parse_refs_from_text():
    wikitext = "Sample <ref>{{cite web|url=https://example.com/foo}}</ref> more text <ref>See [https://example.org bar]</ref>"
    urls = parse_refs_from_text(wikitext)
    assert "https://example.com/foo" in urls
    assert "https://example.org" in urls
