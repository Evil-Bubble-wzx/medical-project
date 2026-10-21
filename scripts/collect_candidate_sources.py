"""Archive permissively licensed candidate sources, without changing the active corpus."""

import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.knowledge.collect import fetch  # noqa: E402
from app.knowledge.library import file_hash, read_json, write_json  # noqa: E402
from app.knowledge.parsing import parse_jats, split_paragraphs  # noqa: E402


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    seed = ROOT / "evaluations/candidate-sources-1.0.json"
    output = ROOT / "evaluations/candidate-library-1.0"
    output.mkdir(parents=True, exist_ok=True)
    documents, failures = [], []
    for source in read_json(seed)["sources"]:
        try:
            pmcid = source["pmcid"]
            url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
            path = output / "raw" / f"{pmcid}.xml"
            data = path.read_bytes() if path.exists() else fetch(url)
            parsed = parse_jats(data, pmcid)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            chunks = split_paragraphs(
                parsed["paragraphs"], source["id"], "mixed_requires_screening"
            )
            normalized = output / "normalized" / f"{source['id']}.json"
            write_json(normalized, {"paragraphs": parsed["paragraphs"], "chunks": chunks})
            document = {
                **source,
                **{k: v for k, v in parsed.items() if k != "paragraphs"},
                "source_url": f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/",
                "download_url": url,
                "raw_path": str(path.relative_to(output)),
                "raw_sha256": hashlib.sha256(data).hexdigest(),
                "normalized_path": str(normalized.relative_to(output)),
                "normalized_sha256": file_hash(normalized),
                "fetched_at": datetime.now(UTC).isoformat(),
                "clinical_review": "pending",
                "population_review": "pending",
                "production_eligible": False,
                "retrieval_activated": False,
            }
            documents.append(document)
            print(
                json.dumps(
                    {
                        "id": source["id"],
                        "status": "archived_pending_review",
                        "chunks": len(chunks),
                        "license": parsed["license"],
                    }
                ),
                flush=True,
            )
        except Exception as exc:
            failures.append({"id": source["id"], "detail": str(exc)[:300]})
            print(json.dumps(failures[-1]), flush=True)
    write_json(
        output / "manifest.json",
        {
            "seed_sha256": file_hash(seed),
            "documents": documents,
            "failures": failures,
            "retrieval_activated": False,
        },
    )
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
