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


SAMPLE_WIKITEXT = (
    "{| class=\"wikitable\"\n"
    "|-\n"
    "! Name !! Status !! Discussion !! Last !! Notes\n"
    "\n|- class=\"s-gr\" id=\"abc\"\n"
    "| [[ABC News (US)]]\n"
    "| {{WP:RSPSTATUS|gr}}\n"
    "| Discussion\n"
    "| {{WP:RSPLAST|2023}}\n"
    "| Good source\n"
    "\n|- class=\"s-d\" id=\"dm\"\n"
    "| [[Daily Mail (MailOnline)]]\n"
    "| {{WP:RSPSTATUS|d}}\n"
    "| Discussion\n"
    "| {{WP:RSPLAST|2023}}\n"
    "| Tabloid\n"
    "|}"
)


def test_integration_run(tmp_path: Path, monkeypatch: Any, capsys: Any) -> None:
    """Run the main script and ensure outputs are generated."""

    rev_file = tmp_path / "revision_ids.json"
    prev = {f"{uc.BASE_TITLE}/{i}": 1 for i in range(1, 9)}
    rev_file.write_text(json.dumps(prev))
    monkeypatch.setattr(uc, "REV_FILE", str(rev_file))

    monkeypatch.setattr(uc, "fetch_revision_id", lambda title: 2)

    import scripts.fetch_perennial_sources as fps
    monkeypatch.setattr(fps, "fetch_subpage", lambda t: SAMPLE_WIKITEXT)

    monkeypatch.chdir(tmp_path)
    uc.main()

    ids = json.loads(rev_file.read_text())
    assert all(v == 2 for v in ids.values())

    data = json.loads((tmp_path / "perennial_sources.json").read_text())
    names = {e["source_name"] for e in data}
    assert {"ABC News (US)", "Daily Mail (MailOnline)"} == names

    csv_lines = (tmp_path / "perennial_sources.csv").read_text().splitlines()
    assert "source_name" in csv_lines[0]

    captured = capsys.readouterr()
    assert "Fetched 2 sources" in captured.out


def test_integration_no_changes(tmp_path: Path, monkeypatch: Any, capsys: Any) -> None:
    """Verify script exits early when nothing changed."""

    rev_file = tmp_path / "revision_ids.json"
    prev = {f"{uc.BASE_TITLE}/{i}": 1 for i in range(1, 9)}
    rev_file.write_text(json.dumps(prev))
    monkeypatch.setattr(uc, "REV_FILE", str(rev_file))

    monkeypatch.setattr(uc, "fetch_revision_id", lambda title: 1)

    def fail(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("fetch should not be called")

    monkeypatch.setattr(uc, "fetch_all", fail)

    monkeypatch.chdir(tmp_path)
    uc.main()

    captured = capsys.readouterr()
    assert "No updates detected." in captured.out
