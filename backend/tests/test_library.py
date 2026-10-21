import xml.etree.ElementTree as ET

import pytest

from app.knowledge.collect import collect, fetch
from app.knowledge.library import file_hash, read_json, rebuild_index, search, write_json
from app.knowledge.parsing import parse_jats, parse_nidcd, split_paragraphs, xml_text


def article(license_url="https://creativecommons.org/licenses/by/4.0/", pmcid="123"):
    return f'''<article xml:lang="en"><front><article-meta>
    <article-id pub-id-type="pmc">{pmcid}</article-id>
    <article-id pub-id-type="doi">10.0000/test</article-id>
    <title-group><article-title>Synthetic adult test</article-title></title-group>
    <permissions><license><ext-link href="{license_url}">{license_url}</ext-link>
    </license></permissions>
    </article-meta></front><body><sec><title>Adult evidence</title>
    <p>Adult tinnitus synthetic paragraph for engineering tests only, not medical evidence.</p>
    <p>Children tinnitus synthetic paragraph for engineering tests only, not medical evidence.</p>
    <sec><title>Nested section</title>
    <p>A nested synthetic paragraph long enough to preserve source location.</p></sec>
    <fig><p>This figure paragraph should not enter the normalized body.</p></fig>
    </sec><sec><title>Funding</title>
    <p>Private funding and author details are excluded from search.</p>
    </sec></body></article>'''.encode()


def test_jats_identity_license_and_real_xpath():
    raw = article()
    parsed = parse_jats(raw, "PMC123")
    assert parsed["license"] == "CC-BY-4.0"
    assert len(parsed["paragraphs"]) == 3
    root = ET.fromstring(raw)
    for paragraph in parsed["paragraphs"]:
        assert xml_text(root.find(paragraph["locator"])) == paragraph["text"]
    assert parsed["paragraphs"][-1]["section"] == "Adult evidence / Nested section"


@pytest.mark.parametrize(
    "license_url", ["https://creativecommons.org/licenses/by-nc/4.0/", "All rights reserved"]
)
def test_non_allowlisted_license_rejected(license_url):
    with pytest.raises(ValueError, match="license_not_allowlisted"):
        parse_jats(article(license_url), "PMC123")


def test_wrong_source_identity_rejected():
    with pytest.raises(ValueError, match="identity_mismatch"):
        parse_jats(article(), "PMC999")


def test_explicit_textual_cc_by_license_without_url():
    text = "Creative Commons Attribution License CC-BY 4.0."
    parsed = parse_jats(article(license_url=text), "PMC123")
    assert parsed["license"] == "CC-BY-4.0"
    assert parsed["license_url"] is None


def test_default_author_role_preserves_attribution_but_excludes_editors():
    data = article().replace(
        b"</article-meta>",
        b"""<contrib-group>
        <contrib><name><surname>Author</surname><given-names>Test</given-names></name></contrib>
        <contrib contrib-type="editor"><name><surname>Editor</surname></name></contrib>
        </contrib-group></article-meta>""",
    )
    assert parse_jats(data, "PMC123")["authors"] == ["Test Author"]


@pytest.mark.parametrize(
    "text",
    [
        "Creative Commons Attribution License CC-BY-NC 4.0.",
        "Creative Commons Attribution License CC-BY-ND 4.0.",
        "Creative Commons Attribution License CC-BY 4.0. Non-commercial only",
    ],
)
def test_restricted_textual_license_is_rejected(text):
    with pytest.raises(ValueError, match="license"):
        parse_jats(article(license_url=text), "PMC123")


def test_chunk_offsets_and_population_screening_are_stable():
    parsed = parse_jats(article(), "PMC123")
    chunks = split_paragraphs(parsed["paragraphs"], "test-v1", "adult_relevant_general", 40)
    assert chunks == split_paragraphs(parsed["paragraphs"], "test-v1", "adult_relevant_general", 40)
    lookup = {p["locator"]: p for p in parsed["paragraphs"]}
    for chunk in chunks:
        assert lookup[chunk["locator"]]["text"][chunk["start"] : chunk["end"]] == chunk["text"]
    assert any(c["population_status"] == "requires_screening" for c in chunks)
    mixed = split_paragraphs(parsed["paragraphs"], "test-v1", "mixed_requires_screening")
    assert all(c["population_status"] == "requires_screening" for c in mixed)


def test_html_parser_excludes_navigation_toc_images_and_scripts():
    html = b"""<html><nav><p>Navigation text should never appear in results.</p></nav>
    <main><h1>Test page</h1><ul><li>This is a table of contents entry not evidence.</li></ul>
    <h2>Evidence</h2><p>Synthetic adult content only, sufficiently long for this parser.</p>
    <script>secret script should never appear in search</script>
    <figure><p>Third party image caption must be excluded completely.</p></figure></main></html>"""
    parsed = parse_nidcd(html)
    assert parsed["title"] == "Test page"
    assert len(parsed["paragraphs"]) == 1
    assert parsed["paragraphs"][0]["section"] == "Evidence"


@pytest.fixture
def local_library(tmp_path, monkeypatch):
    seed = tmp_path / "seed.json"
    write_json(
        seed,
        {
            "version": "test",
            "scope": "development",
            "sources": [
                {
                    "id": "adult-test",
                    "kind": "jats",
                    "pmcid": "PMC123",
                    "title_zh": "成人耳鸣测试",
                    "topics": ["tinnitus"],
                    "document_type": "synthetic",
                    "population": "adult_only",
                },
            ],
            "metadata_only": [
                {
                    "id": "metadata-only-test",
                    "title": "中文题录",
                    "source_url": "https://example.org/metadata",
                    "status": "permission_unverified",
                    "note": "test",
                }
            ],
        },
    )
    monkeypatch.setattr(
        "app.knowledge.collect.fetch", lambda url: b"policy" if "policies" in url else article()
    )
    monkeypatch.setattr("app.knowledge.collect.time.sleep", lambda seconds: None)
    root = tmp_path / "library"
    counts = collect(seed, root)
    return root, seed, counts


def test_library_build_chinese_search_and_metadata_boundary(local_library):
    root, _, counts = local_library
    assert counts["documents"] == 1
    assert counts["indexed_chunks"] == 2
    assert counts["staged_chunks"] == 1
    hits = search(root, "耳鸣", topic="tinnitus")
    assert hits and all("Children" not in h["text"] for h in hits)
    assert all(h["clinical_review"] == "pending" and not h["production_eligible"] for h in hits)
    assert search(root, "中文题录") == []
    assert search(root, "耳鸣", topic="rhinitis") == []
    assert (root / "CATALOG.md").exists()


def test_repeat_collection_uses_verified_cache(local_library, monkeypatch):
    root, seed, _ = local_library
    before = file_hash(root / "library.sqlite3")

    def forbidden(url):
        raise AssertionError("Repeated collection should not fetch remotely")

    monkeypatch.setattr("app.knowledge.collect.fetch", forbidden)
    result = collect(seed, root)
    assert result["failures"] == 0
    assert file_hash(root / "library.sqlite3") != ""
    assert before
    assert search(root, "耳鸣")


def test_changed_original_detected(local_library):
    root, _, _ = local_library
    manifest = read_json(root / "manifest.json")
    (root / manifest["documents"][0]["raw_path"]).write_bytes(b"corrupted")
    with pytest.raises(ValueError, match="checksum_mismatch"):
        search(root, "耳鸣")


def test_stale_index_detected(local_library):
    root, _, _ = local_library
    manifest = read_json(root / "manifest.json")
    manifest["version"] = "changed"
    write_json(root / "manifest.json", manifest)
    with pytest.raises(ValueError, match="stale"):
        search(root, "耳鸣")


def test_failed_rebuild_preserves_existing_index(local_library):
    root, _, _ = local_library
    before = file_hash(root / "library.sqlite3")
    manifest = read_json(root / "manifest.json")
    manifest["documents"][0]["production_eligible"] = True
    write_json(root / "manifest.json", manifest)
    with pytest.raises(ValueError, match="must_not_claim_clinical_approval"):
        rebuild_index(root)
    assert file_hash(root / "library.sqlite3") == before


@pytest.mark.parametrize(
    "url", ["http://www.ebi.ac.uk/test", "https://example.org/test", "https://127.0.0.1/private"]
)
def test_collector_download_host_allowlist(url):
    with pytest.raises(ValueError, match="origin_not_allowlisted"):
        fetch(url)
