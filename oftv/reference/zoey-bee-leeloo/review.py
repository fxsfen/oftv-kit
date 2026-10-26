"""Review sheet per timeline item: frames every `step` s of source (labelled item/time) + the words spoken."""
import json, subprocess, sys
from pathlib import Path
P = Path(__file__).resolve().parents[1]
tl = json.load(open(P / "artifacts/timeline.json", encoding="utf-8"))
tr = json.load(open(P / "assets/analysis/transcripts.json", encoding="utf-8"))
out = P / "assets/review"
for n, v in enumerate(tl["video"]):
    if v["group"] == "outro" and v["src"] == "IMG_1371":
        pass
    a, b = v["in"], v["out"]
    step = 1.0 if v.get("speech") else 2.5
    ts = [a + 0.2 + k * step for k in range(int((b - a - 0.2) / step) + 1)]
    if ts[-1] < b - 0.4:
        ts.append(b - 0.3)
    imgs = []
    for k, t in enumerate(ts):
        f = out / f"_{n:02d}_{k:02d}.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", tl["sources"][v["src"]], "-frames:v", "1",
                        "-vf", f"scale=240:-2,drawtext=fontfile='C\:/Windows/Fonts/arial.ttf':text='{n} {t:.1f}':"
                               "x=3:y=3:fontsize=16:fontcolor=yellow:box=1:boxcolor=black", str(f)])
        imgs.append(f)
    cols = 12
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(out / f"_{n:02d}_%02d.jpg"), "-vf",
                    f"tile={cols}x{-(-len(imgs) // cols)}:color=black", "-frames:v", "1", str(out / f"item_{n:02d}.jpg")])
    words = " ".join(f"{w['word'].strip()}@{w['start']:.1f}" for w in tr[v["src"]] if a <= w["start"] < b)
    print(f"[{n}] {v['src']} {a}-{b} {'SPEECH' if v.get('speech') else 'FAST x' + str(v.get('speed'))} :: {words}", flush=True)
