"""large-v3 accurate pass with word dicts (plan_common format) for selected stems of one project.
usage: python _accurate_words_1026.py <project> <stem> [<stem> ...]"""
import json, sys, unicodedata
from pathlib import Path
from faster_whisper import WhisperModel

A = Path(__file__).resolve().parent / sys.argv[1] / "assets/analysis"
dst = A / "transcripts.json"
out = json.loads(dst.read_text(encoding="utf-8")) if dst.exists() else {}
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
WAVS = {unicodedata.normalize("NFC", w.stem): w for w in (A / "wav16").glob("*.wav")}
for k in sys.argv[2:]:
    wav = WAVS[unicodedata.normalize("NFC", k)]
    k = wav.stem   # keep the on-disk (possibly NFD) stem as the key, like sources.json
    if k in out:
        continue
    segs, _ = m.transcribe(str(wav), language="en", vad_filter=False, word_timestamps=True,
                           condition_on_previous_text=False, temperature=0.0, beam_size=5)
    out[k] = [{"word": w.word, "start": round(w.start, 2), "end": round(w.end, 2), "p": round(w.probability, 2)}
              for s in segs for w in (s.words or [])]
    print(k, "".join(w["word"] for w in out[k]), flush=True)
    dst.write_text(json.dumps(out, indent=0, ensure_ascii=False), encoding="utf-8")
print("ALL DONE", flush=True)
