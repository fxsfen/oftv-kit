"""B-roll safety check: Silero VAD speech on camera audio + face-crop sheets every 3 s."""
import json, subprocess
from pathlib import Path

import numpy as np
from faster_whisper.vad import VadOptions, get_speech_timestamps

SRC = Path(r"C:\Users\fosfe\Downloads\Новая папка (14)")
OUT = Path(__file__).resolve().parents[1] / "assets" / "analysis"
FACES = OUT / "faces"
FACES.mkdir(parents=True, exist_ok=True)
BROLL = ["IMG_2975", "IMG_2976", "IMG_2978", "IMG_2979", "IMG_2980", "IMG_2981", "IMG_2983", "IMG_2984",
         "IMG_2986", "IMG_2987", "IMG_2988", "IMG_2989", "IMG_2990", "IMG_2991", "IMG_2992", "IMG_2993"]

res = {}
for c in BROLL:
    p = SRC / f"{c}.MOV"
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    ts = get_speech_timestamps(x, VadOptions(threshold=0.5, min_speech_duration_ms=200))
    res[c] = [[round(t["start"] / 16000, 2), round(t["end"] / 16000, 2)] for t in ts]
    print(c, res[c], flush=True)
    vf = ("fps=1/3,crop=iw*0.5:ih*0.6:iw*0.25:0,scale=260:-2,"
          f"drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='{c[4:]} %{{pts\\:hms}}':x=4:y=4:fontsize=16:"
          "fontcolor=yellow:box=1:boxcolor=black@0.6,tile=12x3")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(p), "-vf", vf, "-frames:v", "1",
                    str(FACES / f"{c}.jpg")], check=True)
(OUT / "camera_speech.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
