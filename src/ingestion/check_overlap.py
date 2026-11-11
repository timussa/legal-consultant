import json
import re
from src.config import CHUNKS_FILE

SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[А-ЯЁA-Z«(])")


def last_sentence(text: str) -> str:
    sentences = [s.strip() for s in SENTENCE_SPLIT_RE.split(text) if s.strip()]
    return sentences[-1] if sentences else ""


def check_overlap():
    chunks = []
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line))

    print(f"Всего чанков: {len(chunks)}\n")

    # 1. Пары с ОДИНАКОВЫМ anchor (один пункт разрезан) — overlap ОБЯЗАТЕЛЕН.
    same_anchor_pairs = 0
    same_anchor_ok = 0
    same_anchor_fail = []
    # 2. Пары с РАЗНЫМ anchor (разные пункты) — overlap НЕ нужен.
    diff_anchor_pairs = 0

    for i in range(len(chunks) - 1):
        a, b = chunks[i], chunks[i + 1]
        if a["doc_id"] != b["doc_id"]:
            continue
        if a["anchor"] == b["anchor"]:
            same_anchor_pairs += 1
            tail = last_sentence(a["text"])
            probe = tail[:40]
            if probe and probe in b["text"][:300]:
                same_anchor_ok += 1
            else:
                same_anchor_fail.append((a["chunk_id"], b["chunk_id"], tail, b["text"][:120]))
        else:
            diff_anchor_pairs += 1

    print(f"Пар с ОДИНАКОВЫМ anchor (разрезан один пункт): {same_anchor_pairs}")
    print(f"  Overlap OK: {same_anchor_ok} ({100*same_anchor_ok/max(same_anchor_pairs,1):.1f}%)")
    print(f"  Overlap НЕТ: {len(same_anchor_fail)}")
    if same_anchor_fail:
        print("\n  Примеры провалов:")
        for a_id, b_id, tail, head in same_anchor_fail[:5]:
            print(f"    {a_id} → {b_id}")
            print(f"      tail: {tail[:80]!r}")
            print(f"      head: {head[:80]!r}")

    print(f"\nПар с РАЗНЫМ anchor (разные пункты): {diff_anchor_pairs}")
    print("  (overlap тут не нужен — пункты семантически независимы)")

    # 3. Отдельно — НК-гиганты.
    print("\n" + "=" * 60)
    for doc_id in ["НК_ст284", "НК_ст164", "КоАП_ст13.11"]:
        sub = [c for c in chunks if c["doc_id"] == doc_id]
        if not sub:
            continue
        print(f"\n{doc_id}: {len(sub)} чанков")
        ok, fail = 0, 0
        for i in range(len(sub) - 1):
            a, b = sub[i], sub[i + 1]
            if a["anchor"] != b["anchor"]:
                continue
            tail = last_sentence(a["text"])
            probe = tail[:40]
            if probe and probe in b["text"][:300]:
                ok += 1
            else:
                fail += 1
                if fail <= 3:
                    print(f"  {a['chunk_id']} → {b['chunk_id']}")
                    print(f"    tail: {tail[:80]!r}")
                    print(f"    head: {b['text'][:80]!r}")
        print(f"  Same-anchor пар: OK={ok}, FAIL={fail}")


if __name__ == "__main__":
    check_overlap()