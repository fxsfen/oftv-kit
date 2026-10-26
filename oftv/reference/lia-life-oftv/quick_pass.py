"""Quick analysis pass for the 'лия' folder.
  audio   -> 16 kHz mono wav per clip (fast, no video decode)
  sheets  -> 8 seeked frames per clip tiled 8x1 (seek per frame: 4K HEVC full decode is far too slow)
  whisper -> small model, language auto, on the extracted wavs
"""
import json, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SRC = [d for d in Path(r"C:\Users\fosfe\Downloads").iterdir() if d.name == "лия"][0]
OUT = Path(__file__).resolve().parents[1] / "assets" / "analysis"
SHEETS = OUT / "sheets"
WAV = OUT / "wav16"
for d in (SHEETS, WAV):
    d.mkdir(parents=True, exist_ok=True)


def probe(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type",
                        "-of", "json", str(p)], capture_output=True, text=True)
    j = json.loads(r.stdout)
    return float(j["format"]["duration"]), any(s["codec_type"] == "audio" for s in j["streams"])


clips = sorted(list(SRC.glob("*.MOV")) + list(SRC.glob("*.MP4")))
info = {c.stem: probe(c) for c in clips}

if "audio" in sys.argv:
    def ext(c):
        dst = WAV / f"{c.stem}.wav"
        if info[c.stem][1] and not dst.exists():
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(c), "-map", "0:a:0", "-vn", "-ac", "1",
                            "-ar", "16000", str(dst)], check=True)
    with ThreadPoolExecutor(4) as ex:
        list(ex.map(ext, clips))
    print("audio done", flush=True)

if "sheets" in sys.argv:
    def sheet(c):
        out = SHEETS / f"{c.stem}.jpg"
        if out.exists():
            return
        d = info[c.stem][0]
        tmp = SHEETS / f"_{c.stem}"
        tmp.mkdir(exist_ok=True)
        for k in range(8):
            t = d * (k + 0.5) / 8
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(c), "-frames:v", "1",
                            "-vf", f"scale=400:-2,drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':"
                                   f"text='{c.stem[4:]} {t:.0f}s':x=6:y=6:fontsize=20:fontcolor=yellow:"
                                   "box=1:boxcolor=black@0.6", str(tmp / f"{k}.jpg")], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp / "%d.jpg"), "-vf", "tile=8x1",
                        "-frames:v", "1", str(out)], check=True)
        print("sheet", c.name, flush=True)
    with ThreadPoolExecutor(3) as ex:
        list(ex.map(sheet, clips))

if "whisper" in sys.argv:
    from faster_whisper import WhisperModel
    m = WhisperModel("small", device="cpu", compute_type="int8")
    qf = OUT / "quick_transcripts.json"
    res = json.loads(qf.read_text(encoding="utf-8")) if qf.exists() else {}
    for c in clips:
        w = WAV / f"{c.stem}.wav"
        if not w.exists() or c.stem in res:
            continue
        segs, inf = m.transcribe(str(w), vad_filter=False, condition_on_previous_text=False)
        res[c.stem] = {"lang": inf.language, "dur": round(info[c.stem][0], 1),
                       "segs": [{"s": round(s.start, 2), "e": round(s.end, 2), "t": s.text.strip()} for s in segs]}
        print(c.stem, inf.language, " | ".join(x["t"] for x in res[c.stem]["segs"]), flush=True)
        (OUT / "quick_transcripts.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
