import csv
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE = Path(__file__).resolve().parents[1]
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass
    def do_POST(self):
        payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        system = payload["messages"][0]["content"]
        data = json.loads(payload["messages"][1]["content"])
        if "supported" in system:
            result = {"supported": True}
        else:
            c = next(c for c in data["evidence"] if "450 000" in c["text"])
            result = {"status":"confirmed", "paragraphs":[{"text":"Арендная плата 450 000 рублей в месяц.","references":[{"id":c["id"],"quote":c["text"].strip()}]}]}
        body = json.dumps({"choices":[{"message":{"content":json.dumps(result,ensure_ascii=False)}}]}).encode()
        self.send_response(200)
        self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",str(len(body)))
        self.end_headers()
        self.wfile.write(body)

class SubmissionTests(unittest.TestCase):
    def test_flat_zip_runs_in_isolation(self):
        subprocess.run([sys.executable, str(BASE/"scripts/package_submission.py")],check=True,capture_output=True)
        server = ThreadingHTTPServer(("127.0.0.1",0),Handler)
        thread = threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                work = Path(tmp)
                with zipfile.ZipFile(BASE/"output/submission.zip") as z:
                    self.assertTrue(all("/" not in n for n in z.namelist()))
                    z.extractall(work)
                data = work/"data"
                data.mkdir()
                with zipfile.ZipFile(data/"knowledge-base.zip","w") as z:
                    for f in (BASE/"data/raw").glob("*.txt"):
                        z.write(f,f.name)
                with (data/"questions.csv").open("w",encoding="utf-8",newline="") as f:
                    w = csv.writer(f)
                    w.writerow(["id","question"])
                    w.writerow(["1","Какая арендная плата Северный Склад?"])
                environment = dict(os.environ, ENABLE_EMBEDDINGS="false",LLM_BASE_URL=f"http://127.0.0.1:{server.server_port}",LLM_API_KEY="test",LLM_MODEL="test",RERANKER_MODEL="",DATA_DIR=str(data))
                process = subprocess.run([sys.executable,"solution.py"],cwd=work,env=environment,capture_output=True,text=True,timeout=30)
                self.assertEqual(process.returncode,0,process.stderr)
                with (work/"submission.csv").open(encoding="utf-8",newline="") as f:
                    rows=list(csv.DictReader(f))
                self.assertEqual(len(rows),1)
                self.assertIn("450 000",rows[0]["answer"])
                self.assertIn("[1]",rows[0]["answer"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join()
