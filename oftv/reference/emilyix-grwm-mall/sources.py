"""sources.json for Emily's 'домонтаж' videos: camera clips by stem, 'get ready' voice notes as gr01.. (time order)."""
import json, subprocess
from pathlib import Path
PROJ = Path(__file__).resolve().parents[1]
SRC = [d for d in Path(r"C:\Users\fosfe\Downloads").iterdir() if d.name == "домонтаж"][0] / "emilyix"
S = {"sources": {}, "dur": {}}
files = [(p.stem, p) for p in sorted(SRC.glob("*.MOV"))] + \
        [(f"gr{i + 1:02d}", p) for i, p in enumerate(sorted((SRC / "get ready").glob("*.ogg")))]
for k, p in files:
    S["sources"][k] = str(p).replace("\\", "/")
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True)
    S["dur"][k] = round(float(r.stdout), 3)
    wav = PROJ / "assets/analysis/wav16" / f"{k}.wav"
    if not wav.exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(p), "-map", "0:a:0", "-vn", "-ac", "1", "-ar", "16000", str(wav)], check=True)
(PROJ / "assets/analysis/sources.json").write_text(json.dumps(S, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(S["sources"]))
