"""large-v3 accurate pass (no VAD, word times) for selected clips of one project.
usage: python _accurate_batch.py <project> <lang> <stem> [<stem> ...]   (stems of assets/analysis/wav16/*.wav)"""
import json, sys
from pathlib import Path
from faster_whisper import WhisperModel

A = Path(__file__).resolve().parent / sys.argv[1] / "assets/analysis"
lang = sys.argv[2]
dst = A / "transcripts.json"
out = json.loads(dst.read_text(encoding="utf-8")) if dst.exists() else {}
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
for k in sys.argv[3:]:
    if k in out:
        continue
    segs, _ = m.transcribe(str(A / "wav16" / f"{k}.wav"), language=lang, vad_filter=False, word_timestamps=True,
                           condition_on_previous_text=False, temperature=0.0)
    out[k] = [[round(w.start, 2), round(w.end, 2), w.word] for s in segs for w in s.words]
    print(k, "".join(w[2] for w in out[k]), flush=True)
    dst.write_text(json.dumps(out, indent=0, ensure_ascii=False), encoding="utf-8")
print("ALL DONE", flush=True)
