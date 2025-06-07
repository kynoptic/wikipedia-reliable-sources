import sys
import json
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import scripts.update_checker as uc


def test_regeneration_on_change(tmp_path: Path, monkeypatch: Any) -> None:
    rev_file = tmp_path / "revision_ids.json"
    prev = {f"{uc.BASE_TITLE}/{i}": 1 for i in range(1, 9)}
    rev_file.write_text(json.dumps(prev))
    monkeypatch.setattr(uc, "REV_FILE", str(rev_file))

    monkeypatch.setattr(uc, "fetch_revision_id", lambda title: 2)

    called = []
    original_save = uc.save_revision_ids

    def fake_fetch_all() -> list:
        called.append("fetch_all")
        return []

    def fake_clean(entries: list) -> list:
        called.append("clean_entries")
        return entries

    def fake_validate(entries: list) -> None:
        called.append("validate_entries")

    def fake_save_json(entries: list, path: str) -> None:
        called.append("save_json")

    def fake_save_csv(entries: list, path: str) -> None:
        called.append("save_csv")

    def fake_save_rev(ids: dict) -> None:
        called.append("save_revision_ids")
        original_save(ids)

    monkeypatch.setattr(uc, "fetch_all", fake_fetch_all)
    monkeypatch.setattr(uc, "clean_entries", fake_clean)
    monkeypatch.setattr(uc, "validate_entries", fake_validate)
    monkeypatch.setattr(uc, "save_to_json", fake_save_json)
    monkeypatch.setattr(uc, "save_to_csv", fake_save_csv)
    monkeypatch.setattr(uc, "save_revision_ids", fake_save_rev)

    uc.main()

    assert "fetch_all" in called
    assert "save_revision_ids" in called
    data = json.loads(rev_file.read_text())
    assert all(v == 2 for v in data.values())
