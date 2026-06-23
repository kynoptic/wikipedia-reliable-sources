"""Restore the raw citation datasets from their published archives.

Each bulk file in ``data/raw/citations/`` originates from a durable public
archive (Zenodo, figshare, or a GitHub release). This script re-downloads,
decompresses, and renames them to the project's convention, so the dumps never
need to be mirrored in git. See ``data/raw/citations/README.md`` for full
provenance.

Not handled here: the Featured/Good article lists, which are a point-in-time
snapshot — regenerate current ones with ``python -m core.fetch_articles``.

Usage::

    python -m scripts.fetch_citation_data            # fetch any missing files
    python -m scripts.fetch_citation_data --force    # re-fetch even if present
    python -m scripts.fetch_citation_data --check     # verify URLs, download nothing
"""

from __future__ import annotations

import argparse
import bz2
import gzip
import shutil
import sys
import tarfile
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path

import requests

from scripts.common import HEADERS

DEST_DIR = Path("data/raw/citations")
_CHUNK = 1 << 20  # 1 MiB


@dataclass(frozen=True)
class Dataset:
    """A published dataset file and how to restore it locally."""

    target: str  # final filename written under DEST_DIR
    url: str
    archive: str  # "bz2", "gz", or "tar.gz"
    source: str  # human-readable provenance
    member: str | None = None  # file to extract from a tar.gz


DATASETS: list[Dataset] = [
    Dataset(
        "zenodo-55004/enwiki_2016-06-01_CS1_citations.tsv",
        "https://zenodo.org/api/records/55004/files/"
        "enwiki_2016-06-01_CS1_citations.tsv.bz2/content",
        "bz2",
        "Delpeuch, Structured citations in the English Wikipedia (Zenodo 55004)",
    ),
    Dataset(
        "figshare-1299540/enwiki.tsv",
        "https://ndownloader.figshare.com/files/10843094",
        "tar.gz",
        "Halfaker et al., Citations with identifiers in Wikipedia (figshare 1299540)",
        member="enwiki.tsv",
    ),
    Dataset(
        "figshare-6819710/enwiki.tsv",
        "https://ndownloader.figshare.com/files/12403163",
        "gz",
        "Redi & Taraborelli, Accessibility and topics of citations (figshare 6819710)",
    ),
    Dataset(
        "figshare-4296476/enwiki_20161101_headings.tsv",
        "https://ndownloader.figshare.com/files/7007114",
        "bz2",
        "Farooqui (WMF), Wikipedia Article Section Headings (figshare 4296476)",
    ),
    Dataset(
        "corradomonti/page2cat.tsv",
        "https://github.com/corradomonti/wikipedia-categories/"
        "releases/download/enwiki-20160407/page2cat.tsv.gz",
        "gz",
        "corradomonti/wikipedia-categories (enwiki-20160407 release)",
    ),
]

# Opt-in only: the 2023 dataset is a ~7.3 GB zip of a partitioned Parquet
# directory, fetched separately from the core re-fetchable set above.
CURRENT_2023 = Dataset(
    "zenodo-8107239/en_citations.parquet",
    "https://zenodo.org/api/records/8107239/files/en_citations.zip/content",
    "zip-dir",
    "Kokash & Colavizza, Classified Citations from English Wikipedia 2023 (Zenodo 8107239)",
)


def _download(url: str, dest: Path) -> None:
    """Stream ``url`` to ``dest``."""
    with requests.get(url, headers=HEADERS, stream=True, timeout=60) as resp:
        resp.raise_for_status()
        with dest.open("wb") as f:
            for chunk in resp.iter_content(_CHUNK):
                f.write(chunk)


def _decompress(src: Path, archive: str, dest: Path, member: str | None) -> None:
    """Decompress ``src`` (``archive`` format) to ``dest``."""
    if archive == "bz2":
        with bz2.open(src, "rb") as f_in, dest.open("wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
    elif archive == "gz":
        with gzip.open(src, "rb") as f_in, dest.open("wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
    elif archive == "tar.gz":
        with tarfile.open(src, "r:gz") as tar:
            name = member or _sole_member(tar)
            extracted = tar.extractfile(name)
            if extracted is None:
                raise ValueError(f"{member!r} not found in {src.name}")
            with extracted as f_in, dest.open("wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
    else:
        raise ValueError(f"unknown archive format: {archive!r}")


def _sole_member(tar: tarfile.TarFile) -> str:
    files = [m.name for m in tar.getmembers() if m.isfile()]
    if len(files) != 1:
        raise ValueError(f"expected one file in archive, found {len(files)}")
    return files[0]


def _extract_zip_dir(src: Path, out: Path) -> None:
    """Extract a zip whose top-level directory is named ``out.name`` into place."""
    if out.exists():
        shutil.rmtree(out)
    with zipfile.ZipFile(src) as zf:
        zf.extractall(out.parent)


def restore_dataset(ds: Dataset, dest_dir: Path, force: bool = False) -> bool:
    """Restore one dataset. Returns ``True`` if it was fetched, ``False`` if skipped."""
    out = dest_dir / ds.target
    if out.exists() and not force:
        print(f"skip   {ds.target} (already present)")
        return False
    out.parent.mkdir(parents=True, exist_ok=True)
    print(f"fetch  {ds.target}\n         from {ds.source}")
    with tempfile.NamedTemporaryFile(dir=out.parent, delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        _download(ds.url, tmp_path)
        if ds.archive == "zip-dir":
            _extract_zip_dir(tmp_path, out)
        else:
            partial = out.with_suffix(out.suffix + ".part")
            _decompress(tmp_path, ds.archive, partial, ds.member)
            partial.replace(out)
    finally:
        tmp_path.unlink(missing_ok=True)
    return True


def check_url(ds: Dataset) -> bool:
    """Confirm a dataset URL is reachable without downloading its body."""
    with requests.get(ds.url, headers=HEADERS, stream=True, timeout=60) as resp:
        ok = resp.ok
        size = resp.headers.get("Content-Length", "?")
    print(f"{'ok  ' if ok else 'FAIL'}  {resp.status_code}  {size:>12} bytes  {ds.target}")
    return ok


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="re-fetch even if present")
    parser.add_argument(
        "--check", action="store_true", help="verify URLs are reachable, download nothing"
    )
    parser.add_argument(
        "--fetch-2023",
        action="store_true",
        help="also fetch the ~7.3 GB 2023 Parquet dataset (Zenodo 8107239)",
    )
    args = parser.parse_args(argv)

    datasets = list(DATASETS)
    if args.fetch_2023:
        datasets.append(CURRENT_2023)

    if args.check:
        return 0 if all([check_url(ds) for ds in datasets]) else 1

    fetched = sum(restore_dataset(ds, DEST_DIR, args.force) for ds in datasets)
    print(f"\nDone — {fetched} fetched, {len(datasets) - fetched} already present.")
    print("Regenerate Featured/Good article lists with: python -m core.fetch_articles")
    return 0


if __name__ == "__main__":
    sys.exit(main())
