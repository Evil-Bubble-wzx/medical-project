"""Check real workbench retrieval for fixed synthetic cases without an LLM API call."""

import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.knowledge.library import read_json, write_json  # noqa: E402
from app.retrieval.corpus import key  # noqa: E402
from app.retrieval.generation import evidence_packet  # noqa: E402


def main():
    cases = read_json(ROOT / "evaluations/datasets/generation-acceptance-1.0.json")["cases"]
    anchors = {
        c["case_id"]: c
        for c in read_json(ROOT / "evaluations/datasets/adult-ent-dev-1.0.json")["cases"]
    }
    reports = []
    with httpx.Client(
        base_url="http://127.0.0.1:8011",
        trust_env=False,
        timeout=180,
        headers={"Origin": "http://127.0.0.1:8011"},
    ) as client:
        client.get("/").raise_for_status()
        for case in cases:
            if case["case_id"] not in ("GEN-ENT-002", "GEN-ENT-036"):
                continue
            payload = {k: v for k, v in case["input"].items() if k != "synthetic_only"}
            response = client.post("/api/v1/validation/retrieve", json=payload)
            response.raise_for_status()
            result = response.json()
            packet = evidence_packet(result["reranked"])
            expected = {
                key(e) for e in anchors[case["original_development_case"]]["expected_evidence"]
            }
            rank = next((i for i, e in enumerate(packet, 1) if key(e) in expected), None)
            reports.append(
                {
                    "case_id": case["case_id"],
                    "query_policy": result.get("query_policy"),
                    "snapshot_id": result["snapshot_id"],
                    "packet_anchor_rank": rank,
                    "packet_keys": [key(e) for e in packet],
                    "elapsed_ms": result["elapsed_ms"],
                }
            )
            if result.get("query_policy") != "dual_question_first" or rank is None:
                raise ValueError("runtime_retrieval_target_not_recovered")
    write_json(ROOT / "evaluations/reports/patient-query-alias-1.0/runtime-targets.json", reports)
    print(reports)


if __name__ == "__main__":
    main()
