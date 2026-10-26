"""Quick analysis pass: contact sheets + small whisper (language auto-detected) for every clip / voice note."""
import json, subprocess, sys
from pathlib import Path

SRC = [d for d in Path(r"C:\Users\fosfe\Downloads").iterdir() if d.name.startswith("Лине")][0]
OUT = Path(__file__).resolve().parents[1] / "assets" / "analysis"
SHEETS = OUT / "sheets"
SHEETS.mkdir(parents=True, exist_ok=True)


def dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(p)], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


clips = [c for c in sorted(list(SRC.glob("*.MOV")) + list(SRC.glob("*.mp4"))) if dur(c) > 0]
audio = sorted(SRC.glob("*.ogg"))

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
    for c in audio + clips:
        segs, info = m.transcribe(str(c), vad_filter=False, condition_on_previous_text=False)
        res[c.name] = {"lang": info.language,
                       "segs": [{"s": round(s.start, 2), "e": round(s.end, 2), "t": s.text.strip()} for s in segs]}
        print(c.name, info.language, " | ".join(x["t"] for x in res[c.name]["segs"]), flush=True)
        (OUT / "quick_transcripts.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
