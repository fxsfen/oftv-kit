"""Accurate pass: large-v3 word timestamps (no VAD) + energy speech bounds for every talking clip."""
import json, subprocess
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel

SRC = [d for d in Path(r"C:\Users\fosfe\Downloads").iterdir() if d.name == "шелли 1"][0]
OUT = Path(__file__).resolve().parents[1] / "assets" / "analysis"


def pcm(p, sr=16000):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-map", "0:a:0", "-ac", "1", "-ar", str(sr),
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0


def bounds_of(x, sr=16000):
    hop = int(sr * 0.02)
    n = len(x) // hop
    r = 20 * np.log10(np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
    floor, p90 = np.percentile(r, 10), np.percentile(r, 90)
    idx = np.where(r > floor + 0.45 * (p90 - floor))[0]
    return {"dur": round(len(x) / sr, 3), "speech_in": round(idx[0] * 0.02, 2) if len(idx) else 0.0,
            "speech_out": round((idx[-1] + 1) * 0.02, 2) if len(idx) else 0.0,
            "floor": round(float(floor), 1), "p90": round(float(p90), 1)}


m = WhisperModel("large-v3", device="cpu", compute_type="int8")
tr, bounds = {}, {}
for p in sorted(SRC.glob("*.MOV")):
    x = pcm(p)
    bounds[p.stem] = bounds_of(x)
    segs, _ = m.transcribe(x, language="en", vad_filter=False, word_timestamps=True,
                           condition_on_previous_text=False, beam_size=5, temperature=0.0)
    tr[p.stem] = [{"word": w.word, "start": round(w.start, 2), "end": round(w.end, 2)}
                  for s in segs for w in (s.words or [])]
    print(p.stem, bounds[p.stem]["speech_in"], bounds[p.stem]["speech_out"],
          "".join(w["word"] for w in tr[p.stem]), flush=True)
(OUT / "transcripts.json").write_text(json.dumps(tr, ensure_ascii=False, indent=1), encoding="utf-8")
(OUT / "speech_bounds.json").write_text(json.dumps(bounds, indent=1), encoding="utf-8")
