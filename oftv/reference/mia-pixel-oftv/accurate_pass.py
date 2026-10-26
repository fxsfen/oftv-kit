"""Accurate pass (Russian):
  - VO recording full of retakes: split by energy into phrases (>= 0.35 s silence),
    each phrase transcribed on its own with large-v3 -> assets/analysis/vo_phrases.json
  - every camera clip: large-v3, no VAD, word timestamps -> transcripts.json + speech_bounds.json
Usage: python accurate_pass.py [vo] [clips]
"""
import json, subprocess, sys, wave
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel

SRC = Path(r"C:\Users\fosfe\Downloads\Новая папка (14)")
PROJ = Path(__file__).resolve().parents[1]
OUT = PROJ / "assets" / "analysis"
OUT.mkdir(parents=True, exist_ok=True)
VO = SRC / "Новая запись 3.m4a"
VO_WAV = PROJ / "assets" / "audio" / "vo_main_q.wav"


def dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def db_curve(x, sr):
    hop = int(sr * 0.02)
    n = len(x) // hop
    return 20 * np.log10(np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)


def pcm(p, sr=16000):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-map", "0:a:0", "-ac", "1", "-ar", str(sr),
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0, sr


m = WhisperModel("large-v3", device="cpu", compute_type="int8")


def words_of(audio, offset=0.0):
    segs, _ = m.transcribe(audio, language="ru", vad_filter=False, word_timestamps=True,
                           condition_on_previous_text=False, beam_size=5)
    return [{"word": w.word, "start": round(w.start + offset, 2), "end": round(w.end + offset, 2)}
            for s in segs for w in (s.words or [])]


if "vo" in sys.argv:
    VO_WAV.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(VO), "-ac", "1", "-ar", "16000", str(VO_WAV)], check=True)
    w = wave.open(str(VO_WAV))
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    r = db_curve(x, 16000)
    floor = float(np.percentile(r, 10))
    voiced = r > floor + 10
    phrases, st, quiet = [], None, 0
    for i, v in enumerate(voiced):
        if v:
            if st is None:
                st = i
            quiet = 0
        elif st is not None:
            quiet += 1
            if quiet * 0.02 >= 0.35:
                phrases.append((st * 0.02, (i - quiet + 1) * 0.02))
                st, quiet = None, 0
    if st is not None:
        phrases.append((st * 0.02, len(voiced) * 0.02))
    res = []
    for k, (a, b) in enumerate(phrases):
        if b - a < 0.25:
            continue
        a0, b0 = max(0.0, a - 0.15), min(len(x) / 16000, b + 0.2)
        ws = words_of(x[int(a0 * 16000): int(b0 * 16000)], offset=a0)
        text = "".join(w["word"] for w in ws).strip()
        res.append({"i": len(res), "start": round(a, 2), "end": round(b, 2), "text": text, "words": ws})
        print(f"{a:7.2f}-{b:7.2f} {text}", flush=True)
    (OUT / "vo_phrases.json").write_text(json.dumps({"floor": floor, "phrases": res}, ensure_ascii=False, indent=1),
                                        encoding="utf-8")

if "clips" in sys.argv:
    tpath, bpath = OUT / "transcripts.json", OUT / "speech_bounds.json"
    tr = json.loads(tpath.read_text(encoding="utf-8")) if tpath.exists() else {}
    bounds = json.loads(bpath.read_text()) if bpath.exists() else {}
    for c in sorted(SRC.glob("*.MOV")):
        if c.stem in tr or dur(c) <= 0:
            continue
        x, sr = pcm(c)
        r = db_curve(x, sr)
        floor, p90 = np.percentile(r, 10), np.percentile(r, 90)
        idx = np.where(r > floor + 0.45 * (p90 - floor))[0]
        bounds[c.stem] = {"dur": round(len(x) / sr, 3),
                          "speech_in": round(idx[0] * 0.02, 2) if len(idx) else 0.0,
                          "speech_out": round((idx[-1] + 1) * 0.02, 2) if len(idx) else 0.0,
                          "floor": round(float(floor), 1), "p90": round(float(p90), 1)}
        tr[c.stem] = words_of(x)
        print(c.stem, "".join(w["word"] for w in tr[c.stem]), flush=True)
        tpath.write_text(json.dumps(tr, ensure_ascii=False, indent=1), encoding="utf-8")
        bpath.write_text(json.dumps(bounds, indent=1), encoding="utf-8")
