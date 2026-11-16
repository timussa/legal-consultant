"""Build docs/presentation.pdf: static 16:9 slides, no animation, no speaker notes.

Usage (from the repo root): python scripts/build_presentation.py [chrome_exe]
Slides live in docs/presentation/slides/*.html, order in docs/presentation/deck.json.
Team photos are picked up from ../team/<surname>.jpg|png|webp; without them initials are shown.
Needs a Chromium-based browser (Chrome or Edge) for printing to PDF.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import os
import shutil
import tempfile

repo = Path(__file__).resolve().parents[1]
deck = repo / "docs/presentation"
out_pdf = repo / "docs/presentation.pdf"
out_html = Path(tempfile.gettempdir()) / "legal-consultant-deck.html"
chrome = (sys.argv[1] if len(sys.argv) > 1 else os.getenv("CHROME_PATH")) or next((c for c in (
    shutil.which("chrome"), shutil.which("msedge"),
    r"C:/Program Files/Google/Chrome/Application/chrome.exe",
    r"C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe") if c and Path(c).exists()), None)
if not chrome:
    sys.exit("Не найден Chrome/Edge: передайте путь первым аргументом или через CHROME_PATH")
img = repo / "frontend/src/assets/images"
BLOBS = {
    "ff39e87b8a78691bf574acfa96496d61": img / "hero-scene.webp",
    "70d1ef9785ac97afae3968d9ef886841": img / "verification/scene.webp",
    "3145d10c8a1aec8bbadc86b6bc549a9c": img / "brand-mark.webp",
    "f340ffb7274f6499f48f284355a69716": img / "verification/icon-question.webp",
    "f31019fca64c2b773e4e1ac849e630b6": img / "verification/icon-search.webp",
    "1730d51c4946cbd0301c71c0585070fe": img / "verification/icon-compose.webp",
    "fd024fc246529a4bc082b54fe6e43a99": img / "verification/icon-parse.webp",
    "2a6451bfe1607611b7786134d822c731": img / "verification/icon-selfcheck.webp",
    "a563af466ae920964a4c49cba5708af3": img / "verification/icon-guard.webp",
    "c11f87598c92e9b049824511a1b09106": img / "verification/icon-clarify.webp",
    "37d017c7aea0cc7be5f7a165ce46340b": img / "verification/icon-refusal.webp",
    "fc2c7985c74021f923f5596e23a76a93": repo / "docs/screenshots/dialog.png",
    "1ebdc27a9e4798931e3da803fc02c26d": repo / "docs/screenshots/document.png",
    "252c456c40d0bc7ce60b87c07147fc8e": repo / "docs/screenshots/pressure.png",
    "6b8fe59f2b44e2b418b0b13289ce2332": img / "brand-paragraph.png",
}
ARROW = ('<svg width="96" height="48" viewBox="0 0 96 48" aria-label="стрелка">'
         '<path d="M0 18h56V4l40 20-40 20V30H0z" fill="#7B4FD8"/></svg>')

index = json.loads((deck / "deck.json").read_text(encoding="utf-8"))
css = (deck / "deck.css").read_text(encoding="utf-8")
slides = []
for slide_id in index["order"]:
    html = (deck / "slides" / f"{slide_id}.html").read_text(encoding="utf-8")
    html = re.sub(r"<aside>.*?</aside>", "", html, flags=re.S)
    html = re.sub(r"<x-shape[^>]*kind=\"arrow-right\"[^>]*></x-shape>", ARROW, html)
    for blob, path in BLOBS.items():
        if not path.is_file():
            sys.exit(f"missing image {path}")
        html = html.replace(f"/_blob/{blob}", path.resolve().as_uri())
    team_dir = repo.parent / "team"
    def avatar(match):
        name, initials = match[1], match[2]
        photo = next((p for p in sorted(team_dir.glob(name + ".*")) if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")), None) if team_dir.is_dir() else None
        if photo:
            return f'<img class="avatar" src="{photo.resolve().as_uri()}" alt="'
        return f'<div class="avatar avatar--initials">{initials}</div><img hidden alt="'
    html = re.sub(r'<img class="avatar" src="team:(\w+)" alt="(?=[^"]*" data-initials="(\w+)")', lambda m: avatar(m), html)
    html = re.sub(r'<img hidden alt="[^"]*" data-initials="\w+">', "", html)
    html = re.sub(r' data-initials="\w+"', "", html)
    if "/_blob/" in html:
        sys.exit(f"unmapped image in {slide_id}")
    slides.append(html)

fonts = "&".join("family=" + f["family"].replace(" ", "+") + (":wght@400;500;600;700;800" if f["family"] == "Manrope" else ":wght@400;700")
                 for f in index["faces"].values())
page = f"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8">
<title>{index['title']}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{fonts}&display=swap">
<style>
@page {{ size: 1920px 1080px; margin: 0; }}
html, body {{ margin: 0; padding: 0; }}
* {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
h1, h2, h3, p, ul, ol {{ margin: 0; }}
body {{ counter-reset: page; }}
section {{ position: relative; width: 1920px; height: 1080px; overflow: hidden; page-break-after: always; break-after: page; }}
section:last-child {{ page-break-after: auto; break-after: auto; }}
section > *:not(.scene):not(.shade):not(.foot) {{ position: relative; }}
table {{ border-collapse: collapse; width: 100%; }}
th {{ text-align: left; font-weight: 800; border-bottom: 2px solid #1F2A85; padding: 14px 18px; }}
td {{ padding: 14px 18px; border-bottom: 1px solid #E1E3EE; }}
a {{ color: inherit; }}
{css}
.rise {{ animation: none !important; opacity: 1 !important; transform: none !important; }}
.avatar {{ width: 240px; height: 240px; border-radius: 50%; object-fit: cover; border: 4px solid rgba(255,255,255,0.35);
  box-shadow: 0 20px 40px -20px rgba(5,8,46,0.9); }}
.avatar--initials {{ display: flex; align-items: center; justify-content: center; box-sizing: border-box;
  background: linear-gradient(150deg, #7B4FD8, #1F2A85); color: #F4F3FF; font-size: 72px; font-weight: 800; }}
</style></head><body>
{''.join(slides)}
</body></html>"""
out_html.write_text(page, encoding="utf-8")
out_pdf.parent.mkdir(parents=True, exist_ok=True)
subprocess.run([chrome, "--headless", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=15000",
                "--run-all-compositor-stages-before-draw", f"--print-to-pdf={out_pdf.resolve()}",
                out_html.resolve().as_uri()], check=True, capture_output=True, timeout=180)
print(out_pdf, out_pdf.stat().st_size, "bytes")
