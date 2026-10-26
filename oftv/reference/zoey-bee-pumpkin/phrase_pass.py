"""Split recordings into energy phrases (>=0.35 s silence) and transcribe each phrase on its own (large-v3),
so retakes / note-to-self lines stay separate and phrase bounds are exact."""
import json, sys
from pathlib import Path
import numpy as np
from faster_whisper import WhisperModel
from faster_whisper.audio import decode_audio

A = Path(__file__).resolve().parents[1] / "assets/analysis"
W = A / "wav16"
vo = [p for p in W.iterdir() if p.stem.startswith("Закадровая")][0]
JOBS = [("vo", vo, 0, None), ("IMG_1807", W / "IMG_1807.wav", 0, None), ("IMG_1808", W / "IMG_1808.wav", 0, None),
        ("IMG_1806", W / "IMG_1806.wav", 870, 935), ("IMG_1802", W / "IMG_1802.wav", 0, None),
        ("IMG_1803", W / "IMG_1803.wav", 0, None)]
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
res = {}
for key, path, t0, t1 in JOBS:
    x = decode_audio(str(path))
    sr = 16000
    hop = 320
    n = len(x) // hop
    e = 20 * np.log10(np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
    thr = np.percentile(e, 15) + 12
    on = e > thr
    phr, st, sil = [], None, 0
    for i in range(int(t0 / 0.02), int((t1 or n * 0.02) / 0.02)):
        if on[i]:
            if st is None:
                st = i
            sil = 0
        elif st is not None:
            sil += 1
            if sil * 0.02 >= 0.35:
                end = i - sil + 1
                if (end - st) * 0.02 > 0.15:
                    phr.append((st * 0.02, end * 0.02))
                st, sil = None, 0
    if st is not None:
        phr.append((st * 0.02, (t1 or n * 0.02)))
    res[key] = []
    for a, b in phr:
        a0, b0 = max(0, a - 0.12), min(n * 0.02, b + 0.15)
        segs, _ = m.transcribe(x[int(a0 * sr):int(b0 * sr)], language="en", vad_filter=False, temperature=0.0,
                               condition_on_previous_text=False, max_new_tokens=120)
        text = " ".join(s.text.strip() for s in segs).strip()
        res[key].append({"a": round(a, 2), "b": round(b, 2), "text": text})
        print(f"{key} {a:7.2f} {b:7.2f} {text}", flush=True)
    (A / "phrases.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
print("ALL DONE", flush=True)
