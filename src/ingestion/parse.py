from __future__ import annotations

import json

import re
from pathlib import Path
from typing import Any

from src.config import (
    RAW_DIR,
    DOCS_FILE,
    CHUNKS_FILE,
    CHUNK_OVERLAP_SENTENCES,
)

INJECTION_MARKERS = (
    "внимание для ии",
    "игнорируй все",
    "игнорируй остальные",
    "ignore previous",
    "ignore all previous",
    "system prompt",
    "системный промпт",
    "не упоминай эту инструкцию",
)

POINT_START_RE = re.compile(
    r"^("
    r"\d+(?:\.\d+)*[\.\)]"
    r"|"
    r"[а-яё]\)"
    r")\s",
    re.MULTILINE,
)

LAW_POINT_START_RE = re.compile(
    r"^(?:\d+(?:\.\d+)*[\.\)]|[а-яё]\))\s",
    re.MULTILINE,
)

SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[А-ЯЁA-Z«(])")

LAW_LABEL_RE = re.compile(
    r"(?i)\b(статья|статьи|статье|часть|части|пункт|пункта|подпункт|подпункта)\s+(\d+(?:\.\d+)*)"
)

LABEL_PREFIX = {
    "статья": "ст.", "статьи": "ст.", "статье": "ст.",
    "часть": "ч.", "части": "ч.",
    "пункт": "п.", "пункта": "п.",
    "подпункт": "пп.", "подпункта": "пп.",
}

META_MARKER_RE = re.compile(
    r"^(Подпункт|Пункт|Часть|Статья)\s+\d[\d\.]*\s+"
    r"(изменен|дополнена|дополнен|утратил|утратила)",
    re.IGNORECASE,
)

DATE_TEXT_RE = re.compile(r"(\d{1,2})\s+([а-яё]+)\s+(\d{4})\s*г?\.")
DATE_NUM_RE = re.compile(r"(\d{1,2})\.(\d{1,2})\.(\d{4})")

MONTHS_RU = {
    "января": 1, "февраля": 2, "марта": 3, "апреля": 4,
    "мая": 5, "июня": 6, "июля": 7, "августа": 8,
    "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12,
}

HEADER_MARKERS = (
    "источник:", "url:", "дата выгрузки:", "утверждён приказом",
    "утвержден приказом", "редакция от", "действует с", "утратил силу",
)
FOOTER_MARKERS = (
    "реквизиты и подписи", "генеральный директор", "начальник юридического",
    "руководитель службы", "поставщик:", "покупатель:", "арендодатель:",
    "арендатор:", "источник:", "url:",
)

CHUNK_MAX_CONTRACT = 500
CHUNK_MAX_LAW = 1500
CHUNK_MAX_OTHER = 1200


def to_iso_date(text: str | None) -> str | None:
    if not text:
        return None
    m = DATE_TEXT_RE.search(text)
    if m:
        day = int(m.group(1))
        month = MONTHS_RU.get(m.group(2).lower())
        year = int(m.group(3))
        if month:
            return f"{year:04d}-{month:02d}-{day:02d}"
    m = DATE_NUM_RE.search(text)
    if m:
        return f"{int(m.group(3)):04d}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    return None


def has_injection(text: str) -> bool:
    t = text.lower()
    return any(m in t for m in INJECTION_MARKERS)


def normalize_ws(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n").strip()


def is_meta_paragraph(text: str) -> bool:
    return bool(META_MARKER_RE.match(text.strip()))


def _detect_code(filename: str, header: str) -> tuple[str | None, str | None]:
    fn = filename.lower()
    h = header.lower()
    m = re.search(r"ст(?:атья|\.)\s*(\d+(?:\.\d+)*)", header, re.IGNORECASE)
    if "коап" in fn or "коап" in h:
        return "КоАП", m.group(1) if m else None
    if "нк_ст" in fn or "налоговый кодекс" in h:
        return "НК", m.group(1) if m else None
    if "тк_ст" in fn or "трудовой кодекс" in h:
        return "ТК", m.group(1) if m else None
    if "152фз" in fn or "о персональных данных" in h:
        return "152-ФЗ", m.group(1) if m else None
    if "мрот" in fn:
        return "82-ФЗ", "1"
    return None, None


def extract_metadata(text: str, filename: str) -> dict[str, Any]:
    meta: dict[str, Any] = {
        "doc_id": Path(filename).stem,
        "doc_type": "unknown",
        "title": "",
        "doc_number": "",
        "doc_date": None,
        "effective_from": None,
        "effective_to": None,
        "status": "active",
        "parent_doc_id": None,
        "source_file": filename,
        "code": None,
        "article": None,
    }

    header = text[:1500]
    fn = filename.lower()

    if fn.startswith("законы__"):
        meta["doc_type"] = "law"
        code, article = _detect_code(filename, header)
        meta["code"] = code
        meta["article"] = article
        if code and article:
            meta["doc_id"] = f"{code}_ст{article}"
            meta["doc_number"] = f"ст. {article} {code}"
        title_match = re.search(r"Статья\s+\d+(?:\.\d+)*\.\s*([^\n]+)", header)
        if title_match:
            meta["title"] = title_match.group(1).strip().rstrip(".")
        return meta

    addendum_match = re.search(
        r"(ДОПОЛНИТЕЛЬНОЕ\s+СОГЛАШЕНИЕ)\s*(?:№\s*)?([\w\-/]+)?\s*к\s*договору(?:\s+\w+)?\s*№\s*([\w\-/]+)",
        header, re.IGNORECASE,
    )
    if addendum_match:
        meta["doc_type"] = "addendum"
        num = (addendum_match.group(2) or "").strip()
        parent_num = (addendum_match.group(3) or "").strip()
        meta["doc_number"] = num
        meta["parent_doc_id"] = parent_num
        meta["title"] = f"Доп. соглашение № {num} к договору № {parent_num}".strip()
        d = re.search(
            r"г\.\s*[А-ЯЁ][а-яё\-]+\s*[—-]\s*(\d{1,2}\s+[а-яё]+\s+\d{4}\s*г?\.)",
            header,
        )
        meta["doc_date"] = to_iso_date(d.group(1)) if d else None
        meta["doc_id"] = f"доп_{num}_к_{parent_num}".replace("/", "_")
        return meta

    contract_match = re.search(r"(ДОГОВОР\s+[А-ЯЁ\s]+)\s*№\s*([\w\-/]+)", header)
    if contract_match:
        meta["doc_type"] = "contract"
        meta["title"] = contract_match.group(1).strip()
        num = contract_match.group(2).strip()
        meta["doc_number"] = num
        meta["doc_id"] = num.replace("/", "_")
        d = re.search(
            r"г\.\s*[А-ЯЁ][а-яё\-]+\s*[—-]\s*(\d{1,2}\s+[а-яё]+\s+\d{4}\s*г?\.)",
            header,
        )
        meta["doc_date"] = to_iso_date(d.group(1)) if d else None
        return meta

    if re.search(r"^РЕГЛАМЕНТ\b", header, re.MULTILINE):
        meta["doc_type"] = "regulation"
        title_match = re.search(r"^РЕГЛАМЕНТ\s+(.+)$", header, re.MULTILINE)
        if title_match:
            meta["title"] = title_match.group(1).strip()
        ed = re.search(r"Редакция от\s+(\d{2}\.\d{2}\.\d{4})", header)
        eff = re.search(r"Действует с\s+(\d{2}\.\d{2}\.\d{4})", header)
        if ed:
            meta["effective_from"] = to_iso_date(ed.group(1))
        elif eff:
            meta["effective_from"] = to_iso_date(eff.group(1))
        if "УТРАТИЛА СИЛУ" in header or "утратил силу" in header:
            meta["status"] = "superseded"
            eff_to = re.search(r"с\s+(\d{2}\.\d{2}\.\d{4})", header)
            if eff_to:
                meta["effective_to"] = to_iso_date(eff_to.group(1))
        meta["doc_id"] = f"reg_{meta['effective_from'] or 'unknown'}".replace("-", "")
        return meta

    if "СЛУЖЕБНАЯ ЗАПИСКА" in header or "Исх. №" in header:
        meta["doc_type"] = "memo"
        meta["title"] = "Служебная записка / Письмо"
        d = re.search(
            r"от\s+(\d{1,2}(?:\.\d{1,2}\.\d{4}|\s+[а-яё]+\s+\d{4}\s*г?\.?))",
            header,
        )
        meta["doc_date"] = to_iso_date(d.group(1)) if d else None
        num = re.search(r"№\s*([\w\-/]+)\s+от", header)
        if num:
            meta["doc_id"] = f"memo_{num.group(1)}".replace("/", "_")
        return meta

    return meta


def _link_parent_docs(docs: list[dict[str, Any]]) -> None:
    by_number = {d["doc_number"]: d["doc_id"] for d in docs if d["doc_number"]}
    for d in docs:
        if d["doc_type"] == "addendum" and d.get("parent_doc_id"):
            d["parent_doc_id"] = by_number.get(d["parent_doc_id"], d["parent_doc_id"])


def extract_anchor_from_part(part: str, doc_type: str = "contract") -> str:
    head = part.lstrip()

    if doc_type == "law":
        m = LAW_LABEL_RE.search(head[:100])
        if m:
            prefix = LABEL_PREFIX.get(m.group(1).lower(), "п.")
            return f"{prefix} {m.group(2)}"
        m = re.match(r"^(\d+(?:\.\d+)*)[\.\)]", head)
        if m:
            return f"ч. {m.group(1)}"
        m = re.match(r"^(\d+)\)", head)
        if m:
            return f"п. {m.group(1)})"
        return ""

    m = re.match(r"^(\d+(?:\.\d+)*)[\.\)]", head)
    if m:
        return m.group(1)
    m = re.match(r"^[а-яё]\)", head)
    if m:
        return head[:2]
    return ""


def extract_anchor_from_chunk(parts: list[str], doc_type: str = "contract") -> str:
    for p in parts:
        if is_meta_paragraph(p):
            continue
        a = extract_anchor_from_part(p, doc_type)
        if a:
            return a
    return ""


def split_into_sentences(text: str) -> list[str]:
    return [s.strip() for s in SENTENCE_SPLIT_RE.split(text) if s.strip()]


def take_tail_sentences(text: str, n: int) -> str:
    if n <= 0:
        return ""
    sentences = split_into_sentences(text)
    return " ".join(sentences[-n:]) if sentences else ""


def _classify_chunk_type(text: str, idx: int, total: int) -> str:
    if is_meta_paragraph(text):
        return "meta"
    low = text.lower()
    if any(m in low for m in HEADER_MARKERS) and idx == 0:
        return "header"
    if any(m in low for m in FOOTER_MARKERS) and idx == total - 1:
        return "footer"
    return "body"


def _max_chars(doc_type: str) -> int:
    if doc_type in ("contract", "addendum"):
        return CHUNK_MAX_CONTRACT
    if doc_type == "law":
        return CHUNK_MAX_LAW
    return CHUNK_MAX_OTHER


def _split_points(text: str, doc_type: str) -> list[str]:
    if doc_type == "law":
        pattern = LAW_POINT_START_RE
    else:
        pattern = POINT_START_RE

    starts = [m.start() for m in pattern.finditer(text)]

    if not starts:
        return [text]

    parts: list[str] = []
    if starts[0] > 0:
        parts.append(text[:starts[0]])
    for i, s in enumerate(starts):
        e = starts[i + 1] if i + 1 < len(starts) else len(text)
        parts.append(text[s:e])
    return [p.strip() for p in parts if p.strip()]


def split_into_chunks(text: str, meta: dict[str, Any]) -> list[dict[str, Any]]:
    text = normalize_ws(text)
    if not text:
        return []

    doc_type = meta["doc_type"]
    max_chars = _max_chars(doc_type)
    parts = _split_points(text, doc_type)

    chunks: list[dict[str, Any]] = []
    buffer = ""
    buffer_parts: list[str] = []

    def flush():
        nonlocal buffer, buffer_parts
        if not buffer.strip():
            return
        anchor = (
            extract_anchor_from_chunk(buffer_parts, doc_type)
            or extract_anchor_from_part(buffer, doc_type)
        )
        chunk_idx = len(chunks) + 1
        chunk_id = f"{meta['doc_id']}::p{anchor or 'hdr'}_{chunk_idx}"
        chunks.append({
            "chunk_id": chunk_id,
            "doc_id": meta["doc_id"],
            "anchor": anchor,
            "text": buffer.strip(),
            "contains_injection": has_injection(buffer),
            "meta": meta,
        })
        buffer = ""
        buffer_parts = []

    for part in parts:
        if len(part) > max_chars:
            if buffer:
                flush()
            sentences = split_into_sentences(part)
            current = ""
            for s in sentences:
                if len(current) + len(s) + 1 <= max_chars:
                    current = (current + " " + s) if current else s
                else:
                    if current:
                        buffer, buffer_parts = current, [current]
                        flush()
                    current = s
            if current:
                buffer, buffer_parts = current, [current]
            continue

        is_new_item = bool(
            re.match(r"^\d+(?:\.\d+)*[\.\)]", part)
            or re.match(r"^[а-яё]\)", part)
        )
        if is_new_item and buffer:
            flush()

        if len(buffer) + len(part) + 1 <= max_chars:
            buffer = (buffer + "\n" + part) if buffer else part
            buffer_parts.append(part)
            continue

        flush()
        overlap = take_tail_sentences(chunks[-1]["text"], CHUNK_OVERLAP_SENTENCES) if chunks else ""
        buffer = (overlap + "\n" + part) if overlap else part
        buffer_parts = [part]

    flush()

    total = len(chunks)
    for i, c in enumerate(chunks):
        c["chunk_type"] = _classify_chunk_type(c["text"], i, total)

    return chunks


def process_all() -> None:
    docs: list[dict[str, Any]] = []
    all_chunks: list[dict[str, Any]] = []

    for filepath in sorted(RAW_DIR.glob("*.txt")):
        text = filepath.read_text(encoding="utf-8-sig")
        meta = extract_metadata(text, filepath.name)

        doc_record = meta.copy()
        doc_record["text"] = text
        docs.append(doc_record)

        chunks = split_into_chunks(text, meta)
        all_chunks.extend(chunks)

        n_inj = sum(1 for c in chunks if c["contains_injection"])
        n_meta = sum(1 for c in chunks if c.get("chunk_type") == "meta")
        print(
            f"Обработан: {filepath.name} | "
            f"тип: {meta['doc_type']:<10} | "
            f"doc_id: {meta['doc_id']:<22} | "
            f"чанков: {len(chunks):>3} | "
            f"meta: {n_meta:>2} | "
            f"инъекций: {n_inj}"
        )

    _link_parent_docs(docs)
    by_id = {d["doc_id"]: d for d in docs}
    for c in all_chunks:
        doc = by_id.get(c["doc_id"])
        if doc:
            c["meta"] = {k: v for k, v in doc.items() if k != "text"}

    with open(DOCS_FILE, "w", encoding="utf-8") as f:
        for d in docs:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
        for c in all_chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    unknown = [d["doc_id"] for d in docs if d["doc_type"] == "unknown"]
    no_anchor = sum(1 for c in all_chunks if not c["anchor"])
    n_meta = sum(1 for c in all_chunks if c.get("chunk_type") == "meta")
    n_header_footer = sum(1 for c in all_chunks if c.get("chunk_type") in ("header", "footer"))
    inj = sum(1 for c in all_chunks if c["contains_injection"])

    print(f"\nГотово! Документов: {len(docs)}, чанков: {len(all_chunks)}")
    print(f"unknown doc_type: {len(unknown)} → {unknown}")
    print(f"Чанков без anchor: {no_anchor} / {len(all_chunks)}")
    print(f"Чанков meta: {n_meta} / {len(all_chunks)}")
    print(f"Чанков header/footer: {n_header_footer} / {len(all_chunks)}")
    print(f"Чанков с инъекцией: {inj} / {len(all_chunks)}")


if __name__ == "__main__":
    process_all()