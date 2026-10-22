import hashlib
import json
import re
import sqlite3
from pathlib import Path

from app.knowledge.population import population_restriction

TOPICS = {
    "rhinitis": ("鼻炎", "变应性鼻炎", "allergic rhinitis"),
    "sinusitis": ("鼻窦炎", "鼻息肉", "rhinosinusitis", "nasal polyps"),
    "otitis_media": ("中耳炎", "otitis media"),
    "hearing_loss": ("听力", "听力损失", "听力下降", "hearing loss"),
    "tinnitus": ("耳鸣", "tinnitus"),
    "throat": ("咽喉", "咽痛", "扁桃体", "声嘶", "hoarseness", "sore throat"),
}
QUERY_ALIASES = {
    "鼻炎": "rhinitis",
    "变应性鼻炎": "allergic rhinitis",
    "鼻窦炎": "rhinosinusitis",
    "鼻息肉": "nasal polyps",
    "中耳炎": "otitis media",
    "听力": "hearing",
    "听力损失": "hearing loss",
    "听力下降": "hearing loss",
    "耳鸣": "tinnitus",
    "咽喉": "throat",
    "咽痛": "sore throat",
    "扁桃体": "tonsillitis",
    "声嘶": "hoarseness",
    "嘶哑": "hoarseness",
    "粗哑": "hoarseness",
    "沙哑": "hoarseness",
}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def resolve_member(root, member):
    root = root.resolve()
    target = (root / member).resolve()
    if not target.is_relative_to(root):
        raise ValueError("library_path_outside_root")
    return target


def verify_document(root, document):
    for path_key, hash_key in (
        ("raw_path", "raw_sha256"),
        ("normalized_path", "normalized_sha256"),
    ):
        if file_hash(resolve_member(root, document[path_key])) != document[hash_key]:
            raise ValueError("library_checksum_mismatch")
    return read_json(resolve_member(root, document["normalized_path"]))


def rebuild_index(root: Path):
    manifest = read_json(root / "manifest.json")
    # Build a fresh database, then atomically replace. A failed rebuild preserves the old index.
    temporary = root / "library.build.sqlite3"
    temporary.unlink(missing_ok=True)
    connection = sqlite3.connect(temporary)
    try:
        connection.executescript("""
            CREATE TABLE documents (id TEXT PRIMARY KEY, metadata TEXT NOT NULL);
            CREATE TABLE passages (
                id TEXT PRIMARY KEY, document_id TEXT NOT NULL, section TEXT NOT NULL,
                locator TEXT NOT NULL, start INTEGER, end INTEGER, text TEXT NOT NULL,
                population_status TEXT NOT NULL
            );
            CREATE VIRTUAL TABLE search_index USING fts5(
                chunk_id UNINDEXED, document_id UNINDEXED, text, catalog,
                tokenize='unicode61'
            );
            CREATE TABLE build_info (key TEXT PRIMARY KEY, value TEXT);
        """)
        indexed = staged = 0
        by_topic = {topic: {"documents": 0, "indexed_chunks": 0} for topic in TOPICS}
        for document in manifest["documents"]:
            normalized = verify_document(root, document)
            if document["clinical_review"] != "pending" or document["production_eligible"]:
                raise ValueError("development_library_must_not_claim_clinical_approval")
            connection.execute(
                "INSERT INTO documents VALUES (?, ?)",
                (document["id"], json.dumps(document, ensure_ascii=False)),
            )
            for topic in document["topics"]:
                by_topic[topic]["documents"] += 1
            catalog = f"{document['title_zh']} {document['title']}"
            for chunk in normalized["chunks"]:
                connection.execute(
                    "INSERT INTO passages VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        chunk["id"],
                        document["id"],
                        chunk["section"],
                        chunk["locator"],
                        chunk["start"],
                        chunk["end"],
                        chunk["text"],
                        chunk["population_status"],
                    ),
                )
                if chunk["population_status"] == "adult_dev_candidate":
                    connection.execute(
                        "INSERT INTO search_index VALUES (?, ?, ?, ?)",
                        (chunk["id"], document["id"], chunk["text"], catalog),
                    )
                    indexed += 1
                    for topic in document["topics"]:
                        by_topic[topic]["indexed_chunks"] += 1
                else:
                    staged += 1
        connection.execute(
            "INSERT INTO build_info VALUES (?, ?)",
            ("manifest_sha256", file_hash(root / "manifest.json")),
        )
        connection.commit()
    except Exception:
        connection.close()
        temporary.unlink(missing_ok=True)
        raise
    connection.close()
    temporary.replace(root / "library.sqlite3")
    return {
        "documents": len(manifest["documents"]),
        "indexed_chunks": indexed,
        "staged_chunks": staged,
        "metadata_only": len(manifest["metadata_only"]),
        "by_topic": by_topic,
    }


def search_expression(query):
    terms = re.findall(r"[\w\u4e00-\u9fff]+", query, flags=re.UNICODE)
    for term, translation in QUERY_ALIASES.items():
        if term in query:
            terms.append(translation)
    return " OR ".join('"' + term.replace('"', '""') + '"' for term in dict.fromkeys(terms))


def search(root: Path, query: str, limit=5, topic=None):
    if not 1 <= limit <= 20 or len(query) > 500:
        raise ValueError("invalid_search_limits")
    if topic is not None and topic not in TOPICS:
        raise ValueError("unknown_topic")
    if (root / "governance.sqlite3").exists():
        from app.knowledge.governance import GovernanceStore

        return GovernanceStore(root).search(query, limit, topic, channel="development")["results"]
    expression = search_expression(query)
    if not expression:
        return []
    db_path = root / "library.sqlite3"
    if not db_path.is_file():
        raise ValueError("library_not_built")
    with sqlite3.connect(db_path.resolve().as_uri() + "?mode=ro", uri=True) as connection:
        connection.row_factory = sqlite3.Row
        fingerprint = connection.execute(
            "SELECT value FROM build_info WHERE key='manifest_sha256'"
        ).fetchone()[0]
        if fingerprint != file_hash(root / "manifest.json"):
            raise ValueError("library_index_stale_rebuild_required")
        rows = connection.execute(
            """
            SELECT p.*, d.metadata, bm25(search_index, 0, 0, 1, 0.2) AS rank
            FROM search_index JOIN passages p ON p.id = search_index.chunk_id
            JOIN documents d ON d.id = p.document_id
            WHERE search_index MATCH ? ORDER BY rank, p.id
        """,
            (expression,),
        ).fetchall()
    results = []
    verified = set()
    for row in rows:
        document = json.loads(row["metadata"])
        if population_restriction(document):
            continue
        if topic and topic not in document["topics"]:
            continue
        if document["id"] not in verified:
            verify_document(root, document)
            verified.add(document["id"])
        results.append(
            {
                "chunk_id": row["id"],
                "document_id": row["document_id"],
                "title": document["title"],
                "title_zh": document["title_zh"],
                "section": row["section"],
                "locator": row["locator"],
                "start": row["start"],
                "end": row["end"],
                "text": row["text"],
                "source_url": document["source_url"],
                "license": document["license"],
                "publication_date": document["publication_date"],
                "clinical_review": document["clinical_review"],
                "production_eligible": False,
                "bm25": row["rank"],
            }
        )
        if len(results) == limit:
            break
    return results


def write_catalog(root: Path):
    manifest = read_json(root / "manifest.json")
    counts = rebuild_index(root)
    lines = [
        "# 成人耳鼻喉本地开发资料库",
        "",
        "版本：1.0；临床审核：全部待审。",
        "",
        "英文原文与中文目录；中文指南目前只有题录，未伪造中文全文。",
        "",
        "## 已保存原文",
        "",
        "| 中文目录名 | 原文日期 | 类型 | 许可 | 成人范围 | 原文 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for d in manifest["documents"]:
        lines.append(
            f"| {d['title_zh']} | {d['publication_date'] or '待核实'} | "
            f"{d['document_type']} | {d['license']} | {d['population']} | "
            f"[来源]({d['source_url']}) / [本地原文]({d['raw_path']}) |"
        )
    lines += ["", "## 中文及授权待核实目录（无全文、不入检索）", ""]
    for d in manifest["metadata_only"]:
        lines.append(
            f"- [{d['title']}]({d['source_url']})，DOI：{d.get('doi', '未记录')}。"
            f"状态：{d['status']}。{d['note']}"
        )
    lines += [
        "",
        "## 覆盖与缺口",
        "",
        f"已保存 {counts['documents']} 份原文；默认成人开发索引 "
        f"{counts['indexed_chunks']} 个块；待人群筛选 {counts['staged_chunks']} 个块。",
        "",
        "- 中文全文、各病种完整中国诊疗指南尚未补齐；中文目录名是检索辅助，不是译文。",
        "- mixed_requires_screening 文献整篇不进入默认索引；其他文献含儿童词的段落也隔离。",
        "- 人群关键词隔离只是保守工程筛选，无法证明其余段落均适用于成人；必须临床复核。",
        "- 科普、指南、综述和单项研究分别标注，不能因为可下载而视为同等级证据。",
        "- 全部资料均未核实为最新有效版本；不能用于生产回答。",
        "- XML/HTML 原文保留；规范化文本省略图片、表格和参考文献，定位使用章节/段落/字符，"
        "不编造 PDF 页码。原文及许可声明保留用于复核。",
        "",
    ]
    (root / "CATALOG.md").write_text("\n".join(lines), encoding="utf-8")
    write_json(root / "build-summary.json", counts)
    return counts
