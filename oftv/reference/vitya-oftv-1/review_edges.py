"""Edge review sheets: for every on-camera item of the given clip prefix, frames every 0.25 s over the first and the
last 2 s of the item (as used in the edit), labelled with source time and the first/last word times."""
import json
import subprocess
import sys
from pathlib import Path

PROJ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJ / "scripts"))
import plan_timeline as P  # noqa: E402

OUT = PROJ / "assets/analysis/edges"
OUT.mkdir(parents=True, exist_ok=True)
pref = sys.argv[1] if len(sys.argv) > 1 else "IMG_08"
tl = json.load(open(PROJ / "artifacts/timeline.json", encoding="utf-8"))
items = [v for v in tl["video"] if v.get("speech") and v["src"].startswith(pref)]
for v in items:
    k, a, b = v["src"], v["in"], v["out"]
    ws = [w for w in P.words(k) if a - 0.05 <= w[0] < b]
    lab = f"{k[-4:]} {a:.2f}-{b:.2f} words {ws[0][0]:.2f}-{ws[-1][1]:.2f}" if ws else f"{k} no words"
    ts = [a + i * 0.25 for i in range(9)] + [b - 2 + i * 0.25 for i in range(9)]
    tiles = []
    for j, t in enumerate(ts):
        f = OUT / f"_{j:02d}.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(0, t):.2f}", "-i", str(P.SRC / f"{k}.MOV"), "-frames:v", "1",
                        "-vf", f"scale=200:-2,drawtext=fontfile='C\:/Windows/Fonts/arial.ttf':text='{t:.2f}':x=2:y=2:"
                               "fontsize=16:fontcolor=yellow:box=1:boxcolor=black@0.6", str(f)], check=False)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(OUT / "_%02d.jpg"), "-vf",
                    f"tile=9x2,pad=iw:ih+30:0:30,drawtext=fontfile='C\:/Windows/Fonts/arial.ttf':text='{lab}':x=4:y=4:"
                    "fontsize=22:fontcolor=white", "-frames:v", "1", str(OUT / f"{k[-4:]}_{a:.0f}.jpg")], check=True)
    print(lab, flush=True)
