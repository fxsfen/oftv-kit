"""Quick pass for OFTV 27 (Ana, English): wavs, contact sheets, small-model whisper (language en)."""
import json, subprocess, sys, unicodedata
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SRC = Path(r"C:\Users\fosfe\Downloads") / "ана2" / "OFTV 27-20261019T165215Z-1-001" / "OFTV 27"
OUT = Path(__file__).resolve().parents[1] / "assets" / "analysis"
SHEETS = OUT / "sheets"
WAV = OUT / "wav16"
for d in (SHEETS, WAV):
    d.mkdir(parents=True, exist_ok=True)

files = sorted(SRC.iterdir())
clips = [p for p in files if p.suffix.lower() == ".mov"]
vos = {}
for p in files:
    n = unicodedata.normalize("NFC", p.name)
    if p.suffix.lower() == ".m4a":
        vos["vo" + n.split()[-1].split(".")[0]] = p


def key(c):
    return c.stem.replace("(", "_").replace(")", "")


def probe(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(p)],
                       capture_output=True, text=True)
    return float(json.loads(r.stdout)["format"]["duration"])


info = {key(c): probe(c) for c in clips}
srcmap = {key(c): c.name for c in clips}
srcmap.update({k: unicodedata.normalize("NFC", v.name) for k, v in vos.items()})
(OUT / "sources.json").write_text(json.dumps(srcmap, ensure_ascii=False, indent=1), encoding="utf-8")

if "audio" in sys.argv:
    jobs = [(c, WAV / f"{key(c)}.wav") for c in clips] + [(p, WAV / f"{k}.wav") for k, p in vos.items()]
    def ext(j):
        src, dst = j
        if not dst.exists():
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-map", "0:a:0", "-vn", "-ac", "1",
                            "-ar", "16000", str(dst)])
    with ThreadPoolExecutor(4) as ex:
        list(ex.map(ext, jobs))
    print("audio done", flush=True)

if "sheets" in sys.argv:
    def sheet(c):
        k = key(c)
        out = SHEETS / f"{k}.jpg"
        if out.exists():
            return
        d = info[k]
        tmp = SHEETS / f"_{k}"
        tmp.mkdir(exist_ok=True)
        n = 6
        for i in range(n):
            t = d * (i + 0.5) / n
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(c), "-frames:v", "1",
                            "-vf", f"scale=400:-2,drawtext=fontfile='C\:/Windows/Fonts/arial.ttf':"
                                   f"text='{k[4:]} {t:.1f}s':x=6:y=6:fontsize=20:fontcolor=yellow:"
                                   "box=1:boxcolor=black@0.6", str(tmp / f"{i}.jpg")], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp / "%d.jpg"), "-vf", f"tile={n}x1",
                        "-frames:v", "1", str(out)], check=True)
    with ThreadPoolExecutor(4) as ex:
        list(ex.map(sheet, clips))
    print("sheets done", flush=True)

if "whisper" in sys.argv:
    from faster_whisper import WhisperModel
    m = WhisperModel("small", device="cpu", compute_type="int8")
    res = {}
    for w in sorted(WAV.glob("*.wav")):
        segs, inf = m.transcribe(str(w), language="en", vad_filter=False, condition_on_previous_text=False,
                                 temperature=0.0)
        res[w.stem] = [{"s": round(s.start, 2), "e": round(s.end, 2), "t": s.text.strip()} for s in segs]
        (OUT / "quick_transcripts.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print("whisper done", flush=True)
