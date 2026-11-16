"""Run public demo questions against a real model; golden answers are never fed to the model.

Modes reproduce what each submission writes to submission.csv:
  --mode v4      engine.ask(fallback=True) + answer_text  (best platform score so far)
  --mode simple  engine.ask_simple                        (v10: our retrieval + one prose answer)
  --mode web     engine.ask (strict, as the web API)      + answer_text

If the golden file is found (DEMO_GOLDEN, default ../demo_output.csv or ../demo/demo_output.csv),
output/compare-<mode>.md puts every answer next to the golden one for manual review.
"""
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


def first_existing(*paths):
    return next((p for p in paths if p and p.is_file()), None)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ids", help="Comma-separated demo IDs for a targeted run")
    parser.add_argument("--mode", choices=["v4", "simple", "web"], default="web")
    parser.add_argument("--output-dir", type=Path, default=BASE / "output")
    arguments = parser.parse_args()
    selected_ids = set(arguments.ids.split(",")) if arguments.ids else None
    load_dotenv(BASE / ".env", override=False)
    env_questions = os.getenv("DEMO_QUESTIONS")
    source = first_existing(Path(env_questions) if env_questions else None,
                            BASE.parent / "demo_questions.csv", BASE.parent / "demo" / "demo_questions.csv")
    if source is None:
        sys.exit("Не найден demo_questions.csv: положите его рядом с проектом или задайте DEMO_QUESTIONS")
    env_golden = os.getenv("DEMO_GOLDEN")
    golden_path = first_existing(Path(env_golden) if env_golden else None,
                                 BASE.parent / "demo_output.csv", BASE.parent / "demo" / "demo_output.csv")
    golden = {}
    if golden_path:
        with golden_path.open(encoding="utf-8-sig", newline="") as f:
            golden = {r["id"]: r["answer"] for r in csv.DictReader(f)}
    output = arguments.output_dir
    output.mkdir(parents=True, exist_ok=True)
    began = time.monotonic()
    engine = Engine(BASE / "data/raw", BASE / "data/index")
    report, compare = [], []
    suffix = "" if arguments.mode == "web" else "-" + arguments.mode

    def write_report():
        (output / f"evaluation{suffix}.json").write_text(json.dumps(
            {"mode": arguments.mode, "totalSeconds": round(time.monotonic() - began, 2), "results": report},
            ensure_ascii=False, indent=2), encoding="utf-8")
        if golden:
            (output / f"compare{suffix or '-web'}.md").write_text("\n".join(compare), encoding="utf-8")

    try:
        with source.open(encoding="utf-8-sig", newline="") as f, \
                (output / f"demo_answers{suffix}.csv").open("w", encoding="utf-8", newline="") as out:
            writer = csv.writer(out)
            writer.writerow(["id", "answer"])
            for row in csv.DictReader(f):
                if selected_ids is not None and row["id"] not in selected_ids:
                    continue
                started = time.monotonic()
                try:
                    if arguments.mode == "simple":
                        text = engine.ask_simple(row["question"])
                        entry = {"id": row["id"], "status": "prose"}
                    else:
                        answer = engine.ask(row["question"], fallback=arguments.mode == "v4")
                        text = answer_text(answer)
                        entry = {"id": row["id"], "status": answer["status"], "sourceCount": len(answer["sources"]), "answer": answer}
                except ModelError as exc:
                    text = "Техническая ошибка проверки ответа"
                    entry = {"id": row["id"], "error": str(exc)}
                entry["seconds"] = round(time.monotonic() - started, 2)
                writer.writerow([row["id"], text])
                report.append(entry)
                if golden:
                    compare += [f"## {row['id']}. {row['question']}", "",
                                f"**Наш ответ ({arguments.mode}):** {text}", "",
                                f"**Эталон:** {golden.get(row['id'], '—')}", "", "---", ""]
                out.flush()
                write_report()
                print(row["id"], entry.get("status", "error"), entry["seconds"], "s", flush=True)
    finally:
        engine.gateway.client.close()
        write_report()


if __name__ == "__main__":
    main()
