"""Home page data: knowledge base sections, recent answers, changes and team metrics from real records."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends

from server.deps import User, current_user, state
from server.kb import SECTIONS, TYPE_LABELS, document_date
from server.labels import date_label, iso_to_ru, percent, seconds_label, short_name
from server.routers.dialogs import DIALOG_SELECT, document_label, effective_status, safe_text

router = APIRouter(prefix="/api/v1", tags=["overview"])

EXAMPLES = [
    "С кем нужно согласовать договор поставки П-17/2024?",
    "Какая арендная плата по договору с Северным Складом?",
    "Какая ставка НДС применяется к поставке по договору П-17/2024?",
    "Сколько хранятся оригиналы договоров в архиве?",
]


def recent(row, offset: int) -> dict:
    answer = json.loads(row["answer"])
    return {"id": f"dialog-{row['id']}", "dialogId": row["id"], "number": f"№{row['number']}",
            "question": row["question"], "preview": safe_text(answer)[:180], "documentLabel": document_label(answer),
            "author": short_name(row["owner_name"]), "sourceCount": len(answer.get("sources", [])),
            "isVerified": bool(answer.get("sources")) and row["status"] in ("confirmed", "correction"),
            "status": effective_status(row), "dateLabel": date_label(row["updated_at"], offset),
            "isOutdated": bool(row["outdated_reason"])}


def since(days: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).replace(microsecond=0).isoformat()


@router.get("/knowledge-base")
def overview(user: User = Depends(current_user), app=Depends(state)):
    engine = app.kb.engine
    offset = app.settings.utc_offset_hours
    with app.db.connect() as con:
        mine = con.execute(DIALOG_SELECT + " AND d.owner_id=? ORDER BY d.updated_at DESC LIMIT 10", (user.id,)).fetchall()
        team = con.execute(DIALOG_SELECT + " ORDER BY d.updated_at DESC LIMIT 10").fetchall()
        disputed = con.execute(DIALOG_SELECT + " AND d.feedback='disputed' AND d.review IS NULL"
                               " ORDER BY d.updated_at DESC LIMIT 20").fetchall()
        month = con.execute("SELECT status, answer, duration_ms FROM dialogs WHERE deleted_at IS NULL AND updated_at >= ?",
                            (since(30),)).fetchall()
        affected = con.execute(DIALOG_SELECT + " AND d.outdated_reason IS NOT NULL"
                               + ("" if user.is_head else " AND d.owner_id = ?") + " ORDER BY d.updated_at DESC LIMIT 10",
                               () if user.is_head else (user.id,)).fetchall()
        changed = {r["doc_id"]: r["changed_at"] for r in con.execute("SELECT doc_id, changed_at FROM kb_documents")}
        team_stats = _team_stats(con) if user.is_head else []

    grounded = [r for r in month if r["status"] in ("confirmed", "correction")]
    cited = [r for r in grounded if json.loads(r["answer"]).get("sources")]
    durations = [r["duration_ms"] for r in month if r["duration_ms"]]

    sections = []
    for key, title, subtitle, image, predicate in SECTIONS:
        matching = [d for d in engine.docs if predicate(d)]
        if not matching:
            continue
        dates = sorted(filter(None, (document_date(d) for d in matching)))
        laws = all(d["doc_type"] == "law" for d in matching)
        sections.append({"id": key, "title": title, "subtitle": subtitle,
                         "documentCount": len({d["public_id"] for d in matching}),
                         "updatedLabel": "действующая редакция" if laws else (f"обновлено {iso_to_ru(dates[-1])}" if dates else "загружено"),
                         "image": image, "initials": "".join(w[0] for w in title.split()[:2]).upper(),
                         "documentId": matching[0]["public_id"]})

    # Recent dated company documents: new regulation editions, letters, addenda.
    fresh_cutoff = since(14)
    dated = sorted([d for d in engine.docs if d["doc_type"] != "law" and document_date(d)],
                   key=document_date, reverse=True)[:5]
    updates = [{"id": d["doc_id"], "title": d["title"] if d["doc_type"] != "regulation" else f"{d['title']}, ред. {d['effective_from'][:4]}",
                "text": f"{TYPE_LABELS.get(d['doc_type'], 'Документ')}"
                        + (f" № {d['doc_number']}" if d.get("doc_number") else "")
                        + (f" · действует с {iso_to_ru(d['effective_from'])}" if d.get("effective_from") else ""),
                "meta": iso_to_ru(document_date(d)), "isNew": bool(changed.get(d["doc_id"]) and changed[d["doc_id"]] >= fresh_cutoff),
                "documentId": d["public_id"], "editionId": d["edition_id"]} for d in dated]

    affected_answers = [{"dialogId": r["id"], "number": f"№{r['number']}", "title": r["title"], "reason": r["outdated_reason"]}
                        for r in affected]
    team_answers = [recent(r, offset) for r in team]
    # Disputed answers wait for the head even if they dropped out of the recent list.
    if user.is_head:
        listed = {a["dialogId"] for a in team_answers}
        team_answers += [recent(r, offset) for r in disputed if r["id"] not in listed]
    return {
        "stats": {"documentCount": len(engine.docs), "citedShare": percent(len(cited), len(grounded)),
                  "averageAnswerTime": seconds_label(sum(durations) / len(durations) if durations else None),
                  "metricsNote": f"По {len(month)} ответам команды за 30 дней" if month else "Ответов за 30 дней пока нет"},
        "sections": sections,
        "myAnswers": [recent(r, offset) for r in mine],
        "teamAnswers": team_answers,
        "updates": updates,
        "affected": {"summary": (f"{len(affected_answers)} ответ(ов) ссылаются на изменённые документы"
                                 if affected_answers else "Изменения базы не затронули ваши ответы"),
                     "answers": affected_answers},
        "teamStats": team_stats,
        "examples": EXAMPLES,
    }


def _team_stats(con) -> list[dict]:
    week = since(7)
    rows = con.execute("SELECT status, feedback, review, owner_id, duration_ms FROM dialogs"
                       " WHERE deleted_at IS NULL AND updated_at >= ?", (week,)).fetchall()
    waiting = con.execute("SELECT COUNT(*) FROM dialogs WHERE deleted_at IS NULL AND feedback='disputed' AND review IS NULL").fetchone()[0]
    refusals = sum(r["status"] == "refusal" for r in rows)
    wrong = sum(r["feedback"] in ("wrong", "disputed") for r in rows)
    durations = [r["duration_ms"] for r in rows if r["duration_ms"]]
    return [
        {"id": "questions", "label": "Вопросов за 7 дней", "value": str(len(rows))},
        {"id": "lawyers", "label": "Активных юристов", "value": str(len({r["owner_id"] for r in rows}))},
        {"id": "disputed", "label": "Спорных на проверке", "value": str(waiting), "isAlert": waiting > 0},
        {"id": "refusals", "label": "Доля отказов", "value": percent(refusals, len(rows))},
        {"id": "wrong", "label": "Отмечены как неверные", "value": percent(wrong, len(rows)), "isAlert": wrong > 0},
        {"id": "time", "label": "Среднее время ответа",
         "value": seconds_label(sum(durations) / len(durations) if durations else None)},
    ]
