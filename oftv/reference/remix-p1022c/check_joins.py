"""Transcribe +-2.4 s around every join of the rendered speech bed to catch clipped or leaked words."""
import json
import subprocess
import sys
from pathlib import Path

from faster_whisper import WhisperModel

PROJ = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
t = json.load(open(PROJ / "artifacts/timeline.json", encoding="utf-8"))["items"]
m = WhisperModel("large-v3", device="cpu", compute_type="int8", cpu_threads=8)
snip = PROJ / "work_audio/snip_join.wav"
out = []
for a, b in zip(t, t[1:]):
    end = a["a_at"] + a["a_out"] - a["a_in"]
    st = b["a_at"]
    s0 = end - 2.4
    d = (st + 2.4) - s0
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{s0:.2f}", "-t", f"{d:.2f}",
                    "-i", str(PROJ / "work_audio/speech_bed.wav"), "-ac", "1", "-ar", "16000", str(snip)], check=True)
    segs, _ = m.transcribe(str(snip), language="en")
    line = f"{a['i']:>2}->{b['i']:<2} {a['src']}{a['a_out']:.2f}|{b['src']}{b['a_in']:.2f} @{st:7.2f} | " + \
        " ".join(x.text.strip() for x in segs)
    print(line, flush=True)
    out.append(line)
(PROJ / "artifacts/joins.txt").write_text("\n".join(out), encoding="utf-8")
