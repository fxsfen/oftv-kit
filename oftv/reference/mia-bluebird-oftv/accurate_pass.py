"""Accurate pass (English): large-v3 word timestamps for the voice notes + talking clips,
energy speech bounds for them, Silero VAD on every camera clip, face-crop sheets for b-roll."""
import json, subprocess
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel
from faster_whisper.vad import VadOptions, get_speech_timestamps

SRC = [d for d in Path(r"C:\Users\fosfe\Downloads").iterdir() if d.name.startswith("Лине")][0]
OUT = Path(__file__).resolve().parents[1] / "assets" / "analysis"
FACES = OUT / "faces"
FACES.mkdir(parents=True, exist_ok=True)
TALK = ["IMG_9933", "joi"]


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
tr, bounds, vad = {}, {}, {}
speech_files = sorted(SRC.glob("*.ogg")) + [p for p in sorted(SRC.iterdir()) if p.stem in TALK]
for p in speech_files:
    x = pcm(p)
    bounds[p.stem] = bounds_of(x)
    segs, _ = m.transcribe(x, language="en", vad_filter=False, word_timestamps=True,
                           condition_on_previous_text=False, beam_size=5)
    tr[p.stem] = [{"word": w.word, "start": round(w.start, 2), "end": round(w.end, 2)}
                  for s in segs for w in (s.words or [])]
    print(p.stem, "".join(w["word"] for w in tr[p.stem]), flush=True)
(OUT / "transcripts.json").write_text(json.dumps(tr, ensure_ascii=False, indent=1), encoding="utf-8")
(OUT / "speech_bounds.json").write_text(json.dumps(bounds, indent=1), encoding="utf-8")

for p in sorted(SRC.glob("*.MOV")):
    if p.stem in TALK:
        continue
    x = pcm(p)
    ts = get_speech_timestamps(x, VadOptions(threshold=0.5, min_speech_duration_ms=200))
    vad[p.stem] = [[round(t["start"] / 16000, 2), round(t["end"] / 16000, 2)] for t in ts]
    print(p.stem, "VAD", vad[p.stem], flush=True)
    vf = ("fps=1/3,scale=300:-2,"
          f"drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='{p.stem[4:]} %{{pts\\:hms}}':x=4:y=4:fontsize=16:"
          "fontcolor=yellow:box=1:boxcolor=black@0.6,tile=10x5")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(p), "-vf", vf, "-frames:v", "1",
                    str(FACES / f"{p.stem}.jpg")], check=True)
(OUT / "camera_speech.json").write_text(json.dumps(vad, indent=1), encoding="utf-8")
