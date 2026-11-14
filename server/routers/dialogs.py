"""Questions, dialog history, lawyer feedback and the head's review of disputed answers."""
from __future__ import annotations

import json
import logging
import threading
import time
from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field

from legal_core import ModelError, answer_text
from server import guard
from server.db import dumps, now
from server.deps import User, audit, client_ip, current_user, head_user, state
from server.kb import TYPE_LABELS, short_label
from server.labels import date_label, initials, short_name
from server.notify import active_users, dialog_target, notify

router = APIRouter(prefix="/api/v1", tags=["dialogs"])
log = logging.getLogger(__name__)

HISTORY_TURNS = 12
TITLE_LENGTH = 48
# Striped locks: turns of one dialog are serialized, different dialogs run in parallel.
_locks = [threading.Lock() for _ in range(64)]


class Ask(BaseModel):
    question: str = Field(min_length=1, max_length=15000)
    dialogId: str = Field(min_length=1, max_length=100, pattern=r"^[\w.-]+$")
    documentId: str | None = Field(default=None, max_length=200)
    eventDate: date | None = None


class Feedback(BaseModel):
    value: Literal["correct", "wrong", "disputed"] | None = None
    comment: str | None = Field(default=None, max_length=2000)


class Review(BaseModel):
    decision: Literal["approved", "needs-fix"]
    comment: str | None = Field(default=None, max_length=2000)


class DialogPatch(BaseModel):
    title: str = Field(min_length=1, max_length=200)


def make_title(question: str) -> str:
    text = " ".join(question.split()).rstrip("?")
    return text if len(text) <= TITLE_LENGTH else text[:TITLE_LENGTH] + "…"


def effective_status(row) -> str:
    if row["feedback"] == "disputed" and row["review"] is None:
        return "disputed"
    return row["status"]


def document_label(answer: dict) -> str:
    chips = [c["value"] for c in answer.get("context", []) if c.get("label") != "База"]
    return ", ".join(chips[:2]) if chips else "База знаний"


def serialize(row, offset: int, with_messages: list | None = None) -> dict:
    answer = json.loads(row["answer"])
    result = {
        "id": row["id"], "number": f"№{row['number']}", "title": row["title"], "question": row["question"],
        "documentLabel": document_label(answer), "timeLabel": date_label(row["updated_at"], offset, with_time=True),
        "status": effective_status(row), "answerStatus": row["status"], "answer": answer,
        "eventDate": row["event_date"], "documentId": row["document_id"],
        "feedback": row["feedback"], "review": row["review"],
        "isOutdated": bool(row["outdated_reason"]), "outdatedReason": row["outdated_reason"],
        "author": {"id": row["owner_id"], "name": row["owner_name"], "initials": initials(row["owner_name"]),
                   "shortName": short_name(row["owner_name"])},
        "createdAt": row["created_at"], "updatedAt": row["updated_at"],
    }
    if with_messages is not None:
        result["messages"] = with_messages
        questions = [m for m in with_messages if m["role"] == "user"]
        answers = [m for m in with_messages if m["role"] == "assistant"]
        if len(questions) > 1 and len(answers) > 1:
            previous = answers[-2].get("answer") or {}
            result["history"] = {"summary": f"предыдущий вопрос · {str(previous.get('verdict', '')).lower()}",
                                 "question": questions[-2]["text"], "answer": previous.get("verdict", "")}
    return result


DIALOG_SELECT = ("SELECT d.*, u.name AS owner_name FROM dialogs d JOIN users u ON u.id = d.owner_id"
                 " WHERE d.deleted_at IS NULL")


def load_dialog(con, dialog_id: str, user: User, for_write: bool = False):
    row = con.execute(DIALOG_SELECT + " AND d.id = ?", (dialog_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "Диалог не найден")
    # Heads may read team dialogs; only the author changes them (review has its own route).
    if row["owner_id"] != user.id and (for_write or not user.is_head):
        raise HTTPException(404, "Диалог не найден")
    return row


def messages_of(con, dialog_id: str) -> list[dict]:
    rows = con.execute("SELECT * FROM messages WHERE dialog_id=? ORDER BY id", (dialog_id,))
    return [{"role": r["role"], "text": r["text"], "answer": json.loads(r["answer"]) if r["answer"] else None,
             "eventDate": r["event_date"], "createdAt": r["created_at"]} for r in rows]


def enrich(answer: dict, engine) -> list[tuple]:
    """Builds document chips from cited sources and returns rows for answer_sources."""
    by_edition = {(d["public_id"], d["edition_id"]): d for d in engine.docs}
    cited, rows = [], []
    for number, source in enumerate(answer.get("sources", []), 1):
        doc = by_edition.get((source.get("documentId"), source.get("editionId")))
        if doc is None:
            continue
        rows.append((number, doc["doc_id"], doc["public_id"], doc["edition_id"], source.get("clauseId", "")))
        if doc["doc_id"] not in [d["doc_id"] for d in cited]:
            cited.append(doc)
    if cited:
        answer["context"] = [{"label": TYPE_LABELS.get(d["doc_type"], "Документ"), "value": short_label(d)} for d in cited[:4]]
    return rows


def safe_text(answer: dict) -> str:
    try:
        return answer_text(answer)
    except ModelError:
        return " ".join(p.get("text", "") for row in answer.get("paragraphs", []) for p in row)[:10000]


@router.get("/dialogs")
def list_dialogs(scope: Literal["mine", "team"] = "mine", user: User = Depends(current_user), app=Depends(state)):
    if scope == "team" and not user.is_head:
        raise HTTPException(403, "Диалоги команды доступны руководителю")
    query = DIALOG_SELECT + ("" if scope == "team" else " AND d.owner_id = ?") + " ORDER BY d.updated_at DESC LIMIT 200"
    with app.db.connect() as con:
        rows = con.execute(query, () if scope == "team" else (user.id,)).fetchall()
    return [serialize(r, app.settings.utc_offset_hours) for r in rows]


@router.get("/dialogs/{dialog_id}")
def get_dialog(dialog_id: str, user: User = Depends(current_user), app=Depends(state)):
    with app.db.connect() as con:
        row = load_dialog(con, dialog_id, user)
        return serialize(row, app.settings.utc_offset_hours, messages_of(con, dialog_id))


@router.post("/ask")
def ask(body: Ask, request: Request, user: User = Depends(current_user), app=Depends(state)):
    question = body.question.strip()
    if not question:
        raise HTTPException(422, "Введите вопрос")
    if not app.limiter.allow(f"ask:{user.id}"):
        raise HTTPException(429, "Слишком много вопросов подряд. Подождите минуту")
    with _locks[hash(body.dialogId) % len(_locks)]:
        with app.db.connect() as con:
            row = con.execute("SELECT owner_id, deleted_at FROM dialogs WHERE id=?", (body.dialogId,)).fetchone()
            if row is not None and (row["owner_id"] != user.id or row["deleted_at"]):
                raise HTTPException(409, "Этот диалог недоступен. Начните новый диалог")
            history = [{"role": m["role"], "text": m["text"]} for m in messages_of(con, body.dialogId)][-HISTORY_TURNS:]
        engine = app.kb.engine
        event_date = body.eventDate.isoformat() if body.eventDate else None
        began = time.monotonic()
        try:
            answer = engine.ask(question, history, event_date, body.documentId)
        except ModelError as exc:
            with app.db.connect(write=True) as con:
                audit(con, user.id, "ask_failed", body.dialogId, {"error": str(exc)[:300]}, client_ip(request))
            raise HTTPException(503, str(exc)) from exc
        duration = int((time.monotonic() - began) * 1000)
        kind = guard.classify(question)
        guard.annotate(answer, question, kind)
        sources = enrich(answer, engine)
        stamp = now()
        with app.db.connect(write=True) as con:
            exists = con.execute("SELECT 1 FROM dialogs WHERE id=?", (body.dialogId,)).fetchone()
            if exists:
                con.execute(
                    "UPDATE dialogs SET question=?, document_id=?, event_date=?, status=?, answer=?, duration_ms=?,"
                    " feedback=NULL, feedback_at=NULL, review=NULL, reviewed_by=NULL, reviewed_at=NULL,"
                    " outdated_reason=NULL, updated_at=? WHERE id=?",
                    (question, body.documentId, event_date, answer["status"], dumps(answer), duration, stamp, body.dialogId))
            else:
                number = con.execute("SELECT COALESCE(MAX(number), 0) + 1 FROM dialogs").fetchone()[0]
                con.execute(
                    "INSERT INTO dialogs (id, owner_id, number, title, question, document_id, event_date, status, answer,"
                    " duration_ms, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                    (body.dialogId, user.id, number, make_title(question), question, body.documentId, event_date,
                     answer["status"], dumps(answer), duration, stamp, stamp))
            con.execute("INSERT INTO messages (dialog_id, role, text, event_date, created_at) VALUES (?,?,?,?,?)",
                        (body.dialogId, "user", question, event_date, stamp))
            con.execute("INSERT INTO messages (dialog_id, role, text, answer, event_date, duration_ms, created_at)"
                        " VALUES (?,?,?,?,?,?,?)",
                        (body.dialogId, "assistant", safe_text(answer), dumps(answer), event_date, duration, stamp))
            con.execute("DELETE FROM answer_sources WHERE dialog_id=?", (body.dialogId,))
            con.executemany("INSERT OR IGNORE INTO answer_sources VALUES (?,?,?,?,?,?)",
                            [(body.dialogId, *r) for r in sources])
            audit(con, user.id, "ask", body.dialogId,
                  {"status": answer["status"], "sources": len(sources), "ms": duration, "guard": kind}, client_ip(request))
    return answer


@router.patch("/dialogs/{dialog_id}")
def rename_dialog(dialog_id: str, body: DialogPatch, user: User = Depends(current_user), app=Depends(state)):
    with app.db.connect(write=True) as con:
        load_dialog(con, dialog_id, user, for_write=True)
        con.execute("UPDATE dialogs SET title=? WHERE id=?", (body.title.strip(), dialog_id))
        return serialize(load_dialog(con, dialog_id, user), app.settings.utc_offset_hours)


@router.delete("/dialogs/{dialog_id}", status_code=204)
def delete_dialog(dialog_id: str, request: Request, user: User = Depends(current_user), app=Depends(state)):
    with app.db.connect(write=True) as con:
        load_dialog(con, dialog_id, user, for_write=True)
        # Soft delete keeps the audit trail and the dialog number unique.
        con.execute("UPDATE dialogs SET deleted_at=? WHERE id=?", (now(), dialog_id))
        con.execute("DELETE FROM answer_sources WHERE dialog_id=?", (dialog_id,))
        audit(con, user.id, "dialog_deleted", dialog_id, ip=client_ip(request))
    return Response(status_code=204)


@router.post("/dialogs/{dialog_id}/feedback", status_code=204)
def feedback(dialog_id: str, body: Feedback, request: Request, user: User = Depends(current_user), app=Depends(state)):
    with app.db.connect(write=True) as con:
        row = load_dialog(con, dialog_id, user, for_write=True)
        con.execute("UPDATE dialogs SET feedback=?, feedback_at=?, review=NULL, reviewed_by=NULL, reviewed_at=NULL"
                    " WHERE id=?", (body.value, now() if body.value else None, dialog_id))
        if body.value == "disputed":
            heads = [i for i in active_users(con, "head") if i != user.id]
            notify(con, heads, "disputed", f"Спорный ответ №{row['number']}",
                   f"{short_name(user.name)} отметил(а) ответ «{row['title']}» как спорный."
                   + (f" Комментарий: {body.comment.strip()}" if body.comment else ""),
                   dialog_target(dialog_id), head_only=True, dedupe_key=f"disputed:{dialog_id}:{now()}")
        audit(con, user.id, "feedback", dialog_id, {"value": body.value, "comment": body.comment}, client_ip(request))
    return Response(status_code=204)


@router.post("/dialogs/{dialog_id}/review", status_code=204)
def review(dialog_id: str, body: Review, request: Request, user: User = Depends(head_user), app=Depends(state)):
    with app.db.connect(write=True) as con:
        row = load_dialog(con, dialog_id, user)
        con.execute("UPDATE dialogs SET review=?, reviewed_by=?, reviewed_at=? WHERE id=?",
                    (body.decision, user.id, now(), dialog_id))
        if row["owner_id"] != user.id:
            verdict = "подтвердил(а) ответ" if body.decision == "approved" else "вернул(а) ответ на доработку"
            notify(con, [row["owner_id"]], "disputed", f"Проверка ответа №{row['number']}",
                   f"{short_name(user.name)} {verdict} «{row['title']}»."
                   + (f" Комментарий: {body.comment.strip()}" if body.comment else ""),
                   dialog_target(dialog_id), dedupe_key=f"review:{dialog_id}:{now()}")
        audit(con, user.id, "review", dialog_id, {"decision": body.decision, "comment": body.comment}, client_ip(request))
    return Response(status_code=204)
