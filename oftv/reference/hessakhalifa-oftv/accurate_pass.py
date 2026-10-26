"""large-v3 Spanish pass (no VAD, word times) for the single assembled clip."""
import json
from pathlib import Path
from faster_whisper import WhisperModel

A = Path(__file__).resolve().parents[1] / "assets/analysis"
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
segs, _ = m.transcribe(str(A / "wav16/IMG_5941.wav"), language="es", vad_filter=False, word_timestamps=True,
                       condition_on_previous_text=False, temperature=0.0)
out = {"IMG_5941": [[round(w.start, 2), round(w.end, 2), w.word] for s in segs for w in s.words]}
(A / "transcripts.json").write_text(json.dumps(out, indent=0, ensure_ascii=False), encoding="utf-8")
print("".join(w[2] for w in out["IMG_5941"]), flush=True)
print("ALL DONE", flush=True)
