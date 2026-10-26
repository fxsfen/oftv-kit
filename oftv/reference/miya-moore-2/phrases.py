"""Single long talking-head take full of retakes: split the camera audio by energy into
phrases (>= 0.35 s silence) and transcribe each phrase on its own with large-v3 (English,
word timestamps) -> assets/analysis/phrases.json. Retakes show up as near-identical
consecutive phrases instead of being merged by Whisper."""
import json, subprocess, sys
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel

PROJ = Path(__file__).resolve().parents[1]
SRC = Path(r"C:\Users\fosfe\Downloads\Новая папка (18)\мм1.MOV")
OUT = PROJ / "assets" / "analysis"
OUT.mkdir(parents=True, exist_ok=True)
SR = 16000

raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(SRC), "-map", "0:a:0", "-ac", "1", "-ar", str(SR),
                      "-f", "s16le", "-"], capture_output=True, check=True).stdout
x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
np.save(OUT / "audio16k.npy", x)  # cached for later passes
hop = SR // 50
n = len(x) // hop
r = 20 * np.log10(np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
np.save(OUT / "energy20ms.npy", r)
floor = float(np.percentile(r, 10))
voiced = r > floor + 10
phr, st, q = [], None, 0
for i, v in enumerate(voiced):
    if v:
        st = i if st is None else st
        q = 0
    elif st is not None:
        q += 1
        if q * 0.02 >= 0.35:
            phr.append((st * 0.02, (i - q + 1) * 0.02))
            st, q = None, 0
if st is not None:
    phr.append((st * 0.02, n * 0.02))
print(f"floor {floor:.1f} dB, {len(phr)} phrases", flush=True)

m = WhisperModel("large-v3", device="cpu", compute_type="int8")
res = []
for a, b in phr:
    if b - a < 0.25:
        continue
    a0, b0 = max(0.0, a - 0.15), min(len(x) / SR, b + 0.2)
    segs, _ = m.transcribe(x[int(a0 * SR): int(b0 * SR)], language="en", vad_filter=False, word_timestamps=True,
                           condition_on_previous_text=False, beam_size=5,
                           temperature=0.0, max_new_tokens=120)  # no fallback loops: a hallucinating phrase stalled for minutes
    ws = [{"word": w.word, "start": round(w.start + a0, 2), "end": round(w.end + a0, 2)}
          for s in segs for w in (s.words or [])]
    text = "".join(w["word"] for w in ws).strip()
    res.append({"i": len(res), "start": round(a, 2), "end": round(b, 2), "text": text, "words": ws})
    print(f"{len(res) - 1:3d} {a:7.2f}-{b:7.2f} {text}", flush=True)
    (OUT / "phrases.json").write_text(json.dumps({"floor": floor, "phrases": res}, ensure_ascii=False, indent=1),
                                      encoding="utf-8")
