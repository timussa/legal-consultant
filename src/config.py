from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

DOCS_FILE = PROCESSED_DIR / "docs.jsonl"
CHUNKS_FILE = PROCESSED_DIR / "chunks.jsonl"

CHUNK_MAX_CHARS = 1200
CHUNK_OVERLAP_SENTENCES = 1

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)