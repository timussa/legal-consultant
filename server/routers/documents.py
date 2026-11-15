"""Document viewer with editions, citations from answers and clause comments; search; uploads."""
from __future__ import annotations

import re
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field

from server.db import now
from server.deps import User, audit, client_ip, current_user, head_user, state
from server.kb import TYPE_LABELS, document_date
from server.labels import date_label, initials, iso_to_ru, short_name

router = APIRouter(prefix="/api/v1", tags=["documents"])

SAFE_NAME = re.compile(r"^[\w .,()№«»\-]{3,150}$")


class NewComment(BaseModel):
    clauseId: str = Field(min_length=1, max_length=200)
    text: str = Field(min_length=1, max_length=2000)


class Upload(BaseModel):
    fileName: str = Field(min_length=3, max_length=150)
    kind: Literal["company", "law"] = "company"
    text: str = Field(min_length=20, max_length=500_000)


def render_clauses(engine, docs: list[dict]) -> list[dict]:
    clauses: dict[str, dict] = {}
    for d in docs:
        for c in engine.chunks:
            if c["doc_id"] != d["doc_id"]:
                continue
            # Chunk ids preserve exact reference targets even when an anchor repeats.
            key = c["anchor"] or c["chunk_id"]
            clauses.setdefault(key, {}).setdefault(d["edition_id"], []).append(c)
    rendered = []
    for key, versions in clauses.items():
        values = {}
        for edition, chunks in versions.items():
            d = next(d for d in docs if d["edition_id"] == edition)
            values[edition] = d["text"][min(c["start"] for c in chunks):max(c["end"] for c in chunks)]
        rendered.append({"id": key, "versions": values})
    return rendered


def edition_record(d: dict) -> dict:
    if d["doc_type"] == "regulation" and d.get("effective_from"):
        until = f" по {iso_to_ru(d['effective_to'])}" if d.get("effective_to") else " · действует"
        label, note = f"ред. {d['effective_from'][:4]}", f"Действует с {iso_to_ru(d['effective_from'])}{until}"
    elif d["doc_type"] == "law":
        label = "действующая редакция"
        note = f"Выгрузка от {iso_to_ru(d['snapshot_date'])}" if d.get("snapshot_date") else "Текст исходного документа"
    else:
        label, note = "исходный текст", (f"Документ от {iso_to_ru(d['doc_date'])}" if d.get("doc_date") else "Текст исходного документа")
    return {"id": d["edition_id"], "label": label, "date": document_date(d) or "", "note": note}


@router.get("/documents")
def list_documents(user: User = Depends(current_user), app=Depends(state)):
    return app.kb.catalogue()


@router.get("/documents/{document_id}")
def get_document(document_id: str, user: User = Depends(current_user), app=Depends(state)):
    engine = app.kb.engine
    docs = app.kb.editions(document_id)
    if not docs:
        raise HTTPException(404, "Документ не найден")
    latest = docs[-1]
    offset = app.settings.utc_offset_hours
    visible = "" if user.is_head else " AND d.owner_id = ?"
    params = (document_id,) if user.is_head else (document_id, user.id)
    with app.db.connect() as con:
        citations = [{"clauseId": r["clause_id"], "dialogId": r["dialog_id"], "dialogNumber": f"№{r['number']}",
                      "dialogTitle": r["title"], "cite": r["cite"], "editionId": r["edition_id"]}
                     for r in con.execute(
                         "SELECT s.*, d.number, d.title FROM answer_sources s JOIN dialogs d ON d.id = s.dialog_id"
                         " WHERE s.document_id = ? AND d.deleted_at IS NULL" + visible + " ORDER BY d.number DESC", params)]
        comments = [{"id": str(r["id"]), "author": short_name(r["name"]), "initials": initials(r["name"]),
                     "clauseId": r["clause_id"], "dateLabel": date_label(r["created_at"], offset), "text": r["text"],
                     "isOwn": r["user_id"] == user.id}
                    for r in con.execute(
                        "SELECT c.*, u.name FROM comments c JOIN users u ON u.id = c.user_id"
                        " WHERE c.document_id = ? AND c.deleted_at IS NULL ORDER BY c.id", (document_id,))]
    image = "laws" if latest["doc_type"] == "law" else ("internal" if latest["doc_type"] in ("regulation", "memo") else "contracts")
    return {"id": document_id, "title": latest["title"], "kindLabel": latest["doc_number"] or TYPE_LABELS.get(latest["doc_type"], ""),
            "type": latest["doc_type"], "image": image, "editions": [edition_record(d) for d in docs],
            "outline": [{"id": "body", "title": "Положения документа"}],
            "sections": [{"id": "body", "title": "Положения документа", "clauses": render_clauses(engine, docs)}],
            "citations": citations, "comments": comments, "files": [d["source_file"] for d in docs]}


@router.post("/documents/{document_id}/comments", status_code=201)
def add_comment(document_id: str, body: NewComment, request: Request, user: User = Depends(current_user), app=Depends(state)):
    docs = app.kb.editions(document_id)
    if not docs:
        raise HTTPException(404, "Документ не найден")
    if body.clauseId not in {c["id"] for c in render_clauses(app.kb.engine, docs)}:
        raise HTTPException(422, "Пункт не найден в документе")
    with app.db.connect(write=True) as con:
        cursor = con.execute("INSERT INTO comments (document_id, clause_id, user_id, text, created_at) VALUES (?,?,?,?,?)",
                             (document_id, body.clauseId, user.id, body.text.strip(), now()))
        audit(con, user.id, "comment_added", f"{document_id}#{body.clauseId}", ip=client_ip(request))
        comment_id = cursor.lastrowid
    return {"id": str(comment_id), "author": short_name(user.name), "initials": initials(user.name),
            "clauseId": body.clauseId, "dateLabel": "сегодня", "text": body.text.strip(), "isOwn": True}


@router.delete("/documents/{document_id}/comments/{comment_id}", status_code=204)
def delete_comment(document_id: str, comment_id: int, request: Request, user: User = Depends(current_user), app=Depends(state)):
    with app.db.connect(write=True) as con:
        row = con.execute("SELECT user_id FROM comments WHERE id=? AND document_id=? AND deleted_at IS NULL",
                          (comment_id, document_id)).fetchone()
        if row is None:
            raise HTTPException(404, "Комментарий не найден")
        if row["user_id"] != user.id and not user.is_head:
            raise HTTPException(403, "Удалить можно только свой комментарий")
        con.execute("UPDATE comments SET deleted_at=? WHERE id=?", (now(), comment_id))
        audit(con, user.id, "comment_deleted", str(comment_id), ip=client_ip(request))
    return Response(status_code=204)


@router.get("/search")
def search(q: str = "", user: User = Depends(current_user), app=Depends(state)):
    if len(q.strip()) < 2:
        return []
    engine = app.kb.engine
    return [{"type": "clause", "documentId": engine.by_id[c["doc_id"]]["public_id"],
             "clauseId": c["anchor"] or c["chunk_id"], "editionId": engine.by_id[c["doc_id"]]["edition_id"],
             "title": engine.by_id[c["doc_id"]]["title"], "snippet": c["text"][:180]}
            for c in engine.search(q[:2000], limit=8)]


@router.post("/documents", status_code=201)
def upload_document(body: Upload, request: Request, user: User = Depends(head_user), app=Depends(state)):
    """Adds a .txt document to the knowledge base directory and rebuilds the index."""
    folder = app.settings.kb_path
    if not app.settings.allow_uploads or not folder.is_dir():
        raise HTTPException(403, "Загрузка документов отключена для этой базы знаний")
    name = body.fileName.strip()
    if name.lower().endswith(".txt"):
        name = name[:-4]
    if not SAFE_NAME.match(name) or ".." in name:
        raise HTTPException(422, "Недопустимое имя файла")
    prefix = "законы__" if body.kind == "law" else "документы компании__"
    target = folder / f"{prefix}{name}.txt"
    if target.exists():
        raise HTTPException(409, "Документ с таким именем уже есть в базе")
    target.write_text(body.text.replace("\r\n", "\n"), encoding="utf-8")
    try:
        app.kb.reload()
    except (ValueError, OSError) as exc:
        target.unlink(missing_ok=True)
        app.kb.reload()
        raise HTTPException(422, f"Документ не принят: {exc}") from exc
    changes = app.kb.sync(app.db)
    with app.db.connect(write=True) as con:
        audit(con, user.id, "document_uploaded", target.name, {"changes": len(changes)}, client_ip(request))
    return {"fileName": target.name, "changes": changes, "documents": len(app.kb.engine.docs)}
