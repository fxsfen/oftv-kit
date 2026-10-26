"""Re-transcribe a rendered preview (small model, word times) to catch doubled / clipped words at splices."""
import sys
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8")
segs, _ = m.transcribe(sys.argv[1], language=sys.argv[2] if len(sys.argv) > 2 else "en", vad_filter=False,
                       condition_on_previous_text=False, temperature=0.0)
for s in segs:
    print(f"{int(s.start // 60)}:{s.start % 60:05.2f} {s.text.strip()}", flush=True)
