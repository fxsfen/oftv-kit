"""Quick pass for Bela Cruz 'Guion NN' folders (ESC 1 intro, ESC 2-6 takes + VOZ EN OFF, ESC 7 outro).
Voice is recorded on the RIGHT channel only (left is silent) -> wavs take the louder channel.
Usage: quick_pass.py <guion-number> audio sheets whisper"""
import json, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

N = sys.argv[1]
ROOT = Path(r"C:\Users\fosfe\Downloads") / "Новая папка (19)"
SRC = next(d for d in ROOT.iterdir() if d.name.startswith(f"Guion {N}"))
PROJ = Path(__file__).resolve().parents[2] / f"bela-cruz-{N}"
OUT = PROJ / "assets" / "analysis"
SHEETS, WAV = OUT / "sheets", OUT / "wav16"
for d in (SHEETS, WAV):
    d.mkdir(parents=True, exist_ok=True)


def key(p):
    s = p.stem.upper()
    if p.suffix.lower() == ".m4a":
        return "vo" + re.findall(r"ESC (\d)", s)[0]
    esc = re.findall(r"ESC (\d)", s)[0]
    if "DIALOGOS" in s or "DALOGOS" in s:
        return f"e{esc}"
    take = re.findall(r"(?:TOMA|ROMA) ([\d.]+)", s)[0].replace(".", "_")
    return f"e{esc}t{take}"


files = sorted(p for p in SRC.rglob("*") if p.is_file() and p.suffix.lower() in (".mov", ".m4a"))
smap = {key(p): str(p).replace("\\", "/") for p in files}
assert len(smap) == len(files)
dur = {}
for k, p in smap.items():
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                       capture_output=True, text=True)
    dur[k] = round(float(r.stdout), 2)
(OUT / "sources.json").write_text(json.dumps({"sources": smap, "dur": dur}, ensure_ascii=False, indent=1), encoding="utf-8")
print({k: dur[k] for k in smap}, flush=True)

if "audio" in sys.argv:
    def ext(k):
        dst = WAV / f"{k}.wav"
        if not dst.exists():
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", smap[k], "-map", "0:a:0", "-vn",
                            "-af", "pan=mono|c0=c1", "-ar", "16000", str(dst)])
    with ThreadPoolExecutor(4) as ex:
        list(ex.map(ext, smap))
    print("audio done", flush=True)

if "sheets" in sys.argv:
    def sheet(k):
        out = SHEETS / f"{k}.jpg"
        if out.exists() or k.startswith("vo"):
            return
        d, n = dur[k], 6
        tmp = SHEETS / f"_{k}"
        tmp.mkdir(exist_ok=True)
        for i in range(n):
            t = d * (i + 0.5) / n
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", smap[k], "-frames:v", "1",
                            "-vf", f"scale=400:-2,drawtext=fontfile='C\:/Windows/Fonts/arial.ttf':"
                                   f"text='{k} {t:.1f}s':x=6:y=6:fontsize=20:fontcolor=yellow:"
                                   "box=1:boxcolor=black@0.6", str(tmp / f"{i}.jpg")], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp / "%d.jpg"), "-vf", f"tile={n}x1",
                        "-frames:v", "1", str(out)], check=True)
    with ThreadPoolExecutor(3) as ex:
        list(ex.map(sheet, smap))
    print("sheets done", flush=True)

if "whisper" in sys.argv:
    from faster_whisper import WhisperModel
    m = WhisperModel("small", device="cpu", compute_type="int8")
    res = {}
    for k in sorted(smap):
        w = WAV / f"{k}.wav"
        segs, inf = m.transcribe(str(w), vad_filter=False, condition_on_previous_text=False, temperature=0.0)
        res[k] = {"lang": inf.language, "segs": [{"s": round(s.start, 2), "e": round(s.end, 2), "t": s.text.strip()} for s in segs]}
        (OUT / "quick_transcripts.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print("whisper done", flush=True)
