import bz2
import gzip
import io
import sys
import tarfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.fetch_citation_data as fcd
from scripts.fetch_citation_data import Dataset, _decompress, restore_dataset


def test_decompress_bz2(tmp_path: Path) -> None:
    src = tmp_path / "x.bz2"
    src.write_bytes(bz2.compress(b"hello\tworld\n"))
    out = tmp_path / "x.tsv"
    _decompress(src, "bz2", out, None)
    assert out.read_bytes() == b"hello\tworld\n"


def test_decompress_gz(tmp_path: Path) -> None:
    src = tmp_path / "x.gz"
    src.write_bytes(gzip.compress(b"a\tb\n"))
    out = tmp_path / "x.tsv"
    _decompress(src, "gz", out, None)
    assert out.read_bytes() == b"a\tb\n"


def test_decompress_tar_gz_named_member(tmp_path: Path) -> None:
    src = tmp_path / "x.tar.gz"
    payload = b"row1\nrow2\n"
    with tarfile.open(src, "w:gz") as tar:
        info = tarfile.TarInfo("enwiki.tsv")
        info.size = len(payload)
        tar.addfile(info, io.BytesIO(payload))
    out = tmp_path / "out.tsv"
    _decompress(src, "tar.gz", out, "enwiki.tsv")
    assert out.read_bytes() == payload


def test_restore_dataset_skips_existing(tmp_path: Path, monkeypatch: Any) -> None:
    (tmp_path / "target.tsv").write_text("already here")

    def fail(*a: Any, **k: Any) -> None:
        raise AssertionError("should not download when file exists")

    monkeypatch.setattr(fcd, "_download", fail)
    ds = Dataset("target.tsv", "http://example/x", "gz", "src")
    assert restore_dataset(ds, tmp_path) is False


def test_restore_dataset_fetches_and_decompresses(tmp_path: Path, monkeypatch: Any) -> None:
    def fake_download(url: str, dest: Path) -> None:
        dest.write_bytes(gzip.compress(b"fetched\tcontent\n"))

    monkeypatch.setattr(fcd, "_download", fake_download)
    ds = Dataset("target.tsv", "http://example/x", "gz", "src")
    assert restore_dataset(ds, tmp_path) is True
    assert (tmp_path / "target.tsv").read_bytes() == b"fetched\tcontent\n"
    leftover = [p.name for p in tmp_path.iterdir() if p.name != "target.tsv"]
    assert leftover == [], f"temp files left behind: {leftover}"
