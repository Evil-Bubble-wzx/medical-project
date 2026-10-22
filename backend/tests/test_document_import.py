import io
import json
import zipfile
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject
from test_audit_backend import audit  # noqa: F401
from test_development_bridge import Encoder
from test_local_import import payload

from app.api.validation import create_validation_app
from app.knowledge.document_extract import DocumentError, extract_document
from app.knowledge.library import file_hash, read_json
from app.retrieval.audit_service import AuditError
from app.retrieval.corpus import eligible_corpus
from app.retrieval.development_service import DevelopmentService
from app.retrieval.document_preview import DocumentPrepare, create_preview, prepare_preview
from app.retrieval.engine import RetrievalEngine


@pytest.fixture
def bridge(request):
    return DevelopmentService(request.getfixturevalue("audit"), Encoder())


def pdf_bytes(texts=("Synthetic PDF first page", "Synthetic PDF second page"), encrypted=False):
    writer = PdfWriter()
    for text in texts:
        page = writer.add_blank_page(width=595, height=842)
        if text:
            font = DictionaryObject(
                {
                    NameObject("/Type"): NameObject("/Font"),
                    NameObject("/Subtype"): NameObject("/Type1"),
                    NameObject("/BaseFont"): NameObject("/Helvetica"),
                }
            )
            page[NameObject("/Resources")] = DictionaryObject(
                {NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})}
            )
            stream = DecodedStreamObject()
            stream.set_data(("BT /F1 12 Tf 50 780 Td (" + text + ") Tj ET").encode())
            page[NameObject("/Contents")] = writer._add_object(stream)
    if encrypted:
        writer.encrypt("synthetic-password")
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


def docx_bytes():
    output = io.BytesIO()
    xml = b"""<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>
    <w:p><w:r><w:t>Synthetic Word first paragraph for indexing.</w:t></w:r></w:p>
    <w:p><w:r><w:t>Synthetic Word second paragraph.</w:t></w:r></w:p>
    <w:tbl><w:tr><w:tc><w:p><w:r><w:t>Cell content.</w:t></w:r></w:p></w:tc></w:tr></w:tbl>
    </w:body></w:document>"""
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("word/document.xml", xml)
    return output.getvalue()


def prepare_payload(preview, **updates):
    return DocumentPrepare(
        **{
            **payload().model_dump(exclude={"text"}),
            "preview_id": preview["preview_id"],
            "preview_sha256": preview["preview_sha256"],
            "extraction_confirmed": True,
            **updates,
        }
    )


def test_pdf_preserves_page_order_and_empty_pages_block_complete_import():
    value = extract_document(pdf_bytes(), "pdf")
    assert value["can_import"]
    assert [u["locator"] for u in value["units"]] == ["PDF page 1", "PDF page 2"]
    partial = extract_document(pdf_bytes(("Synthetic text", "")), "pdf")
    assert not partial["can_import"] and partial["empty_pages"] == [2]
    empty = extract_document(pdf_bytes(("",)), "pdf")
    assert not empty["can_import"] and "no_extractable_text" in empty["warnings"]


def test_encrypted_pdf_is_rejected():
    with pytest.raises(DocumentError, match="encrypted_document"):
        extract_document(pdf_bytes(encrypted=True), "pdf")


def test_docx_paragraphs_and_cells_have_distinct_locations():
    value = extract_document(docx_bytes(), "docx")
    assert value["can_import"]
    assert [u["locator"] for u in value["units"]] == [
        "Word paragraph 1",
        "Word paragraph 2",
        "Word table 1/row 1/cell 1",
    ]
    assert "docx_tables_linearized_verify_relationships" in value["warnings"]


@pytest.mark.parametrize(
    "kind,data", [("pdf", b"not a PDF"), ("docx", b"not a zip"), ("doc", b"legacy")]
)
def test_invalid_formats_do_not_produce_usable_units(kind, data):
    with pytest.raises((DocumentError, zipfile.BadZipFile)):
        extract_document(data, kind)


@pytest.mark.parametrize("kind", ["pdf", "docx"])
def test_preview_bound_to_original_file_then_indexed_with_locators(bridge, kind):
    data = pdf_bytes() if kind == "pdf" else docx_bytes()
    preview = create_preview(bridge.root, data, kind)
    assert bridge.active() is None
    staged = prepare_preview(bridge, prepare_payload(preview))
    assert bridge.active() is None
    bridge.activate(staged["snapshot_id"], None, "fixture", "Synthetic file activation")
    _, corpus = eligible_corpus(bridge.knowledge)
    assert len(corpus) == len(preview["units"])
    assert all(c["locator"].startswith("PDF page" if kind == "pdf" else "Word ") for c in corpus)
    engine = RetrievalEngine(bridge.knowledge, Encoder(), bridge.root / "missing.json")
    assert engine.retrieve("Synthetic", "hybrid")["results"]
    from app.knowledge.governance import GovernanceStore

    citation = GovernanceStore(bridge.knowledge).citation(
        staged["snapshot_id"], staged["version_id"], corpus[0]["id"]
    )
    metadata = citation["metadata"]
    raw = bridge.knowledge / metadata["raw_path"]
    assert raw.read_bytes() == data and file_hash(raw) == metadata["raw_sha256"]
    assert metadata["clinical_review"] == "pending"


def test_changed_preview_or_missing_confirmation_cannot_prepare(bridge):
    preview = create_preview(bridge.root, docx_bytes(), "docx")
    with pytest.raises(AuditError, match="document_preview_confirmation_required"):
        prepare_preview(bridge, prepare_payload(preview, extraction_confirmed=False))
    folder = bridge.root / "var/import-previews" / preview["preview_id"]
    extracted = read_json(folder / "extracted.json")
    extracted["units"][0]["locator"] = "forged page"
    (folder / "extracted.json").write_text(json.dumps(extracted))
    with pytest.raises(AuditError, match="document_preview_changed_or_expired"):
        prepare_preview(bridge, prepare_payload(preview))


def test_preview_of_image_only_pdf_cannot_be_prepared(bridge):
    preview = create_preview(bridge.root, pdf_bytes(("",)), "pdf")
    with pytest.raises(AuditError, match="document_requires_ocr_or_manual_check"):
        prepare_preview(bridge, prepare_payload(preview))


def test_document_api_rejects_cross_origin_and_preserves_preview_on_same_origin(bridge):
    app = create_validation_app(SimpleNamespace(root=bridge.root), development_service=bridge)
    with TestClient(app) as client:
        path = "/api/v1/validation/development/document-preview?kind=docx"
        assert client.post(path, content=docx_bytes()).status_code == 401
        client.get("/imports")
        assert client.post(path, content=docx_bytes()).status_code == 403
        client.headers["Origin"] = "http://testserver"
        response = client.post(path, content=docx_bytes())
        assert response.status_code == 200
        prepared = client.post(
            "/api/v1/validation/development/document-prepare",
            json=prepare_payload(response.json()).model_dump(mode="json"),
        )
        assert prepared.status_code == 200 and prepared.json()["active"] is False


def test_pdf_page_limit_rejects_partial_import():
    with pytest.raises(DocumentError, match="document_page_limit"):
        extract_document(pdf_bytes(tuple("" for _ in range(101))), "pdf")


def test_oversize_upload_rejected_before_preview_is_created(bridge):
    from app.knowledge.document_extract import MAX_BYTES

    with pytest.raises(AuditError, match="document_size_limit"):
        create_preview(bridge.root, b"x" * (MAX_BYTES + 1), "pdf")
    assert not (bridge.root / "var/import-previews").exists()


def test_docx_entities_are_not_expanded():
    from defusedxml.common import DefusedXmlException

    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        archive.writestr(
            "word/document.xml",
            '<!DOCTYPE document [<!ENTITY x "unsafe">]><document>&x;</document>',
        )
    with pytest.raises(DefusedXmlException):
        extract_document(output.getvalue(), "docx")


def test_parser_timeout_preserves_active_library(bridge, monkeypatch):
    import subprocess

    from app.retrieval import document_preview

    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired("synthetic", 35)

    monkeypatch.setattr(document_preview.subprocess, "run", timeout)
    with pytest.raises(AuditError, match="document_parse_timeout"):
        create_preview(bridge.root, docx_bytes(), "docx")
    assert bridge.active() is None
