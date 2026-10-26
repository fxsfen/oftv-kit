"""Word-level transcripts of both sources (faster-whisper large-v3, CPU int8)."""
import json, sys, time
from pathlib import Path
from faster_whisper import WhisperModel

PROJ = Path(__file__).resolve().parents[1]
m = WhisperModel("large-v3", device="cpu", compute_type="int8", cpu_threads=8)
out = {}
for key in sys.argv[1:]:
    t = time.time()
    segs, info = m.transcribe(str(PROJ / f"assets/audio/{key}_48k.wav"), language="en", word_timestamps=True,
                              vad_filter=False, condition_on_previous_text=False, beam_size=5)
    words, sents = [], []
    for s in segs:
        sents.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()})
        for w in s.words:
            words.append({"word": w.word, "start": round(w.start, 2), "end": round(w.end, 2), "p": round(w.probability, 3)})
    json.dump({"segments": sents, "words": words}, open(PROJ / f"assets/analysis/transcript_{key}.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(key, len(words), "words", round(time.time() - t), "s", flush=True)
