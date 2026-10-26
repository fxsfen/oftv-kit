"""Accurate pass: Silero VAD on every clip; clips with real speech get large-v3 word
timestamps (English, no VAD filter, no previous-text conditioning) + energy bounds."""
import json, sys
from pathlib import Path

import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel
from faster_whisper.vad import VadOptions, get_speech_timestamps

OUT = Path(__file__).resolve().parents[1] / "assets" / "analysis"
WAV = OUT / "wav16"
ONLY = set(sys.argv[1:])

vad, tr = {}, {}
trp = OUT / "transcripts.json"
if trp.exists():
    tr = json.loads(trp.read_text(encoding="utf-8"))
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
for w in sorted(WAV.glob("*.wav")):
    if ONLY and w.stem not in ONLY:
        continue
    x, sr = sf.read(str(w), dtype="float32")
    ts = get_speech_timestamps(x, VadOptions(threshold=0.5, min_speech_duration_ms=200))
    vad[w.stem] = [[round(t["start"] / sr, 2), round(t["end"] / sr, 2)] for t in ts]
    speech = sum(e - s for s, e in vad[w.stem])
    print(w.stem, f"VAD speech {speech:.1f}s", flush=True)
    if speech < 2.5 or (w.stem in tr and not ONLY):
        continue
    segs, _ = m.transcribe(x, language="en", vad_filter=False, word_timestamps=True,
                           condition_on_previous_text=False, beam_size=5)
    tr[w.stem] = [{"word": wd.word, "start": round(wd.start, 2), "end": round(wd.end, 2), "p": round(wd.probability, 2)}
                  for s in segs for wd in (s.words or [])]
    print("  ", "".join(wd["word"] for wd in tr[w.stem]), flush=True)
    trp.write_text(json.dumps(tr, ensure_ascii=False, indent=1), encoding="utf-8")
(OUT / "camera_speech.json").write_text(json.dumps(vad, indent=1), encoding="utf-8")
