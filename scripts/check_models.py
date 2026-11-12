"""Small paid API probes without printing keys or provider response bodies."""
from pathlib import Path
import sys

from dotenv import load_dotenv

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from legal_core import Gateway, ModelError, env


def main():
    load_dotenv(BASE / ".env", override=False)
    gateway = Gateway()
    failed = False
    try:
        try:
            result = gateway.chat('Return JSON {"ok":true}.', {"test": "connection"})
            if not isinstance(result, dict) or result.get("ok") is not True:
                raise ModelError("Unexpected JSON response")
            print("Generation: OK")
        except ModelError as exc:
            failed = True
            print("Generation:", exc)

        if env("ENABLE_EMBEDDINGS", "true").lower() == "true":
            try:
                vectors = gateway.embed(["Проверка доступа к модели эмбеддингов"])
                print("Embeddings: OK, dimensions", vectors.shape[1])
            except (ModelError, KeyError, ValueError, TypeError) as exc:
                failed = True
                print("Embeddings:", type(exc).__name__, str(exc) if isinstance(exc, ModelError) else "Invalid response")
        else:
            print("Embeddings: disabled, BM25 enabled")

        if gateway.rerank_model:
            try:
                response = gateway.post("/rerank", {
                    "model": gateway.rerank_model, "query": "срок оплаты",
                    "documents": ["Срок оплаты 30 дней.", "Адрес склада."], "top_n": 1,
                })
                results = response.get("results", response.get("data", []))
                if not results or results[0].get("index") not in (0, 1):
                    raise ModelError("Invalid reranker response")
                print("Reranker: OK")
            except (ModelError, KeyError, ValueError, TypeError) as exc:
                failed = True
                print("Reranker:", type(exc).__name__, str(exc) if isinstance(exc, ModelError) else "Invalid response")
        else:
            print("Reranker: disabled")
    finally:
        gateway.client.close()
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
