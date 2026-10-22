"""Build and search an isolated, unapproved otitis supplement. Never activates a corpus."""

import argparse
import hashlib
import json
import sqlite3
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.knowledge.library import file_hash, read_json, verify_document, write_json  # noqa: E402
from app.knowledge.parsing import parse_jats, split_paragraphs, xml_text  # noqa: E402

PACKAGE = ROOT / "knowledge/supplements/otitis-2026-10"
FLAGS = {"clinical_review": "pending", "production_eligible": False, "retrieval_activated": False}
SEARCHABLE = {"adult_analysis_subset", "adult_inclusion"}


def build(package, cache):
    seed = read_json(package / "sources.json")
    documents = []
    for source in seed["sources"]:
        data = (cache / (source["pmcid"] + ".xml")).read_bytes()
        if hashlib.sha256(data).hexdigest() != source["raw_sha256"]:
            raise ValueError("source_archive_changed")
        parsed = parse_jats(data, source["pmcid"])
        # License and identity must pass before copying a full text into this package.
        if source["population_status"] in SEARCHABLE:
            evidence = next(
                (p for p in parsed["paragraphs"] if p["locator"] == source["age_evidence_locator"]),
                None,
            )
            if not evidence or source["age_evidence_anchor"] not in evidence["text"]:
                raise ValueError("population_evidence_changed")
        raw = package / "raw" / (source["pmcid"] + ".xml")
        normalized = package / "normalized" / (source["id"] + ".json")
        raw.parent.mkdir(parents=True, exist_ok=True)
        if raw.exists() and raw.read_bytes() != data:
            raise ValueError("immutable_source_archive_changed")
        raw.write_bytes(data)
        chunks = split_paragraphs(parsed["paragraphs"], source["id"], "mixed_requires_screening")
        write_json(normalized, {"paragraphs": parsed["paragraphs"], "chunks": chunks})
        tree = ET.fromstring(data)
        tables = [
            {
                "id": t.get("id"),
                "locator": f".//table-wrap[@id='{t.get('id')}']",
                "text": xml_text(t),
            }
            for t in tree.findall(".//table-wrap")
        ]
        # Tables are an audit attachment, not silently merged into clinical passages.
        write_json(package / "tables" / (source["id"] + ".json"), tables)
        documents.append(
            {
                **source,
                **{k: v for k, v in parsed.items() if k != "paragraphs"},
                "source_url": f"https://pmc.ncbi.nlm.nih.gov/articles/{source['pmcid']}/",
                "download_url": f"https://www.ebi.ac.uk/europepmc/webservices/rest/{source['pmcid']}/fullTextXML",
                "topics": ["otitis_media"],
                "raw_path": raw.relative_to(package).as_posix(),
                "normalized_path": normalized.relative_to(package).as_posix(),
                "normalized_sha256": file_hash(normalized),
                "tables_path": f"tables/{source['id']}.json",
                "tables_sha256": file_hash(package / "tables" / (source["id"] + ".json")),
                "supplement_search_enabled": source["population_status"] in SEARCHABLE,
                **FLAGS,
            }
        )
    manifest = {
        "version": seed["version"],
        "seed_sha256": file_hash(package / "sources.json"),
        "documents": documents,
        "metadata_only": seed["metadata_only"],
        **FLAGS,
    }
    write_json(package / "manifest.json", manifest)
    return manifest


def search(package, query, limit=5):
    """Engineering discovery only; results remain unapproved, including all retrieved text."""
    manifest = read_json(package / "manifest.json")
    if manifest["seed_sha256"] != file_hash(package / "sources.json"):
        raise ValueError("supplement_seed_changed_rebuild_required")
    terms = query.strip().split()
    if not terms or len(query) > 500 or not 1 <= limit <= 20:
        raise ValueError("invalid_search_parameters")
    expression = " OR ".join('"' + t.replace('"', '""') + '"' for t in terms)
    seeds = {s["id"]: s for s in read_json(package / "sources.json")["sources"]}
    if len(manifest["documents"]) != len(seeds):
        raise ValueError("supplement_manifest_changed")
    items = []
    seen = set()
    for document in manifest["documents"]:
        source = seeds.get(document["id"])
        if (
            not source
            or document["id"] in seen
            or any(document.get(k) != v for k, v in source.items())
            or any(document.get(k) != v for k, v in FLAGS.items())
        ):
            raise ValueError("supplement_manifest_changed")
        seen.add(document["id"])
        if document["supplement_search_enabled"] != (source["population_status"] in SEARCHABLE):
            raise ValueError("supplement_search_scope_changed")
        if file_hash(package / document["tables_path"]) != document["tables_sha256"]:
            raise ValueError("supplement_table_archive_changed")
        normalized = verify_document(package, document)
        if not document["supplement_search_enabled"]:
            continue
        if document["population_status"] not in SEARCHABLE:
            raise ValueError("unresolved_population_cannot_search")
        for chunk in normalized["chunks"]:
            items.append(
                {
                    "document_id": document["id"],
                    "title": document["title"],
                    "source_url": document["source_url"],
                    "scope_limitations": document["scope_limitations"],
                    "population_status": document["population_status"],
                    "chunk_id": chunk["id"],
                    "locator": chunk["locator"],
                    "start": chunk["start"],
                    "end": chunk["end"],
                    "text": chunk["text"],
                    "section": chunk["section"],
                    **FLAGS,
                }
            )
    db = sqlite3.connect(":memory:")
    try:
        db.execute("CREATE VIRTUAL TABLE passages USING fts5(text, title)")
        db.executemany(
            "INSERT INTO passages(rowid,text,title) VALUES (?,?,?)",
            [(i + 1, item["text"], item["title"]) for i, item in enumerate(items)],
        )
        rows = db.execute(
            "SELECT rowid FROM passages WHERE passages MATCH ? "
            "ORDER BY bm25(passages),rowid LIMIT ?",
            (expression, limit),
        ).fetchall()
        return {
            "purpose": "unapproved_supplement_discovery_only",
            **FLAGS,
            "results": [items[row[0] - 1] for row in rows],
        }
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["build", "search"])
    parser.add_argument("--cache", type=Path, default=ROOT / "var/source-discovery")
    parser.add_argument("--query")
    args = parser.parse_args()
    if args.action == "build":
        result = build(PACKAGE, args.cache)
        print(json.dumps({"archived": len(result["documents"]), **FLAGS}))
    else:
        print(json.dumps(search(PACKAGE, args.query or ""), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
