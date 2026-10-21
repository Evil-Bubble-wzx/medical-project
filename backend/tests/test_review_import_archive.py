import importlib.util
import json
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "check_candidate_review_tool",
    Path(__file__).resolve().parents[2] / "scripts/check_candidate_review.py",
)
TOOL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TOOL)


def archive(tmp_path):
    library = tmp_path / "evaluations/candidate-library-1.0"
    library.mkdir(parents=True)
    (library / "source.xml").write_text("Synthetic archived source", encoding="utf-8")
    normalized = {
        "paragraphs": [{"locator": "p", "text": "Synthetic excerpt"}],
        "chunks": [{"id": "c", "locator": "p", "text": "Synthetic excerpt", "start": 0, "end": 17}],
    }
    (library / "source.json").write_text(json.dumps(normalized), encoding="utf-8")
    source = {
        "id": "d",
        "raw_path": "source.xml",
        "normalized_path": "source.json",
        "raw_sha256": TOOL.digest(library / "source.xml"),
        "normalized_sha256": TOOL.digest(library / "source.json"),
    }
    manifest = {"documents": [source]}
    (library / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    candidate = {
        "source_manifest_sha256": TOOL.digest(library / "manifest.json"),
        "cases": [
            {
                "case_id": "Q",
                "expected_evidence": [
                    {
                        "document_id": "d",
                        "version_id": "candidate-sha256:" + source["raw_sha256"],
                        "chunk_id": "c",
                        "locator": "p",
                        "text": "Synthetic excerpt",
                        "start": 0,
                        "end": 17,
                    }
                ],
            }
        ],
    }
    return library, candidate, manifest


def test_archived_hashes_and_offsets_match(tmp_path):
    _, candidate, manifest = archive(tmp_path)
    assert TOOL.archive_errors(tmp_path, candidate, manifest) == []


@pytest.mark.parametrize("change", ["raw", "normalized", "offset", "path_escape"])
def test_archive_changes_block_readiness(tmp_path, change):
    library, candidate, manifest = archive(tmp_path)
    if change in {"raw", "normalized"}:
        name = "source.xml" if change == "raw" else "source.json"
        (library / name).write_text("Changed contents", encoding="utf-8")
    elif change == "offset":
        candidate["cases"][0]["expected_evidence"][0]["start"] = 1
    else:
        manifest["documents"][0]["raw_path"] = "../outside.xml"
        (library / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        candidate["source_manifest_sha256"] = TOOL.digest(library / "manifest.json")
    assert TOOL.archive_errors(tmp_path, candidate, manifest)


def test_existing_audit_report_cannot_be_overwritten(tmp_path, monkeypatch):
    output = tmp_path / "report.json"
    output.write_text("original audit", encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["check_candidate_review.py", "--output", str(output)])
    monkeypatch.setattr(
        TOOL, "check", lambda *args: pytest.fail("must stop before reading reviews")
    )
    with pytest.raises(SystemExit) as error:
        TOOL.main()
    assert error.value.code == 2
    assert output.read_text(encoding="utf-8") == "original audit"
