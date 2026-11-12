"""Build flat ZIP compatible with the platform module-copy rules."""
from pathlib import Path
import argparse
import zipfile
BASE = Path(__file__).resolve().parents[1]
arguments = argparse.ArgumentParser()
arguments.add_argument("--index-dir", type=Path, help="Include precomputed .npy indices from this directory")
options = arguments.parse_args()
if options.index_dir is not None and not options.index_dir.is_dir():
    arguments.error("Index directory does not exist")
out = BASE / "output/submission.zip"
out.parent.mkdir(exist_ok=True)
parser = (BASE / "src/ingestion/parse.py").read_text(encoding="utf-8")
start = parser.index("from src.config import (")
end = parser.index("\n)", start) + 2
parser = parser[:start] + 'from ingestion_config import RAW_DIR, DOCS_FILE, CHUNKS_FILE, CHUNK_MAX_CHARS, CHUNK_OVERLAP_SENTENCES' + parser[end:]
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for name in ("solution.py", "legal_core.py"):
        z.write(BASE / name, name)
    z.writestr("requirements.txt", "httpx==0.28.1\nnumpy==2.2.6\nrank-bm25==0.2.2\n")
    z.writestr("ingestion_parser.py", parser)
    z.writestr("ingestion_config.py", (BASE / "src/config.py").read_text(encoding="utf-8").replace(".parent.parent", ".parent"))
    if options.index_dir:
        for index in sorted(options.index_dir.glob("*.npy")):
            z.write(index, index.name)
print(out)
