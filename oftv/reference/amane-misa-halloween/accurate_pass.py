"""large-v3 accurate pass: talking clips whole (word times), VO split into phrases by energy
(>=0.35 s silence) and each phrase transcribed on its own so retakes stay separate."""
import json, sys, wave
from pathlib import Path
import numpy as np
from faster_whisper import WhisperModel

PROJ = Path(__file__).resolve().parents[1]
A = PROJ / "assets/analysis"
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
out = {}
for key in ["VID_20261019_020033", "VID_20261019_025536"]:
    segs, _ = m.transcribe(str(A / f"{key}.wav"), language="en", vad_filter=False, word_timestamps=True,
                           condition_on_previous_text=False, temperature=0.0)
    out[key] = [[round(w.start, 2), round(w.end, 2), w.word] for s in segs for w in s.words]
    print("done", key, len(out[key]), flush=True)
json.dump(out, open(A / "talk_words.json", "w", encoding="utf-8"), indent=0, ensure_ascii=False)

w = wave.open(str(A / "vo42.wav")); sr = w.getframerate()
x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
hop = int(sr * 0.02); n = len(x) // hop
e = 20 * np.log10(np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
thr = np.percentile(e, 10) + 10
on = e > thr
phr, st, sil = [], None, 0
for i in range(n):
    if on[i]:
        if st is None: st = i
        sil = 0
    elif st is not None:
        sil += 1
        if sil * 0.02 >= 0.35:
            end = i - sil + 1
            if (end - st) * 0.02 > 0.15: phr.append((st * 0.02, end * 0.02))
            st, sil = None, 0
if st is not None: phr.append((st * 0.02, n * 0.02))
res = []
for a, b in phr:
    a0, b0 = max(0, a - 0.12), min(n * 0.02, b + 0.15)
    seg = x[int(a0 * sr):int(b0 * sr)]
    segs, _ = m.transcribe(seg, language="en", vad_filter=False, word_timestamps=True, temperature=0.0,
                           condition_on_previous_text=False, max_new_tokens=120)
    words = [[round(a0 + w.start, 2), round(a0 + w.end, 2), w.word] for s in segs for w in s.words]
    text = "".join(wd[2] for wd in words).strip()
    res.append({"a": round(a, 2), "b": round(b, 2), "text": text, "words": words})
    print(f"{a:7.2f} {b:7.2f} {text}", flush=True)
json.dump(res, open(A / "vo_phrases.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("ALL DONE", flush=True)
