"""Placeholder script to download article wikitext."""

from pathlib import Path


def fetch_wikitext(article_list: list, output_dir: Path):
    """Fetch wikitext for each article in `article_list`."""
    output_dir.mkdir(parents=True, exist_ok=True)
    for article in article_list:
        # TODO: Implement real fetching logic
        (output_dir / f"{article}.txt").write_text("")


if __name__ == "__main__":
    fetch_wikitext([], Path("data/raw/wikitext"))
