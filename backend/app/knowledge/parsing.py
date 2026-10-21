import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

CC_BY = re.compile(r"https?://creativecommons\.org/licenses/by/(2\.0|3\.0|4\.0)/?", re.I)
PEDIATRIC = re.compile(
    r"\b(child(?:ren|hood)?|pediatric|paediatric|adolescen\w*|infant\w*)\b"
    r"|儿童|患儿|小儿|儿科|婴儿|青少年",
    re.I,
)


def clean(text):
    return re.sub(r"\s+", " ", text).strip()


def xml_text(node):
    return clean("".join(node.itertext())) if node is not None else ""


def parse_jats(data: bytes, expected_pmcid: str) -> dict:
    root = ET.fromstring(data)
    meta = root.find("./front/article-meta")
    if meta is None:
        raise ValueError("missing_article_metadata")
    ids = {n.get("pub-id-type"): xml_text(n) for n in meta.findall("article-id")}
    actual_pmcid = "PMC" + ids.get("pmc", ids.get("pmcid", "")).removeprefix("PMC")
    if actual_pmcid != expected_pmcid:
        raise ValueError("article_identity_mismatch")
    permissions = meta.find("permissions")
    license_text = xml_text(permissions)
    raw_permissions = (
        ET.tostring(permissions, encoding="unicode") if permissions is not None else ""
    )
    match = CC_BY.search(raw_permissions)
    # Some Frontiers JATS uses the full CC BY label without a URL/version.
    label_only = "Creative Commons Attribution License (CC BY)" in license_text
    textual_version = re.search(
        r"Creative Commons Attribution License\s+CC-BY\s+(2\.0|3\.0|4\.0)\b", license_text
    )
    if not match and not label_only and not textual_version:
        raise ValueError("license_not_allowlisted")
    if re.search(r"no commercial|non.?commercial|no.?derivatives", license_text, re.I):
        raise ValueError("license_conflict_requires_review")
    date_node = next(
        (
            n
            for n in meta.findall("pub-date")
            if n.get("pub-type") in ("epub", "ppub") or n.get("date-type") == "pub"
        ),
        meta.find("pub-date"),
    )
    date = "-".join(
        xml_text(date_node.find(k))
        for k in ("year", "month", "day")
        if date_node is not None and date_node.find(k) is not None
    )
    authors = [
        clean(xml_text(n.find("given-names")) + " " + xml_text(n.find("surname")))
        for contributor in meta.findall(".//contrib")
        if contributor.get("contrib-type", "author") == "author"
        for n in contributor.findall("name")
    ]
    paragraphs = []

    def walk(node, sections=(), locator="body"):
        if node.tag in ("fig", "table-wrap", "supplementary-material", "ref-list"):
            return
        if node.tag == "sec":
            title = xml_text(node.find("title"))
            if re.search(
                r"participating professional|author|contribution|funding|acknowledg|"
                r"competing interest|conflict of interest|data availability|publisher|"
                r"supplementary|disclosure|ethics|abbreviations|^contents$",
                title,
                re.I,
            ):
                return
            sections = (*sections, title) if title else sections
        if node.tag == "p":
            text = xml_text(node)
            if len(text) > 35:
                paragraphs.append(
                    {
                        "text": text,
                        "section": " / ".join(sections) or "Body",
                        "locator": locator,
                    }
                )
            return
        counts = {}
        for child in node:
            counts[child.tag] = counts.get(child.tag, 0) + 1
            walk(child, sections, f"{locator}/{child.tag}[{counts[child.tag]}]")

    body = root.find("body")
    if body is None:
        raise ValueError("no_fulltext_body")
    walk(body)
    if not paragraphs:
        raise ValueError("empty_fulltext_body")
    return {
        "title": xml_text(meta.find("title-group/article-title")),
        "authors": authors,
        "doi": ids.get("doi"),
        "publication_date": date,
        "language": root.get("{http://www.w3.org/XML/1998/namespace}lang", "en"),
        "license": "CC-BY-" + (match or textual_version).group(1)
        if match or textual_version
        else "CC-BY-version-unspecified",
        "license_url": match.group(0) if match else None,
        "license_statement": license_text,
        "paragraphs": paragraphs,
        "transformation": "JATS正文段落抽取；省略图、表、补充材料和参考文献，非完整排版复刻",
    }


class NIDCDParser(HTMLParser):
    VOID = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }
    SKIP = {"script", "style", "nav", "footer", "header", "aside", "figure", "form", "svg"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.active = None
        self.blocks = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)
        if (
            "main" in self.stack
            and not self.SKIP.intersection(self.stack)
            and tag in ("h1", "h2", "h3", "p", "li")
            and self.active is None
        ):
            self.active = (tag, len(self.stack), [])

    def handle_endtag(self, tag):
        if self.active and tag == self.active[0] and len(self.stack) == self.active[1]:
            self.blocks.append((tag, clean("".join(self.active[2]))))
            self.active = None
        if tag in self.stack:
            self.stack = self.stack[: len(self.stack) - 1 - self.stack[::-1].index(tag)]

    def handle_data(self, data):
        if self.active and not self.SKIP.intersection(self.stack):
            self.active[2].append(data)


def parse_nidcd(data: bytes) -> dict:
    parser = NIDCDParser()
    parser.feed(data.decode("utf-8"))
    title = next((text for tag, text in parser.blocks if tag == "h1"), "")
    paragraphs = []
    section = "Overview"
    for tag, text in parser.blocks:
        if tag in ("h2", "h3"):
            section = text
        elif tag in ("p", "li") and len(text) > 35:
            if tag == "li" and section == "Overview":
                continue
            if re.search(
                r"where can i find|additional information|more information|last updated",
                section,
                re.I,
            ):
                continue
            paragraphs.append(
                {"text": text, "section": section, "locator": f"main/block[{len(paragraphs) + 1}]"}
            )
    if not title or not paragraphs:
        raise ValueError("nidcd_main_body_missing")
    date = re.search(r"Last Updated Date.*?(\w+\s+\d{1,2},\s+\d{4})", data.decode("utf-8"), re.S)
    return {
        "title": title,
        "authors": ["National Institute on Deafness and Other Communication Disorders"],
        "doi": None,
        "publication_date": date.group(1) if date else None,
        "language": "en",
        "license": "NIDCD-public-domain-unless-noted",
        "license_url": "https://www.nidcd.nih.gov/policies",
        "license_statement": "NIDCD Copyright Policy: unless otherwise stated, site information "
        "is public domain. Third-party material requires separate review.",
        "paragraphs": paragraphs,
        "transformation": "网页main文字抽取；不提取图片/第三方媒体，导航等非正文可能需人工复核",
    }


def split_paragraphs(paragraphs, source_id, population, max_chars=1800):
    """Stable paragraph/character locators; no fabricated PDF page numbers."""
    import hashlib

    chunks = []
    for paragraph in paragraphs:
        text = paragraph["text"]
        review = population == "mixed_requires_screening" or bool(
            PEDIATRIC.search(text + " " + paragraph["section"])
        )
        for start in range(0, len(text), max_chars):
            part = text[start : start + max_chars]
            identity = f"{source_id}:{paragraph['locator']}:{start}:{part}"
            chunks.append(
                {
                    "id": hashlib.sha256(identity.encode()).hexdigest()[:24],
                    "text": part,
                    "section": paragraph["section"],
                    "locator": paragraph["locator"],
                    "start": start,
                    "end": start + len(part),
                    "population_status": "requires_screening" if review else "adult_dev_candidate",
                }
            )
    return chunks
