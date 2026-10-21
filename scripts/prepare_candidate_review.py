"""Export pending-review copies and a baseline fingerprint without running candidate queries."""

import hashlib
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.retrieval.corpus import eligible_corpus  # noqa: E402


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def prepare(root=ROOT, output=None):
    output = output or root / "evaluations/reviews/candidate-readiness-1.1"
    if output.exists() and any(output.iterdir()):
        raise ValueError("review_package_already_exists")
    candidate_path = root / "evaluations/datasets/adult-ent-candidate-1.0.json"
    source_path = root / "evaluations/candidate-library-1.0/manifest.json"
    candidate, manifest = read(candidate_path), read(source_path)
    old = read(root / "knowledge/manifest.json")["documents"]
    protected = (
        candidate_path,
        source_path,
        root / "knowledge/manifest.json",
        root / "configs/generation.json",
        root / "configs/retrieval.json",
    )
    before = {p: digest(p) for p in protected}
    if candidate["source_manifest_sha256"] != digest(source_path):
        raise ValueError("candidate_manifest_changed")
    source_forms, chunks, paragraphs = [], {}, {}
    for source in manifest["documents"]:
        doc = source["id"]
        for field in ("raw", "normalized"):
            if digest(source_path.parent / source[field + "_path"]) != source[field + "_sha256"]:
                raise ValueError("candidate_archive_changed")
        if any(
            (source.get("pmcid") and prior.get("pmcid") == source["pmcid"])
            or (
                source.get("doi")
                and (prior.get("doi") or "").casefold() == source["doi"].casefold()
            )
            or prior.get("raw_sha256") == source["raw_sha256"]
            for prior in old
        ):
            raise ValueError("candidate_known_source_overlap")
        normalized = read(source_path.parent / source["normalized_path"])
        chunks.update({(doc, c["id"]): c for c in normalized["chunks"]})
        paragraphs.update({(doc, p["locator"]): p for p in normalized["paragraphs"]})
        source_forms.append(
            {
                "source": source,
                "review": dict.fromkeys(
                    (
                        "decision",
                        "adult_scope",
                        "evidence_quality",
                        "license_version_confirmed",
                        "conflicts_of_interest",
                        "source_family_aliases_checked",
                        "reviewer",
                        "reviewed_at",
                        "notes",
                    )
                ),
            }
        )
    cases, anchor_count = [], 0
    sources = {d["id"]: d for d in manifest["documents"]}
    for case in candidate["cases"]:
        if (
            case["annotation_status"] != "draft_pending_human_review"
            or case.get("reviewer")
            or case["retrieval_run"]
        ):
            raise ValueError("candidate_state_changed")
        for evidence in case["expected_evidence"]:
            doc = evidence["document_id"]
            chunk = chunks[(doc, evidence["chunk_id"])]
            paragraph = paragraphs[(doc, evidence["locator"])]
            if (
                evidence["version_id"] != "candidate-sha256:" + sources[doc]["raw_sha256"]
                or any(evidence[k] != chunk[k] for k in ("locator", "start", "end", "text"))
                or paragraph["text"][evidence["start"] : evidence["end"]] != evidence["text"]
            ):
                raise ValueError("candidate_evidence_binding_changed")
            anchor_count += 1
        cases.append(
            {
                "case": case,
                "review": dict.fromkeys(
                    (
                        "decision",
                        "question_clarity",
                        "adult_applicability",
                        "scope_limitations",
                        "evidence_sufficiency",
                        "additional_relevant_evidence",
                        "boundary_expected_behavior_confirmed",
                        "reviewer",
                        "reviewed_at",
                        "notes",
                    )
                ),
            }
        )
    snapshot, corpus = eligible_corpus(root / "knowledge", "development")
    paths = set((root / "backend/app").rglob("*.py"))
    for directory, pattern in (
        ("configs", "*.json"),
        ("knowledge", "*.json"),
        ("frontend/validation", "*"),
    ):
        paths.update(p for p in (root / directory).rglob(pattern) if p.is_file())
    paths.update((candidate_path, source_path, Path(__file__).resolve(), root / "AGENTS.md"))
    hashes = {p.relative_to(root).as_posix(): digest(p) for p in sorted(paths)}
    model_records = []
    for path in sorted((root / "models").glob("*/model-manifest.json")):
        model = read(path)
        actual = {name: digest(path.parent / name) for name in model["files"]}
        if actual != model["files"]:
            raise ValueError("local_model_file_changed")
        model_records.append(
            {
                "model_id": model["model_id"],
                "revision": model["revision"],
                "manifest_sha256": digest(path),
                "verified_files": actual,
            }
        )
    baseline_id = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()
    report = {
        "created_at": datetime.now(UTC).isoformat(),
        "candidate_sha256": digest(candidate_path),
        "candidate_cases": len(cases),
        "evidence_cases": sum(bool(c["case"]["expected_evidence"]) for c in cases),
        "boundary_cases": sum(not c["case"]["expected_evidence"] for c in cases),
        "source_count": len(source_forms),
        "bound_evidence_chunks_verified": anchor_count,
        "topic_counts": dict(Counter(c["case"]["topic"] for c in cases)),
        "archive_hashes_and_evidence_bindings": "passed",
        "known_identity_overlap": False,
        "source_family_semantic_review": "pending",
        "medical_review": "pending",
        "candidate_model_evaluation_run": False,
        "formal_holdout_frozen": False,
        "eligible_for_formal_independent_scoring": False,
        "clinical_approval": False,
        "baseline_id": baseline_id,
        "original_artifacts_unchanged": all(digest(p) == h for p, h in before.items()),
    }
    if not report["original_artifacts_unchanged"]:
        raise ValueError("original_artifact_changed")
    output.mkdir(parents=True, exist_ok=True)
    artifacts = {
        "source-review.json": {"status": "pending_human_review", "sources": source_forms},
        "case-review.json": {"candidate_sha256": digest(candidate_path), "cases": cases},
        "readiness-report.json": report,
        "baseline-manifest.json": {
            "baseline_id": baseline_id,
            "purpose": "development_baseline_only",
            "formal_holdout_frozen": False,
            "active_development_snapshot": snapshot,
            "active_chunks": len(corpus),
            "file_hashes": hashes,
            "local_models": model_records,
            "remote_model_pin": "API alias only; provider weights cannot be pinned",
        },
    }
    for name, data in artifacts.items():
        (output / name).write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    lines = [
        "# 候选资料与题目审核入口",
        "",
        "状态：全部待审。此次未运行候选问题、未激活资料、未签发医学合格结论。",
        "",
        "先审核source-review.json中的6份来源，再审核case-review.json中的36题；填写accept/revise/exclude、理由、真实审核者与日期。",
        "证据题核查成人适用性、相关性、充分性和遗漏证据；边界题单独审核预期行为，不用检索命中率替代。",
        "候选题曾由开发助手拟写与查看，不能作为严格盲测金标准。严格独立评估需要审核者另行保管问题与标签。",
        "baseline-manifest.json仅是当前开发基线指纹；候选审核、治理版本与统一索引完成后才可正式冻结。",
        "",
    ]
    for entry in cases:
        case = entry["case"]
        lines += [f"## {case['case_id']} / {case['topic']}", "", case["question"], ""]
        for e in case["expected_evidence"]:
            lines += [
                f"来源：[{e['source_family']}]({e['source_url']})",
                "",
                f"定位：{e['locator']}；字符区间 [{e['start']}, {e['end']})",
                "",
                e["text"],
                "",
            ]
        if case.get("proposed_expected_behavior"):
            lines += ["候选预期行为（待审核）：" + case["proposed_expected_behavior"], ""]
        lines += ["审核结论、理由、审核者与日期：待填写。", ""]
    (output / "审核入口.md").write_text("\n".join(lines), encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(prepare(), ensure_ascii=False, indent=2))
