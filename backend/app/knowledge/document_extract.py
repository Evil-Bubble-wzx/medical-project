"""Bounded text-only PDF/DOCX extraction. No OCR, scripts, external links or macros."""

import io
import zipfile

from defusedxml.ElementTree import fromstring
from pypdf import PdfReader, apply_configuration

MAX_BYTES = 8 * 1024 * 1024
MAX_CHARS = 150000
MAX_UNITS = 2000
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


class DocumentError(ValueError):
    pass


def clean(text):
    return "".join(c for c in text if ord(c) >= 32 or c in "\n\t").strip()


def extract_document(data, kind):
    if not data or len(data) > MAX_BYTES:
        raise DocumentError("document_size_limit")
    units, warnings = [], []
    if kind == "pdf":
        if not data.startswith(b"%PDF-"):
            raise DocumentError("invalid_pdf")
        with apply_configuration(
            maximum_declared_stream_length=MAX_BYTES,
            zlib_maximum_output_length=MAX_BYTES,
            array_based_stream_maximum_output_length=MAX_BYTES,
            stream_decoding_work_maximum_length=MAX_BYTES * 3,
        ):
            reader = PdfReader(io.BytesIO(data), strict=True)
            if reader.is_encrypted:
                raise DocumentError("encrypted_document")
            if not 1 <= len(reader.pages) <= 100:
                raise DocumentError("document_page_limit")
            empty = []
            for number, page in enumerate(reader.pages, 1):
                text = clean(page.extract_text() or "")
                if not text:
                    empty.append(number)
                else:
                    units.append(
                        {
                            "text": text,
                            "section": f"PDF第{number}页",
                            "locator": f"PDF page {number}",
                            "page": number,
                        }
                    )
                if sum(len(u["text"]) for u in units) > MAX_CHARS:
                    raise DocumentError("document_text_limit")
            if empty:
                warnings.append("pdf_pages_without_text_need_ocr_or_check")
            if not units:
                warnings.append("no_extractable_text")
            # Mixed scanned/text pages must not silently become a complete import.
            return result(kind, units, warnings, not empty and bool(units), empty)
    if kind != "docx":
        raise DocumentError("unsupported_document_type")
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        entries = archive.infolist()
        if (
            len(entries) > 1500
            or sum(e.file_size for e in entries) > 32 * 1024 * 1024
            or len({e.filename for e in entries}) != len(entries)
            or any(e.flag_bits & 1 for e in entries)
        ):
            raise DocumentError("unsafe_docx_archive")
        if "word/document.xml" not in archive.namelist():
            raise DocumentError("invalid_docx")
        info = archive.getinfo("word/document.xml")
        if info.file_size > 8 * 1024 * 1024:
            raise DocumentError("document_text_limit")
        root = fromstring(archive.read(info))
        body = root.find(W + "body")
        if body is None:
            raise DocumentError("invalid_docx")
        paragraph, table = 0, 0
        for child in body:
            if child.tag == W + "p":
                paragraph += 1
                text = paragraph_text(child)
                if text:
                    units.append(
                        {
                            "text": text,
                            "section": f"Word第{paragraph}段",
                            "locator": f"Word paragraph {paragraph}",
                        }
                    )
            elif child.tag == W + "tbl":
                table += 1
                warnings.append("docx_tables_linearized_verify_relationships")
                for row_number, row in enumerate(child.findall(W + "tr"), 1):
                    for cell_number, cell in enumerate(row.findall(W + "tc"), 1):
                        text = "\n".join(paragraph_text(p) for p in cell.findall(W + "p"))
                        if text.strip():
                            label = f"Word表{table}第{row_number}行第{cell_number}单元格"
                            units.append(
                                {
                                    "text": text,
                                    "section": label,
                                    "locator": (
                                        f"Word table {table}/row {row_number}/cell {cell_number}"
                                    ),
                                }
                            )
                        if cell.find(".//" + W + "tbl") is not None:
                            warnings.append("docx_nested_tables_not_importable")
            if len(units) > MAX_UNITS or sum(len(u["text"]) for u in units) > MAX_CHARS:
                raise DocumentError("document_text_limit")
        if any(e.filename.startswith("word/media/") for e in entries):
            warnings.append("docx_images_not_extracted")
        warnings.append("docx_headers_footnotes_textboxes_not_extracted")
        if not units:
            warnings.append("no_extractable_text")
        return result(
            kind,
            units,
            warnings,
            bool(units) and "docx_nested_tables_not_importable" not in warnings,
            [],
        )


def paragraph_text(paragraph):
    fragments = []

    def visit(node):
        if node.tag in (W + "drawing", W + "pict", W + "object", W + "del"):
            return
        if node.tag == W + "t":
            fragments.append(node.text or "")
        elif node.tag == W + "tab":
            fragments.append("\t")
        elif node.tag in (W + "br", W + "cr"):
            fragments.append("\n")
        else:
            for child in node:
                visit(child)

    visit(paragraph)
    return clean("".join(fragments))


def result(kind, units, warnings, allowed, empty):
    return {
        "format": kind,
        "parser_version": "local-document-extract-1.0",
        "units": units,
        "warnings": sorted(set(warnings)),
        "can_import": allowed,
        "empty_pages": empty,
        "characters": sum(len(u["text"]) for u in units),
        "clinical_approval": False,
    }
