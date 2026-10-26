"""large-v3 accurate pass with dict words. Talking clips: whole file. Voice notes (prefix 'vo:'): split into phrases by
energy (>=0.35 s silence) and transcribed phrase by phrase (exposes retakes). Also Silero VAD of every wav.
usage: python _accurate_phrases.py <project> <lang> <stem> ... vo:<stem> ...   -> transcripts.json, phrases.json, camera_speech.json"""
import json, sys
from pathlib import Path

import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel
from faster_whisper.vad import VadOptions, get_speech_timestamps

A = Path(__file__).resolve().parent / sys.argv[1] / "assets/analysis"
lang = sys.argv[2]
W = A / "wav16"
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
KW = dict(language=lang, vad_filter=False, word_timestamps=True, condition_on_previous_text=False, beam_size=5,
          temperature=0.0)


def words(x, off=0.0):
    segs, _ = m.transcribe(x, **KW)
    return [{"word": w.word, "start": round(w.start + off, 2), "end": round(w.end + off, 2), "p": round(w.probability, 2)}
            for s in segs for w in (s.words or [])]


def phrases(x, sr, gap=0.35):
    hop = int(sr * 0.02)
    n = len(x) // hop
    db = 20 * np.log10(np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
    thr = max(np.percentile(db, 30) + 6, np.percentile(db, 95) - 35)
    on = db > thr
    runs, i = [], 0
    while i < n:
        if on[i]:
            j = i
            while j < n and on[j]:
                j += 1
            runs.append([i * 0.02, j * 0.02])
            i = j
        else:
            i += 1
    merged = []
    for a, b in runs:
        if merged and a - merged[-1][1] < gap:
            merged[-1][1] = b
        else:
            merged.append([a, b])
    return [(max(0, a - 0.1), min(len(x) / sr, b + 0.15)) for a, b in merged if b - a > 0.15]


vad = {}
for w in sorted(W.glob("*.wav")):
    x, sr = sf.read(str(w), dtype="float32")
    ts = get_speech_timestamps(x, VadOptions(threshold=0.5, min_speech_duration_ms=200))
    vad[w.stem] = [[round(t["start"] / sr, 2), round(t["end"] / sr, 2)] for t in ts]
(A / "camera_speech.json").write_text(json.dumps(vad, indent=1), encoding="utf-8")
print("vad done", flush=True)
trp, php = A / "transcripts.json", A / "phrases.json"
tr = json.loads(trp.read_text(encoding="utf-8")) if trp.exists() else {}
ph = json.loads(php.read_text(encoding="utf-8")) if php.exists() else {}
for arg in sys.argv[3:]:
    isvo = arg.startswith("vo:")
    k = arg[3:] if isvo else arg
    if k in tr:
        continue
    x, sr = sf.read(str(W / f"{k}.wav"), dtype="float32")
    if isvo:
        ph[k], allw = [], []
        for a, b in phrases(x, sr):
            ws = words(x[int(a * sr): int(b * sr)], a)
            ph[k].append({"a": round(a, 2), "b": round(b, 2), "t": "".join(w["word"] for w in ws).strip()})
            allw += ws
        tr[k] = allw
    else:
        tr[k] = words(x)
    php.write_text(json.dumps(ph, ensure_ascii=False, indent=1), encoding="utf-8")
    trp.write_text(json.dumps(tr, ensure_ascii=False, indent=1), encoding="utf-8")
    print(k, "done", flush=True)
print("accurate done", flush=True)
