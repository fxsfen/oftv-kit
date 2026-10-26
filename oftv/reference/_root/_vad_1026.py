"""Silero VAD speech ranges for every wav16 of a project -> assets/analysis/camera_speech.json"""
import json, sys
from pathlib import Path
import soundfile as sf
from faster_whisper.vad import VadOptions, get_speech_timestamps
A = Path(__file__).resolve().parent / sys.argv[1] / "assets/analysis"
out = {}
for w in sorted((A / "wav16").glob("*.wav")):
    x, sr = sf.read(str(w), dtype="float32")
    ts = get_speech_timestamps(x, VadOptions(threshold=0.4, min_speech_duration_ms=150, min_silence_duration_ms=300))
    out[w.stem] = [[round(t["start"] / sr, 2), round(t["end"] / sr, 2)] for t in ts]
(A / "camera_speech.json").write_text(json.dumps(out, indent=0, ensure_ascii=False), encoding="utf-8")
for k, v in out.items():
    print(k, v)
