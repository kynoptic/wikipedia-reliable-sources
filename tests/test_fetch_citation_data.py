import bz2
import gzip
import io
import sys
import tarfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import zipfile

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


def test_download_resumes_after_broken_connection(tmp_path: Path, monkeypatch: Any) -> None:
    full = bytes(i % 256 for i in range(1000))
    state = {"calls": 0}

    class FirstResp:  # delivers part of the body, then drops the connection
        status_code = 200

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def raise_for_status(self):
            pass

        def iter_content(self, _n):
            yield full[:400]
            raise fcd.requests.exceptions.ChunkedEncodingError("drop")

    class ResumeResp:
        status_code = 206

        def __init__(self, start):
            self.start = start

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def raise_for_status(self):
            pass

        def iter_content(self, _n):
            yield full[self.start:]

    def fake_get(url, headers=None, stream=True, timeout=None):
        state["calls"] += 1
        rng = (headers or {}).get("Range")
        if rng:
            return ResumeResp(int(rng.removeprefix("bytes=").rstrip("-")))
        return FirstResp()

    monkeypatch.setattr(fcd.requests, "get", fake_get)
    monkeypatch.setattr(fcd.time, "sleep", lambda _s: None)
    dest = tmp_path / "f.bin"
    fcd._download("http://x", dest)
    assert dest.read_bytes() == full
    assert state["calls"] == 2  # initial failure + one resumed request


def test_restore_dataset_extracts_zip_dir(tmp_path: Path, monkeypatch: Any) -> None:
    def fake_download(url: str, dest: Path) -> None:
        with zipfile.ZipFile(dest, "w") as zf:
            zf.writestr("en_citations.parquet/part-0.parquet", b"p0")
            zf.writestr("en_citations.parquet/part-1.parquet", b"p1")

    monkeypatch.setattr(fcd, "_download", fake_download)
    ds = Dataset("zenodo-8107239/en_citations.parquet", "http://example/z", "zip-dir", "src")
    assert restore_dataset(ds, tmp_path) is True
    out = tmp_path / "zenodo-8107239" / "en_citations.parquet"
    assert (out / "part-0.parquet").read_bytes() == b"p0"
    assert (out / "part-1.parquet").read_bytes() == b"p1"


def test_restore_dataset_fetches_into_source_subfolder(tmp_path: Path, monkeypatch: Any) -> None:
    def fake_download(url: str, dest: Path) -> None:
        dest.write_bytes(gzip.compress(b"fetched\tcontent\n"))

    monkeypatch.setattr(fcd, "_download", fake_download)
    ds = Dataset("figshare-1299540/enwiki.tsv", "http://example/x", "gz", "src")
    assert restore_dataset(ds, tmp_path) is True
    out = tmp_path / "figshare-1299540" / "enwiki.tsv"
    assert out.read_bytes() == b"fetched\tcontent\n"
    leftover = [p.name for p in out.parent.iterdir() if p.name != "enwiki.tsv"]
    assert leftover == [], f"temp files left behind: {leftover}"
