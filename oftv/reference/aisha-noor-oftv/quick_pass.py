"""Quick analysis pass: contact sheets + small whisper (Spanish) for every clip."""
import json, subprocess, sys
from pathlib import Path

SRC = Path(r"C:\Users\fosfe\Downloads\аиш")
OUT = Path(__file__).resolve().parents[1] / "assets" / "analysis"
SHEETS = OUT / "sheets"
SHEETS.mkdir(parents=True, exist_ok=True)

clips = sorted(SRC.glob("*.MOV"))


def dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(p)], capture_output=True, text=True)
    return float(r.stdout.strip())


if "sheets" in sys.argv:
    for c in clips:
        d = dur(c)
        out = SHEETS / f"{c.stem}.jpg"
        if out.exists():
            continue
        vf = (f"fps=6/{d:.3f},scale=480:-2,"
              f"drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='{c.stem} %{{pts\\:hms}}':"
              f"x=8:y=8:fontsize=20:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=6x1")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(c), "-vf", vf,
                        "-frames:v", "1", str(out)], check=True)
        print("sheet", c.name, flush=True)

if "whisper" in sys.argv:
    from faster_whisper import WhisperModel
    m = WhisperModel("small", device="cpu", compute_type="int8")
    res = {}
    for c in clips:
        segs, info = m.transcribe(str(c), language="es", vad_filter=False,
                                  condition_on_previous_text=False)
        res[c.name] = [{"s": round(s.start, 2), "e": round(s.end, 2), "t": s.text.strip()} for s in segs]
        print(c.name, " | ".join(x["t"] for x in res[c.name]), flush=True)
    (OUT / "quick_transcripts.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
