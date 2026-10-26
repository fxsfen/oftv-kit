"""Accurate pass: faster-whisper large-v3 (Spanish, no VAD, word timestamps), incremental save."""
import json, subprocess, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from faster_whisper import WhisperModel

SRC = Path(r"C:\Users\fosfe\Downloads\ее")
OUT = Path(__file__).resolve().parents[1] / "assets" / "analysis"
bounds = json.load(open(OUT / "speech_bounds.json"))
dst = OUT / "transcripts.json"
res = json.load(open(dst, encoding="utf-8")) if dst.exists() else {}
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
for c in sorted(SRC.glob("*.MOV")):
    if c.stem in res or bounds[c.stem].get("no_audio"):
        continue
    segs, _ = m.transcribe(str(c), language="es", vad_filter=False, word_timestamps=True,
                           condition_on_previous_text=False, beam_size=5, temperature=0.0)
    words = [{"word": w.word, "start": round(w.start, 2), "end": round(w.end, 2), "p": round(w.probability, 2)}
             for s in segs for w in (s.words or [])]
    res[c.stem] = words
    print(c.stem, "".join(w["word"] for w in words), flush=True)
    dst.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
print("ALL DONE", flush=True)
