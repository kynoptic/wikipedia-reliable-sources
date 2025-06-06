"""Placeholder for fetching lists of good and featured articles."""

from pathlib import Path


def fetch_good_and_featured(output_dir: Path):
    """Fetch article lists and write them under `output_dir`."""
    output_dir.mkdir(parents=True, exist_ok=True)
    # TODO: Implement fetching logic
    (output_dir / "good_articles.json").write_text("[]")
    (output_dir / "featured_articles.json").write_text("[]")


if __name__ == "__main__":
    fetch_good_and_featured(Path("data/raw"))
