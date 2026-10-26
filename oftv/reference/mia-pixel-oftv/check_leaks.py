"""Transcribe the rendered preview audio to catch leaked retake words / swearing at splices."""
import sys
from faster_whisper import WhisperModel
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
segs, _ = m.transcribe(sys.argv[1], language="ru", vad_filter=False, condition_on_previous_text=False, word_timestamps=True)
for s in segs:
    print(f"{s.start:7.2f}-{s.end:7.2f} {s.text.strip()}", flush=True)
