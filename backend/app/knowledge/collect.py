import json
import re
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

from app.knowledge.library import file_hash, read_json, write_catalog, write_json
from app.knowledge.parsing import parse_jats, parse_nidcd, split_paragraphs

ALLOWED_HOSTS = {"www.ebi.ac.uk", "www.nidcd.nih.gov"}


def fetch(url):
    if urlparse(url).scheme != "https" or urlparse(url).hostname not in ALLOWED_HOSTS:
        raise ValueError("download_origin_not_allowlisted")
    for attempt in range(3):
        try:
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "ENTLocalDevCorpus/1.0 (open-license research collection)",
                },
            )
            with urllib.request.urlopen(request, timeout=25) as response:
                if urlparse(response.url).hostname not in ALLOWED_HOSTS:
                    raise ValueError("redirect_origin_not_allowlisted")
                data = response.read(10_000_001)
                if len(data) > 10_000_000:
                    raise ValueError("document_too_large")
                return data
        except (urllib.error.URLError, TimeoutError):
            if attempt == 2:
                raise
            time.sleep(1 + attempt)


def collect(seed: Path, root: Path):
    import hashlib

    seeds = read_json(seed)
    root.mkdir(parents=True, exist_ok=True)
    previous = read_json(root / "manifest.json") if (root / "manifest.json").exists() else None
    previous_docs = {d["id"]: d for d in previous["documents"]} if previous else {}
    documents, failures = [], []
    # Preserve a dated copy of the applicable NIDCD policy alongside the source archive.
    policy_path = root / "policies/nidcd.html"
    if not policy_path.exists():
        policy_path.parent.mkdir(parents=True, exist_ok=True)
        policy_path.write_bytes(fetch("https://www.nidcd.nih.gov/policies"))
    for source in seeds["sources"]:
        identity = source["id"]
        if not re.fullmatch(r"[a-z0-9-]+", identity):
            raise ValueError("invalid_source_id")
        try:
            cached = previous_docs.get(identity)
            data = None
            if identity in previous_docs:
                from app.knowledge.library import verify_document

                verify_document(root, cached)
                if source.get("pmcid") != cached.get("pmcid"):
                    raise ValueError("cached_source_identity_changed")
                data = (root / cached["raw_path"]).read_bytes()
            if source["kind"] == "jats":
                pmcid = source["pmcid"]
                if not re.fullmatch(r"PMC\d+", pmcid):
                    raise ValueError("invalid_pmcid")
                url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
                data = data if data is not None else fetch(url)
                parsed = parse_jats(data, pmcid)
                origin = f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/"
                extension = "xml"
            elif source["kind"] == "nidcd":
                url = origin = source["url"]
                if cached and cached["source_url"] != origin:
                    raise ValueError("cached_source_identity_changed")
                data = data if data is not None else fetch(url)
                parsed = parse_nidcd(data)
                extension = "html"
            else:
                raise ValueError("unsupported_source_kind")
            raw_hash = hashlib.sha256(data).hexdigest()
            raw_path = f"raw/{identity}/{raw_hash}.{extension}"
            raw = root / raw_path
            raw.parent.mkdir(parents=True, exist_ok=True)
            raw.write_bytes(data)
            chunks = split_paragraphs(
                parsed["paragraphs"], identity + ":" + raw_hash[:12], source["population"]
            )
            normalized_payload = {"paragraphs": parsed["paragraphs"], "chunks": chunks}
            normalized_identity = hashlib.sha256(
                json.dumps(normalized_payload, sort_keys=True).encode()
            ).hexdigest()
            normalized_path = f"normalized/{identity}/{normalized_identity}.json"
            write_json(root / normalized_path, normalized_payload)
            metadata = {k: v for k, v in parsed.items() if k != "paragraphs"}
            metadata.update({k: v for k, v in source.items() if k not in ("kind", "url")})
            metadata.update(
                {
                    "raw_path": raw_path,
                    "raw_sha256": raw_hash,
                    "normalized_path": normalized_path,
                    "normalized_sha256": file_hash(root / normalized_path),
                    "source_url": origin,
                    "download_url": url,
                    "fetched_at": cached["fetched_at"] if cached else datetime.now(UTC).isoformat(),
                    "processed_at": datetime.now(UTC).isoformat(),
                    "parser_version": "local-fulltext-1.0",
                    "clinical_review": "pending",
                    "latest_version_review": "pending",
                    "production_eligible": False,
                    "release": "development-only",
                    "source_licensing_check": "permissive_license_detected_manual_review_pending",
                    "policy_sha256": file_hash(policy_path) if source["kind"] == "nidcd" else None,
                }
            )
            documents.append(metadata)
            print(
                json.dumps(
                    {
                        "id": identity,
                        "status": "reprocessed_cache" if cached else "downloaded",
                        "chunks": len(chunks),
                    }
                ),
                flush=True,
            )
            if not cached:
                time.sleep(0.4)
        except Exception as exc:
            failures.append({"id": identity, "error": type(exc).__name__, "detail": str(exc)[:200]})
            print(
                json.dumps({"id": identity, "status": "failed", "error": type(exc).__name__}),
                flush=True,
            )
    manifest = {
        "version": seeds["version"],
        "scope": seeds["scope"],
        "updated_at": datetime.now(UTC).isoformat(),
        "seed_sha256": file_hash(seed),
        "documents": documents,
        "metadata_only": seeds["metadata_only"],
        "failures": failures,
    }
    write_json(root / "manifest.json", manifest)
    counts = write_catalog(root)
    if (root / "governance.sqlite3").exists():
        from app.knowledge.governance import GovernanceStore

        GovernanceStore(root).sync(
            "collector", "Sync verified downloaded corpus; no clinical approval"
        )
    return {**counts, "failures": len(failures)}
