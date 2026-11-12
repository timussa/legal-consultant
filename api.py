"""Web API. A single shared workspace; roles in the prototype are not authentication."""
from contextlib import asynccontextmanager, contextmanager
from datetime import date
import json
import os
from pathlib import Path
import sqlite3
import threading

from fastapi import FastAPI, HTTPException, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from legal_core import Engine, ModelError, answer_text

BASE = Path(__file__).resolve().parent
lock = threading.Lock()
engine = None

@contextmanager
def connection():
    location = Path(os.getenv("STATE_DB", str(BASE / "data/state.sqlite")))
    location.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(location)
    con.execute("CREATE TABLE IF NOT EXISTS dialogs (id TEXT PRIMARY KEY, question TEXT, answer TEXT, history TEXT, feedback TEXT, review TEXT)")
    try:
        with con:
            yield con
    finally:
        con.close()

@asynccontextmanager
async def lifespan(app):
    global engine
    engine = Engine(os.getenv("KB_PATH", str(BASE / "data/raw")), BASE / "data/index")
    with connection() as con:
        con.execute("SELECT 1")
    yield
    engine.gateway.client.close()

app = FastAPI(title="Юрассистент", lifespan=lifespan)

@app.exception_handler(HTTPException)
async def http_error(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"error": {"code": exc.status_code, "message": str(exc.detail)}})

@app.exception_handler(RequestValidationError)
async def invalid_request(request, exc):
    return JSONResponse(status_code=422, content={"error": {"code": 422, "message": "Проверьте формат вопроса и даты"}})

class Ask(BaseModel):
    question: str = Field(min_length=1, max_length=15000)
    dialogId: str = Field(min_length=1, max_length=100)
    documentId: str | None = None
    eventDate: date | None = None

class Feedback(BaseModel):
    value: str | None = None

class Review(BaseModel):
    decision: str

@app.get("/api/health")
def health():
    return {"status": "ok", "documents": len(engine.docs), "chunks": len(engine.chunks), "denseSearch": engine.vectors is not None}

def dialog_record(row):
    id_, question, answer, history, feedback, review = row
    a = json.loads(answer)
    return {"id": id_, "number": "№" + id_, "title": question[:48], "question": question,
            "documentLabel": "База знаний", "timeLabel": "сохранён", "status": a["status"], "answer": a,
            "feedback": feedback, "review": review}

@app.get("/api/v1/dialogs")
def dialogs():
    with connection() as con:
        return [dialog_record(r) for r in con.execute("SELECT * FROM dialogs ORDER BY rowid DESC")]

@app.post("/api/v1/ask")
def ask(body: Ask):
    if not body.question.strip():
        raise HTTPException(422, "Введите вопрос")
    # Serialize turns so parallel requests cannot overwrite conversation history.
    with lock:
        with connection() as con:
            row = con.execute("SELECT history FROM dialogs WHERE id=?", (body.dialogId,)).fetchone()
        history = json.loads(row[0]) if row else []
        try:
            answer = engine.ask(body.question, history, body.eventDate.isoformat() if body.eventDate else None, body.documentId)
        except ModelError as exc:
            raise HTTPException(503, str(exc)) from exc
        history = (history + [{"role": "user", "text": body.question}, {"role": "assistant", "text": answer_text(answer)}])[-12:]
        with connection() as con:
            con.execute("INSERT INTO dialogs VALUES (?,?,?,?,NULL,NULL) ON CONFLICT(id) DO UPDATE SET question=excluded.question, answer=excluded.answer, history=excluded.history",
                        (body.dialogId, body.question, json.dumps(answer, ensure_ascii=False), json.dumps(history, ensure_ascii=False)))
        return answer

@app.post("/api/v1/dialogs/{dialog_id}/feedback", status_code=204)
def feedback(dialog_id: str, body: Feedback):
    if body.value not in (None, "correct", "wrong", "disputed"):
        raise HTTPException(422, "Неизвестная оценка")
    with connection() as con:
        if not con.execute("UPDATE dialogs SET feedback=? WHERE id=?", (body.value, dialog_id)).rowcount:
            raise HTTPException(404, "Диалог не найден")
    return Response(status_code=204)

@app.post("/api/v1/dialogs/{dialog_id}/review", status_code=204)
def review(dialog_id: str, body: Review):
    if body.decision not in ("approved", "needs-fix"):
        raise HTTPException(422, "Неизвестное решение")
    with connection() as con:
        if not con.execute("UPDATE dialogs SET review=? WHERE id=?", (body.decision, dialog_id)).rowcount:
            raise HTTPException(404, "Диалог не найден")
    return Response(status_code=204)

@app.get("/api/v1/documents/{document_id}")
def document(document_id: str):
    docs = sorted([d for d in engine.docs if d["public_id"] == document_id], key=lambda d: d["effective_from"] or "")
    if not docs:
        raise HTTPException(404, "Документ не найден")
    clauses = {}
    for d in docs:
        for c in engine.chunks:
            if c["doc_id"] != d["doc_id"]:
                continue
            # Chunk ids preserve exact reference targets even when an anchor repeats.
            key = c["anchor"] or c["chunk_id"]
            clauses.setdefault(key, {}) .setdefault(d["edition_id"], []) .append(c)
    rendered = []
    for key, versions in clauses.items():
        values = {}
        for edition, chunks in versions.items():
            d = next(d for d in docs if d["edition_id"] == edition)
            values[edition] = d["text"][min(c["start"] for c in chunks):max(c["end"] for c in chunks)]
        rendered.append({"id": key, "versions": values})
    return {"id": document_id, "title": docs[-1]["title"], "kindLabel": docs[-1]["doc_number"], "image": "laws" if docs[-1]["doc_type"] == "law" else "contracts",
        "editions": [{"id": d["edition_id"], "label": d["edition_id"], "date": d["effective_from"] or d["doc_date"] or "", "note": "Текст исходного документа"} for d in docs],
        "outline": [{"id": "body", "title": "Положения документа"}], "sections": [{"id": "body", "title": "Положения документа", "clauses": rendered}],
        "citations": [], "comments": [], "files": [d["source_file"] for d in docs]}

@app.get("/api/v1/search")
def search(q: str = ""):
    if len(q.strip()) < 2:
        return []
    return [{"type": "clause", "documentId": engine.by_id[c["doc_id"]]["public_id"],
             "clauseId": c["anchor"] or c["chunk_id"], "editionId": engine.by_id[c["doc_id"]]["edition_id"],
             "title": engine.by_id[c["doc_id"]]["title"], "snippet": c["text"][:180]} for c in engine.search(q[:2000], limit=8)]

@app.get("/api/v1/knowledge-base")
def overview():
    groups = [("contracts", "Договоры и допсоглашения", "contracts", lambda d: d["doc_type"] in ("contract", "addendum")),
              ("internal", "Внутренние документы", "internal", lambda d: d["doc_type"] in ("regulation", "memo")),
              ("laws", "Законы", "laws", lambda d: d["doc_type"] == "law")]
    sections = []
    for key, title, image, predicate in groups:
        matching = [d for d in engine.docs if predicate(d)]
        sections.append({"id": key, "title": title, "subtitle": "Документы базы знаний", "documentCount": len(matching), "updatedLabel": "Загружено из базы", "image": image, "initials": title[:2], "documentId": matching[0]["public_id"] if matching else None})
    recent = []
    for d in dialogs():
        recent.append({"id": d["id"], "dialogId": d["id"], "number": d["number"], "question": d["question"], "preview": answer_text(d["answer"])[:180], "documentLabel": d["documentLabel"], "sourceCount": len(d["answer"]["sources"]), "isVerified": bool(d["answer"]["sources"]), "status": d["status"], "dateLabel": "сохранён"})
    return {"stats": {"documentCount": len(engine.docs), "citedShare": "—", "averageAnswerTime": "—", "metricsNote": "Качество требует отдельного оценочного прогона"},
            "sections": sections, "myAnswers": recent[:10], "teamAnswers": [], "updates": [], "affected": {"summary": "Нет данных об изменениях базы", "answers": []}, "teamStats": [],
            "examples": ["Какая арендная плата по договору с Северным Складом?", "Кто инициирует согласование договора?"]}

@app.get("/api/v1/notifications")
def notifications():
    return []

@app.post("/api/v1/notifications/read", status_code=204)
def notifications_read():
    return Response(status_code=204)
