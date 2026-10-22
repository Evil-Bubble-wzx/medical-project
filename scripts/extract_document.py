"""Subprocess worker for bounded PDF/DOCX extraction; output contains only parsed text."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.knowledge.document_extract import DocumentError, extract_document  # noqa: E402

if __name__ == "__main__":
    source, output, kind = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
    try:
        result = extract_document(source.read_bytes(), kind)
    except DocumentError as exc:
        result = {"error_code": str(exc)}
    except Exception:
        result = {"error_code": "document_parse_failed"}
    output.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
