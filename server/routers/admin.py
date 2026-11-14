"""Head-only operations: audit trail and knowledge base reindexing."""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from server.deps import User, audit, client_ip, head_user, state

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/audit")
def audit_log(limit: int = Query(100, ge=1, le=1000), action: str | None = None, user: User = Depends(head_user),
              app=Depends(state)):
    query = "SELECT a.*, u.name, u.login FROM audit_log a LEFT JOIN users u ON u.id = a.user_id"
    params: tuple = ()
    if action:
        query += " WHERE a.action = ?"
        params = (action,)
    with app.db.connect() as con:
        rows = con.execute(query + " ORDER BY a.id DESC LIMIT ?", (*params, limit)).fetchall()
    return [{"id": r["id"], "action": r["action"], "objectId": r["object_id"], "user": r["login"], "userName": r["name"],
             "details": json.loads(r["details"]) if r["details"] else None, "ip": r["ip"], "createdAt": r["created_at"]}
            for r in rows]


@router.post("/reindex")
def reindex(request: Request, user: User = Depends(head_user), app=Depends(state)):
    try:
        app.kb.reload()
    except (ValueError, OSError) as exc:
        raise HTTPException(422, f"Не удалось перестроить индекс: {exc}") from exc
    changes = app.kb.sync(app.db)
    with app.db.connect(write=True) as con:
        audit(con, user.id, "reindex", details={"changes": len(changes)}, ip=client_ip(request))
    engine = app.kb.engine
    return {"documents": len(engine.docs), "chunks": len(engine.chunks), "denseSearch": engine.vectors is not None,
            "changes": changes}
