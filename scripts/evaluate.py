"""Run public demo questions against real API; do not feed golden answers to model."""
import csv
import argparse
import json
import os
from pathlib import Path
import sys
import time

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from dotenv import load_dotenv
from legal_core import Engine, ModelError, answer_text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ids", help="Comma-separated demo IDs for a targeted run")
    parser.add_argument("--output-dir", type=Path, default=BASE / "output")
    arguments = parser.parse_args()
    selected_ids = set(arguments.ids.split(",")) if arguments.ids else None
    load_dotenv(BASE / ".env", override=False)
    source = Path(os.getenv("DEMO_QUESTIONS", str(BASE.parent / "demo_questions.csv")))
    output = arguments.output_dir
    output.mkdir(parents=True, exist_ok=True)
    began = time.monotonic()
    engine = Engine(BASE / "data/raw", BASE / "data/index")
    report = []
    try:
        with source.open(encoding="utf-8-sig",newline="") as f, (output/"demo_answers.csv").open("w",encoding="utf-8",newline="") as out:
            writer = csv.writer(out)
            writer.writerow(["id","answer"])
            for row in csv.DictReader(f):
                if selected_ids is not None and row["id"] not in selected_ids:
                    continue
                started = time.monotonic()
                try:
                    answer = engine.ask(row["question"])
                    writer.writerow([row["id"],answer_text(answer)])
                    report.append({"id":row["id"],"status":answer["status"],"sourceCount":len(answer["sources"]),"seconds":round(time.monotonic()-started,2), "answer": answer})
                except ModelError as exc:
                    writer.writerow([row["id"],"Техническая ошибка проверки ответа"])
                    report.append({"id":row["id"],"error":str(exc)})
                out.flush()
                (output/"evaluation.json").write_text(json.dumps({"totalSeconds":round(time.monotonic()-began,2),"results":report},ensure_ascii=False,indent=2),encoding="utf-8")
                print(row["id"], report[-1].get("status", "error"), flush=True)
    finally:
        engine.gateway.client.close()
        (output/"evaluation.json").write_text(json.dumps({"totalSeconds":round(time.monotonic()-began,2),"results":report},ensure_ascii=False,indent=2),encoding="utf-8")

if __name__ == "__main__":
    main()
