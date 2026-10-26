"""Word-level transcripts of both sources from the Demucs vocal stems (faster-whisper large-v3-turbo, CPU int8).

Run after separate.py: on the clean stem Whisper does not loop on music (A took 27 min on the mixed track).
Language is auto-detected per source and stored in the transcript.
"""
import json, sys, time
from pathlib import Path
from faster_whisper import WhisperModel

PROJ = Path(__file__).resolve().parents[1]
m = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=8)
for key in sys.argv[1:]:
    t = time.time()
    segs, info = m.transcribe(str(PROJ / f"assets/audio/{key}_vocals.wav"), word_timestamps=True,
                              vad_filter=False, condition_on_previous_text=False, beam_size=5,
                              temperature=[0.0, 0.2])
    words, sents = [], []
    for s in segs:
        sents.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()})
        for w in s.words:
            words.append({"word": w.word, "start": round(w.start, 2), "end": round(w.end, 2), "p": round(w.probability, 3)})
    json.dump({"language": info.language, "segments": sents, "words": words},
              open(PROJ / f"assets/analysis/transcript_{key}.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(key, info.language, len(words), "words", round(time.time() - t), "s", flush=True)
