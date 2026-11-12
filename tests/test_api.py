import os
os.environ["ENABLE_EMBEDDINGS"] = "false"
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
import api
from legal_core import Engine
from test_core import FakeGateway, BASE

class ApiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        os.environ["STATE_DB"] = str(Path(self.temp.name) / "state.sqlite")
        self.engine = Engine(BASE / "data/raw", self.temp.name, FakeGateway())
        self.engine.gateway.client = type("Client", (), {"close": lambda self: None})()
        self.mock = patch.object(api, "Engine", return_value=self.engine)
        self.mock.start()
        self.client = TestClient(api.app)
        self.client.__enter__()
    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.mock.stop()
        self.temp.cleanup()
        os.environ.pop("STATE_DB", None)
    def test_full_answer_source_and_persistence(self):
        r = self.client.post("/api/v1/ask", json={"question":"Какая арендная плата Северный Склад?", "dialogId":"test"})
        self.assertEqual(r.status_code, 200, r.text)
        source = r.json()["sources"][0]
        doc = self.client.get("/api/v1/documents/" + source["documentId"])
        self.assertEqual(doc.status_code, 200)
        clauses = doc.json()["sections"][0]["clauses"]
        clause = next(c for c in clauses if c["id"] == source["clauseId"])
        self.assertIn(source["quote"], clause["versions"][source["editionId"]])
        self.assertEqual(len(self.client.get("/api/v1/dialogs").json()), 1)
        self.assertEqual(self.client.post("/api/v1/dialogs/test/feedback",json={"value":"disputed"}).status_code, 204)
        self.assertEqual(self.client.get("/api/v1/dialogs").json()[0]["feedback"], "disputed")
        self.assertEqual(self.client.get("/api/v1/knowledge-base").json()["stats"]["documentCount"],21)
    def test_errors(self):
        self.assertEqual(self.client.get("/api/v1/documents/unknown").status_code,404)
        r = self.client.post("/api/v1/ask",json={"question":"", "dialogId":"x"})
        self.assertEqual(r.status_code,422)
        self.assertIn("error", r.json())
    def test_history_loaded(self):
        with patch.object(self.engine, "ask", wraps=self.engine.ask) as ask:
            for q in ("Какая арендная плата Северный Склад?", "А какая плата по этому договору?"):
                self.assertEqual(self.client.post("/api/v1/ask",json={"question":q,"dialogId":"history"}).status_code,200)
            self.assertEqual(len(ask.call_args.args[1]),2)

if __name__ == "__main__":
    unittest.main()
