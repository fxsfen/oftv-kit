"""Per-second sharpness of lana b-roll (ffmpeg blurdetect on a 960 px proxy, 5 fps): higher blur = softer frame."""
import json, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
AN = Path(__file__).resolve().parents[1] / "assets/analysis"
S = json.load(open(AN / "sources.json", encoding="utf-8"))
keys = [k for k in S["sources"] if k.startswith("IMG") and k not in ("IMG_1070", "IMG_1084")]

def one(k):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", S["sources"][k], "-vf",
                        "fps=5,scale=960:-2,blurdetect=block_width=32:block_height=32,metadata=print:file=-",
                        "-an", "-f", "null", "-"], capture_output=True, text=True, errors="replace")
    vals = [float(x) for x in re.findall(r"lavfi.blur=([\d.]+)", r.stdout)]
    per = [round(sum(vals[i:i + 5]) / len(vals[i:i + 5]), 2) for i in range(0, len(vals), 5)]
    return k, per

with ThreadPoolExecutor(4) as ex:
    res = dict(ex.map(one, keys))
(AN / "blur_per_sec.json").write_text(json.dumps(res, indent=0), encoding="utf-8")
for k, v in sorted(res.items()):
    print(k, " ".join(f"{x:.1f}" for x in v))
