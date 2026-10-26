"""large-v3 pass (no VAD, word times) for Zoey's talking clips, the VO recording and the on-camera tail
of IMG_1806; Silero VAD map of IMG_1806 (where she talks on camera -> never under VO)."""
import json
from pathlib import Path
from faster_whisper import WhisperModel
from faster_whisper.audio import decode_audio
from faster_whisper.vad import get_speech_timestamps, VadOptions

A = Path(__file__).resolve().parents[1] / "assets/analysis"
W = A / "wav16"
vo = [p for p in W.iterdir() if p.stem.startswith("Закадровая")][0]
a = decode_audio(str(W / "IMG_1806.wav"))
ts = get_speech_timestamps(a, VadOptions(threshold=0.5, min_silence_duration_ms=300))
(A / "vad_1806.json").write_text(json.dumps([[round(t["start"] / 16000, 2), round(t["end"] / 16000, 2)] for t in ts]))
print("vad 1806:", [(round(t["start"] / 16000, 1), round(t["end"] / 16000, 1)) for t in ts], flush=True)
dst = A / "transcripts.json"
out = json.loads(dst.read_text(encoding="utf-8")) if dst.exists() else {}
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
jobs = [("IMG_1802", str(W / "IMG_1802.wav"), 0), ("IMG_1803", str(W / "IMG_1803.wav"), 0),
        ("IMG_1807", str(W / "IMG_1807.wav"), 0), ("IMG_1808", str(W / "IMG_1808.wav"), 0), ("vo", str(vo), 0),
        ("IMG_1806", a[int(840 * 16000):], 840.0)]
for k, src, off in jobs:
    if k in out:
        continue
    segs, _ = m.transcribe(src, language="en", vad_filter=False, word_timestamps=True,
                           condition_on_previous_text=False, temperature=0.0)
    out[k] = [[round(off + w.start, 2), round(off + w.end, 2), w.word] for s in segs for w in s.words]
    print(k, "".join(w[2] for w in out[k]), flush=True)
    dst.write_text(json.dumps(out, indent=0, ensure_ascii=False), encoding="utf-8")
print("ALL DONE", flush=True)
