import os
os.environ["ENABLE_EMBEDDINGS"] = "false"
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from legal_core import Engine, Gateway, ModelError, event_date_from_text, read_corpus, answer_text, parse_model_json
import numpy as np
import httpx
from src.ingestion.parse import split_into_chunks, extract_metadata

BASE = Path(__file__).resolve().parents[1]

class FakeGateway:
    emb_model = "test"
    rerank_model = ""
    def chat(self, system, data):
        if "supported" in system:
            return {"supported": True}
        c = next(e for e in data["evidence"] if "450 000" in e["text"])
        return {"status": "confirmed", "paragraphs": [{"text": "Арендная плата — 450 000 рублей в месяц.",
                    "references": [{"id": c["id"], "quote": c["text"].strip()}]}]}

class CoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.engine = Engine(BASE / "data/raw", cls.temp.name, FakeGateway())
    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_corpus_unique_and_lossless(self):
        e = self.engine
        self.assertEqual(len(e.docs), 21)
        for d in e.docs:
            covered = bytearray(len(d["text"]))
            for c in e.chunks:
                if c["doc_id"] == d["doc_id"]:
                    self.assertEqual(c["text"], d["text"][c["start"]:c["end"]])
                    self.assertLessEqual(len(c["text"]), 1200)
                    covered[c["start"]:c["end"]] = b"1" * (c["end"]-c["start"])
            self.assertTrue(all(covered), d["doc_id"])

    def test_oversized_no_loss(self):
        text = "1.1. " + "абв " * 3000 + "КОНЕЦ"
        chunks = split_into_chunks(text, {"doc_id": "x", "doc_type": "contract"})
        self.assertIn("КОНЕЦ", chunks[-1]["text"])
        self.assertTrue(all(len(c["text"]) <= 1200 for c in chunks))

    def test_regulation_date(self):
        e = self.engine
        for day, expected in [("2024-08-01", "reg_20230110"), ("2025-03-01", "reg_20250301")]:
            hits = e.search("согласование договоров генерального директора", day, 40)
            regs = {c["doc_id"] for c in hits if e.by_id[c["doc_id"]]["doc_type"] == "regulation"}
            self.assertEqual(regs, {expected})

    def test_counterparty_routing_keeps_full_contract(self):
        engine = self.engine
        matches = engine.contract_matches("По договору с Северным Складом нас должны пропускать ночью?")
        self.assertEqual(matches, {"А-08_2024"})
        hits = engine.search("По договору с Северным Складом нас должны пропускать ночью?")
        self.assertTrue(any(c["doc_id"] == "А-08_2024" and c["anchor"] == "4.3" for c in hits))
        matches = engine.contract_matches("Пользователь: Альфа-Трейд или Альфа-Трейдинг? Пользователь: Альфа-Трейдинг, покупали компьютеры")
        self.assertEqual(matches, {"ПТ-05_2023"})

    def test_amendment_link(self):
        e = self.engine
        ds = next(d for d in e.docs if d["doc_type"] == "addendum")
        self.assertIn(ds["parent_doc_id"], e.by_id)
        self.assertEqual(ds["doc_date"], "2024-09-03")
        rent = next(d for d in e.docs if "А-08" in d["doc_number"])
        self.assertEqual(rent["doc_date"], "2024-08-01")

    def test_injection_removed_from_context(self):
        e = self.engine
        memo = next(d for d in e.docs if "ЮО-7" in d["doc_id"])
        self.assertIn("90 календарных дней", memo["text"])
        self.assertNotIn("90 календарных дней", e.safe_text(memo["text"]))
        self.assertIn("3 (трёх)", e.safe_text(memo["text"]))

    def test_event_date_from_question(self):
        self.assertEqual(event_date_from_text("Договор в августе 2024 года"), "2024-08-01")
        self.assertEqual(event_date_from_text("дата 05.03.2025"), "2025-03-05")
        self.assertIsNone(event_date_from_text("31.02.2025"))

    def test_incomplete_json_delimiter_from_local_runner(self):
        self.assertEqual(parse_model_json('{"ok":true'), {"ok": True})
        with self.assertRaises(ValueError):
            parse_model_json('{"text":"unfinished')
        with self.assertRaises(ValueError):
            parse_model_json('{"value":')

    def test_embedding_cache_and_invalidation(self):
        class DenseGateway(FakeGateway):
            def __init__(self):
                self.calls = 0
            def embed(self, texts):
                self.calls += 1
                return np.tile(np.array([[1., 0.]], dtype=np.float32), (len(texts), 1))
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"ENABLE_EMBEDDINGS":"true"}):
            g = DenseGateway()
            first = Engine(BASE / "data/raw", tmp, g)
            self.assertIsNotNone(first.vectors)
            self.assertGreater(g.calls, 0)
            calls = g.calls
            second = Engine(BASE / "data/raw", tmp, g)
            self.assertEqual(g.calls, calls)
            self.assertTrue(second.search("поставка"))
            g.emb_model = "different-model"
            Engine(BASE / "data/raw", tmp, g)
            self.assertGreater(g.calls, calls + 1)

    def test_gateway_embedding_order(self):
        g = Gateway()
        try:
            response = {"data":[{"index":1,"embedding":[0,2]},{"index":0,"embedding":[3,0]}]}
            with patch.object(g,"post",return_value=response):
                vectors=g.embed(["a","b"])
                np.testing.assert_allclose(vectors, [[1,0],[0,1]])
            response["data"][0]["index"]=0
            with patch.object(g,"post",return_value=response), self.assertRaises(ModelError):
                g.embed(["a","b"])
        finally:
            g.client.close()

    def test_precomputed_index_loaded_from_package_root(self):
        class DenseGateway(FakeGateway):
            def embed(self, texts):
                return np.tile(np.array([[1., 0.]], dtype=np.float32), (len(texts), 1))
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"ENABLE_EMBEDDINGS": "true"}):
            folder = Path(tmp)
            gateway = DenseGateway()
            initial = Engine(BASE / "data/raw", folder / "built", gateway)
            packaged = folder / initial.vector_path.name
            packaged.write_bytes(initial.vector_path.read_bytes())
            with patch("legal_core.__file__", str(folder / "legal_core.py")):
                with patch.object(gateway, "embed", side_effect=AssertionError("Index must be loaded")):
                    restored = Engine(BASE / "data/raw", folder / "empty", gateway)
            np.testing.assert_allclose(initial.vectors, restored.vectors)

    def test_grounded_answer(self):
        answer = self.engine.ask("Какая арендная плата по договору Северный Склад?")
        self.assertEqual(answer["status"], "confirmed")
        self.assertIn("450 000", answer_text(answer))
        self.assertTrue(answer["sources"])

    def test_default_date_in_submission_text(self):
        from datetime import date
        answer = self.engine.ask("Какая арендная плата Северный Склад?")
        self.assertIn(date.today().isoformat(), answer_text(answer))
        self.assertIn("Дата события не указана", answer["dateNote"])

    def test_current_question_overrides_contract_date(self):
        from datetime import date
        original = self.engine.gateway.chat
        with patch.object(self.engine.gateway, "chat", wraps=original) as chat:
            self.engine.ask("Договор от 12.02.2024. Какая сейчас арендная плата Северный Склад?")
        generation_data = chat.call_args_list[0].args[1]
        self.assertEqual(generation_data["eventDate"], date.today().isoformat())

    def test_partial_answer_with_explicit_gap(self):
        original = self.engine.gateway.chat
        def response(system, data):
            answer = original(system, data)
            if "supported" not in system:
                answer["missingInfo"] = ["Документ об увеличении арендной платы"]
            return answer
        with patch.object(self.engine.gateway, "chat", side_effect=response):
            answer = self.engine.ask("Какая арендная плата Северный Склад и было ли повышение?")
        self.assertTrue(answer["sources"])
        self.assertTrue(answer["missingInfo"])
        self.assertIn("Документ об увеличении", answer_text(answer))

    def test_separate_service_credentials(self):
        settings = {
            "LLM_BASE_URL": "https://generation.test/v1", "LLM_API_KEY": "generation-key",
            "EMBEDDER_BASE_URL": "https://embedding.test/v1", "EMBEDDER_API_KEY": "embedding-key",
            "RERANKER_BASE_URL": "https://reranking.test/v1", "RERANKER_API_KEY": "reranking-key",
        }
        received = []
        def handler(request):
            received.append((request.url.host, request.headers["Authorization"]))
            return httpx.Response(200, json={"ok": True})
        with patch.dict(os.environ, settings):
            gateway = Gateway()
        gateway.client.close()
        gateway.client = httpx.Client(transport=httpx.MockTransport(handler))
        try:
            for route in ("/chat/completions", "/embeddings", "/rerank"):
                gateway.post(route, {})
        finally:
            gateway.client.close()
        self.assertEqual(received, [
            ("generation.test", "Bearer generation-key"),
            ("embedding.test", "Bearer embedding-key"),
            ("reranking.test", "Bearer reranking-key"),
        ])
        settings["EMBEDDER_API_KEY"] = ""
        with patch.dict(os.environ, settings):
            gateway = Gateway()
        try:
            with self.assertRaises(ModelError):
                gateway.post("/embeddings", {})
        finally:
            gateway.client.close()

    def test_unknown_source_rejected(self):
        with patch.object(self.engine.gateway, "chat", return_value={"status":"confirmed", "paragraphs":[{"text":"90 дней", "references":[{"id":"fake", "quote":"90 календарных дней"}]}]}):
            with self.assertRaises(ModelError):
                self.engine.ask("оплата")

    def test_unknown_source_is_corrected_once(self):
        original = self.engine.gateway.chat
        generations = 0
        def response(system, data):
            nonlocal generations
            if "supported" in system:
                return {"supported": True}
            generations += 1
            if generations == 1:
                return {"status": "confirmed", "paragraphs": [{
                    "text": "Плата 450 000 рублей", "references": [{"id": "missing", "quote": "Плата ..."}],
                }]}
            self.assertIn("validationError", data)
            return original(system, data)
        with patch.object(self.engine.gateway, "chat", side_effect=response):
            answer = self.engine.ask("Какая арендная плата Северный Склад?")
        self.assertEqual(generations, 2)
        self.assertTrue(answer["sources"])

    def test_quote_is_copied_from_source(self):
        chunk = next(c for c in self.engine.chunks if "450 000" in c["text"])
        result = {"status": "confirmed", "paragraphs": [{
            "text": "Плата составляет 450 000 рублей в месяц.",
            "references": [{"id": chunk["chunk_id"], "quote": "Придуманный пересказ"}],
        }]}
        sources, paragraphs = self.engine.validate_answer(result, [chunk])
        self.assertEqual(sources[0]["quote"], chunk["text"].strip())
        self.assertEqual(paragraphs[0][1]["cite"], 1)

    def test_unsupported_answer_rejected(self):
        original = self.engine.gateway.chat
        def response(system, data):
            return {"supported": False} if "supported" in system else original(system, data)
        with patch.object(self.engine.gateway, "chat", side_effect=response):
            with self.assertRaises(ModelError):
                self.engine.ask("арендная плата Северный Склад")

if __name__ == "__main__":
    unittest.main()
