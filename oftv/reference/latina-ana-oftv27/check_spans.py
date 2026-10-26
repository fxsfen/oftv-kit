import sys, json
import soundfile as sf
from faster_whisper import WhisperModel
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
W = "projects/latina-ana-oftv27/assets/analysis/wav16/"
for key, a, b in [("vo16", 62.5, 73.1), ("vo4", 47.2, 58.0), ("vo4", 59.8, 68.0), ("vo4", 81.9, 89.7), ("vo4", 21.2, 35.4), ("vo4", 101.5, 105.7)]:
    x, sr = sf.read(W + key + ".wav", dtype="float32")
    segs, _ = m.transcribe(x[int(a*sr):int(b*sr)], language="en", vad_filter=False, word_timestamps=True,
                           condition_on_previous_text=False, beam_size=5, temperature=0.0,
                           initial_prompt="Turning home clothes into an alternative outfit: sheer mesh top, silver chains, choker, rings, studded belt, chunky boots, dark makeup.")
    print(key, a, b, " ".join(f"{w.word.strip()}@{w.start+a:.2f}" for s in segs for w in s.words), flush=True)
