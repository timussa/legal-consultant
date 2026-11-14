"""Knowledge base holder: owns the Engine, reloads it and tracks document changes.

When a document changes, answers that cited it are marked outdated and their authors are notified.
"""
from __future__ import annotations

import hashlib
import logging
import threading
from typing import Callable

from server.db import Database, now
from server.labels import iso_to_ru
from server.notify import active_users, dialog_target, document_target, notify

log = logging.getLogger(__name__)

TYPE_LABELS = {"contract": "Договор", "addendum": "Допсоглашение", "regulation": "Регламент",
               "memo": "Внутренний документ", "law": "Закон", "unknown": "Документ"}

# Home page tiles. The image keys are the ones the frontend ships.
SECTIONS = [
    ("contracts", "Договоры и допсоглашения", "Поставка, аренда, ДС", "contracts",
     lambda d: d["doc_type"] in ("contract", "addendum")),
    ("internal", "Внутренние документы", "Регламенты, письма, записки", "internal",
     lambda d: d["doc_type"] in ("regulation", "memo")),
    ("taxes", "Налоговый кодекс", "НДС, НДФЛ, налог на прибыль", "taxes",
     lambda d: d["doc_type"] == "law" and d.get("code") == "НК"),
    ("personal-data", "Персональные данные", "152-ФЗ, КоАП ст. 13.11", "personalData",
     lambda d: d["doc_type"] == "law" and d.get("code") in ("152-ФЗ", "КоАП")),
    ("labor", "Трудовой кодекс", "Трудовой договор, отпуска, оплата", "labor",
     lambda d: d["doc_type"] == "law" and d.get("code") == "ТК"),
    ("other", "Прочие законы", "Федеральные законы", "laws",
     lambda d: d["doc_type"] == "law" and d.get("code") not in ("НК", "ТК", "152-ФЗ", "КоАП")),
]


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def short_label(doc: dict) -> str:
    """Compact document name for chips: «П-17/2024», «Регламент ред. 2025», «ст. 164 НК»."""
    if doc["doc_type"] == "regulation":
        return "Регламент" + (f" ред. {doc['effective_from'][:4]}" if doc.get("effective_from") else "")
    if doc["doc_type"] == "addendum":
        return f"ДС № {doc['doc_number']}" if doc.get("doc_number") else doc["title"]
    return doc.get("doc_number") or doc["title"][:40]


def document_date(doc: dict) -> str | None:
    return doc.get("effective_from") or doc.get("doc_date")


class KnowledgeBase:
    def __init__(self, factory: Callable[[], object]):
        self.factory = factory
        self.engine = None
        self.reload_lock = threading.Lock()

    def load(self) -> None:
        self.engine = self.factory()

    def close(self) -> None:
        _close(self.engine)

    def reload(self) -> None:
        # Build first, swap afterwards: requests keep the previous engine until the new one is ready.
        with self.reload_lock:
            fresh = self.factory()
            old, self.engine = self.engine, fresh
            _close(old)

    # ---- documents -------------------------------------------------------------------------
    def editions(self, document_id: str) -> list[dict]:
        return sorted([d for d in self.engine.docs if d["public_id"] == document_id],
                      key=lambda d: d.get("effective_from") or "")

    def catalogue(self) -> list[dict]:
        grouped: dict[str, list[dict]] = {}
        for d in self.engine.docs:
            grouped.setdefault(d["public_id"], []).append(d)
        result = []
        for document_id, docs in grouped.items():
            latest = sorted(docs, key=lambda d: d.get("effective_from") or "")[-1]
            result.append({"id": document_id, "title": latest["title"], "type": latest["doc_type"],
                           "typeLabel": TYPE_LABELS.get(latest["doc_type"], "Документ"),
                           "label": short_label(latest), "number": latest.get("doc_number") or "",
                           "date": document_date(latest), "editionCount": len(docs),
                           "files": [d["source_file"] for d in docs]})
        return sorted(result, key=lambda d: (d["type"] == "law", d["title"]))

    # ---- change tracking -------------------------------------------------------------------
    def sync(self, db: Database) -> list[dict]:
        """Compares the loaded corpus with the last known state. The first run only records a baseline."""
        current = {d["doc_id"]: d for d in self.engine.docs}
        changes = []
        stamp = now()
        with db.connect(write=True) as con:
            known = {r["doc_id"]: r for r in con.execute("SELECT * FROM kb_documents")}
            baseline = not known
            for doc_id, doc in current.items():
                digest = content_hash(doc["text"])
                row = known.get(doc_id)
                if row is None:
                    con.execute("INSERT INTO kb_documents VALUES (?,?,?,?,?,?,NULL)",
                                (doc_id, doc["public_id"], doc["title"], digest, stamp, None if baseline else stamp))
                    if not baseline:
                        changes.append({"docId": doc_id, "change": "added", "doc": doc})
                elif row["content_hash"] != digest or row["removed_at"]:
                    con.execute("UPDATE kb_documents SET content_hash=?, title=?, changed_at=?, removed_at=NULL WHERE doc_id=?",
                                (digest, doc["title"], stamp, doc_id))
                    changes.append({"docId": doc_id, "change": "changed", "doc": doc})
            for doc_id, row in known.items():
                if doc_id not in current and not row["removed_at"]:
                    con.execute("UPDATE kb_documents SET removed_at=?, changed_at=? WHERE doc_id=?", (stamp, stamp, doc_id))
                    changes.append({"docId": doc_id, "change": "removed",
                                    "doc": {"doc_id": doc_id, "public_id": row["document_id"], "title": row["title"],
                                            "edition_id": "original", "doc_type": "unknown"}})
            if changes:
                self._announce(con, changes)
        if changes:
            log.info("knowledge base changes: %s", ", ".join(f"{c['change']}:{c['docId']}" for c in changes))
        return [{"docId": c["docId"], "documentId": c["doc"]["public_id"], "title": c["doc"]["title"],
                 "change": c["change"]} for c in changes]

    @staticmethod
    def _announce(con, changes: list[dict]) -> None:
        verbs = {"added": "Добавлен документ", "changed": "Изменён документ", "removed": "Документ исключён из базы"}
        users = active_users(con)
        for c in changes:
            doc = c["doc"]
            target = None if c["change"] == "removed" else document_target(doc["public_id"], doc.get("edition_id"))
            when = iso_to_ru(document_date(doc)) if c["change"] != "removed" and document_date(doc) else ""
            notify(con, users, "update", f"{verbs[c['change']]}: {doc['title'][:90]}",
                   ("Действует с " + when + ". " if when else "") + "Ответы, которые на него ссылаются, стоит перепроверить.",
                   target, dedupe_key=f"kb:{c['docId']}:{c['change']}:{now()[:16]}")
            if c["change"] == "added":
                continue
            reason = ("Источник исключён из базы: " if c["change"] == "removed" else "Источник изменён: ") + doc["title"][:120]
            rows = con.execute(
                "SELECT DISTINCT d.id, d.number, d.owner_id FROM answer_sources s JOIN dialogs d ON d.id = s.dialog_id"
                " WHERE s.doc_id = ? AND d.deleted_at IS NULL", (c["docId"],)).fetchall()
            for row in rows:
                con.execute("UPDATE dialogs SET outdated_reason=? WHERE id=?", (reason, row["id"]))
                notify(con, [row["owner_id"]], "outdated", f"Ответ №{row['number']} мог устареть",
                       reason + ". Задайте вопрос повторно, чтобы получить ответ по актуальной базе.",
                       dialog_target(row["id"]), dedupe_key=f"outdated:{row['id']}:{c['docId']}:{now()[:16]}")


def _close(engine) -> None:
    client = getattr(getattr(engine, "gateway", None), "client", None)
    if client is not None and hasattr(client, "close"):
        client.close()
