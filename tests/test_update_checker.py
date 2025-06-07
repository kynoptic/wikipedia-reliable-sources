import sys
import json
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import scripts.update_checker as uc
from scripts.fetch_perennial_sources import SourceEntry


def test_regeneration_on_change(tmp_path: Path, monkeypatch: Any) -> None:
    rev_file = tmp_path / "revision_ids.json"
    prev = {f"{uc.BASE_TITLE}/{i}": 1 for i in range(1, 9)}
    rev_file.write_text(json.dumps(prev))
    monkeypatch.setattr(uc, "REV_FILE", str(rev_file))

    monkeypatch.setattr(uc, "fetch_revision_id", lambda title: 2)

    entry = SourceEntry("Example", "gr", "note")
    monkeypatch.setattr(uc, "fetch_all", lambda: [entry])
    monkeypatch.setattr(uc, "clean_entries", lambda e: e)
    monkeypatch.setattr(uc, "validate_entries", lambda e: None)

    json_path = tmp_path / "perennial_sources.json"
    csv_path = tmp_path / "perennial_sources.csv"
    json_path.write_text("old")
    csv_path.write_text("old")

    monkeypatch.chdir(tmp_path)
    uc.main()

    ids = json.loads(rev_file.read_text())
    assert all(v == 2 for v in ids.values())

    data = json.loads(json_path.read_text())
    assert data[0]["source_name"] == "Example"

    csv_text = csv_path.read_text()
    assert "source_name" in csv_text.splitlines()[0]
    assert "Example" in csv_text
