"""Competition entry point: no web server required."""
import csv
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from legal_core import Engine, ModelError, answer_text


def main():
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s %(message)s")
    logging.getLogger("legal_core").setLevel(logging.INFO)
    data = Path(os.getenv("DATA_DIR", "data"))
    source = next((data / n for n in ("knowledge-base.zip", "knowledge_base.zip", "kb.zip") if (data / n).is_file()), None)
    if source is None:
        raise FileNotFoundError("Не найден архив базы знаний в DATA_DIR")
    with (data / "questions.csv").open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not {"id", "question"}.issubset(reader.fieldnames or []):
            raise ValueError("Нужны колонки id,question")
        questions = list(reader)
    ids = [r["id"] for r in questions]
    if len(ids) != len(set(ids)) or any(not i for i in ids):
        raise ValueError("Некорректные ID")
    os.environ.setdefault("RUN_TIMEOUT_SECONDS", "1080")
    engine = Engine(source)
    def work(row):
        try:
            return row["id"], answer_text(engine.ask(row["question"]))
        except (ModelError, ValueError, KeyError, TypeError) as exc:
            print("Ошибка обработки: " + type(exc).__name__, file=sys.stderr)
            return row["id"], "Не удалось проверить ответ по базе знаний из-за технической ошибки. Требуется повторная проверка; юридический вывод не сформирован."
    try:
        with ThreadPoolExecutor(max_workers=max(1, min(8, int(os.getenv("MAX_WORKERS", "2"))))) as pool:
            with Path("submission.csv").open("w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f, quoting=csv.QUOTE_ALL)
                writer.writerow(["id", "answer"])
                for row in pool.map(work, questions):
                    writer.writerow(row)
                    f.flush()
    finally:
        engine.gateway.client.close()

if __name__ == "__main__":
    main()
