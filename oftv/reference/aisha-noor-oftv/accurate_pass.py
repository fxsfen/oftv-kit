"""Accurate pass: faster-whisper large-v3 (Spanish, no VAD, word timestamps) + energy speech bounds."""
import json, subprocess
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel

SRC = Path(r"C:\Users\fosfe\Downloads\аиш")
OUT = Path(__file__).resolve().parents[1] / "assets" / "analysis"
clips = sorted(SRC.glob("*.MOV"))


def pcm(p, sr=16000):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-map", "0:a:0", "-ac", "1",
                          "-ar", str(sr), "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0, sr


bounds = {}
for c in clips:
    x, sr = pcm(c)
    hop = int(sr * 0.02)
    n = len(x) // hop
    db = 20 * np.log10(np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
    floor, p90 = np.percentile(db, 10), np.percentile(db, 90)
    thr = floor + 0.45 * (p90 - floor)
    idx = np.where(db > thr)[0]
    bounds[c.stem] = {"dur": round(len(x) / sr, 3),
                      "speech_in": round(idx[0] * 0.02, 2) if len(idx) else 0.0,
                      "speech_out": round((idx[-1] + 1) * 0.02, 2) if len(idx) else 0.0,
                      "floor": round(float(floor), 1), "p90": round(float(p90), 1)}
(OUT / "speech_bounds.json").write_text(json.dumps(bounds, indent=1), encoding="utf-8")
print("bounds done", flush=True)

m = WhisperModel("large-v3", device="cpu", compute_type="int8")
res = {}
for c in clips:
    segs, _ = m.transcribe(str(c), language="es", vad_filter=False, word_timestamps=True,
                           condition_on_previous_text=False, beam_size=5)
    words = [{"word": w.word, "start": round(w.start, 2), "end": round(w.end, 2)}
             for s in segs for w in (s.words or [])]
    res[c.stem] = words
    print(c.stem, "".join(w["word"] for w in words), flush=True)
    (OUT / "transcripts.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
