"""Face sheets of every take: one frame per second, centre crop, label = real seconds. Usage: face_sheets.py <29|30>"""
import json, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
N = sys.argv[1]
AN = Path(__file__).resolve().parents[2] / f"bela-cruz-{N}" / "assets" / "analysis"
S = json.load(open(AN / "sources.json", encoding="utf-8"))
out = AN / "faces"
out.mkdir(exist_ok=True)

def one(k):
    d = S["dur"][k]
    n = max(1, int(d))
    tmp = out / f"_{k}"
    tmp.mkdir(exist_ok=True)
    for i in range(n):
        t = i + 0.5
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", S["sources"][k], "-frames:v", "1", "-vf",
                        "crop=iw*0.5:ih*0.75:iw*0.25:0,scale=-2:240,drawtext=fontfile='C\:/Windows/Fonts/arial.ttf':"
                        f"text='{k} {t:.1f}':x=4:y=4:fontsize=20:fontcolor=yellow:box=1:boxcolor=black@0.6",
                        str(tmp / f"{i:02d}.jpg")])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp / "%02d.jpg"), "-vf", f"tile=16x{-(-n // 16)}:color=black",
                    "-frames:v", "1", str(out / f"{k}.jpg")])

keys = [k for k in S["sources"] if k.startswith("e") and "t" in k]
with ThreadPoolExecutor(3) as ex:
    list(ex.map(one, keys))
print("faces done")
